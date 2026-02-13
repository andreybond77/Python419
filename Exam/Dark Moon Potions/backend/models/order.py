from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import enum

from core.database import Base


class OrderStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    REFUNDED = "refunded"


class Order(Base):
    __tablename__ = "orders"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Информация о заказе
    order_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        index=True,
        nullable=False
    )
    status: Mapped[str] = mapped_column(String(20), default=OrderStatus.PENDING.value, nullable=False)
    
    # Цены
    subtotal: Mapped[float] = mapped_column(Float, nullable=False)
    shipping_cost: Mapped[float] = mapped_column(Float, default=0.0)
    discount_amount: Mapped[float] = mapped_column(Float, default=0.0)
    tax_amount: Mapped[float] = mapped_column(Float, default=0.0)
    total_amount: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Доставка
    shipping_method: Mapped[str] = mapped_column(String(50))
    shipping_address: Mapped[str] = mapped_column(Text)
    shipping_city: Mapped[str] = mapped_column(String(100))
    shipping_zip: Mapped[str] = mapped_column(String(20))
    shipping_country: Mapped[str] = mapped_column(String(100))
    
    # Контактная информация
    customer_name: Mapped[str] = mapped_column(String(255))
    customer_email: Mapped[str] = mapped_column(String(255))
    customer_phone: Mapped[str] = mapped_column(String(20))
    
    # Заметки
    notes: Mapped[Optional[str]] = mapped_column(Text)
    internal_notes: Mapped[Optional[str]] = mapped_column(Text)
    
    # Отслеживание
    tracking_number: Mapped[Optional[str]] = mapped_column(String(100))
    carrier: Mapped[Optional[str]] = mapped_column(String(50))
    estimated_delivery: Mapped[Optional[datetime]] = mapped_column(DateTime)
    delivered_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Оплата
    payment_status: Mapped[str] = mapped_column(String(20), default="pending")
    payment_method: Mapped[str] = mapped_column(String(50))
    
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
        CheckConstraint('subtotal >= 0', name='check_subtotal_positive'),
        CheckConstraint('total_amount >= 0', name='check_total_positive'),
    )
    
    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="orders")
    items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="order",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    payments: Mapped[List["Payment"]] = relationship(
        "Payment",
        back_populates="order",
        cascade="all, delete-orphan"
    )
    
    def __repr__(self) -> str:
        return f"<Order(id={self.id}, order_number={self.order_number}, status={self.status})>"


class OrderItem(Base):
    __tablename__ = "order_items"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    potion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("potions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Детали элемента (снимок на момент покупки)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    unit_price: Mapped[float] = mapped_column(Float, nullable=False)
    total_price: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Денормализованные поля
    potion_name: Mapped[str] = mapped_column(String(255))
    potion_image: Mapped[str] = mapped_column(String(500))
    potion_category: Mapped[str] = mapped_column(String(50))
    potion_rarity: Mapped[str] = mapped_column(String(20))
    
    # Отношения
    order: Mapped["Order"] = relationship("Order", back_populates="items")
    potion: Mapped["Potion"] = relationship("Potion", back_populates="order_items")
    
    def __repr__(self) -> str:
        return f"<OrderItem(id={self.id}, potion={self.potion_name}, quantity={self.quantity})>"