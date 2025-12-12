import asyncio
from datetime import datetime
from decimal import Decimal

from faststream.rabbit import RabbitBroker

# Создаём брокер
broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")


class _BrokerConnection:
    """Менеджер подключения к брокеру"""

    _initialized = False

    @classmethod
    async def ensure_connected(cls):
        """Обеспечивает подключение к брокеру"""
        if not cls._initialized:
            await broker.connect()
            cls._initialized = True


async def publish_order_created(
    order_id: int, user_id: int, total_amount: Decimal, status: str = "created"
) -> None:
    """Отправляет событие создания заказа в RabbitMQ"""
    # Подключаемся если ещё не подключены
    await _BrokerConnection.ensure_connected()
    message = {
        "order_id": order_id,
        "user_id": user_id,
        "status": status,
        "total_amount": str(total_amount),
        "created_at": datetime.utcnow().isoformat(),
    }

    await broker.publish(message, queue="order")


async def publish_product_created(product_id: int, name: str, price: Decimal) -> None:
    message = {
        "product_id": product_id,
        "name": name,
        "price": str(price),
        "created_at": datetime.utcnow().isoformat(),
    }
    await broker.publish(message, queue="products")
