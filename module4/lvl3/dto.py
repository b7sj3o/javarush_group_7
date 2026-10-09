from enum import StrEnum
from datetime import date


from pydantic import BaseModel, Field, ConfigDict, field_validator, model_validator


class Genre(StrEnum):
    POETRY = "poetry"
    NOVEL = "novel"
    DRAMA = "drama"
    HISTORY = "history"
    

class Author(BaseModel):
    name: str = Field(min_length=2, max_length=100)
    year_born: int | None = Field(default=None, ge=1000, le=2100)


class BookCreate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    
    title: str = Field(min_length=1, max_length=200)
    author: Author
    year_born: int = Field(ge=1450, le=2100)
    available: bool = True
    genre: Genre
    
    @field_validator("title")
    @classmethod
    def no_ads_in_title(cls, value: str) -> str:
        if "реклама" in value.lower():
            raise ValueError("назва не може містити рекламу")
        return value
    
    
    @model_validator(mode="after")
    def published_after_birth(self):
        print(self.author, type(self.author), self)
        if self.author.year_born is not None and self.year_born < self.author.year_born:
            raise ValueError("книга не може вийти раніше, ніж народився автор")
        return self

class Book(BookCreate):
    id: int
    added_at: date


class BookUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    
    title: str | None = Field(default=None, min_length=1, max_length=200)
    author: Author | None = None
    year_born: int | None = Field(default=None, ge=1450, le=2100)
    available: bool | None = None
    genre: Genre | None = None
    
