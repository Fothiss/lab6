from app.cache.redis_client import get_redis

print("Тестируем Redis модуль...")

redis_client = get_redis()

if redis_client:
    print("✅ Redis подключен")

    # Тест записи
    redis_client.set("project:test", "lab6")
    value = redis_client.get("project:test")
    print(f"✅ Прочитали: {value}")

    # Очистка
    redis_client.delete("project:test")
else:
    print("❌ Redis недоступен")
