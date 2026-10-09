from fastapi import FastAPI
import uvicorn
from pydantic import BaseModel, EmailStr, field_validator
from typing import Optional # Для опціональних полів


app = FastAPI()


# class Item(BaseModel):
#     # Обов'язкові поля
#     id: int
#     name: str
#     price: float

#     # Опціональне поле зі значенням None за замовчуванням
#     description: Optional[str] = None

#     # Поле з іншим значенням за замовчуванням
#     is_offer: bool = False
    
# item = Item(
#     id=1,
#     name="Item 1", 
#     price=10.0
# )


# print(item) # id=1 name='Item 1' price=10.0 description=None is_offer=False
# print(item.description) # None
# print(item.model_dump()) # dict
# print(item.model_dump_json()) # str





class Author(BaseModel):
    id: int
    name: str
    email: EmailStr
    

class Book(BaseModel):
    id: int
    title: str
    year: int
    author: Author
    available: bool = True
    
    @field_validator("title")
    @classmethod
    def validate_title_starts_with_uppercase(cls, value: str) -> str:
        if not value[0].isupper():
            raise ValueError("Title must start with an uppercase letter")
        return value


author = Author(id=1, name="Author 1", email="sawsasw@wasaws.com")

book = Book(
    id=1,
    title="book 1",
    year=2023,
    author=author
)

# @app.get("/items", response_model=list[Item])
# async def get_items():
#     return [
#         Item(id=1, name="Item 1", price=10.0),
#         Item(id=2, name="Item 2", price=20.0, description="This is item 2"),
#         Item(id=3, name="Item 3", price=30.0, is_offer=True)
#     ]

# if __name__ == "__main__":
#     uvicorn.run(app)
    