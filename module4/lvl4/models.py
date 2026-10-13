from enum import StrEnum
from itertools import count

from pydantic import BaseModel, ConfigDict, EmailStr, Field, SecretStr, model_validator

from security import hash_password


class Role(StrEnum):
    READER = "reader"
    ADMIN = "admin"


class UserCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    password: SecretStr = Field(min_length=8)
    password_confirm: SecretStr

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("паролі не збігаються")
        return self


class UserOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    role: Role


class User(UserOut):
    hashed_password: str


users_db: dict[int, User] = {}
user_seq = count(1)


def add_user(name: str, email: str, password: str, role: Role = Role.READER) -> User:
    user = User(id=next(user_seq), name=name, email=email, role=role, hashed_password=hash_password(password))
    users_db[user.id] = user
    return user


def get_user_by_email(email: str) -> User | None:
    for user in users_db.values():
        if user.email.lower() == email.lower():
            return user
    return None


# Стартові користувачі: хеші рахуються при запуску
add_user("Адмін", "admin@library.ua", "admin12345", Role.ADMIN)
add_user("Оля", "olia@example.com", "secret123")
