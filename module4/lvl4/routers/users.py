from typing import Annotated

from fastapi import APIRouter, HTTPException, Path, status

from dependencies import AdminUser, CurrentUser
from models import (
    ActiveUpdate,
    PasswordChange,
    Role,
    RoleUpdate,
    User,
    UserCreate,
    UserNameUpdate,
    UserOut,
    add_user,
    get_user_by_email,
    get_user_by_id,
    users_db,
)
from security import hash_password, verify_password

router = APIRouter(prefix="/users", tags=["users"])

UserId = Annotated[int, Path(ge=1, description="Номер користувача")]


def get_user_or_404(user_id: int) -> User:
    user = get_user_by_id(user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Користувача з id={user_id} не знайдено",
        )
    return user


# ---------- Реєстрація та список ----------

@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate):
    if get_user_by_email(data.email) is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Такий email вже зайнятий",
        )
    return add_user(data.name, data.email, data.password.get_secret_value())


@router.get("", response_model=list[UserOut])
async def list_users(admin: AdminUser):
    return list(users_db.values())


# ---------- Профіль (/me має стояти ПЕРЕД /{user_id}) ----------

@router.get("/me", response_model=UserOut)
async def read_users_me(user: CurrentUser):
    return user


@router.patch("/me", response_model=UserOut)
async def update_users_me(data: UserNameUpdate, user: CurrentUser):
    user.name = data.name
    return user


@router.post("/me/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_my_password(data: PasswordChange, user: CurrentUser) -> None:
    if not verify_password(data.old_password.get_secret_value(), user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Неправильний старий пароль",
        )
    user.hashed_password = hash_password(data.new_password.get_secret_value())


# ---------- Керування користувачами (лише admin) ----------

@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: UserId, admin: AdminUser):
    return get_user_or_404(user_id)


@router.patch("/{user_id}/role", response_model=UserOut)
async def change_role(user_id: UserId, data: RoleUpdate, admin: AdminUser):
    user = get_user_or_404(user_id)
    if user.id == admin.id and data.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Адмін не може зняти з себе роль admin",
        )
    user.role = data.role
    return user


@router.patch("/{user_id}/active", response_model=UserOut)
async def change_active(user_id: UserId, data: ActiveUpdate, admin: AdminUser):
    user = get_user_or_404(user_id)
    user.is_active = data.is_active
    return user