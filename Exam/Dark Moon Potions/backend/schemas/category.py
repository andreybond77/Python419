# backend/schemas/category.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID

class PotionCategoryBase(BaseModel):
    """Базовая схема категории зелий"""
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: bool = True
    
    class Config:
        from_attributes = True

class PotionCategoryCreate(PotionCategoryBase):
    """Схема для создания категории"""
    slug: str = Field(..., min_length=1, max_length=100)
    
    @validator('slug')
    def slug_alphanumeric(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Slug must be alphanumeric with hyphens or underscores')
        return v

class PotionCategoryResponse(PotionCategoryBase):
    """Схема для ответа с данными категории"""
    id: str
    slug: str
    created_at: datetime
    updated_at: datetime
    potion_count: Optional[int] = 0
    
    @validator('id', pre=True, always=True)
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

class PotionCategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    slug: Optional[str] = Field(None, min_length=1, max_length=100)
    icon: Optional[str] = None
    color: Optional[str] = None
    is_active: Optional[bool] = None
    
    class Config:
        from_attributes = True

class PotionCategoryListResponse(BaseModel):
    """Схема для списка категорий с пагинацией"""
    items: List[PotionCategoryResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True