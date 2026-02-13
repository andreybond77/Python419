# models/__init__.py
from __future__ import annotations

from .user import User
from .cart import Cart, CartItem
from .order import Order, OrderItem
from .payment import Payment
from .potion import Potion, PotionCategory
from .review import Review
from .wishlist import Wishlist

# Экспорт для удобства
__all__ = [
    'User',
    'Cart', 
    'CartItem',
    'Order', 
    'OrderItem',
    'Payment',
    'Potion', 
    'PotionCategory',
    'Review',
    'Wishlist',
]