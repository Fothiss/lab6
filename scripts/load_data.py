import asyncio
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.models import Address, Base, Order, OrderItem, Product, User

DB_URL = "sqlite+aiosqlite:///./lab3.db"


async def load_data():
    """Создает таблицы и загружает тестовые данные"""
    engine = create_async_engine(DB_URL, echo=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)  # Очищаем перед заполнением
        await conn.run_sync(Base.metadata.create_all)

    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Создаем пользователей и адреса
        users_data = [
            {
                "username": "ivanov",
                "email": "ivanov@example.com",
                "addresses": [
                    {
                        "street": "ул. Ленина, 15",
                        "city": "Москва",
                        "state": "Московская область",
                        "zip_code": "101000",
                        "country": "Russia",
                        "is_primary": True,
                    },
                    {
                        "street": "пр. Победы, 42",
                        "city": "Москва",
                        "state": "Московская область",
                        "zip_code": "101001",
                        "country": "Russia",
                        "is_primary": False,
                    },
                ],
            },
            {
                "username": "petrov",
                "email": "petrov@example.com",
                "addresses": [
                    {
                        "street": "Невский пр., 25",
                        "city": "Санкт-Петербург",
                        "state": "Ленинградская область",
                        "zip_code": "190000",
                        "country": "Russia",
                        "is_primary": True,
                    }
                ],
            },
            {
                "username": "sidorova",
                "email": "sidorova@example.com",
                "addresses": [
                    {
                        "street": "ул. Баумана, 8",
                        "city": "Казань",
                        "state": "Татарстан",
                        "zip_code": "420000",
                        "country": "Russia",
                        "is_primary": True,
                    },
                    {
                        "street": "ул. Кремлевская, 35",
                        "city": "Казань",
                        "state": "Татарстан",
                        "zip_code": "420001",
                        "country": "Russia",
                        "is_primary": False,
                    },
                ],
            },
        ]

        users = []
        all_addresses = []

        for user_data in users_data:
            user = User(username=user_data["username"], email=user_data["email"])
            users.append(user)

            for addr_data in user_data["addresses"]:
                address = Address(**addr_data, user=user)
                all_addresses.append(address)

        # Создаем продукты
        products = [
            Product(
                name="Ноутбук",
                description="Игровой ноутбук",
                price=Decimal("1500.00"),
                stock_quantity=10,
            ),
            Product(
                name="Мышь",
                description="Беспроводная мышь",
                price=Decimal("25.50"),
                stock_quantity=50,
            ),
            Product(
                name="Клавиатура",
                description="Механическая клавиатура",
                price=Decimal("120.00"),
                stock_quantity=30,
            ),
        ]

        # Добавляем все в сессию
        session.add_all(users + all_addresses + products)
        await session.commit()

        print("✅ Данные успешно загружены!")
        print(f"👥 Создано пользователей: {len(users)}")
        print(f"🏠 Создано адресов: {len(all_addresses)}")
        print(f"📦 Создано товаров: {len(products)}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(load_data())
