from datetime import date, datetime
from enum import StrEnum

from sqlalchemy import Column, ForeignKey, Table, func
from sqlalchemy.types import String, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship

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


authors_books_table = Table(
    "authors_books_table",
    Base.metadata,
    Column("author_id", ForeignKey("authors.id")),
    Column("book_id", ForeignKey("books.id")),
)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str]
    role: Mapped[Role] = mapped_column(default=Role.READER)
    is_active: Mapped[bool] = mapped_column(default=True)
    

class Author(Base):
    __tablename__ = "authors"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)
    born: Mapped[int | None]
    
    books: Mapped[list["Book"]] = relationship(
        secondary=authors_books_table,
        back_populates="authors"
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
    
    authors: Mapped[list["Author"]] = relationship(
        secondary=authors_books_table,
        back_populates="books"
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