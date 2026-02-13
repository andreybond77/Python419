# backend/schemas/potion.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

# ============= Базовые схемы =============

class PotionBase(BaseModel):
    """Базовая схема зелья"""
    name: str = Field(..., min_length=3, max_length=255)
    slug: str = Field(..., min_length=3, max_length=255)
    description: str = Field(..., min_length=10)
    category: str = Field(..., min_length=3, max_length=50)
    price: float = Field(..., gt=0)
    image_url: Optional[str] = None
    in_stock: bool = True
    stock_quantity: int = Field(0, ge=0)
    rarity: str = "common"
    brewing_time: Optional[str] = None
    brewing_difficulty: str = "medium"
    
    class Config:
        from_attributes = True

# ============= Схемы для создания =============

class PotionCreate(PotionBase):
    """Схема для создания нового зелья"""
    category_id: str
    original_price: Optional[float] = None
    discount_percent: int = Field(0, ge=0, le=100)
    min_stock_level: int = Field(10, ge=0)
    ingredients: List[str] = []
    effects: List[str] = []
    warnings: List[str] = []
    image_gallery: List[str] = []
    thumbnail_url: Optional[str] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    published_at: Optional[datetime] = None
    
    @validator('category_id', pre=True)
    def validate_category_id(cls, v):
        """Конвертирует UUID в строку"""
        if isinstance(v, UUID):
            return str(v)
        return str(v)

# ============= Схемы для обновления =============

class PotionUpdate(BaseModel):
    """Схема для обновления зелья (все поля опциональны)"""
    name: Optional[str] = Field(None, min_length=3, max_length=255)
    slug: Optional[str] = Field(None, min_length=3, max_length=255)
    description: Optional[str] = Field(None, min_length=10)
    category: Optional[str] = Field(None, min_length=3, max_length=50)
    category_id: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    original_price: Optional[float] = None
    discount_percent: Optional[int] = Field(None, ge=0, le=100)
    in_stock: Optional[bool] = None
    stock_quantity: Optional[int] = Field(None, ge=0)
    min_stock_level: Optional[int] = Field(None, ge=0)
    rarity: Optional[str] = None
    brewing_time: Optional[str] = None
    brewing_difficulty: Optional[str] = None
    ingredients: Optional[List[str]] = None
    effects: Optional[List[str]] = None
    warnings: Optional[List[str]] = None
    image_url: Optional[str] = None
    thumbnail_url: Optional[str] = None
    image_gallery: Optional[List[str]] = None
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    published_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
    
    @validator('category_id', pre=True, always=True)
    def validate_category_id(cls, v):
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return str(v)

# ============= Схемы для ответа =============

class PotionResponse(PotionBase):
    """Схема для ответа с данными зелья"""
    id: str
    category_id: str
    original_price: Optional[float] = None
    discount_percent: int = 0
    stock_quantity: int = 0
    min_stock_level: int = 10
    brewing_difficulty: str = "medium"
    ingredients: List[str] = []
    effects: List[str] = []
    warnings: List[str] = []
    image_gallery: List[str] = []
    thumbnail_url: Optional[str] = None
    popularity_score: int = 0
    purchase_count: int = 0
    review_count: int = 0
    average_rating: float = 0.0
    meta_title: Optional[str] = None
    meta_description: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    published_at: Optional[datetime] = None
    
    @validator('id', 'category_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        """Конвертирует UUID в строку"""
        if v is None:
            return None
        if isinstance(v, UUID):
            return str(v)
        return str(v)
    
    @validator('image_url', 'thumbnail_url', pre=True, always=True)
    def handle_image_url(cls, v):
        """Обрабатывает URL изображений"""
        if v is None:
            return None
        return str(v)
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

# ============= Схемы для категорий =============

class PotionCategoryBase(BaseModel):
    """Базовая схема категории зелий"""
    name: str = Field(..., min_length=2, max_length=50)
    slug: str = Field(..., min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    
    class Config:
        from_attributes = True

class PotionCategoryCreate(PotionCategoryBase):
    """Схема для создания категории"""
    pass

class PotionCategoryUpdate(BaseModel):
    """Схема для обновления категории"""
    name: Optional[str] = Field(None, min_length=2, max_length=50)
    slug: Optional[str] = Field(None, min_length=2, max_length=50)
    description: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None

class PotionCategoryResponse(PotionCategoryBase):
    """Схема для ответа с данными категории"""
    id: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    @validator('id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v)
    
    class Config:
        from_attributes = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

# ============= Схемы для списков =============

class PotionListResponse(BaseModel):
    """Схема для списка зелий с пагинацией"""
    items: List[PotionResponse]
    total: int
    page: int
    size: int
    pages: int

class PotionCategoryListResponse(BaseModel):
    """Схема для списка категорий"""
    items: List[PotionCategoryResponse]
    total: int

# ============= Схемы для фильтрации =============

class PotionFilter(BaseModel):
    """Схема для фильтрации зелий"""
    category: Optional[str] = None
    rarity: Optional[str] = None
    min_price: Optional[float] = Field(None, ge=0)
    max_price: Optional[float] = Field(None, ge=0)
    in_stock: Optional[bool] = None
    search: Optional[str] = Field(None, min_length=2)
    min_rating: Optional[float] = Field(None, ge=0, le=5)
    brewing_difficulty: Optional[str] = None
    discount_only: Optional[bool] = None
    sort_by: Optional[str] = Field(None, pattern='^(price|rating|popularity|created_at|name)$')  # 🔥 ИСПРАВЛЕНО!
    sort_order: Optional[str] = Field('asc', pattern='^(asc|desc)$')  # 🔥 ИСПРАВЛЕНО!
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    @validator('max_price')
    def validate_price_range(cls, v, values):
        """Проверяет что минимальная цена не больше максимальной"""
        if v is not None and 'min_price' in values and values['min_price'] is not None:
            if values['min_price'] > v:
                raise ValueError('Минимальная цена не может быть больше максимальной')
        return v
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "category": "healing",
                "rarity": "legendary",
                "min_price": 100,
                "max_price": 5000,
                "in_stock": True,
                "search": "зелье",
                "min_rating": 4.5,
                "discount_only": True,
                "sort_by": "popularity",
                "sort_order": "desc",
                "page": 1,
                "page_size": 20
            }
        }

class PotionFilterResponse(BaseModel):
    """Схема для ответа с отфильтрованными зельями"""
    items: List[PotionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "items": [],
                "total": 0,
                "page": 1,
                "page_size": 20,
                "total_pages": 0,
                "filters_applied": {
                    "category": "healing",
                    "in_stock": True
                }
            }
        }