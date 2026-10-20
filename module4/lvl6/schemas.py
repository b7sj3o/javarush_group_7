"""Pydantic-схеми: що API приймає і що віддає. Таблиці бази описані окремо, у models.py."""

from datetime import date, datetime
from typing import Annotated, Literal

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

from models import Genre, OrderStatus, Role

# ---------- Користувачі ----------


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
    is_active: bool


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


class AuthorSchema(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    born: int | None = Field(default=None, ge=1000, le=2100)


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200, examples=["Кобзар"])
    author: AuthorSchema
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


class BookOut(BookCreate):
    id: int
    added_at: date


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: AuthorSchema | None = None
    year: int | None = Field(default=None, ge=1450, le=2100)
    genre: Genre | None = None
    isbn: ISBN | None = None
    available: bool | None = None


class BookFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author: str | None = None
    q: str | None = Field(default=None, min_length=2, description="Пошук у назві")
    genre: Genre | None = None
    available: bool | None = None
    year_from: int | None = Field(default=None, ge=1450)
    year_to: int | None = Field(default=None, le=2100)
    sort: Literal["id", "title", "year"] = "id"
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)

    @model_validator(mode="after")
    def years_in_order(self):
        if self.year_from is not None and self.year_to is not None and self.year_from > self.year_to:
            raise ValueError("year_from не може бути більшим за year_to")
        return self


# ---------- Замовлення ----------


class NovaPoshtaDelivery(BaseModel):
    type: Literal["nova_poshta"]
    city: str = Field(min_length=2)
    warehouse: int = Field(ge=1)


class CourierDelivery(BaseModel):
    type: Literal["courier"]
    address: str = Field(min_length=5)


Delivery = Annotated[NovaPoshtaDelivery | CourierDelivery, Field(discriminator="type")]


def check_not_in_past(value: date) -> date:
    if value < date.today():
        raise ValueError("дата доставки вже минула")
    return value


DeliveryDate = Annotated[date, AfterValidator(check_not_in_past)]


class OrderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    book_id: int = Field(ge=1)
    delivery: Delivery
    delivery_date: DeliveryDate


class OrderUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    delivery: Delivery | None = None
    delivery_date: DeliveryDate | None = None


class OrderOut(BaseModel):
    id: int
    owner_id: int
    book_id: int
    status: OrderStatus
    delivery: Delivery
    delivery_date: date  # без перевірки «не в минулому»: старе замовлення має право мати минулу дату
    created_at: datetime


class OrderStatusUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus


class OrderFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: OrderStatus | None = None
    book_id: int | None = Field(default=None, ge=1)
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)
