from datetime import datetime, timezone
from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, Query, status
from pydantic import BaseModel, ConfigDict, Field

from dependencies import CurrentUser, ManagerUser
from models import (
    Order,
    OrderCreate,
    OrderStatus,
    OrderUpdate,
    Role,
    User,
    order_seq,
    orders_db,
)
from routers.books import get_book_or_404

router = APIRouter(prefix="/orders", tags=["orders"])

OrderId = Annotated[int, Path(ge=1, description="Номер замовлення")]


def get_order_or_404(order_id: int) -> Order:
    order = orders_db.get(order_id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Замовлення з id={order_id} не знайдено",
        )
    return order


def get_visible_order_or_404(order_id: int, user: User) -> Order:
    """reader бачить лише власні; чуже для нього виглядає як неіснуюче (404)."""
    order = get_order_or_404(order_id)
    if user.role == Role.READER and order.owner_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Замовлення з id={order_id} не знайдено",
        )
    return order


class OrderFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus | None = None
    book_id: int | None = Field(default=None, ge=1)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)


@router.post("", response_model=Order, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, user: CurrentUser):
    book = get_book_or_404(data.book_id)                      # 404
    if not book.available:                                    # 409
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Книга зараз недоступна")
    order = Order(
        id=next(order_seq),
        owner_id=user.id,
        status=OrderStatus.NEW,
        created_at=datetime.now(timezone.utc),
        **data.model_dump(),
    )
    orders_db[order.id] = order
    book.available = False
    return order


@router.get("", response_model=list[Order])
async def list_orders(filters: Annotated[OrderFilter, Query()], user: ManagerUser):
    orders = list(orders_db.values())
    if filters.status is not None:
        orders = [o for o in orders if o.status == filters.status]
    if filters.book_id is not None:
        orders = [o for o in orders if o.book_id == filters.book_id]
    orders.sort(key=lambda o: o.id)
    return orders[filters.offset : filters.offset + filters.limit]


@router.get("/{order_id}", response_model=Order)
async def get_order(order_id: OrderId, user: CurrentUser):
    return get_visible_order_or_404(order_id, user)


@router.patch("/{order_id}", response_model=Order)
async def update_order(order_id: OrderId, data: OrderUpdate, user: CurrentUser):
    order = get_order_or_404(order_id)
    if order.owner_id != user.id:                             # чуже -> 404 (для будь-якої ролі)
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Замовлення з id={order_id} не знайдено",
        )
    if order.status != OrderStatus.NEW:                       # 409
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Редагувати можна лише замовлення зі статусом new",
        )
    if data.delivery is not None:
        order.delivery = data.delivery
    if data.delivery_date is not None:
        order.delivery_date = data.delivery_date
    return order