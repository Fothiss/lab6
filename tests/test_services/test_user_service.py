import asyncio

from app.schemas import UserCreate, UserUpdate
from app.services.user_service import UserService


class TestUserService:
    def test_create_user(self, session, user_service: UserService):
        async def _run():
            user = await user_service.create(
                session,
                UserCreate(username="service_user_1", email="service1@example.com"),
            )
            assert user.username == "service_user_1"
            assert user.email == "service1@example.com"

        asyncio.run(_run())

    def test_get_users(self, session, user_service: UserService):
        async def _run():
            await user_service.create(
                session,
                UserCreate(username="service_user_2a", email="service2a@example.com"),
            )
            await user_service.create(
                session,
                UserCreate(username="service_user_2b", email="service2b@example.com"),
            )

            users = await user_service.get_by_filter(session, count=10, page=1)
            assert len(users) >= 2

        asyncio.run(_run())

    def test_update_user(self, session, user_service: UserService):
        async def _run():
            created = await user_service.create(
                session,
                UserCreate(
                    username="service_user_3",
                    email="service3@example.com",
                    description="old description",
                ),
            )

            updated = await user_service.update(
                session,
                created.id,
                UserUpdate(description="updated via service"),
            )
            assert updated is not None
            assert updated.description == "updated via service"
            assert updated.username == "service_user_3"

        asyncio.run(_run())

    def test_delete_user(self, session, user_service: UserService):
        async def _run():
            created = await user_service.create(
                session,
                UserCreate(username="service_user_4", email="service4@example.com"),
            )

            await user_service.delete(session, created.id)
            found = await user_service.get_by_id(session, created.id)
            assert found is None

        asyncio.run(_run())
