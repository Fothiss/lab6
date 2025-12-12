from typing import List, Optional

from litestar import Controller, delete, get, post, put
from litestar.exceptions import NotFoundException
from litestar.params import Body, Parameter
from sqlalchemy.orm import Session

from app.schemas import ProductCreate, ProductResponse, ProductUpdate
from app.services.product_service import ProductService


class ProductController(Controller):
    path = "/products"

    @post()
    async def create_product(
        self,
        product_service: ProductService,
        session: Session,
        data: ProductCreate = Body(),
    ) -> ProductResponse:
        product = await product_service.create_product(session, data)
        return ProductResponse.model_validate(product)

    @get("/{product_id:int}")
    async def get_product(
        self,
        product_service: ProductService,
        session: Session,
        product_id: int = Parameter(),
    ) -> ProductResponse:
        product = await product_service.get_product(session, product_id)
        if not product:
            raise NotFoundException(detail=f"Product {product_id} not found")
        return ProductResponse.model_validate(product)

    @get()
    async def get_products(
        self,
        product_service: ProductService,
        session: Session,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(ge=1, default=1),
        name: Optional[str] = Parameter(default=None),
        min_price: Optional[float] = Parameter(default=None),
        max_price: Optional[float] = Parameter(default=None),
    ) -> List[ProductResponse]:
        products = await product_service.list_products(
            session,
            count=count,
            page=page,
            name=name,
            min_price=min_price,
            max_price=max_price,
        )
        return [ProductResponse.model_validate(product) for product in products]

    @put("/{product_id:int}")
    async def update_product(
        self,
        product_service: ProductService,
        session: Session,
        product_id: int = Parameter(),
        data: ProductUpdate = Body(),
    ) -> ProductResponse:
        product = await product_service.update_product(session, product_id, data)
        if not product:
            raise NotFoundException(detail=f"Product {product_id} not found")
        return ProductResponse.model_validate(product)

    @delete("/{product_id:int}")
    async def delete_product(
        self,
        product_service: ProductService,
        session: Session,
        product_id: int = Parameter(),
    ) -> None:
        success = await product_service.delete_product(session, product_id)
        if not success:
            raise NotFoundException(detail=f"Product {product_id} not found")
