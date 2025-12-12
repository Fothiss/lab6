from typing import List

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from litestar.params import Body, Parameter
from sqlalchemy.orm import Session

from app.schemas import OrderCreate, OrderResponse, OrderUpdate
from app.services.order_service import OrderService


class OrderController(Controller):
    path = "/orders"

    @post()
    async def create_order(
        self,
        order_service: OrderService,
        session: Session,
        data: OrderCreate = Body(),
    ) -> OrderResponse:
        """Создать заказ (отправляет событие в RabbitMQ)"""
        order = await order_service.create_order(session, data)
        return OrderResponse.model_validate(order)

    @get("/{order_id:int}")
    async def get_order(
        self,
        order_service: OrderService,
        session: Session,
        order_id: int = Parameter(),
    ) -> OrderResponse:
        """Получить заказ по ID"""
        order = await order_service.get_order(session, order_id)
        if not order:
            raise NotFoundException(detail=f"Order {order_id} not found")
        return OrderResponse.model_validate(order)

    @get()
    async def get_orders(
        self,
        order_service: OrderService,
        session: Session,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(ge=1, default=1),
    ) -> List[OrderResponse]:
        """Список заказов"""
        orders = await order_service.list_orders(session, count=count, page=page)
        return [OrderResponse.model_validate(order) for order in orders]

    @put("/{order_id:int}")
    async def update_order(
        self,
        order_service: OrderService,
        session: Session,
        order_id: int = Parameter(),
        data: OrderUpdate = Body(),  # ← Используем схему
    ) -> OrderResponse:
        """Обновить заказ"""
        if data.status:
            order = await order_service.update_status(session, order_id, data.status)
        else:
            order = await order_service.get_order(session, order_id)

        if not order:
            raise NotFoundException(detail=f"Order {order_id} not found")
        return OrderResponse.model_validate(order)

    @delete("/{order_id:int}")
    async def delete_order(
        self,
        order_service: OrderService,
        session: Session,
        order_id: int = Parameter(),
    ) -> None:
        """Удалить заказ"""
        success = await order_service.delete_order(session, order_id)
        if not success:
            raise NotFoundException(detail=f"Order {order_id} not found")
