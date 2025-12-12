import logging
import os
import traceback

from dotenv import load_dotenv
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.controllers import OrderController, ProductController, UserController
from app.repositories import OrderRepository, ProductRepository, UserRepository
from app.services import OrderService, ProductService, UserService

# Включаем подробное логирование
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

load_dotenv()

# Настройка базы данных
DB_URL = os.getenv("DB_URL", "sqlite:///./lab3.db")

# Создаем синхронный движок
engine = create_engine(DB_URL, echo=True)

# Создаем фабрику для синхронных сессий
session_factory = sessionmaker(engine, expire_on_commit=False)


def provide_session() -> Session:
    """Провайдер сессии базы данных"""
    session = session_factory()
    try:
        yield session
    except Exception as e:
        logger.error(f"Session error: {e}")
        logger.error(traceback.format_exc())
        raise
    finally:
        session.close()


def provide_user_repository() -> UserRepository:
    return UserRepository()


def provide_order_repository() -> OrderRepository:
    return OrderRepository()


def provide_product_repository() -> ProductRepository:
    return ProductRepository()


def provide_user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)


def provide_order_service(
    order_repository: OrderRepository,
    product_repository: ProductRepository,
    user_repository: UserRepository,
) -> OrderService:
    return OrderService(order_repository, product_repository, user_repository)


def provide_product_service(product_repository: ProductRepository) -> ProductService:
    return ProductService(product_repository)


app = Litestar(
    route_handlers=[UserController, OrderController, ProductController],
    dependencies={
        "session": Provide(provide_session),
        "user_repository": Provide(provide_user_repository),
        "user_service": Provide(provide_user_service),
        "order_service": Provide(provide_order_service),
        "order_repository": Provide(provide_order_repository),
        "product_repository": Provide(provide_product_repository),
        "product_service": Provide(provide_product_service),
    },
    debug=True,
)

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
