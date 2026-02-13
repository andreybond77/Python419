from datetime import datetime
from typing import Optional
from sqlalchemy import String, Float, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import enum

from core.database import Base


class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Payment(Base):
    __tablename__ = "payments"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    order_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Информация об оплате
    payment_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    status: Mapped[str] = mapped_column(String(20), default=PaymentStatus.PENDING.value, nullable=False)
    
    # Сумма
    amount: Mapped[float] = mapped_column(Float, nullable=False)
    currency: Mapped[str] = mapped_column(String(3), default="USD")
    
    # Метод оплаты
    payment_method: Mapped[str] = mapped_column(String(50))
    payment_gateway: Mapped[str] = mapped_column(String(50))
    
    # Детали транзакции
    transaction_id: Mapped[Optional[str]] = mapped_column(String(100))
    gateway_response: Mapped[Optional[str]] = mapped_column(Text)  # JSON как текст
    
    # Детали карты (замаскированные)
    card_last4: Mapped[Optional[str]] = mapped_column(String(4))
    card_brand: Mapped[Optional[str]] = mapped_column(String(20))
    
    # Платежный адрес
    billing_address: Mapped[Optional[str]] = mapped_column(Text)
    billing_city: Mapped[Optional[str]] = mapped_column(String(100))
    billing_country: Mapped[Optional[str]] = mapped_column(String(100))
    
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
    completed_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="payments")
    order: Mapped["Order"] = relationship("Order", back_populates="payments")
    
    def __repr__(self) -> str:
        return f"<Payment(id={self.id}, payment_id={self.payment_id}, status={self.status})>"