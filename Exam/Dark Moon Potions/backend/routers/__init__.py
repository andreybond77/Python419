# routers/__init__.py
from .auth import router as auth_router
from .users import router as users_router
from .potions import router as potions_router
from .cart import router as cart_router
from .orders import router as orders_router
from .reviews import router as reviews_router
from .wishlist import router as wishlist_router
from .payments import router as payments_router
from .categories import router as categories_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router",
    "potions_router",
    "cart_router",
    "orders_router",
    "reviews_router",
    "wishlist_router",
    "payments_router",
    "categories_router",
    "admin_router",
]