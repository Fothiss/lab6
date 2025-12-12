from decimal import Decimal
from typing import List, Optional

from sqlalchemy.orm import Session, selectinload

from app.models import Order, OrderItem, Product
from app.schemas import OrderCreate, OrderUpdate


class OrderRepository:
    def __init__(self):
        self.model = Order

    async def get(self, session: Session, order_id: int) -> Optional[Order]:
        return (
            session.query(self.model)
            .options(selectinload(Order.items).selectinload(OrderItem.product))
            .filter(self.model.id == order_id)
            .first()
        )

    async def list(
        self,
        session: Session,
        count: int = 10,
        page: int = 1,
        user_id: Optional[int] = None,
    ) -> List[Order]:
        query = session.query(self.model).options(
            selectinload(Order.items).selectinload(OrderItem.product)
        )

        if user_id:
            query = query.filter(self.model.user_id == user_id)

        return query.offset((page - 1) * count).limit(count).all()

    async def create(self, session: Session, order_data: OrderCreate) -> Order:
        order = self.model(
            user_id=order_data.user_id,
            address_id=order_data.address_id,
            status=order_data.status or "pending",
        )
        session.add(order)
        session.flush()  # Получаем ID без коммита

        total_amount = Decimal("0")

        for item_data in order_data.items:
            product = (
                session.query(Product)
                .filter(Product.id == item_data.product_id)
                .first()
            )
            if not product:
                raise ValueError(f"Product with ID {item_data.product_id} not found")

            if product.stock_quantity < item_data.quantity:
                raise ValueError(f"Insufficient stock for {product.name}")

            item_total = product.price * item_data.quantity
            order_item = OrderItem(
                order_id=order.id,
                product_id=item_data.product_id,
                quantity=item_data.quantity,
                price_at_purchase=product.price,
                total_price=item_total,
            )
            session.add(order_item)

            total_amount += item_total
            product.stock_quantity -= item_data.quantity

        order.total_amount = total_amount
        session.commit()
        session.refresh(order)
        return order

    async def update_status(
        self, session: Session, order_id: int, status: str
    ) -> Optional[Order]:
        order = await self.get(session, order_id)
        if not order:
            return None
        order.status = status
        session.commit()
        session.refresh(order)
        return order

    async def delete(self, session: Session, order_id: int) -> bool:
        order = await self.get(session, order_id)
        if not order:
            return False

        for item in order.items:
            product = (
                session.query(Product).filter(Product.id == item.product_id).first()
            )
            if product:
                product.stock_quantity += item.quantity

        session.delete(order)
        session.commit()
        return True
