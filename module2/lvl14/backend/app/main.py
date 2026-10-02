import os
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session, joinedload

from .database import Base, engine, get_db
from .models import Category, Product
from .schemas import CategoryOut, ProductCreate, ProductOut
from .seed import seed_data


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    db = next(get_db())
    try:
        if os.getenv("ENV") == "development":
            seed_data(db)
    finally:
        db.close()
    yield


app = FastAPI(title="Mini Shop API", lifespan=lifespan)

frontend_url = os.getenv("FRONTEND_URL")

if not frontend_url:
    raise RuntimeError("FRONTEND_URL is not set")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/health")
def health_check():
    return {"status": "ok"}


@app.get("/api/products", response_model=list[ProductOut])
def list_products(db: Session = Depends(get_db)):
    return (
        db.query(Product)
        .options(joinedload(Product.category))
        .order_by(Product.id)
        .all()
    )


@app.post("/api/products", response_model=ProductOut, status_code=201)
def create_product(product_data: ProductCreate, db: Session = Depends(get_db)):
    category = db.get(Category, product_data.category_id)

    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    product = Product(**product_data.model_dump())
    db.add(product)
    db.commit()
    db.refresh(product)

    return product


@app.get("/api/products/{product_id}", response_model=ProductOut)
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = (
        db.query(Product)
        .options(joinedload(Product.category))
        .filter(Product.id == product_id)
        .first()
    )

    if product is None:
        raise HTTPException(status_code=404, detail="Product not found")

    return product


@app.get("/api/categories", response_model=list[CategoryOut])
def list_categories(db: Session = Depends(get_db)):
    return db.query(Category).order_by(Category.name).all()
