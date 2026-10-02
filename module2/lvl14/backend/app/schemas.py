from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class CategoryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    description: str


class ProductOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    short_description: str
    description: str
    price: Decimal
    image_url: str
    stock: int
    category: CategoryOut


class ProductCreate(BaseModel):
    title: str = Field(min_length=1, max_length=120)
    short_description: str = Field(min_length=1, max_length=240)
    description: str = Field(min_length=1)
    price: Decimal = Field(gt=0, max_digits=10, decimal_places=2)
    image_url: str = Field(min_length=1, max_length=500)
    stock: int = Field(ge=0)
    category_id: int
