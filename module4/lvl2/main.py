import asyncio
import time

import httpx
import uvicorn
from pydantic import BaseModel, Field, model_validator
from fastapi import FastAPI, HTTPException, Response

app = FastAPI()


class ItemRead(BaseModel):
    id: int = Field(..., ge=0, description="Item ID must be a non-negative integer")
    name: str = Field(..., min_length=1, max_length=20, description="Item name must be a non-empty string")
    price: float
    

class ItemCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=20, description="Item name must be a non-empty string")
    price: float
    
    
class ItemUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=20, description="Item name must be a non-empty string")
    price: float | None = None
    
    @model_validator(mode="after")
    def at_least_one_field(self):
        if not self.model_fields_set:
            raise ValueError("At least one field must be provided")
        return self


items: list[ItemRead] = [
    ItemRead(id=1, name="Item 1", price=10.0),
    ItemRead(id=2, name="Item 2", price=20.0),
    ItemRead(id=3, name="Item 3", price=30.0)
]

def _get_item(item_id: int) -> ItemRead:
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(
            status_code=404,
            detail="Item not found"
        ) 


@app.get("/items", response_model=list[ItemRead])
async def get_items():
    return items
    
    
@app.get("/items/{item_id}", response_model=ItemRead)
async def get_item(item_id: int):
    return _get_item(item_id)
    


@app.post("/items", response_model=ItemRead)
async def get_item(item: ItemCreate):
    new_item = ItemRead(item_id=len(items)+1, name=item.name, price=item.price)
    items.append(new_item)
    
    return new_item


@app.put("/items/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, item: ItemCreate):
    old_item = _get_item(item_id)
    
    for k,v in item.model_dump(exclude_unset=True).items():
        setattr(old_item, k, v)
    
    # old_item.name = item.name
    # old_item.price = item.price
    
    return old_item


@app.patch("/items/{item_id}", response_model=ItemRead)
async def update_item(item_id: int, item: ItemUpdate):
    old_item = _get_item(item_id)
    
    for k,v in item.model_dump(exclude_unset=True).items():
        if v is not None:
            setattr(old_item, k, v)
    
    # old_item.name = item.name
    # old_item.price = item.price
    
    return old_item


@app.delete("/items/{item_id}", response_model=ItemRead)
async def delete_item(item_id: int):
    old_item = _get_item(item_id)
    items.remove(old_item)
    
    return Response(status_code=204)

# @app.get("/slow/async", tags=["async"])
# async def slow_async():
#     await asyncio.sleep(3)      # чекаємо, але event loop вільний
#     return {"mode": "async def + await asyncio.sleep"}


# @app.get("/slow/blocking", tags=["async"])
# async def slow_blocking():
#     time.sleep(3)               # блокує event loop: стоїть увесь сервер
#     return {"mode": "async def + time.sleep"}


# @app.get("/slow/sync", tags=["async"])
# def slow_sync():
#     time.sleep(3)               # звичайний def FastAPI сам виконує в пулі потоків
#     return {"mode": "def + time.sleep"}

# NBU_URL = "https://bank.gov.ua/NBUStatService/v1/statdirectory/exchange"

# async def fetch_rate(client: httpx.AsyncClient, code: str) -> float:
#     response = await client.get(NBU_URL, params={"valcode": code, "json": ""})
#     response.raise_for_status()
#     return response.json()[0]["rate"]

# @app.get("/rates", tags=["async"])
# async def rates():
#     codes = ["USD", "EUR", "PLN"]
#     async with httpx.AsyncClient(timeout=10) as client:
#         values = await asyncio.gather(*(fetch_rate(client, code) for code in codes))
#     return dict(zip(codes, values))


if __name__ == "__main__":
    uvicorn.run(app)