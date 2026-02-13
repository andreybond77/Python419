# backend/schemas/wishlist.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List
from uuid import UUID
from datetime import datetime

# ============= Базовые схемы =============

class WishlistBase(BaseModel):
    """Базовая схема избранного"""
    potion_id: str
    note: Optional[str] = Field(None, max_length=500)
    
    class Config:
        from_attributes = True

# ============= Схемы для создания =============

class WishlistCreate(BaseModel):
    """Схема для добавления в избранное"""
    potion_id: str
    note: Optional[str] = Field(None, max_length=500)
    
    @validator('potion_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Конвертирует UUID в строку"""
        if isinstance(v, UUID):
            return str(v)
        return str(v)

# ============= Схемы для обновления =============

class WishlistUpdate(BaseModel):
    """Схема для обновления заметки в избранном"""
    note: Optional[str] = Field(None, max_length=500)
    
    class Config:
        from_attributes = True

# ============= Схемы для ответа =============

class WishlistResponse(BaseModel):
    """Схема для ответа с данными избранного"""
    id: str
    user_id: str
    potion_id: str
    note: Optional[str] = None
    created_at: datetime
    
    # Данные о зелье (опционально, для вложенных запросов)
    potion_name: Optional[str] = None
    potion_image: Optional[str] = None
    potion_price: Optional[float] = None
    potion_rarity: Optional[str] = None
    potion_category: Optional[str] = None
    
    @validator('id', 'user_id', 'potion_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        """Конвертирует UUID в строку"""
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

class WishlistDetailResponse(WishlistResponse):
    """Расширенная схема с детальной информацией о зелье"""
    potion_description: Optional[str] = None
    potion_effects: Optional[List[str]] = None
    in_stock: Optional[bool] = None
    
    class Config:
        from_attributes = True

# ============= Схемы для списков =============

class WishlistListResponse(BaseModel):
    """Схема для списка избранного с пагинацией"""
    items: List[WishlistResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True

# ============= Схемы для проверки =============

class WishlistCheckResponse(BaseModel):
    """Схема для проверки наличия в избранном"""
    in_wishlist: bool
    wishlist_id: Optional[str] = None
    
    @validator('wishlist_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        json_encoders = {UUID: str}

# ============= Схемы для массовых операций =============

class WishlistBulkCreate(BaseModel):
    """Схема для массового добавления в избранное"""
    potion_ids: List[str]
    
    @validator('potion_ids', each_item=True)
    def validate_potion_ids(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v)

class WishlistBulkDelete(BaseModel):
    """Схема для массового удаления из избранного"""
    potion_ids: List[str]
    
    @validator('potion_ids', each_item=True)
    def validate_potion_ids(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v)

# ============= Схемы для статистики =============

class WishlistStats(BaseModel):
    """Схема для статистики избранного"""
    total_items: int
    unique_categories: int
    most_popular_category: Optional[str] = None
    total_value: float = 0.0
    
    class Config:
        from_attributes = True