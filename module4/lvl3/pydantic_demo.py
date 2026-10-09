from pydantic import BaseModel, ConfigDict, ValidationError


class Book(BaseModel):
    title: str
    year: int
    available: bool = True
    

raw = {"title": "Кобзар", "year": "1840", "available": "yes"}
book = Book.model_validate(raw)
print(book)
print(type(book.year), type(book.available))
print(book.model_dump())
print(book.model_dump_json())

print("--- невалідні дані")
try:
    Book.model_validate({"title": 123, "year": "давно"})
except ValidationError as e:
    print(e)
    print(e.errors()[0])
    
    
print("--- strict")


class StrictBook(Book):
    model_config = ConfigDict(strict=True)


try:
    StrictBook.model_validate(raw)
except ValidationError as e:
    print(e)
    
    
print("--- frozen")


class FrozenBook(Book):
    model_config = ConfigDict(frozen=True)


frozen = FrozenBook(title="Кобзар", year=1840)
try:
    frozen.title = "Інша назва"
except ValidationError as e:
    print(e)
print(frozen.model_copy(update={"title": "Інша назва"}))


print("--- extra")


class StrictFields(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str


print(StrictFields(title="  Кобзар  "))
try:
    StrictFields(title="Кобзар", titel="одрук")
except ValidationError as e:
    print(e)