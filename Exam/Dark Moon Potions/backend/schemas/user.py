# backend/schemas/user.py
from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional, List, Any
from uuid import UUID
from datetime import datetime

# ============= Базовые схемы =============

class UserBase(BaseModel):
    """Базовая схема пользователя"""
    email: EmailStr
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    is_active: bool = True
    is_verified: bool = False
    
    class Config:
        from_attributes = True

# ============= Схемы для аутентификации =============

class LoginRequest(BaseModel):
    """Схема для запроса на вход"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    
    class Config:
        from_attributes = True

# Алиас для обратной совместимости
UserLogin = LoginRequest

class Token(BaseModel):
    """Схема для токена доступа"""
    access_token: str
    token_type: str = "bearer"
    
    class Config:
        from_attributes = True

class TokenData(BaseModel):
    """Данные, хранящиеся в токене"""
    user_id: Optional[str] = None
    email: Optional[str] = None
    is_admin: bool = False
    
    class Config:
        from_attributes = True

# ============= Схемы для создания пользователя =============

class UserCreate(UserBase):
    """Схема для регистрации нового пользователя"""
    password: str = Field(..., min_length=6)
    wizard_level: str = "novice"
    address: Optional[str] = None
    bio: Optional[str] = None
    
    @validator('name', pre=True, always=True)
    def set_default_name(cls, v, values):
        """Устанавливает имя по умолчанию из email"""
        if not v and 'email' in values:
            return values['email'].split('@')[0]
        return v

class UserRegister(BaseModel):
    """Схема для регистрации (альтернативная)"""
    email: EmailStr
    password: str = Field(..., min_length=6)
    name: Optional[str] = None
    
    @validator('name', pre=True, always=True)
    def set_default_name(cls, v, values):
        if not v and 'email' in values:
            return values['email'].split('@')[0]
        return v

# ============= Схемы для обновления пользователя =============

class UserUpdate(BaseModel):
    """Схема для обновления данных пользователя"""
    name: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)
    wizard_level: Optional[str] = None
    address: Optional[str] = None
    bio: Optional[str] = None
    is_active: Optional[bool] = None
    is_verified: Optional[bool] = None
    
    class Config:
        from_attributes = True

class UserPasswordChange(BaseModel):
    """Схема для смены пароля"""
    current_password: str = Field(..., min_length=6)
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Пароли не совпадают')
        return v

# ============= Схемы для ответа =============

class UserResponse(UserBase):
    """Схема для ответа с данными пользователя"""
    id: str
    wizard_level: str = "novice"
    address: Optional[str] = None
    bio: Optional[str] = None
    preferences: Optional[dict] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
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

class UserProfileResponse(UserResponse):
    """Расширенная схема профиля пользователя"""
    order_count: int = 0
    total_spent: float = 0.0
    wishlist_count: int = 0
    review_count: int = 0
    
    class Config:
        from_attributes = True

# ============= Схемы для списков =============

class UserListResponse(BaseModel):
    """Схема для списка пользователей с пагинацией"""
    items: List[UserResponse]
    total: int
    page: int
    size: int
    pages: int

# ============= Схемы для восстановления пароля =============

class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля"""
    email: EmailStr

class PasswordResetConfirm(BaseModel):
    """Подтверждение сброса пароля"""
    token: str
    new_password: str = Field(..., min_length=6)
    confirm_password: str = Field(..., min_length=6)
    
    @validator('confirm_password')
    def passwords_match(cls, v, values, **kwargs):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Пароли не совпадают')
        return v

# ============= Схемы для верификации email =============

class EmailVerificationRequest(BaseModel):
    """Запрос на верификацию email"""
    token: str

class EmailVerificationResponse(BaseModel):
    """Ответ на верификацию email"""
    message: str
    verified: bool

# ============= Алиасы для обратной совместимости =============

UserLogin = LoginRequest