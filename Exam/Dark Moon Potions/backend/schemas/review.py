# backend/schemas/review.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, validator
from uuid import UUID

# ============= Базовые схемы =============

class ReviewBase(BaseModel):
    """Базовая схема отзыва"""
    potion_id: str
    rating: int = Field(..., ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: str = Field(..., min_length=1)
    
    @validator('comment')
    def validate_comment_length(cls, v):
        if len(v) > 2000:
            raise ValueError('Comment cannot exceed 2000 characters')
        return v
    
    @validator('potion_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Конвертирует UUID в строку"""
        if isinstance(v, UUID):
            return str(v)
        return str(v)
    
    class Config:
        from_attributes = True

# ============= Схемы для создания =============

class ReviewCreate(ReviewBase):
    """Схема для создания отзыва"""
    pass

# ============= Схемы для обновления =============

class ReviewUpdate(BaseModel):
    """Схема для обновления отзыва"""
    rating: Optional[int] = Field(None, ge=1, le=5)
    title: Optional[str] = Field(None, max_length=255)
    comment: Optional[str] = Field(None, min_length=1)
    
    class Config:
        from_attributes = True

# ============= Схемы для ответа =============

class ReviewResponse(ReviewBase):
    """Схема для ответа с данными отзыва"""
    id: str
    user_id: str
    
    # Moderation
    is_approved: bool
    is_verified_purchase: bool
    
    # Helpfulness
    helpful_count: int
    not_helpful_count: int
    
    # Calculated
    helpful_score: float
    
    # Timestamps
    created_at: datetime
    updated_at: datetime
    
    # User info
    user_name: Optional[str] = None
    user_avatar: Optional[str] = None
    
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

# ============= Схемы для списков =============

class ReviewListResponse(BaseModel):
    """Схема для списка отзывов с пагинацией"""
    items: List[ReviewResponse]
    total: int
    page: int
    size: int
    pages: int
    average_rating: float = 0.0
    total_ratings: int = 0
    
    class Config:
        from_attributes = True

# ============= Схемы для модерации =============

class ReviewModerationUpdate(BaseModel):
    """Схема для обновления статуса модерации"""
    is_approved: bool
    
    class Config:
        from_attributes = True

# ============= Схемы для полезности отзыва =============

class ReviewHelpfulCreate(BaseModel):
    """Схема для отметки полезности отзыва"""
    is_helpful: bool
    
    class Config:
        from_attributes = True

class ReviewHelpfulResponse(BaseModel):
    """Схема для ответа после отметки полезности"""
    helpful_count: int
    not_helpful_count: int
    message: str
    
    class Config:
        from_attributes = True

# ============= Схемы для статистики =============

class ReviewStats(BaseModel):
    """Схема для статистики отзывов"""
    total_reviews: int
    average_rating: float
    rating_distribution: dict = {
        "1": 0, "2": 0, "3": 0, "4": 0, "5": 0
    }
    approved_reviews: int
    pending_reviews: int
    verified_purchases: int
    
    class Config:
        from_attributes = True