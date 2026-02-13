from datetime import datetime
from typing import Optional
from sqlalchemy import String, Integer, Float, DateTime, Text, ForeignKey, CheckConstraint, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from core.database import Base


class Review(Base):
    __tablename__ = "reviews"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False
    )
    potion_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("potions.id", ondelete="CASCADE"),
        nullable=False
    )
    
    # Содержание отзыва
    rating: Mapped[int] = mapped_column(Integer, nullable=False)
    title: Mapped[Optional[str]] = mapped_column(String(255))
    comment: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Модерация
    is_approved: Mapped[bool] = mapped_column(Boolean, default=False)
    is_verified_purchase: Mapped[bool] = mapped_column(Boolean, default=True)
    
    # Полезность
    helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    not_helpful_count: Mapped[int] = mapped_column(Integer, default=0)
    
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
        CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
    )
    
    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="reviews")
    potion: Mapped["Potion"] = relationship("Potion", back_populates="reviews")
    
    # Вычисляемые свойства
    @property
    def helpful_score(self) -> float:
        total = self.helpful_count + self.not_helpful_count
        if total == 0:
            return 0.0
        return self.helpful_count / total * 100
    
    def __repr__(self) -> str:
        return f"<Review(id={self.id}, rating={self.rating}, potion_id={self.potion_id})>"