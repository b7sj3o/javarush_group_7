from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, joinedload

from database import SessionDep, get_or_404
from models import Order, Profile, User
from schemas import (
    OrderRead,
    ProfileRead,
    ProfileUpdate,
    UserCreate,
    UserRead,
    UserUpdate,
)

router = APIRouter()


@router.post("", response_model=UserRead, status_code=201)
async def create_user(data: UserCreate, session: SessionDep):
    async with session.begin():
        user = User(**data.model_dump(), balance=0)
        session.add(user)

        await session.flush()

        session.add(Profile(user_id=user.id, city=""))
    return user


@router.get("", response_model=list[UserRead])
async def list_users(session: SessionDep, limit: int = Query(default=50, ge=1, le=200), offset: int = Query(default=0, ge=0)):
    return (await session.scalars(select(User).order_by(User.id).limit(limit).offset(offset))).all()


@router.get("/{user_id}", response_model=UserRead)
async def get_user(user_id: int, session: SessionDep):
    user = await session.scalar(
        select(User)
        .where(User.id == user_id)
        .options(
            joinedload(User.profile)
        )
    )

    print(user.profile)
    
    return user

@router.patch("/{user_id}", response_model=UserRead)
async def update_user(user_id: int, data: UserUpdate, session: SessionDep):
    async with session.begin():
        user = await get_or_404(session, User, user_id)
        for field, value in data.model_dump(exclude_none=True).items():
            setattr(user, field, value)
    return user


@router.delete("/{user_id}", status_code=204)
async def delete_user(user_id: int, session: SessionDep):
    """Є замовлення -> зовнішній ключ не дасть видалити -> 409, і профіль теж лишиться: одна транзакція."""
    async with session.begin():
        await get_or_404(session, User, user_id)
        await session.execute(delete(Profile).where(Profile.user_id == user_id))
        await session.execute(delete(User).where(User.id == user_id))


# ---------- Профіль: 1:1 із юзером, створюється разом із ним ----------


async def _get_profile_or_404(session: AsyncSession, user_id: int) -> Profile:
    profile = await session.scalar(select(Profile).where(Profile.user_id == user_id))
    if profile is None:
        raise HTTPException(status_code=404, detail=f"Профіль юзера {user_id} не знайдено")
    return profile


@router.get("/{user_id}/profile", response_model=ProfileRead)
async def get_profile(user_id: int, session: SessionDep):
    return await _get_profile_or_404(session, user_id)


@router.put("/{user_id}/profile", response_model=ProfileRead)
async def update_profile(user_id: int, data: ProfileUpdate, session: SessionDep):
    async with session.begin():
        profile = await _get_profile_or_404(session, user_id)
        profile.city = data.city
    return profile


# ---------- Замовлення юзера: на цьому запиті EXPLAIN (слайд 9) ----------


@router.get("/{user_id}/orders", response_model=list[OrderRead])
async def user_orders(user_id: int, session: SessionDep):
    """Поки немає індексу на orders.user_id, це Seq Scan по 200 тис. рядків на кожен запит."""
    return (await session.scalars(select(Order).where(Order.user_id == user_id))).all()
