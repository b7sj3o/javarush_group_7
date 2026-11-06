from .categories import router as categories_router
from .orders import router as orders_router
from .products import router as products_router
from .stats import router as stats_router
from .tags import router as tags_router
from .transfers import router as transfers_router
from .users import router as users_router

__all__ = [
    "categories_router",
    "orders_router",
    "products_router",
    "stats_router",
    "tags_router",
    "transfers_router",
    "users_router",
]
