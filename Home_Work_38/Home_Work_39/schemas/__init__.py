# schemas/__init__.py
from .product import ProductCreate, ProductResponse
from .category import CategoryCreate, CategoryResponse

__all__ = ["ProductCreate", "ProductResponse", "CategoryCreate", "CategoryResponse"]