from fastapi import APIRouter, Query

from dependencies import AdminUser
from schemas import EventOut
from services.events import EventServiceDep

router = APIRouter(prefix="/logs", tags=["logs"])


@router.get("", response_model=list[EventOut])
async def list_events(
    admin: AdminUser,
    service: EventServiceDep,
    type: str | None = Query(default=None, description="order_created, order_status, review_created"),
    user_id: int | None = Query(default=None, ge=1),
    limit: int = Query(default=20, ge=1, le=100),
):
    return await service.list(type, user_id, limit)
