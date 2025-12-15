import json
import logging
from datetime import datetime
from typing import List, Optional

import redis
from aio_pika.exceptions import AMQPError
from sqlalchemy.orm import Session

from app.cache.redis_client import get_redis
from app.messaging.producer import publish_product_created
from app.models import Product
from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate, ProductUpdate

logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository
        self.cache_prefix = "product:"

    def _cache_key(self, product_id: int) -> str:
        return f"{self.cache_prefix}{product_id}"

    def _product_to_dict(self, product: Product) -> dict:
        """Преобразование Product в словарь для JSON"""
        return {
            "id": product.id,
            "name": product.name,
            "description": product.description,
            "price": float(product.price),  # Decimal -> float для JSON
            "stock_quantity": product.stock_quantity,
            "created_at": (
                product.created_at.isoformat() if product.created_at else None
            ),
            "updated_at": (
                product.updated_at.isoformat() if product.updated_at else None
            ),
        }

    def _dict_to_product(self, data: dict) -> Product:
        """Создание Product из словаря (только для кеша)"""
        product_data = data.copy()

        # Конвертация строк обратно в datetime
        if product_data.get("created_at"):
            product_data["created_at"] = datetime.fromisoformat(
                product_data["created_at"]
            )
        if product_data.get("updated_at"):
            product_data["updated_at"] = datetime.fromisoformat(
                product_data["updated_at"]
            )

        # Конвертация float обратно (SQLAlchemy сам конвертирует в Decimal)
        return Product(**product_data)

    async def create_product(
        self, session: Session, product_data: ProductCreate
    ) -> Product:
        product = await self.product_repository.create(session, product_data)

        try:
            await publish_product_created(
                product_id=product.id, name=product.name, price=product.price
            )
        except (ConnectionError, AMQPError, TimeoutError) as e:
            logger.error(f"RabbitMQ connection error: {e}")

        return product

    async def get_product(self, session: Session, product_id: int) -> Optional[Product]:
        """Получить продукт по ID с кешированием на 10 минут"""
        redis_client = get_redis()

        # Пробуем получить из кеша
        if redis_client:
            cached_data = redis_client.get(self._cache_key(product_id))
            if cached_data:
                logger.info(f"🟢 [CACHE HIT] Product {product_id} found in Redis")
                try:
                    data = json.loads(cached_data)
                    return self._dict_to_product(data)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(
                        f"🔴 [CACHE ERROR] Invalid cache for product {product_id}: {e}"
                    )
                    # Удаляем повреждённый кеш
                    try:
                        redis_client.delete(self._cache_key(product_id))
                    except (json.JSONDecodeError, ValueError):
                        pass
            else:
                logger.info(f"🟡 [CACHE MISS] Product {product_id} not in Redis")
        else:
            logger.info(f"🔵 [NO REDIS] Redis not available for product {product_id}")

        # Получаем из БД
        logger.info(f"📊 [DB QUERY] Fetching product {product_id} from database")
        product = await self.product_repository.get_by_id(session, product_id)

        # Сохраняем в кеш
        if product and redis_client:
            logger.info(f"💾 [CACHE SAVE] Saving product {product_id} to Redis")
            try:
                data = self._product_to_dict(product)
                redis_client.setex(
                    self._cache_key(product_id), 600, json.dumps(data)
                )  # 10 минут
                logger.info(f"✅ [CACHE SAVED] Product {product_id} cached for 600s")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(
                    f"❌ [CACHE FAILED] Failed to cache product {product_id}: {e}"
                )

        return product

    async def list_products(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
        name: Optional[str] = None,
        min_price: Optional[float] = None,
        max_price: Optional[float] = None,
    ) -> List[Product]:
        filters = {}
        if name:
            filters["name"] = name

        products = await self.product_repository.get_list(
            session, count=count, page=page, **filters
        )

        if min_price is not None:
            products = [p for p in products if float(p.price) >= min_price]
        if max_price is not None:
            products = [p for p in products if float(p.price) <= max_price]

        return products

    async def update_product(
        self, session: Session, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        """Обновить продукт и инвалидировать кеш"""
        product = await self.product_repository.update(
            session, product_id, product_data
        )

        # Удаляем кеш при обновлении
        redis_client = get_redis()
        if redis_client:
            logger.info(f"🗑️ [CACHE INVALIDATE] Deleting cache for product {product_id}")
            try:
                deleted = redis_client.delete(self._cache_key(product_id))
                if deleted:
                    logger.info(
                        f"✅ [CACHE DELETED] Cache for product {product_id} removed"
                    )
                else:
                    logger.info(f"ℹ️ [NO CACHE] No cache found for product {product_id}")
            except redis.RedisError as e:
                logger.warning(
                    f"❌ [CACHE DELETE ERROR] Failed to delete cache for product {product_id}: {e}"
                )
        else:
            logger.info(
                f"🔵 [NO REDIS] Redis not available, cache not invalidated for product {product_id}"
            )

        return product

    async def delete_product(self, session: Session, product_id: int) -> bool:
        """Удалить продукт и инвалидировать кеш"""
        # Сначала удаляем кеш
        redis_client = get_redis()
        if redis_client:
            logger.info(
                f"🗑️ [CACHE INVALIDATE] Deleting cache before removing product {product_id}"
            )
            try:
                deleted = redis_client.delete(self._cache_key(product_id))
                if deleted:
                    logger.info(
                        f"✅ [CACHE DELETED] Cache for product {product_id} removed before deletion"
                    )
                else:
                    logger.info(f"ℹ️ [NO CACHE] No cache found for product {product_id}")
            except redis.RedisError as e:
                logger.warning(
                    f"❌ [CACHE DELETE ERROR] Failed to delete cache for product {product_id}: {e}"
                )
        else:
            logger.info(
                f"🔵 [NO REDIS] Redis not available, cache not invalidated for product {product_id}"
            )

        # Удаляем из БД
        logger.info(f"🗑️ [DB DELETE] Removing product {product_id} from database")
        result = await self.product_repository.delete(session, product_id)
        logger.info(f"✅ [DB DELETED] Product {product_id} removed from database")

        return result

    async def update_stock(
        self, session: Session, product_id: int, quantity_change: int
    ) -> Optional[Product]:
        return await self.product_repository.update_stock(
            session, product_id, quantity_change
        )
