import json
import logging
from datetime import datetime
from typing import List, Optional

import redis
from sqlalchemy.orm import Session

from app.cache.redis_client import get_redis
from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserUpdate

logger = logging.getLogger(__name__)


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.cache_prefix = "user:"

    def _cache_key(self, user_id: int) -> str:
        return f"{self.cache_prefix}{user_id}"

    def _user_to_dict(self, user: User) -> dict:
        """Преобразование User в словарь для JSON"""
        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "description": user.description,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }

    def _dict_to_user(self, data: dict) -> User:
        """Создание User из словаря (только для кеша)"""
        # Конвертация строк обратно в datetime
        user_data = data.copy()

        if user_data.get("created_at"):
            user_data["created_at"] = datetime.fromisoformat(user_data["created_at"])
        if user_data.get("updated_at"):
            user_data["updated_at"] = datetime.fromisoformat(user_data["updated_at"])

        # Создаём объект User без привязки к сессии
        user = User(
            id=user_data["id"],
            username=user_data["username"],
            email=user_data["email"],
            description=user_data["description"],
            created_at=user_data["created_at"],
            updated_at=user_data["updated_at"],
        )
        return user

    async def get_by_id(self, session: Session, user_id: int) -> Optional[User]:
        """Получить пользователя по ID с кешированием"""
        redis_client = get_redis()

        # Пробуем получить из кеша
        if redis_client:
            cached_data = redis_client.get(self._cache_key(user_id))
            if cached_data:
                logger.info(f"🟢 [CACHE HIT] User {user_id} found in Redis")
                try:
                    data = json.loads(cached_data)
                    return self._dict_to_user(data)
                except (json.JSONDecodeError, KeyError) as e:
                    logger.warning(
                        f"🔴 [CACHE ERROR] Invalid cache for user {user_id}: {e}"
                    )
                    # Удаляем повреждённый кеш
                    try:
                        redis_client.delete(self._cache_key(user_id))
                    except (json.JSONDecodeError, ValueError):
                        pass
            else:
                logger.info(f"🟡 [CACHE MISS] User {user_id} not in Redis")
        else:
            logger.info(f"🔵 [NO REDIS] Redis not available for user {user_id}")

        # Получаем из БД
        logger.info(f"📊 [DB QUERY] Fetching user {user_id} from database")
        user = await self.user_repository.get_by_id(session, user_id)

        # Сохраняем в кеш
        if user and redis_client:
            logger.info(f"💾 [CACHE SAVE] Saving user {user_id} to Redis")
            try:
                data = self._user_to_dict(user)
                redis_client.setex(self._cache_key(user_id), 3600, json.dumps(data))
                logger.info(f"✅ [CACHE SAVED] User {user_id} cached successfully")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"❌ [CACHE FAILED] Failed to cache user {user_id}: {e}")

        return user

    async def get_by_filter(
        self, session: Session, count: int = 10, page: int = 1, **kwargs
    ) -> List[User]:
        """Получить пользователей с фильтрацией и пагинацией"""
        return await self.user_repository.get_by_filter(
            session, count=count, page=page, **kwargs
        )

    async def create(self, session: Session, user_data: UserCreate) -> User:
        """Создать нового пользователя"""
        return await self.user_repository.create(session, user_data)

    async def update(
        self, session: Session, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        """Обновить пользователя и инвалидировать кеш"""
        user = await self.user_repository.update(session, user_id, user_data)

        # Удаляем кеш при обновлении
        redis_client = get_redis()
        if redis_client:
            logger.info(f"🗑️ [CACHE INVALIDATE] Deleting cache for user {user_id}")
            try:
                deleted = redis_client.delete(self._cache_key(user_id))
                if deleted:
                    logger.info(f"✅ [CACHE DELETED] Cache for user {user_id} removed")
                else:
                    logger.info(f"ℹ️ [NO CACHE] No cache found for user {user_id}")
            except redis.RedisError as e:
                logger.warning(
                    f"❌ [CACHE DELETE ERROR] Failed to delete cache for user {user_id}: {e}"
                )
        else:
            logger.info(
                f"🔵 [NO REDIS] Redis not available, cache not invalidated for user {user_id}"
            )

        return user

    async def delete(self, session: Session, user_id: int) -> None:
        """Удалить пользователя и инвалидировать кеш"""
        # Сначала удаляем кеш, потом из БД
        redis_client = get_redis()
        if redis_client:
            logger.info(
                f"🗑️ [CACHE INVALIDATE] Deleting cache before removing user {user_id}"
            )
            try:
                deleted = redis_client.delete(self._cache_key(user_id))
                if deleted:
                    logger.info(
                        f"✅ [CACHE DELETED] Cache for user {user_id} removed before deletion"
                    )
                else:
                    logger.info(f"ℹ️ [NO CACHE] No cache found for user {user_id}")
            except redis.RedisError as e:
                logger.warning(
                    f"❌ [CACHE DELETE ERROR] Failed to delete cache for user {user_id}: {e}"
                )
        else:
            logger.info(
                f"🔵 [NO REDIS] Redis not available, cache not invalidated for user {user_id}"
            )

        # Удаляем пользователя из БД
        logger.info(f"🗑️ [DB DELETE] Removing user {user_id} from database")
        await self.user_repository.delete(session, user_id)
        logger.info(f"✅ [DB DELETED] User {user_id} removed from database")
