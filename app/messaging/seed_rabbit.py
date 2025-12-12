import json
import pika


def send_to_queue(queue: str, data: dict):
    connection = pika.BlockingConnection(
        pika.ConnectionParameters(
            host="rabbitmq",  # или 'localhost' не в Docker
            port=5672,
            credentials=pika.PlainCredentials("guest", "guest"),
        )
    )
    channel = connection.channel()
    channel.queue_declare(queue=queue)
    channel.basic_publish(
        exchange="",
        routing_key=queue,
        body=json.dumps(data),
        properties=pika.BasicProperties(delivery_mode=2),
    )
    connection.close()
    print(f"📤 Sent to {queue}: {data['name'] if 'name' in data else 'order'}")


products = [
    {
        "product_id": 101,
        "name": "Игровой ноутбук ASUS ROG",
        "price": "199999.00",
        "created_at": "2025-01-15T14:30:00Z",
    },
    {
        "product_id": 102,
        "name": "Механическая клавиатура Keychron",
        "price": "12500.00",
        "created_at": "2025-01-16T10:15:00Z",
    },
    {
        "product_id": 103,
        "name": "Беспроводные наушники Sony WH-1000XM5",
        "price": "35990.00",
        "created_at": "2025-01-17T16:45:00Z",
    },
    {
        "product_id": 104,
        "name": 'Монитор Samsung 34" UltraWide',
        "price": "78900.00",
        "created_at": "2025-01-18T12:20:00Z",
    },
    {
        "product_id": 105,
        "name": "Внешний SSD Samsung T7 1TB",
        "price": "12900.00",
        "created_at": "2025-01-19T09:30:00Z",
    },
]

orders = [
    {
        "order_id": 1001,
        "user_id": 1,
        "status": "created",
        "total_amount": "265490.00",
        "created_at": "2025-01-20T10:30:00Z",
    },
    {
        "order_id": 1002,
        "user_id": 2,
        "status": "processing",
        "total_amount": "78900.00",  # Монитор
        "created_at": "2025-01-20T11:15:00Z",
    },
    {
        "order_id": 1003,
        "user_id": 3,
        "status": "shipped",
        "total_amount": "34990.00",  # Наушники
        "created_at": "2025-01-20T14:45:00Z",
    },
]

if __name__ == "__main__":
    print("🚀 Sending test data to RabbitMQ...")

    for product in products:
        send_to_queue(
            "products", product
        )  # очередь 'products' (во множественном числе)

    for order in orders:
        send_to_queue("order", order)  # очередь 'order'

    print("✅ Test data sent successfully")
