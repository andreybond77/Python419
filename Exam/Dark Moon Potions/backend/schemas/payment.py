# backend/schemas/payment.py
from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, validator
from uuid import UUID
from enum import Enum


class PaymentStatus(str, Enum):
    """Статусы платежа"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


# ============= Базовые схемы =============

class PaymentBase(BaseModel):
    """Базовая схема платежа"""
    order_id: str
    amount: float = Field(..., gt=0)
    currency: str = Field("USD", min_length=3, max_length=3)
    payment_method: str = Field(..., min_length=1)
    payment_gateway: str = Field(..., min_length=1)
    billing_address: Optional[str] = None
    billing_city: Optional[str] = None
    billing_country: Optional[str] = None
    
    @validator('order_id', pre=True)
    def convert_uuid_to_str(cls, v):
        """Конвертирует UUID в строку"""
        if isinstance(v, UUID):
            return str(v)
        return str(v)
    
    class Config:
        from_attributes = True


# ============= Схемы для создания =============

class PaymentCreate(PaymentBase):
    """Схема для создания платежа"""
    pass


# ============= Схемы для обновления =============

class PaymentUpdate(BaseModel):
    """Схема для обновления платежа"""
    status: Optional[PaymentStatus] = None
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    card_last4: Optional[str] = Field(None, min_length=4, max_length=4)
    card_brand: Optional[str] = None
    completed_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


# ============= Схемы для ответа =============

class PaymentResponse(PaymentBase):
    """Схема для ответа с данными платежа"""
    id: str
    user_id: str
    payment_id: str
    status: PaymentStatus
    transaction_id: Optional[str] = None
    gateway_response: Optional[Dict[str, Any]] = None
    card_last4: Optional[str] = None
    card_brand: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
    
    @validator('id', 'user_id', 'order_id', pre=True, always=True)
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

class PaymentListResponse(BaseModel):
    """Схема для списка платежей с пагинацией"""
    items: List[PaymentResponse]
    total: int
    page: int
    size: int
    pages: int
    
    class Config:
        from_attributes = True


# ============= Схемы для статистики =============

class PaymentStats(BaseModel):
    """Схема для статистики платежей"""
    total_payments: int = 0
    total_revenue: float = 0.0
    completed_payments: int = 0
    pending_payments: int = 0
    failed_payments: int = 0
    refunded_amount: float = 0.0
    
    class Config:
        from_attributes = True


# ============= Схемы для возврата =============

class PaymentRefundRequest(BaseModel):
    """Запрос на возврат платежа"""
    amount: Optional[float] = Field(None, gt=0)
    reason: Optional[str] = Field(None, max_length=500)
    
    class Config:
        from_attributes = True

class PaymentRefundResponse(BaseModel):
    """Ответ на возврат платежа"""
    id: str
    status: PaymentStatus = PaymentStatus.REFUNDED
    refund_amount: float
    message: str = "Платеж успешно возвращен"
    refunded_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('id', pre=True, always=True)
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