# backend/schemas/cart.py (дополните существующий файл)
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ============= Базовые схемы =============

class CartBase(BaseModel):
    """Базовая схема корзины"""
    class Config:
        from_attributes = True

class CartItemBase(BaseModel):
    """Базовая схема элемента корзины"""
    potion_id: str
    quantity: int = Field(1, gt=0, le=99)
    
    class Config:
        from_attributes = True

# ============= Схемы для создания =============

class CartCreate(BaseModel):
    """Схема для создания корзины"""
    user_id: str
    
    @validator('user_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v)

class CartItemCreate(BaseModel):
    """Схема для добавления товара в корзину"""
    potion_id: str
    quantity: int = Field(1, gt=0, le=99)
    
    @validator('potion_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v)

# ============= Схемы для обновления =============

class CartUpdate(BaseModel):
    """Схема для обновления корзины"""
    class Config:
        from_attributes = True

class CartItemUpdate(BaseModel):
    """Схема для обновления количества товара"""
    quantity: int = Field(..., gt=0, le=99)
    
    class Config:
        from_attributes = True

# ============= Схемы для ответа =============

class CartItemResponse(BaseModel):
    """Схема для ответа с данными элемента корзины"""
    id: str
    cart_id: str
    potion_id: str
    quantity: int
    price_per_unit: float
    potion_name: str
    potion_image: Optional[str] = None
    potion_category: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def total_price(self) -> float:
        return self.price_per_unit * self.quantity
    
    @validator('id', 'cart_id', 'potion_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

class CartResponse(BaseModel):
    """Схема для ответа с данными корзины"""
    id: str
    user_id: str
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def total_items(self) -> int:
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self) -> float:
        return sum(item.total_price for item in self.items)
    
    @validator('id', 'user_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

# ============= Схемы для списков =============

class CartListResponse(BaseModel):
    """Схема для списка корзин (для админа)"""
    items: List[CartResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True