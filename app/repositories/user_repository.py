from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import User
from app.schemas import UserCreate, UserUpdate


class UserRepository:
    def __init__(self):
        self.model = User

    async def get_by_id(self, session: Session, user_id: int) -> Optional[User]:
        return session.query(self.model).filter(self.model.id == user_id).first()

    async def get_by_filter(
        self, session: Session, count: int = 10, page: int = 1, **kwargs
    ) -> List[User]:
        query = session.query(self.model)
        for attr, value in kwargs.items():
            query = query.filter(getattr(self.model, attr) == value)
        return query.offset((page - 1) * count).limit(count).all()

    async def create(self, session: Session, user_data: UserCreate) -> User:
        user = self.model(
            username=user_data.username,
            email=user_data.email,
            description=user_data.description or "",
        )
        session.add(user)
        session.commit()
        session.refresh(user)
        return user

    async def update(
        self, session: Session, user_id: int, user_data: UserUpdate
    ) -> Optional[User]:
        user = session.query(self.model).filter(self.model.id == user_id).first()
        if not user:
            return None
        data = user_data.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(user, k, v)
        session.commit()
        session.refresh(user)
        return user

    async def delete(self, session: Session, user_id: int) -> None:
        user = session.query(self.model).filter(self.model.id == user_id).first()
        if user:
            session.delete(user)
            session.commit()
