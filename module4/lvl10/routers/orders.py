from typing import Annotated

from fastapi import APIRouter, Path, Query, status

from dependencies import AdminUser, CurrentUser, ManagerUser
from schemas import OrderCreate, OrderFilter, OrderOut, OrderStatusUpdate, OrderUpdate
from services.orders import OrderServiceDep

router = APIRouter(prefix="/orders", tags=["orders"])

OrderId = Annotated[int, Path(ge=1, description="Номер замовлення")]


@router.post("", response_model=OrderOut, status_code=status.HTTP_201_CREATED)
async def create_order(data: OrderCreate, user: CurrentUser, service: OrderServiceDep):
    return await service.create(data, user)


@router.get("", response_model=list[OrderOut])
async def list_orders(filters: Annotated[OrderFilter, Query()], user: ManagerUser, service: OrderServiceDep):
    return await service.list(filters)


@router.get("/{order_id}", response_model=OrderOut)
async def get_order(order_id: OrderId, user: CurrentUser, service: OrderServiceDep):
    return await service.get_visible(order_id, user)


@router.patch("/{order_id}", response_model=OrderOut)
async def update_order(order_id: OrderId, data: OrderUpdate, user: CurrentUser, service: OrderServiceDep):
    return await service.update(order_id, data, user)


@router.post("/{order_id}/cancel", response_model=OrderOut)
async def cancel_order(order_id: OrderId, user: CurrentUser, service: OrderServiceDep):
    return await service.cancel(order_id, user)


@router.patch("/{order_id}/status", response_model=OrderOut)
async def update_order_status(order_id: OrderId, data: OrderStatusUpdate, user: ManagerUser, service: OrderServiceDep):
    return await service.set_status(order_id, data.status)


@router.delete("/{order_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_order(order_id: OrderId, admin: AdminUser, service: OrderServiceDep) -> None:
    await service.delete(order_id)
