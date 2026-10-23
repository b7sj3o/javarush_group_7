from collections.abc import Sequence
from typing import Annotated

from fastapi import Depends, HTTPException, status

from database import SessionDep
from exceptions import BadRequestError, ConflictError, NotFoundError
from models import Role, User
from repositories.users import UserRepository
from schemas import PasswordChange, UserCreate
from security import hash_password, verify_password


class UserService:
    """Правила роботи з користувачами. Сервіс вирішує, що можна, і робить commit."""

    def __init__(self, session: SessionDep):
        self.session = session
        self.users = UserRepository(session)

    async def get_or_404(self, user_id: int) -> User:
        user = await self.users.get_by_id(user_id)
        if user is None:
            raise NotFoundError(f"Користувача з id={user_id} не знайдено")
        return user

    async def register(self, data: UserCreate) -> User:
        if await self.users.get_by_email(data.email) is not None:
            raise ConflictError("Такий email вже зайнятий")
        user = User(
            name=data.name,
            email=data.email,
            hashed_password=hash_password(data.password.get_secret_value()),
        )
        self.users.add(user)
        await self.session.commit()  # тут база видає user.id
        return user

    async def authenticate(self, email: str, password: str) -> User:
        user = await self.users.get_by_email(email)
        if user is None or not verify_password(password, user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect username or password")
        if not user.is_active:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="User is inactive")
        return user

    async def list(self) -> Sequence[User]:
        return await self.users.list()

    async def rename(self, user: User, name: str) -> User:
        user.name = name  # ORM стежить за змінами: commit сам зробить UPDATE
        await self.session.commit()
        return user

    async def change_password(self, user: User, data: PasswordChange) -> None:
        if not verify_password(data.old_password.get_secret_value(), user.hashed_password):
            raise BadRequestError("Неправильний старий пароль")
        user.hashed_password = hash_password(data.new_password.get_secret_value())
        await self.session.commit()

    async def change_role(self, user_id: int, role: Role, admin: User) -> User:
        user = await self.get_or_404(user_id)
        if user.id == admin.id and role != Role.ADMIN:
            raise ConflictError("Адмін не може зняти з себе роль admin")
        user.role = role
        await self.session.commit()
        return user

    async def change_active(self, user_id: int, is_active: bool) -> User:
        user = await self.get_or_404(user_id)
        user.is_active = is_active
        await self.session.commit()
        return user


# Depends() без аргументу: FastAPI сам створить UserService і передасть у __init__ сесію запиту
UserServiceDep = Annotated[UserService, Depends()]
