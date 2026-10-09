from datetime import date
from enum import StrEnum
from itertools import count
from typing import Annotated, Literal

from fastapi import FastAPI, HTTPException, Path, Query, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    SecretStr,
    StringConstraints,
    ValidationError,
    field_validator,
    model_validator,
)

from config import settings

app = FastAPI(title=settings.app_name, debug=settings.debug)


# ---------- Власні типи ----------

def check_isbn(value: str) -> str:
    digits = value.replace("-", "")
    if len(digits) != 13 or not digits.isdigit():
        raise ValueError("ISBN має містити 13 цифр")
    total = sum(int(d) * (1 if i % 2 == 0 else 3) for i, d in enumerate(digits))
    if total % 10 != 0:
        raise ValueError("не сходиться контрольна сума ISBN")
    return digits


ISBN = Annotated[str, AfterValidator(check_isbn)]
Phone = Annotated[str, StringConstraints(pattern=r"^\+380\d{9}$")]


class Genre(StrEnum):
    POETRY = "poetry"
    NOVEL = "novel"
    DRAMA = "drama"
    HISTORY = "history"


# ---------- Книги ----------

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
id_seq = count(len(books_db) + 1)

BookId = Annotated[int, Path(ge=1, description="Номер книги")]


def get_book_or_404(book_id: int) -> Book:
    book = books_db.get(book_id)
    if book is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Книгу з id={book_id} не знайдено",
        )
    return book


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


@app.get("/books", response_model=list[Book], tags=["books"])
async def list_books(filters: Annotated[BookFilter, Query()]):
    books = list(books_db.values())
    if filters.author:
        books = [b for b in books if filters.author.lower() in b.author.name.lower()]
    if filters.q:
        books = [b for b in books if filters.q.lower() in b.title.lower()]
    if filters.genre:
        books = [b for b in books if b.genre == filters.genre]
    if filters.available is not None:
        books = [b for b in books if b.available == filters.available]
    if filters.year_from is not None:
        books = [b for b in books if b.year >= filters.year_from]
    if filters.year_to is not None:
        books = [b for b in books if b.year <= filters.year_to]
    books.sort(key=lambda b: getattr(b, filters.sort))
    return books[filters.offset : filters.offset + filters.limit]


@app.get("/books/{book_id}", response_model=Book, tags=["books"])
async def get_book(book_id: BookId):
    return get_book_or_404(book_id)


@app.post("/books", response_model=Book, status_code=status.HTTP_201_CREATED, tags=["books"])
async def create_book(data: BookCreate):
    for book in books_db.values():
        if book.title.lower() == data.title.lower() and book.author.name.lower() == data.author.name.lower():
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={"code": "duplicate", "message": "Така книга вже є", "existing_id": book.id},
            )
    book = Book(id=next(id_seq), added_at=date.today(), **data.model_dump())
    books_db[book.id] = book
    return book


@app.put("/books/{book_id}", response_model=Book, tags=["books"])
async def replace_book(book_id: BookId, data: BookCreate):
    old = get_book_or_404(book_id)
    book = Book(id=book_id, added_at=old.added_at, **data.model_dump())
    books_db[book_id] = book
    return book


@app.patch("/books/{book_id}", response_model=Book, tags=["books"])
async def update_book(book_id: BookId, data: BookUpdate):
    book = get_book_or_404(book_id)
    merged = {**book.model_dump(), **data.model_dump(exclude_none=True)}
    try:
        updated = Book.model_validate(merged)      # повна перевірка, разом із model_validator
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=jsonable_encoder(e.errors()))
    books_db[book_id] = updated
    return updated


@app.delete("/books/{book_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["books"])
async def delete_book(book_id: BookId):
    get_book_or_404(book_id)
    del books_db[book_id]


# ---------- Читачі ----------

class ReaderCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=100)
    email: EmailStr
    phone: Phone
    password: SecretStr = Field(min_length=8)
    password_confirm: SecretStr

    @model_validator(mode="after")
    def passwords_match(self):
        if self.password.get_secret_value() != self.password_confirm.get_secret_value():
            raise ValueError("паролі не збігаються")
        return self


class ReaderOut(BaseModel):
    id: int
    name: str
    email: EmailStr
    phone: Phone


class Reader(ReaderOut):
    password: SecretStr


readers_db: dict[int, Reader] = {}
reader_seq = count(1)


@app.post("/readers", response_model=ReaderOut, status_code=status.HTTP_201_CREATED, tags=["readers"])
async def create_reader(data: ReaderCreate):
    reader = Reader(id=next(reader_seq), **data.model_dump(exclude={"password_confirm"}))
    readers_db[reader.id] = reader
    return reader           # response_model відріже password


# ---------- Замовлення з доставкою ----------

class NovaPoshtaDelivery(BaseModel):
    type: Literal["nova_poshta"]
    city: str = Field(min_length=2)
    warehouse: int = Field(ge=1)


class CourierDelivery(BaseModel):
    type: Literal["courier"]
    address: str = Field(min_length=5)


Delivery = Annotated[NovaPoshtaDelivery | CourierDelivery, Field(discriminator="type")]


class OrderCreate(BaseModel):
    book_id: int = Field(ge=1)
    reader_email: EmailStr
    delivery: Delivery
    delivery_date: date

    @field_validator("delivery_date")
    @classmethod
    def not_in_the_past(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("дата доставки вже минула")
        return value


class Order(OrderCreate):
    id: int


orders_db: dict[int, Order] = {}
order_seq = count(1)


@app.post("/orders", response_model=Order, status_code=status.HTTP_201_CREATED, tags=["orders"])
async def create_order(data: OrderCreate):
    book = get_book_or_404(data.book_id)
    if not book.available:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Книга зараз видана")
    order = Order(id=next(order_seq), **data.model_dump())
    orders_db[order.id] = order
    return order


# ---------- Службове ----------

@app.get("/info", tags=["service"])
async def info():
    return {"app": settings.app_name, "debug": settings.debug, "secret": str(settings.secret_key)}


@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    errors = {}
    for err in exc.errors():
        field = ".".join(str(part) for part in err["loc"] if part not in ("body", "query", "path"))
        errors[field or "__all__"] = err["msg"].removeprefix("Value error, ")
    return JSONResponse(status_code=422, content={"errors": errors})