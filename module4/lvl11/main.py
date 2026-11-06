from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError

from database import engine, create_db
from routers import (
    categories_router,
    orders_router,
    products_router,
    stats_router,
    tags_router,
    transfers_router,
    users_router,
)
from sql_counter import install_sql_counter

def create_app():
    
    @asynccontextmanager
    async def lifespan(app: FastAPI):
        await create_db(engine)
        yield
        
    
    app = FastAPI(title="Магазин: транзакції, зв'язки, оптимізація", lifespan=lifespan)
    install_sql_counter(app, engine)
    
    app.include_router(users_router, prefix="/users", tags=["users"])
    app.include_router(categories_router, prefix="/categories", tags=["categories"])
    app.include_router(tags_router, prefix="/tags", tags=["tags"])
    app.include_router(products_router, prefix="/products", tags=["products"])
    app.include_router(orders_router, prefix="/orders", tags=["orders"])
    app.include_router(transfers_router, prefix="/transfers", tags=["transfers"])
    app.include_router(stats_router, prefix="/stats", tags=["stats"])

    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError) -> JSONResponse:
        # Дубль email чи назви, неіснуючий зовнішній ключ, видалення запису, на який посилаються інші
        return JSONResponse(status_code=409, content={"detail": "Конфлікт із даними в базі"})

    return app

app = create_app()