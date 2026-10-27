"""Pydantic-схеми: що API приймає і віддає. У Mongo немає моделей-таблиць, тож це єдиний опис книги в коді."""

from datetime import datetime
from enum import StrEnum
from typing import Annotated, Literal

from pydantic import BaseModel, BeforeValidator, ConfigDict, Field, model_validator

ObjectIdStr = Annotated[str, BeforeValidator(str)]


class Genre(StrEnum):
    POETRY = "poetry"
    NOVEL = "novel"
    DRAMA = "drama"
    HISTORY = "history"


class Author(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    born: int | None = Field(default=None, ge=1000, le=2100)


# ---------- Видання: різні формати мають різні поля ----------


class PaperEdition(BaseModel):
    format: Literal["paper"]
    pages: int = Field(ge=1)
    isbn: str | None = Field(default=None, pattern=r"^\d{13}$")


class EbookEdition(BaseModel):
    format: Literal["ebook"]
    file_format: Literal["epub", "pdf", "fb2"]
    size_mb: float = Field(gt=0)


class AudioEdition(BaseModel):
    format: Literal["audio"]
    narrator: str = Field(min_length=2)
    duration_min: int = Field(ge=1)


# discriminator: Pydantic дивиться на поле format і одразу знає, яку з трьох схем перевіряти
Edition = Annotated[PaperEdition | EbookEdition | AudioEdition, Field(discriminator="format")]


# ---------- Книги ----------


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(min_length=1, max_length=200, examples=["Кобзар"])
    authors: list[Author] = Field(min_length=1)
    year: int = Field(ge=1450, le=2100)
    genre: Genre
    edition: Edition
    tags: list[str] = []

    @model_validator(mode="after")
    def published_after_birth(self):
        if any(a.born is not None and self.year < a.born for a in self.authors):
            raise ValueError("книга не може вийти раніше, ніж народився автор")
        return self


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str | None = Field(default=None, min_length=1, max_length=200)
    authors: list[Author] | None = Field(default=None, min_length=1)
    year: int | None = Field(default=None, ge=1450, le=2100)
    genre: Genre | None = None
    edition: Edition | None = None
    tags: list[str] | None = None


class ReviewCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    user: str = Field(min_length=2, max_length=50)
    rating: int = Field(ge=1, le=5)
    text: str = Field(default="", max_length=1000)


class Review(ReviewCreate):
    created_at: datetime


class BookShort(BaseModel):
    """Книга в списку: без відгуків, їх відрізає projection у запиті."""

    # Читаємо з _id, а у відповіді поле зветься id
    id: ObjectIdStr = Field(validation_alias="_id")
    title: str
    authors: list[Author]
    year: int
    genre: Genre
    edition: Edition
    tags: list[str] = []
    added_at: datetime


class BookOut(BookShort):
    reviews: list[Review] = []


class BookFilter(BaseModel):
    model_config = ConfigDict(extra="forbid")

    author: str | None = None
    q: str | None = Field(default=None, min_length=2, description="Пошук у назві")
    genre: Genre | None = None
    format: Literal["paper", "ebook", "audio"] | None = None
    year_from: int | None = Field(default=None, ge=1450)
    year_to: int | None = Field(default=None, le=2100)
    sort: Literal["title", "year", "added_at"] = "added_at"
    offset: int = Field(default=0, ge=0)
    limit: int = Field(default=10, ge=1, le=50)


# ---------- Статистика (агрегації) ----------


class GenreStats(BaseModel):
    genre: Genre
    books: int
    first_year: int
    last_year: int


class TopRated(BaseModel):
    id: ObjectIdStr = Field(validation_alias="_id")
    title: str
    avg_rating: float
    reviews: int
