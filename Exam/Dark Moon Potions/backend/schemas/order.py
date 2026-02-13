# backend/schemas/order.py
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime
from enum import Enum  # ✅ ИМПОРТИРУЕМ ENUM

# ============= Статусы заказов =============

class OrderStatus(str, Enum):  # ✅ ИСПРАВЛЕНО: теперь наследник str и Enum
    """Статусы заказа"""
    PENDING = "pending"  # Ожидает обработки
    PROCESSING = "processing"  # В обработке
    SHIPPED = "shipped"  # Отправлен
    DELIVERED = "delivered"  # Доставлен
    CANCELLED = "cancelled"  # Отменен
    REFUNDED = "refunded"  # Возвращен

# ============= Базовые схемы =============

class OrderBase(BaseModel):
    """Базовая схема заказа"""
    delivery_address: str = Field(..., min_length=5)
    delivery_method: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=10)
    notes: Optional[str] = None
    status: OrderStatus = OrderStatus.PENDING  # ✅ ИСПРАВЛЕНО: используем Enum
    
    class Config:
        from_attributes = True
        use_enum_values = True  # ✅ ВАЖНО: возвращаем строки, а не объекты Enum

# ============= Схемы для позиций заказа =============

class OrderItemBase(BaseModel):
    """Базовая схема позиции заказа"""
    potion_id: str
    quantity: int = Field(..., gt=0)
    unit_price: float = Field(..., gt=0)
    potion_name: str
    potion_image: Optional[str] = None
    potion_category: Optional[str] = None
    potion_rarity: Optional[str] = None
    
    class Config:
        from_attributes = True

class OrderItemCreate(BaseModel):
    """Схема для создания позиции заказа"""
    potion_id: str
    quantity: int = Field(..., gt=0, le=99)
    
    @validator('potion_id', pre=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v)

class OrderItemUpdate(BaseModel):
    """Схема для обновления позиции заказа"""
    quantity: Optional[int] = Field(None, gt=0, le=99)
    
    class Config:
        from_attributes = True

class OrderItemResponse(OrderItemBase):
    """Схема для ответа с данными позиции заказа"""
    id: str
    order_id: str
    total_price: float
    
    @validator('id', 'order_id', 'potion_id', pre=True, always=True)
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

# ============= Схемы для создания заказа =============

class OrderCreate(BaseModel):
    """Схема для создания нового заказа"""
    delivery_address: str = Field(..., min_length=5)
    delivery_method: str = Field(..., min_length=2)
    phone: str = Field(..., min_length=10)
    notes: Optional[str] = None
    items: List[OrderItemCreate] = Field(..., min_items=1)
    
    @validator('delivery_method')
    def validate_delivery_method(cls, v):
        valid_methods = ['portal', 'owl', 'broom', 'pickup']
        if v not in valid_methods:
            raise ValueError(f'Способ доставки должен быть одним из: {valid_methods}')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        import re
        pattern = r'^[\d\s\-\+\(\)]{10,20}$'
        if not re.match(pattern, v):
            raise ValueError('Неверный формат телефона')
        return v

# ============= Схемы для обновления заказа =============

class OrderUpdate(BaseModel):
    """Схема для обновления заказа"""
    delivery_address: Optional[str] = Field(None, min_length=5)
    delivery_method: Optional[str] = Field(None, min_length=2)
    phone: Optional[str] = Field(None, min_length=10)
    notes: Optional[str] = None
    status: Optional[OrderStatus] = None  # ✅ ИСПРАВЛЕНО: используем Enum
    
    @validator('status')
    def validate_status(cls, v):
        if v is not None and v not in OrderStatus.__members__.values():
            raise ValueError(f'Статус должен быть одним из: {[s.value for s in OrderStatus]}')
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True

class OrderStatusUpdate(BaseModel):
    """Схема для обновления статуса заказа"""
    status: OrderStatus  # ✅ ИСПРАВЛЕНО: используем Enum
    
    @validator('status')
    def validate_status(cls, v):
        if v not in OrderStatus.__members__.values():
            raise ValueError(f'Статус должен быть одним из: {[s.value for s in OrderStatus]}')
        return v
    
    class Config:
        use_enum_values = True

# ============= Схемы для ответа =============

class OrderResponse(OrderBase):
    """Схема для ответа с данными заказа"""
    id: str
    user_id: str
    order_number: str
    total_amount: float
    items: List[OrderItemResponse] = []
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    @property
    def item_count(self) -> int:
        return sum(item.quantity for item in self.items)
    
    @validator('id', 'user_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        use_enum_values = True  # ✅ ВАЖНО: возвращаем строки
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

class OrderDetailResponse(OrderResponse):
    """Расширенная схема с детальной информацией о заказе"""
    user_email: Optional[str] = None
    user_name: Optional[str] = None
    
    class Config:
        from_attributes = True
        use_enum_values = True

# ============= Схемы для статистики =============

class OrderStats(BaseModel):
    """Схема для статистики заказов"""
    total_orders: int = 0
    total_revenue: float = 0.0
    pending_orders: int = 0
    processing_orders: int = 0
    shipped_orders: int = 0
    delivered_orders: int = 0
    cancelled_orders: int = 0
    refunded_orders: int = 0
    
    class Config:
        from_attributes = True

# ============= Схемы для фильтрации =============

class OrderFilter(BaseModel):
    """Схема для фильтрации заказов"""
    status: Optional[OrderStatus] = Field(None)  # ✅ ИСПРАВЛЕНО
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None
    min_amount: Optional[float] = Field(None, ge=0)
    max_amount: Optional[float] = Field(None, ge=0)
    user_id: Optional[str] = None
    order_number: Optional[str] = Field(None, min_length=1, max_length=50)
    delivery_method: Optional[str] = Field(None, pattern='^(portal|owl|broom|pickup)$')
    
    sort_by: Optional[str] = Field(None, pattern='^(created_at|total_amount|status|order_number)$')
    sort_order: Optional[str] = Field('desc', pattern='^(asc|desc)$')
    
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    
    @validator('date_to')
    def validate_date_range(cls, v, values):
        if v is not None and 'date_from' in values and values['date_from'] is not None:
            if values['date_from'] > v:
                raise ValueError('Дата начала не может быть позже даты окончания')
        return v
    
    @validator('max_amount')
    def validate_amount_range(cls, v, values):
        if v is not None and 'min_amount' in values and values['min_amount'] is not None:
            if values['min_amount'] > v:
                raise ValueError('Минимальная сумма не может быть больше максимальной')
        return v
    
    @validator('user_id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return v
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_schema_extra = {
            "example": {
                "status": "delivered",
                "date_from": "2026-01-01T00:00:00",
                "date_to": "2026-12-31T23:59:59",
                "min_amount": 1000,
                "max_amount": 5000,
                "delivery_method": "portal",
                "sort_by": "created_at",
                "sort_order": "desc",
                "page": 1,
                "page_size": 20
            }
        }

class OrderFilterResponse(BaseModel):
    """Схема для ответа с отфильтрованными заказами"""
    items: List[OrderResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
    filters_applied: dict
    summary: Optional[OrderStats] = None
    
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
                    "status": "delivered",
                    "date_from": "2026-01-01T00:00:00"
                }
            }
        }

# ============= Схемы для списков =============

class OrderListResponse(BaseModel):
    """Схема для списка заказов с пагинацией"""
    items: List[OrderResponse]
    total: int
    page: int
    size: int
    pages: int

class OrderSummary(BaseModel):
    """Краткая информация о заказе для списка"""
    id: str
    order_number: str
    created_at: datetime
    status: OrderStatus  # ✅ ИСПРАВЛЕНО
    total_amount: float
    item_count: int
    
    @validator('id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }

# ============= Схемы для отмены заказа =============

class OrderCancelRequest(BaseModel):
    """Запрос на отмену заказа"""
    reason: Optional[str] = Field(None, max_length=500)

class OrderCancelResponse(BaseModel):
    """Ответ на отмену заказа"""
    id: str
    status: OrderStatus = OrderStatus.CANCELLED  # ✅ ИСПРАВЛЕНО
    message: str = "Заказ успешно отменен"
    cancelled_at: datetime = Field(default_factory=datetime.utcnow)
    
    @validator('id', pre=True, always=True)
    def convert_uuid_to_str(cls, v):
        if isinstance(v, UUID):
            return str(v)
        return str(v) if v else None
    
    class Config:
        from_attributes = True
        use_enum_values = True
        json_encoders = {
            UUID: str,
            datetime: lambda v: v.isoformat() if v else None
        }