import os
import sys

import pytest
from litestar import Litestar
from litestar.di import Provide
from litestar.testing import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.controllers.user_controller import UserController
from app.models import Base
from app.repositories import OrderRepository, ProductRepository, UserRepository
from app.services import OrderService, UserService

TEST_DATABASE_URL = "sqlite:///./test.db"


@pytest.fixture(scope="session")
def engine():
    engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    yield engine
    Base.metadata.drop_all(engine)
    engine.dispose()


@pytest.fixture
def session(engine) -> Session:
    connection = engine.connect()
    transaction = connection.begin()
    SessionLocal = sessionmaker(bind=connection)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()


@pytest.fixture
def user_repository():
    return UserRepository()


@pytest.fixture
def product_repository():
    return ProductRepository()


@pytest.fixture
def order_repository():
    return OrderRepository()


@pytest.fixture
def user_service(user_repository):
    return UserService(user_repository)


@pytest.fixture
def order_service(order_repository, product_repository, user_repository):
    return OrderService(order_repository, product_repository, user_repository)


@pytest.fixture
def test_client(session, user_repository, user_service):
    def get_session() -> Session:
        return session

    def get_user_repository():
        return user_repository

    def get_user_service():
        return user_service

    # СОЗДАЕМ ТЕСТОВОЕ ПРИЛОЖЕНИЕ с тестовыми зависимостями
    app = Litestar(
        route_handlers=[UserController],
        dependencies={
            "session": Provide(get_session, sync_to_thread=False),
            "user_repository": Provide(get_user_repository, sync_to_thread=False),
            "user_service": Provide(get_user_service, sync_to_thread=False),
        },
    )

    with TestClient(app=app) as client:
        yield client
