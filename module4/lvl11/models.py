from datetime import datetime
from decimal import Decimal

from sqlalchemy import Column, ForeignKey, Numeric, String, Table, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base

# Many-to-many: товар має багато тегів, тег багато товарів. Обидві колонки разом = композитний ключ
product_tags = Table(
    "product_tags",
    Base.metadata,
    Column("product_id", ForeignKey("products.id"), primary_key=True),
    Column("tag_id", ForeignKey("tags.id"), primary_key=True),
)


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True)

    # One-to-many, сторона «один»: список
    products: Mapped[list["Product"]] = relationship(back_populates="category")


class Tag(Base):
    __tablename__ = "tags"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), unique=True)

    products: Mapped[list["Product"]] = relationship(secondary=product_tags, back_populates="tags")


class Product(Base):
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200))
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    stock: Mapped[int]

    # One-to-many, сторона «багато»: тут зовнішній ключ
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    # lazy не вказуємо навмисно: що й коли завантажувати, вирішуємо в кожному запиті (слайд 6)
    category: Mapped[Category] = relationship(back_populates="products")
    tags: Mapped[list[Tag]] = relationship(secondary=product_tags, back_populates="products")


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100))
    email: Mapped[str] = mapped_column(String(255), unique=True)
    age: Mapped[int]
    balance: Mapped[Decimal] = mapped_column(Numeric(12, 2))

    # One-to-one: анотація без list уже означає uselist=False
    profile: Mapped["Profile"] = relationship(back_populates="user")
    orders: Mapped[list["Order"]] = relationship(back_populates="user")


class Profile(Base):
    __tablename__ = "profiles"

    id: Mapped[int] = mapped_column(primary_key=True)
    # unique=True і робить зв'язок справді 1:1 на рівні бази: другий профіль тому самому юзеру не вставиться
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    city: Mapped[str] = mapped_column(String(100))

    user: Mapped[User] = relationship(back_populates="profile")


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(primary_key=True)
    # Індексу на user_id навмисно немає: Postgres НЕ створює його для зовнішнього ключа сам (демо EXPLAIN, слайд 9)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    total: Mapped[Decimal] = mapped_column(Numeric(12, 2))
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())

    user: Mapped[User] = relationship(back_populates="orders")
    items: Mapped[list["OrderItem"]] = relationship(back_populates="order")


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(ForeignKey("orders.id"))
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))
    quantity: Mapped[int]
    price: Mapped[Decimal] = mapped_column(Numeric(10, 2))  # ціна на момент покупки

    order: Mapped[Order] = relationship(back_populates="items")
    product: Mapped[Product] = relationship()
