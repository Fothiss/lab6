import asyncio
from decimal import Decimal

from app.models import Address, Product, User
from app.repositories.order_repository import OrderRepository
from app.schemas import OrderCreate, OrderItemCreate


class TestOrderRepository:
    def test_create_order(self, session, order_repository: OrderRepository):
        async def _run():
            # Создаем и сохраняем пользователя
            user = User(username="order_user_1", email="order1@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)  # Получаем ID пользователя

            # Создаем адрес с правильным user_id
            address = Address(
                user_id=user.id, street="Street 1", city="City 1", country="Country 1"
            )
            session.add(address)
            session.commit()
            session.refresh(address)  # Получаем ID адреса

            # Создаем продукт
            product = Product(
                name="Order Product 1", price=Decimal("50.00"), stock_quantity=10
            )
            session.add(product)
            session.commit()
            session.refresh(product)  # Получаем ID продукта

            order = await order_repository.create(
                session,
                OrderCreate(
                    user_id=user.id,
                    address_id=address.id,
                    items=[OrderItemCreate(product_id=product.id, quantity=2)],
                ),
            )
            assert order.id is not None
            assert order.total_amount == Decimal("100.00")

        asyncio.run(_run())

    def test_list_orders(self, session, order_repository: OrderRepository):
        async def _run():
            # Создаем и сохраняем первого пользователя
            user1 = User(username="order_user_2a", email="order2a@example.com")
            session.add(user1)
            session.commit()
            session.refresh(user1)

            # Создаем адрес для первого пользователя
            address1 = Address(
                user_id=user1.id,
                street="Street 2a",
                city="City 2a",
                country="Country 2a",
            )
            session.add(address1)
            session.commit()
            session.refresh(address1)

            # Создаем и сохраняем второго пользователя
            user2 = User(username="order_user_2b", email="order2b@example.com")
            session.add(user2)
            session.commit()
            session.refresh(user2)

            # Создаем адрес для второго пользователя
            address2 = Address(
                user_id=user2.id,
                street="Street 2b",
                city="City 2b",
                country="Country 2b",
            )
            session.add(address2)
            session.commit()
            session.refresh(address2)

            # Создаем продукт
            product = Product(
                name="Order Product 2", price=Decimal("25.00"), stock_quantity=20
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            await order_repository.create(
                session,
                OrderCreate(
                    user_id=user1.id,
                    address_id=address1.id,
                    items=[OrderItemCreate(product_id=product.id, quantity=1)],
                ),
            )

            orders = await order_repository.list(session, count=10, page=1)
            assert len(orders) >= 1

        asyncio.run(_run())

    def test_update_order_status(self, session, order_repository: OrderRepository):
        async def _run():
            # Создаем и сохраняем пользователя
            user = User(username="order_user_3", email="order3@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)

            # Создаем адрес
            address = Address(
                user_id=user.id, street="Street 3", city="City 3", country="Country 3"
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            # Создаем продукт
            product = Product(
                name="Order Product 3", price=Decimal("30.00"), stock_quantity=15
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            order = await order_repository.create(
                session,
                OrderCreate(
                    user_id=user.id,
                    address_id=address.id,
                    items=[OrderItemCreate(product_id=product.id, quantity=1)],
                ),
            )

            updated = await order_repository.update_status(
                session, order.id, "completed"
            )
            assert updated.status == "completed"

        asyncio.run(_run())
