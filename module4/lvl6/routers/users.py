from typing import Annotated

from fastapi import APIRouter, Path, status

from dependencies import AdminUser, CurrentUser
from schemas import ActiveUpdate, PasswordChange, RoleUpdate, UserCreate, UserNameUpdate, UserOut
from services.users import UserServiceDep

router = APIRouter(prefix="/users", tags=["users"])

UserId = Annotated[int, Path(ge=1, description="Номер користувача")]


# ---------- Реєстрація та список ----------


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, service: UserServiceDep):
    return await service.register(data)


@router.get("", response_model=list[UserOut])
async def list_users(admin: AdminUser, service: UserServiceDep):
    return await service.list()


# ---------- Профіль (/me має стояти ПЕРЕД /{user_id}) ----------


@router.get("/me", response_model=UserOut)
async def read_users_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserOut)
async def update_users_me(data: UserNameUpdate, user: CurrentUser, service: UserServiceDep):
    return await service.rename(user, data.name)


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(data: PasswordChange, user: CurrentUser, service: UserServiceDep) -> None:
    await service.change_password(user, data)


# ---------- Керування користувачами (лише admin) ----------


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: UserId, admin: AdminUser, service: UserServiceDep):
    return await service.get_or_404(user_id)


@router.patch("/{user_id}/role", response_model=UserOut)
async def change_role(user_id: UserId, data: RoleUpdate, admin: AdminUser, service: UserServiceDep):
    return await service.change_role(user_id, data.role, admin)


@router.patch("/{user_id}/active", response_model=UserOut)
async def change_active(user_id: UserId, data: ActiveUpdate, admin: AdminUser, service: UserServiceDep):
    return await service.change_active(user_id, data.is_active)
