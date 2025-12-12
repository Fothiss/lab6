import asyncio
from decimal import Decimal

from app.repositories.product_repository import ProductRepository
from app.schemas import ProductCreate, ProductUpdate


class TestProductRepository:
    def test_create_product(self, session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                session,
                ProductCreate(
                    name="Test Product 1", price=Decimal("99.99"), stock_quantity=5
                ),
            )
            assert product.id is not None
            assert product.name == "Test Product 1"
            assert product.price == Decimal("99.99")

        asyncio.run(_run())

    def test_get_list_products(self, session, product_repository: ProductRepository):
        async def _run():
            await product_repository.create(
                session,
                ProductCreate(
                    name="Test Product 2a", price=Decimal("50.00"), stock_quantity=2
                ),
            )
            await product_repository.create(
                session,
                ProductCreate(
                    name="Test Product 2b", price=Decimal("75.00"), stock_quantity=4
                ),
            )

            products = await product_repository.get_list(session, count=10, page=1)
            product_names = [product.name for product in products]
            assert "Test Product 2a" in product_names
            assert "Test Product 2b" in product_names

        asyncio.run(_run())

    def test_update_product(self, session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                session,
                ProductCreate(
                    name="Test Product 3", price=Decimal("20.00"), stock_quantity=1
                ),
            )

            updated = await product_repository.update(
                session,
                product.id,
                ProductUpdate(price=Decimal("25.00"), stock_quantity=3),
            )
            assert updated is not None
            assert updated.price == Decimal("25.00")
            assert updated.stock_quantity == 3

        asyncio.run(_run())

    def test_update_stock(self, session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                session,
                ProductCreate(
                    name="Test Product 4", price=Decimal("10.00"), stock_quantity=10
                ),
            )

            updated = await product_repository.update_stock(session, product.id, 5)
            assert updated.stock_quantity == 15

        asyncio.run(_run())

    def test_delete_product(self, session, product_repository: ProductRepository):
        async def _run():
            product = await product_repository.create(
                session,
                ProductCreate(
                    name="Test Product 5", price=Decimal("30.00"), stock_quantity=1
                ),
            )

            await product_repository.delete(session, product.id)
            found = await product_repository.get_by_id(session, product.id)
            assert found is None

        asyncio.run(_run())
