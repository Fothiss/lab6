from typing import List, Optional

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from litestar.params import Body, Parameter
from sqlalchemy.orm import Session

from app.schemas import UserCreate, UserResponse, UserUpdate
from app.services.user_service import UserService


class UserController(Controller):
    path = "/users"

    @get("/{user_id:int}")
    async def get_user_by_id(
        self, user_service: UserService, session: Session, user_id: int = Parameter()
    ) -> UserResponse:
        user = await user_service.get_by_id(session, user_id)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        session: Session,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(ge=1, default=1),
        username: Optional[str] = Parameter(default=None),
        email: Optional[str] = Parameter(default=None),
    ) -> List[UserResponse]:
        filters = {}
        if username:
            filters["username"] = username
        if email:
            filters["email"] = email

        users = await user_service.get_by_filter(
            session, count=count, page=page, **filters
        )
        return [UserResponse.model_validate(user) for user in users]

    @post()
    async def create_user(
        self,
        user_service: UserService,
        session: Session,
        data: UserCreate = Body(),
    ) -> UserResponse:
        user = await user_service.create(session, data)
        return UserResponse.model_validate(user)

    @put("/{user_id:int}")
    async def update_user(
        self,
        user_service: UserService,
        session: Session,
        user_id: int = Parameter(),
        data: UserUpdate = Body(),
    ) -> UserResponse:
        user = await user_service.update(session, user_id, data)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        return UserResponse.model_validate(user)

    @delete("/{user_id:int}")
    async def delete_user(
        self,
        user_service: UserService,
        session: Session,
        user_id: int = Parameter(),
    ) -> None:
        await user_service.delete(session, user_id)
