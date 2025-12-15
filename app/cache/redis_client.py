import redis


def get_redis():
    """Возвращает подключение к Redis или None"""
    try:
        client = redis.Redis(
            host="redis",
            port=6379,
            db=0,
            decode_responses=True,
            socket_connect_timeout=2,
        )
        client.ping()
        return client
    except (redis.ConnectionError, redis.TimeoutError):
        return None
