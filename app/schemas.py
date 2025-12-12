from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


def validate_email(value: Optional[str]) -> Optional[str]:
    if value is None:
        return value
    if "@" not in value:
        raise ValueError("Invalid email address")
    return value


# User Schemas
class UserCreate(BaseModel):
    username: str = Field(..., min_length=1, max_length=50)
    email: str = Field(..., max_length=100)
    description: Optional[str] = Field(None, max_length=300)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: str) -> str:
        return validate_email(value)


class UserUpdate(BaseModel):
    username: Optional[str] = Field(None, min_length=1, max_length=50)
    email: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = Field(None, max_length=300)

    @field_validator("email")
    @classmethod
    def validate_email(cls, value: Optional[str]) -> Optional[str]:
        return validate_email(value)


class UserResponse(BaseModel):
    id: int
    username: str
    email: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Product Schemas
class ProductCreate(BaseModel):
    name: str = Field(..., max_length=100)
    description: Optional[str] = None
    price: Decimal = Field(..., gt=0)
    stock_quantity: int = Field(0, ge=0)


class ProductUpdate(BaseModel):
    name: Optional[str] = Field(None, max_length=100)
    description: Optional[str] = None
    price: Optional[Decimal] = Field(None, gt=0)
    stock_quantity: Optional[int] = Field(None, ge=0)


class ProductResponse(BaseModel):
    id: int
    name: str
    description: Optional[str]
    price: Decimal
    stock_quantity: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# Order Item Schemas
class OrderItemCreate(BaseModel):
    product_id: int
    quantity: int = Field(1, gt=0)


class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    quantity: int
    price_at_purchase: Decimal
    total_price: Decimal

    model_config = {"from_attributes": True}


# Order Schemas
class OrderCreate(BaseModel):
    user_id: int
    address_id: int
    status: str = Field("pending", max_length=50)
    items: List[OrderItemCreate]


class OrderUpdate(BaseModel):
    status: Optional[str] = Field(None, max_length=50)


class OrderResponse(BaseModel):
    id: int
    user_id: int
    address_id: int
    status: str
    total_amount: Decimal
    created_at: datetime
    updated_at: datetime
    items: List[OrderItemResponse]

    model_config = {"from_attributes": True}


class AddressCreate(BaseModel):
    user_id: int
    street: str = Field(..., max_length=200)
    city: str = Field(..., max_length=100)
    state: Optional[str] = Field(None, max_length=100)
    zip_code: Optional[str] = Field(None, max_length=20)
    country: str = Field(..., max_length=100)
    is_primary: bool = False


class AddressResponse(BaseModel):
    id: int
    user_id: int
    street: str
    city: str
    state: Optional[str]
    zip_code: Optional[str]
    country: str
    is_primary: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class OrderMessage(BaseModel):
    order_id: int
    user_id: int
    status: str
    total_amount: Decimal
    created_at: datetime


class ProductMessage(BaseModel):
    product_id: int
    name: str
    price: Decimal
    created_at: datetime
