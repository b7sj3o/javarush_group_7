from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field


class TransferCreate(BaseModel):
    from_user_id: int
    to_user_id: int
    amount: Decimal = Field(gt=0)


# ---------- Замовлення ----------


class OrderCreate(BaseModel):
    user_id: int
    product_id: int
    quantity: int = Field(default=1, ge=1)


class OrderItemRead(BaseModel):
    product_id: int
    quantity: int
    price: Decimal


class OrderRead(BaseModel):
    id: int
    user_id: int
    total: Decimal
    created_at: datetime


class OrderDetail(OrderRead):
    items: list[OrderItemRead]


class OrderCreated(BaseModel):
    order_id: int
    total: Decimal
    stock_left: int


# ---------- Категорії й теги ----------


class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CategoryRead(BaseModel):
    id: int
    name: str


class TagCreate(BaseModel):
    name: str = Field(min_length=1, max_length=50)


class TagRead(BaseModel):
    id: int
    name: str


# ---------- Товари ----------


class ProductCreate(BaseModel):
    name: str = Field(min_length=1, max_length=200)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    stock: int = Field(ge=0)
    category_id: int
    tag_ids: list[int] = []


class ProductUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=200)
    price: Decimal | None = Field(default=None, gt=0, max_digits=10, decimal_places=2)
    stock: int | None = Field(default=None, ge=0)
    category_id: int | None = None
    tag_ids: list[int] | None = None


class ProductShort(BaseModel):
    """Лише колонки таблиці products: зв'язки вантажити не треба."""

    id: int
    name: str
    price: Decimal
    stock: int
    category_id: int


class ProductRead(BaseModel):
    """Зі зв'язками: без eager loading цю схему не віддати (слайд 6)."""

    id: int
    name: str
    price: Decimal
    stock: int
    category: CategoryRead
    tags: list[TagRead]


# ---------- Юзери й профілі ----------


class UserCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    age: int = Field(ge=0, le=150)


class UserUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=100)
    email: str | None = Field(default=None, max_length=255)
    age: int | None = Field(default=None, ge=0, le=150)


class UserRead(BaseModel):
    id: int
    name: str
    email: str
    age: int
    balance: Decimal
    profile: "ProfileRead"

class ProfileUpdate(BaseModel):
    city: str = Field(max_length=100)


class ProfileRead(BaseModel):
    user_id: int
    city: str
