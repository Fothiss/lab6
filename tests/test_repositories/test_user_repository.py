import asyncio

from app.repositories.user_repository import UserRepository
from app.schemas import UserCreate, UserUpdate


class TestUserRepository:
    def test_create_user(self, session, user_repository: UserRepository):
        async def _run():
            user = await user_repository.create(
                session,
                UserCreate(username="test_user_1", email="test1@example.com"),
            )
            assert user.id is not None
            assert user.username == "test_user_1"
            assert user.email == "test1@example.com"

        asyncio.run(_run())

    def test_get_by_filter_returns_list(self, session, user_repository: UserRepository):
        async def _run():
            await user_repository.create(
                session,
                UserCreate(username="test_user_2a", email="test2a@example.com"),
            )
            await user_repository.create(
                session,
                UserCreate(username="test_user_2b", email="test2b@example.com"),
            )

            users = await user_repository.get_by_filter(session, count=10, page=1)
            usernames = sorted([user.username for user in users])
            assert "test_user_2a" in usernames
            assert "test_user_2b" in usernames

        asyncio.run(_run())

    def test_update_user(self, session, user_repository: UserRepository):
        async def _run():
            created = await user_repository.create(
                session,
                UserCreate(
                    username="test_user_3", email="test3@example.com", description="old"
                ),
            )

            updated = await user_repository.update(
                session,
                created.id,
                UserUpdate(description="new description"),
            )
            assert updated is not None
            assert updated.description == "new description"
            assert updated.username == "test_user_3"

        asyncio.run(_run())

    def test_delete_user(self, session, user_repository: UserRepository):
        async def _run():
            created = await user_repository.create(
                session,
                UserCreate(username="test_user_4", email="test4@example.com"),
            )

            await user_repository.delete(session, created.id)
            deleted = await user_repository.get_by_id(session, created.id)
            assert deleted is None

        asyncio.run(_run())
