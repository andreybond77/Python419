# routes/__init__.py
from .products import router as products_router
from .categories import router as categories_router

__all__ = ["products_router", "categories_router"]