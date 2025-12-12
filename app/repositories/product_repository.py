from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Product, OrderItem
from app.schemas import ProductCreate, ProductUpdate


class ProductRepository:
    def __init__(self):
        self.model = Product

    async def get_by_id(self, session: Session, product_id: int) -> Optional[Product]:
        return session.query(self.model).filter(self.model.id == product_id).first()

    async def get_list(
        self, session: Session, count: int = 10, page: int = 1, **filters
    ) -> List[Product]:
        query = session.query(self.model)
        for attr, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, attr) == value)
        return query.offset((page - 1) * count).limit(count).all()

    async def create(self, session: Session, product_data: ProductCreate) -> Product:
        product = self.model(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock_quantity=product_data.stock_quantity or 0,
        )
        session.add(product)
        session.commit()
        session.refresh(product)
        return product

    async def update(
        self, session: Session, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        product = session.query(self.model).filter(self.model.id == product_id).first()
        if not product:
            return None
        data = product_data.model_dump(exclude_unset=True)
        for k, v in data.items():
            setattr(product, k, v)
        session.commit()
        session.refresh(product)
        return product

    async def delete(self, session: Session, product_id: int) -> bool:
        product = session.query(self.model).filter(self.model.id == product_id).first()
        if not product:
            return False

        order_items = (
            session.query(OrderItem).filter(OrderItem.product_id == product_id).count()
        )
        if order_items > 0:
            raise ValueError(
                f"Cannot delete product {product_id} - it has {order_items} order items"
            )

        session.delete(product)
        session.commit()
        return True

    async def update_stock(
        self, session: Session, product_id: int, quantity_change: int
    ) -> Optional[Product]:
        product = session.query(self.model).filter(self.model.id == product_id).first()
        if not product:
            return None
        product.stock_quantity += quantity_change
        session.commit()
        session.refresh(product)
        return product
