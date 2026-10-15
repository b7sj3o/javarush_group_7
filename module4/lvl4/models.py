from datetime import date
from enum import StrEnum
from itertools import count
from typing import Annotated

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    field_validator,
    model_validator,
)

from security import hash_password


class Role(StrEnum):
    READER = "reader"
    MANAGER = "manager"
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
    is_active: bool = True


class User(UserOut):
    hashed_password: str


class UserNameUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)


class PasswordChange(BaseModel):
    model_config = ConfigDict(extra="forbid")

    old_password: SecretStr
    new_password: SecretStr = Field(min_length=8)
    new_password_confirm: SecretStr

    @model_validator(mode="after")
    def passwords_match(self):
        if self.new_password.get_secret_value() != self.new_password_confirm.get_secret_value():
            raise ValueError("паролі не збігаються")
        return self


class RoleUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Role


class ActiveUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_active: bool


users_db: dict[int, User] = {}
user_seq = count(1)


def add_user(
    name: str,
    email: str,
    password: str,
    role: Role = Role.READER,
    is_active: bool = True,
) -> User:
    user = User(
        id=next(user_seq),
        name=name,
        email=email,
        role=role,
        is_active=is_active,
        hashed_password=hash_password(password),
    )
    users_db[user.id] = user
    return user


def get_user_by_email(email: str) -> User | None:
    for user in users_db.values():
        if user.email.lower() == email.lower():
            return user
    return None

def get_user_by_id(user_id: int) -> User | None:
    return users_db.get(user_id)

# Стартові користувачі: хеші рахуються при запуску
add_user("Адмін", "admin@library.ua", "admin12345", Role.ADMIN)
add_user("Менеджер", "manager@library.ua", "manager12345", Role.MANAGER)
add_user("Оля", "olia@example.com", "secret123")
#щоб перевірити 403 для деактивованого
add_user("Неактивний", "off@example.com", "secret123", is_active=False)


# ---------- Книги ----------

def check_isbn(value: str) -> str:
    digits = value.replace("-", "")
    if len(digits) != 13 or not digits.isdigit():
        raise ValueError("ISBN має містити 13 цифр")
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    if total % 10 != 0:
        raise ValueError("не сходиться контрольна сума ISBN")
    return digits


ISBN = Annotated[str, AfterValidator(check_isbn)]


class Genre(StrEnum):
    POETRY = "poetry"
    NOVEL = "novel"
    DRAMA = "drama"
    HISTORY = "history"


class Author(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    born: int | None = Field(default=None, ge=1000, le=2100)


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200, examples=["Кобзар"])
    author: Author
    year: int = Field(ge=1450, le=2100)
    genre: Genre
    isbn: ISBN | None = None
    available: bool = True

    @field_validator("title")
    @classmethod
    def no_ads_in_title(cls, value: str) -> str:
        if "реклама" in value.lower():
            raise ValueError("назва не може містити рекламу")
        return value

    @model_validator(mode="after")
    def published_after_birth(self):
        if self.author.born is not None and self.year < self.author.born:
            raise ValueError("книга не може вийти раніше, ніж народився автор")
        return self


class Book(BookCreate):
    id: int
    added_at: date


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: Author | None = None
    year: int | None = Field(default=None, ge=1450, le=2100)
    genre: Genre | None = None
    isbn: ISBN | None = None
    available: bool | None = None


books_db: dict[int, Book] = {
    1: Book(id=1, title="Кобзар", author=Author(name="Тарас Шевченко", born=1814), year=1840,
            genre=Genre.POETRY, isbn="9789660301016", added_at=date(2026, 10, 1)),
    2: Book(id=2, title="Захар Беркут", author=Author(name="Іван Франко", born=1856), year=1883,
            genre=Genre.HISTORY, added_at=date(2026, 10, 1)),
    3: Book(id=3, title="Лісова пісня", author=Author(name="Леся Українка", born=1871), year=1911,
            genre=Genre.DRAMA, added_at=date(2026, 10, 1)),
    4: Book(id=4, title="Місто", author=Author(name="Валер'ян Підмогильний", born=1901), year=1928,
            genre=Genre.NOVEL, added_at=date(2026, 10, 2)),
    5: Book(id=5, title="Тигролови", author=Author(name="Іван Багряний", born=1906), year=1944,
            genre=Genre.NOVEL, available=False, added_at=date(2026, 10, 2)),
    6: Book(id=6, title="Сад Гетсиманський", author=Author(name="Іван Багряний", born=1906), year=1950,
            genre=Genre.NOVEL, isbn="9789660312227", added_at=date(2026, 10, 3)),
}
book_seq = count(len(books_db) + 1)