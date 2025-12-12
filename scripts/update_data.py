import asyncio
from decimal import Decimal

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import selectinload, sessionmaker

from app.models import Address, Order, OrderItem, Product, User

DB_URL = "sqlite+aiosqlite:///./lab3.db"


async def update_users_with_descriptions():
    """Добавляет описания существующим пользователям"""
    engine = create_async_engine(DB_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Получаем всех пользователей
        result = await session.execute(select(User))
        users = result.scalars().all()

        descriptions = [
            "Любитель путешествий и фотографии",
            "Программист и геймер",
            "Дизайнер интерьеров из Казани",
            "Студент университета в Новосибирске",
            "Предприниматель из Краснодарского края",
        ]

        # Обновляем описания
        for user, description in zip(users, descriptions):
            user.description = description

        await session.commit()

    await engine.dispose()


async def add_products_and_orders():
    """Добавляет продукты и создает заказы"""
    engine = create_async_engine(DB_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Создаем продукты
        products = [
            Product(
                name="Ноутбук Gaming Pro",
                description="Игровой ноутбук с RTX 4060",
                price=Decimal("150000.00"),
                stock_quantity=5,
            ),
            Product(
                name="Смартфон Galaxy S24",
                description="Флагманский смартфон",
                price=Decimal("90000.00"),
                stock_quantity=10,
            ),
            Product(
                name="Наушники Wireless",
                description="Беспровручные наушники с шумоподавлением",
                price=Decimal("15000.00"),
                stock_quantity=20,
            ),
            Product(
                name="Умные часы Pro",
                description="Смарт-часы с функцией ECG",
                price=Decimal("50000.00"),
                stock_quantity=8,
            ),
            Product(
                name="Планшет для рисования",
                description="Графический планшет с пером",
                price=Decimal("30000.00"),
                stock_quantity=15,
            ),
        ]

        session.add_all(products)
        await session.flush()  # Получаем ID продуктов

        # Получаем пользователей с их адресами
        result = await session.execute(
            select(User).options(selectinload(User.addresses))
        )
        users = result.scalars().all()

        # Создаем заказы
        orders = []
        order_items = []

        for i, user in enumerate(users):
            # Находим основной адрес
            primary_address = next(
                (addr for addr in user.addresses if addr.is_primary),
                user.addresses[0] if user.addresses else None,
            )

            if primary_address and i < len(products):
                # Создаем заказ
                order = Order(
                    user_id=user.id,
                    address_id=primary_address.id,
                    status="completed",
                    total_amount=Decimal("0"),  # Будет рассчитано из OrderItems
                )
                orders.append(order)
                session.add(order)
                await session.flush()  # Получаем ID заказа

                # Создаем OrderItem для этого заказа
                product = products[i]
                order_item = OrderItem(
                    order_id=order.id,
                    product_id=product.id,
                    quantity=1,
                    price_at_purchase=product.price,
                    total_price=product.price * 1,
                )
                order_items.append(order_item)

                # Обновляем общую сумму заказа
                order.total_amount = order_item.total_price

        session.add_all(order_items)
        await session.commit()

    await engine.dispose()


async def update_product_prices():
    """Обновляет цены некоторых продуктов"""
    engine = create_async_engine(DB_URL, echo=True)
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        # Получаем первые 3 продукта
        result = await session.execute(select(Product).where(Product.id.in_([1, 2, 3])))
        products = result.scalars().all()

        new_prices = [Decimal("145000.00"), Decimal("85000.00"), Decimal("14000.00")]

        for product, new_price in zip(products, new_prices):
            product.price = new_price

        await session.commit()

    await engine.dispose()


async def main():
    """Основная функция обновления данных"""

    await update_users_with_descriptions()
    await add_products_and_orders()
    await update_product_prices()

    print("🎉 Все данные успешно обновлены!")


if __name__ == "__main__":
    asyncio.run(main())
