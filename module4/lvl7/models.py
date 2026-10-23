from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.types import JSON, String

from database import Base


class Role(StrEnum):
    READER = "reader"
    MANAGER = "manager"
    ADMIN = "admin"


class Genre(StrEnum):
    POETRY = "poetry"
    NOVEL = "novel"
    DRAMA = "drama"
    HISTORY = "history"


class OrderStatus(StrEnum):
    NEW = "new"
    CONFIRMED = "confirmed"
    ISSUED = "issued"
    RETURNED = "returned"
    CANCELLED = "cancelled"


ALLOWED_TRANSITIONS: dict[OrderStatus, set[OrderStatus]] = {
    OrderStatus.NEW: {OrderStatus.CONFIRMED, OrderStatus.CANCELLED},
    OrderStatus.CONFIRMED: {OrderStatus.ISSUED, OrderStatus.CANCELLED},
    OrderStatus.ISSUED: {OrderStatus.RETURNED},
    OrderStatus.RETURNED: set(),
    OrderStatus.CANCELLED: set(),
}

ACTIVE_STATUSES = {OrderStatus.NEW, OrderStatus.CONFIRMED, OrderStatus.ISSUED}


# Асоціативна таблиця many-to-many. primary_key=True на обох колонках = композитний ключ:
# пара (author_id, book_id) унікальна, той самий автор не прив'яжеться до книги двічі.
authors_books_table = Table(
    "authors_books_table",
    Base.metadata,
    Column("author_id", ForeignKey("authors.id"), primary_key=True),
    Column("book_id", ForeignKey("books.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(155), unique=True, index=True)
    phone_number: Mapped[str] = mapped_column(String(15), unique=True)
    hashed_password: Mapped[str]
    role: Mapped[Role] = mapped_column(default=Role.READER)
    is_active: Mapped[bool] = mapped_column(default=True)


class Author(Base):
    __tablename__ = "authors"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)
    born: Mapped[int | None]

    books: Mapped[list["Book"]] = relationship(
        secondary=authors_books_table,
        back_populates="authors",
    )


class Book(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(200), index=True)
    year: Mapped[int]
    genre: Mapped[Genre]
    isbn: Mapped[str | None] = mapped_column(String(13))
    available: Mapped[bool] = mapped_column(default=True)
    added_at: Mapped[date] = mapped_column(default=date.today)
    pages: Mapped[int | None]  # nullable: у старих книг сторінок ще немає

    # lazy="selectin": автори підвантажуються одразу разом із книгою.
    # Без цього book.authors в async-коді падає з MissingGreenlet.
    authors: Mapped[list["Author"]] = relationship(
        secondary=authors_books_table,
        back_populates="books",
        lazy="selectin",
    )


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)

    customer_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    book_id: Mapped[int] = mapped_column(ForeignKey("books.id"))

    status: Mapped[OrderStatus] = mapped_column(default=OrderStatus.NEW)
    delivery: Mapped[dict] = mapped_column(JSON)
    delivery_date: Mapped[date]
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
