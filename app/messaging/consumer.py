# app/messaging/consumer.py
import asyncio
import logging

from faststream import FastStream
from faststream.rabbit import RabbitBroker

from app.schemas import OrderMessage, ProductMessage

# Настройка логгирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Подключение к RabbitMQ
broker = RabbitBroker("amqp://guest:guest@rabbitmq:5672/")
app = FastStream(broker)


@broker.subscriber("order")
async def handle_order(msg: OrderMessage):
    """Обработчик событий создания заказа"""
    try:
        logger.info(
            f"📦 Order #{msg.order_id} received | "
            f"User: {msg.user_id} | "
            f"Status: {msg.status} | "
            f"Total: ${msg.total_amount} | "
            f"Created: {msg.created_at}"
        )

    except Exception as e:
        logger.error(f"❌ Error processing order #{msg.order_id}: {e}")
        # Можно настроить retry или dead letter queue
        raise


@broker.subscriber("products")
async def handle_product(msg: ProductMessage):
    logger.info(f"🛒 Product created: {msg.name} (${msg.price})")


async def main():
    """Точка входа для consumer"""
    logger.info("Order consumer starting...")
    await app.run()


if __name__ == "__main__":
    asyncio.run(main())
