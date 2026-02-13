# backend/schemas/__init__.py
from .user import (
    UserBase, UserCreate, UserUpdate, UserResponse, UserProfileResponse, UserListResponse,
    UserRegister, UserPasswordChange, PasswordResetRequest, PasswordResetConfirm,
    EmailVerificationRequest, EmailVerificationResponse,
    Token, TokenData, LoginRequest
)
from .potion import (
    PotionBase, PotionCreate, PotionUpdate, PotionResponse, PotionListResponse,
    PotionCategoryBase, PotionCategoryCreate, PotionCategoryUpdate, 
    PotionCategoryResponse, PotionCategoryListResponse,
    PotionFilter, PotionFilterResponse
)
from .cart import (
    CartBase, CartCreate, CartUpdate, CartResponse,
    CartItemBase, CartItemCreate, CartItemUpdate, CartItemResponse,
    CartListResponse
)
from .order import (
    OrderBase, OrderCreate, OrderUpdate, OrderResponse, OrderDetailResponse, OrderListResponse,
    OrderItemBase, OrderItemCreate, OrderItemUpdate, OrderItemResponse,
    OrderStatus, OrderStatusUpdate, OrderCancelRequest, OrderCancelResponse,
    OrderStats, OrderSummary,
    OrderFilter, OrderFilterResponse  # ДОБАВЛЕНО!
)
from .review import (
    ReviewBase, ReviewCreate, ReviewUpdate, ReviewResponse,
    ReviewListResponse, ReviewModerationUpdate,
    ReviewHelpfulCreate, ReviewHelpfulResponse,
    ReviewStats
)
from .wishlist import (
    WishlistBase, WishlistCreate, WishlistUpdate, WishlistResponse, 
    WishlistDetailResponse, WishlistListResponse, WishlistCheckResponse,
    WishlistBulkCreate, WishlistBulkDelete, WishlistStats
)
from .payment import (
    PaymentBase, PaymentCreate, PaymentUpdate, PaymentResponse,
    PaymentListResponse, PaymentStats,
    PaymentRefundRequest, PaymentRefundResponse,
    PaymentStatus
)
from .category import (
    PotionCategoryBase as CatBase,
    PotionCategoryCreate as CatCreate,
    PotionCategoryUpdate as CatUpdate,
    PotionCategoryResponse as CatResponse,
    PotionCategoryListResponse as CatListResponse
)

__all__ = [
    # User schemas
    'UserBase', 'UserCreate', 'UserUpdate', 'UserResponse', 'UserProfileResponse', 'UserListResponse',
    'UserRegister', 'UserPasswordChange', 'PasswordResetRequest', 'PasswordResetConfirm',
    'EmailVerificationRequest', 'EmailVerificationResponse',
    'Token', 'TokenData', 'LoginRequest',
    
    # Potion schemas
    'PotionBase', 'PotionCreate', 'PotionUpdate', 'PotionResponse', 'PotionListResponse',
    'PotionCategoryBase', 'PotionCategoryCreate', 'PotionCategoryUpdate',
    'PotionCategoryResponse', 'PotionCategoryListResponse',
    'PotionFilter', 'PotionFilterResponse',
    
    # Cart schemas
    'CartBase', 'CartCreate', 'CartUpdate', 'CartResponse',
    'CartItemBase', 'CartItemCreate', 'CartItemUpdate', 'CartItemResponse',
    'CartListResponse',
    
    # Order schemas
    'OrderBase', 'OrderCreate', 'OrderUpdate', 'OrderResponse', 'OrderDetailResponse', 'OrderListResponse',
    'OrderItemBase', 'OrderItemCreate', 'OrderItemUpdate', 'OrderItemResponse',
    'OrderStatus', 'OrderStatusUpdate', 'OrderCancelRequest', 'OrderCancelResponse',
    'OrderStats', 'OrderSummary',
    'OrderFilter', 'OrderFilterResponse',  # ДОБАВЛЕНО!
    
    # Review schemas
    'ReviewBase', 'ReviewCreate', 'ReviewUpdate', 'ReviewResponse',
    'ReviewListResponse', 'ReviewModerationUpdate',
    'ReviewHelpfulCreate', 'ReviewHelpfulResponse',
    'ReviewStats',
    
    # Wishlist schemas
    'WishlistBase', 'WishlistCreate', 'WishlistUpdate', 'WishlistResponse',
    'WishlistDetailResponse', 'WishlistListResponse', 'WishlistCheckResponse',
    'WishlistBulkCreate', 'WishlistBulkDelete', 'WishlistStats',
    
    # Payment schemas
    'PaymentBase', 'PaymentCreate', 'PaymentUpdate', 'PaymentResponse',
    'PaymentListResponse', 'PaymentStats',
    'PaymentRefundRequest', 'PaymentRefundResponse',
    'PaymentStatus',
    
    # Category schemas (aliases)
    'CatBase', 'CatCreate', 'CatUpdate', 'CatResponse', 'CatListResponse',
]