import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from aio_pika.exceptions import AMQPError

from app.messaging.producer import publish_product_created
from app.models import Product
from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate, ProductUpdate


logger = logging.getLogger(__name__)


class ProductService:
    def __init__(self, product_repository: ProductRepository) -> None:
        self.product_repository = product_repository

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
        return await self.product_repository.get_by_id(session, product_id)

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
        return await self.product_repository.update(session, product_id, product_data)

    async def delete_product(self, session: Session, product_id: int) -> bool:
        return await self.product_repository.delete(session, product_id)

    async def update_stock(
        self, session: Session, product_id: int, quantity_change: int
    ) -> Optional[Product]:
        return await self.product_repository.update_stock(
            session, product_id, quantity_change
        )
