from __future__ import annotations
from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from core.database import Base


class Cart(Base):
    __tablename__ = "carts"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=True  # Важно: NULL для анонимных корзин!
    )
    
    # Расчетные поля
    total_items: Mapped[int] = mapped_column(Integer, default=0)
    total_price: Mapped[float] = mapped_column(Float, default=0.0)
    
    # Сессия для анонимных пользователей
    session_id: Mapped[Optional[str]] = mapped_column(String(100), unique=True)
    
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
    
    # Проверки
    __table_args__ = (
        CheckConstraint('total_items >= 0', name='check_cart_items_positive'),
        CheckConstraint('total_price >= 0', name='check_cart_price_positive'),
    )
    
    # Отношения
    user: Mapped[Optional["User"]] = relationship("User", back_populates="cart", lazy="selectin")
    items: Mapped[list["CartItem"]] = relationship(
        "CartItem",
        back_populates="cart",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<Cart(id={self.id}, user_id={self.user_id}, session_id={self.session_id}, total_items={self.total_items})>"


class CartItem(Base):
    __tablename__ = "cart_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    cart_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("carts.id", ondelete="CASCADE"),
        nullable=False
    )
    potion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("potions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Детали элемента
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    price_per_unit: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Денормализованные поля для производительности
    potion_name: Mapped[str] = mapped_column(String(255))
    potion_image: Mapped[str] = mapped_column(String(500))
    potion_category: Mapped[str] = mapped_column(String(50))
    
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
    
    # Проверки
    __table_args__ = (
        CheckConstraint('quantity > 0', name='check_quantity_positive'),
        CheckConstraint('price_per_unit >= 0', name='check_price_positive'),
    )
    
    # Отношения
    cart: Mapped["Cart"] = relationship("Cart", back_populates="items", lazy="selectin")
    potion: Mapped["Potion"] = relationship("Potion", back_populates="cart_items", lazy="selectin")
    
    # Вычисляемые свойства
    @property
    def total_price(self) -> float:
        return self.quantity * self.price_per_unit
    
    def __repr__(self) -> str:
        return f"<CartItem(id={self.id}, potion={self.potion_name}, quantity={self.quantity})>"