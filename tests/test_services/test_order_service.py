import asyncio
from decimal import Decimal

from app.models import Address, Product, User
from app.schemas import OrderCreate, OrderItemCreate
from app.services.order_service import OrderService


class TestOrderService:
    def test_create_order(self, session, order_service: OrderService):
        async def _run():
            # Подготовка данных
            user = User(username="service_user_1", email="service1@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)

            address = Address(
                user_id=user.id, street="Street 1", city="City 1", country="Country 1"
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            product = Product(
                name="Service Product 1", price=Decimal("50.00"), stock_quantity=10
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            # Создание заказа
            order = await order_service.create_order(
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

    def test_list_orders(self, session, order_service: OrderService):
        async def _run():
            # Подготовка данных
            user = User(username="service_user_2", email="service2@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)

            address = Address(
                user_id=user.id, street="Street 2", city="City 2", country="Country 2"
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            product = Product(
                name="Service Product 2", price=Decimal("25.00"), stock_quantity=20
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            # Создание заказа
            await order_service.create_order(
                session,
                OrderCreate(
                    user_id=user.id,
                    address_id=address.id,
                    items=[OrderItemCreate(product_id=product.id, quantity=1)],
                ),
            )

            # Получение списка
            orders = await order_service.list_orders(session, count=10, page=1)
            assert len(orders) >= 1

        asyncio.run(_run())

    def test_update_order_status(self, session, order_service: OrderService):
        async def _run():
            # Подготовка данных
            user = User(username="service_user_3", email="service3@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)

            address = Address(
                user_id=user.id, street="Street 3", city="City 3", country="Country 3"
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            product = Product(
                name="Service Product 3", price=Decimal("30.00"), stock_quantity=15
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            # Создание заказа
            order = await order_service.create_order(
                session,
                OrderCreate(
                    user_id=user.id,
                    address_id=address.id,
                    items=[OrderItemCreate(product_id=product.id, quantity=1)],
                ),
            )

            # Обновление статуса
            updated = await order_service.update_status(session, order.id, "completed")
            assert updated.status == "completed"

        asyncio.run(_run())

    def test_delete_order(self, session, order_service: OrderService):
        async def _run():
            # Подготовка данных
            user = User(username="service_user_4", email="service4@example.com")
            session.add(user)
            session.commit()
            session.refresh(user)

            address = Address(
                user_id=user.id, street="Street 4", city="City 4", country="Country 4"
            )
            session.add(address)
            session.commit()
            session.refresh(address)

            product = Product(
                name="Service Product 4", price=Decimal("40.00"), stock_quantity=5
            )
            session.add(product)
            session.commit()
            session.refresh(product)

            # Создание заказа
            order = await order_service.create_order(
                session,
                OrderCreate(
                    user_id=user.id,
                    address_id=address.id,
                    items=[OrderItemCreate(product_id=product.id, quantity=1)],
                ),
            )

            # Удаление заказа
            result = await order_service.delete_order(session, order.id)
            assert result is True

            # Проверка что удален
            found = await order_service.get_order(session, order.id)
            assert found is None

        asyncio.run(_run())
