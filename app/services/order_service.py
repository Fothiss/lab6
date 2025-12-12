import logging
from typing import List, Optional

from sqlalchemy.orm import Session

from aio_pika.exceptions import AMQPError

from app.messaging.producer import publish_order_created
from app.models import Order
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.schemas import OrderCreate


logger = logging.getLogger(__name__)


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository,
    ) -> None:
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def create_order(self, session: Session, order_data: OrderCreate) -> Order:
        user = await self.user_repository.get_by_id(session, order_data.user_id)
        if not user:
            raise ValueError("User not found")

        if not order_data.items:
            raise ValueError("Order items cannot be empty")

        order = await self.order_repository.create(session, order_data)

        # Отправка события в RabbitMQ
        try:
            logger.info(f"📤 Sending RabbitMQ event for order {order.id}")
            await publish_order_created(
                order_id=order.id,
                user_id=order.user_id,
                total_amount=order.total_amount,
                status=order.status,
            )
            logger.info(f"✅ RabbitMQ event sent for order {order.id}")
        except (ConnectionError, AMQPError, TimeoutError) as e:
            logger.error(f"RabbitMQ connection error: {e}")

        return order

    async def get_order(self, session: Session, order_id: int) -> Optional[Order]:
        return await self.order_repository.get(session, order_id)

    async def list_orders(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
        user_id: Optional[int] = None,
    ) -> List[Order]:
        return await self.order_repository.list(
            session, count=count, page=page, user_id=user_id
        )

    async def update_status(
        self, session: Session, order_id: int, status: str
    ) -> Optional[Order]:
        return await self.order_repository.update_status(session, order_id, status)

    async def delete_order(self, session: Session, order_id: int) -> bool:
        return await self.order_repository.delete(session, order_id)
