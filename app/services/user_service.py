from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserUpdate


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, session: Session, user_id: int) -> Optional[User]:
        """Получить пользователя по ID"""
        return await self.user_repository.get_by_id(session, user_id)

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
        """Обновить пользователя"""
        return await self.user_repository.update(session, user_id, user_data)

    async def delete(self, session: Session, user_id: int) -> None:
        """Удалить пользователя"""
        await self.user_repository.delete(session, user_id)
