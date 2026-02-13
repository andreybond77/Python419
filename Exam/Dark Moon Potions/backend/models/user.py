from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, DateTime, Text, Boolean, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import json

from core.database import Base


class User(Base):
    __tablename__ = "users"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False
    )
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False
    )
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    
    # Профиль
    full_name: Mapped[Optional[str]] = mapped_column(String(255))
    avatar_url: Mapped[Optional[str]] = mapped_column(String(500))
    bio: Mapped[Optional[str]] = mapped_column(Text)
    address: Mapped[Optional[str]] = mapped_column(Text)
    phone: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Уровень волшебника
    wizard_level: Mapped[str] = mapped_column(
        String(20),
        default="novice",
        nullable=False
    )
    
    # Статусы
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False)
    is_staff: Mapped[bool] = mapped_column(Boolean, default=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False)
    
    # Предпочтения (храним как JSON-строку)
    preferences_json: Mapped[Optional[str]] = mapped_column(
        Text,
        default='{"favoriteCategory": "physical", "newsletter": true, "promotions": false}'
    )
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False
    )
    last_login: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Проверки
    __table_args__ = (
        CheckConstraint(
            "wizard_level IN ('novice', 'apprentice', 'adept', 'master', 'grandmaster')",
            name='check_wizard_level'
        ),
    )
    
    # Свойства для работы с JSON
    @property
    def preferences(self) -> dict:
        return json.loads(self.preferences_json or '{}')
    
    @preferences.setter
    def preferences(self, value: dict):
        self.preferences_json = json.dumps(value or {})
    
    # Отношения
    cart: Mapped[Optional["Cart"]] = relationship(
        "Cart",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    wishlist: Mapped[List["Wishlist"]] = relationship(
        "Wishlist",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"