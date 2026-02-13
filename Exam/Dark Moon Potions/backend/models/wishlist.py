from datetime import datetime
from sqlalchemy import String, DateTime, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid

from core.database import Base


class Wishlist(Base):
    __tablename__ = "wishlist"
    
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
    
    # Опциональная заметка
    note: Mapped[str] = mapped_column(String, default="")
    
    # Временные метки
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False
    )
    
    # Отношения
    user: Mapped["User"] = relationship("User", back_populates="wishlist")
    potion: Mapped["Potion"] = relationship("Potion", back_populates="wishlist_items")
    
    # Уникальное ограничение
    __table_args__ = (
        UniqueConstraint('user_id', 'potion_id', name='unique_user_potion_wishlist'),
    )
    
    def __repr__(self) -> str:
        return f"<Wishlist(id={self.id}, user_id={self.user_id}, potion_id={self.potion_id})>"