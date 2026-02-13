from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, Boolean, DateTime, Text, Integer, Float, ForeignKey, CheckConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
import uuid
import json

from core.database import Base


class PotionCategory(Base):
    __tablename__ = "potion_categories"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )
    slug: Mapped[str] = mapped_column(
        String(50), 
        unique=True, 
        nullable=False, 
        index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text)
    icon: Mapped[Optional[str]] = mapped_column(String(50))
    color: Mapped[Optional[str]] = mapped_column(String(20))
    
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
    
    # Отношения
    potions: Mapped[List["Potion"]] = relationship(
        "Potion",
        back_populates="category_rel",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    def __repr__(self) -> str:
        return f"<PotionCategory(id={self.id}, name={self.name})>"


class Potion(Base):
    __tablename__ = "potions"
    
    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True,
        default=uuid.uuid4
    )
    
    # Основная информация
    name: Mapped[str] = mapped_column(
        String(255), 
        nullable=False, 
        index=True
    )
    slug: Mapped[str] = mapped_column(
        String(255), 
        unique=True, 
        nullable=False, 
        index=True
    )
    description: Mapped[str] = mapped_column(Text, nullable=False)
    
    # Категория
    category_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("potion_categories.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    category: Mapped[str] = mapped_column(
        String(50), 
        nullable=False, 
        index=True
    )
    
    # Цены и скидки
    price: Mapped[float] = mapped_column(Float, nullable=False)
    original_price: Mapped[Optional[float]] = mapped_column(Float)
    discount_percent: Mapped[int] = mapped_column(Integer, default=0)
    
    # Склад
    in_stock: Mapped[bool] = mapped_column(Boolean, default=True, index=True)
    stock_quantity: Mapped[int] = mapped_column(Integer, default=0)
    min_stock_level: Mapped[int] = mapped_column(Integer, default=10)
    
    # Редкость
    rarity: Mapped[str] = mapped_column(
        String(20), 
        default="common", 
        nullable=False, 
        index=True
    )
    
    # Информация о варке
    brewing_time: Mapped[str] = mapped_column(String(100))
    brewing_difficulty: Mapped[str] = mapped_column(
        String(20), 
        default="medium"
    )
    
    # Списки (храним как JSON)
    ingredients_json: Mapped[str] = mapped_column(Text, default="[]")
    effects_json: Mapped[str] = mapped_column(Text, default="[]")
    warnings_json: Mapped[str] = mapped_column(Text, default="[]")
    image_gallery_json: Mapped[str] = mapped_column(Text, default="[]")
    
    # Изображения
    image_url: Mapped[Optional[str]] = mapped_column(String(500))
    thumbnail_url: Mapped[Optional[str]] = mapped_column(String(500))
    
    # Статистика
    popularity_score: Mapped[int] = mapped_column(Integer, default=0, index=True)
    purchase_count: Mapped[int] = mapped_column(Integer, default=0)
    review_count: Mapped[int] = mapped_column(Integer, default=0)
    average_rating: Mapped[float] = mapped_column(Float, default=0.0)
    
    # SEO
    meta_title: Mapped[Optional[str]] = mapped_column(String(255))
    meta_description: Mapped[Optional[str]] = mapped_column(Text)
    
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
    published_at: Mapped[Optional[datetime]] = mapped_column(DateTime)
    
    # Проверки
    __table_args__ = (
        CheckConstraint('price >= 0', name='check_price_positive'),
        CheckConstraint('stock_quantity >= 0', name='check_stock_positive'),
        CheckConstraint('discount_percent >= 0 AND discount_percent <= 100', 
                       name='check_discount_range'),
        CheckConstraint('NOT (discount_percent > 0 AND original_price IS NULL)', 
                       name='check_discount_requires_original'),
        CheckConstraint('original_price IS NULL OR original_price >= price', 
                       name='check_original_price_gte_price'),
    )
    
    # Свойства для JSON-полей
    @property
    def ingredients(self) -> List[str]:
        return json.loads(self.ingredients_json or "[]")
    
    @ingredients.setter
    def ingredients(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("Ingredients must be a list")
        self.ingredients_json = json.dumps(value or [])
    
    @property
    def effects(self) -> List[str]:
        return json.loads(self.effects_json or "[]")
    
    @effects.setter
    def effects(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("Effects must be a list")
        self.effects_json = json.dumps(value or [])
    
    @property
    def warnings(self) -> List[str]:
        return json.loads(self.warnings_json or "[]")
    
    @warnings.setter
    def warnings(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("Warnings must be a list")
        self.warnings_json = json.dumps(value or [])
    
    @property
    def image_gallery(self) -> List[str]:
        return json.loads(self.image_gallery_json or "[]")
    
    @image_gallery.setter
    def image_gallery(self, value: List[str]):
        if not isinstance(value, list):
            raise ValueError("Image gallery must be a list")
        self.image_gallery_json = json.dumps(value or [])
    
    # Отношения
    category_rel: Mapped["PotionCategory"] = relationship(
        "PotionCategory",
        back_populates="potions",
        lazy="selectin"
    )
    
    cart_items: Mapped[List["CartItem"]] = relationship(
        "CartItem",
        back_populates="potion",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    order_items: Mapped[List["OrderItem"]] = relationship(
        "OrderItem",
        back_populates="potion",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    reviews: Mapped[List["Review"]] = relationship(
        "Review",
        back_populates="potion",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    wishlist_items: Mapped[List["Wishlist"]] = relationship(
        "Wishlist",
        back_populates="potion",
        cascade="all, delete-orphan",
        lazy="selectin"
    )
    
    # Вычисляемые свойства
    @property
    def final_price(self) -> float:
        if self.discount_percent > 0:
            return self.price * (1 - self.discount_percent / 100)
        return self.price
    
    @property
    def is_discounted(self) -> bool:
        return self.discount_percent > 0
    
    @property
    def low_stock(self) -> bool:
        return self.stock_quantity <= self.min_stock_level
    
    def __repr__(self) -> str:
        return f"<Potion(id={self.id}, name={self.name}, price={self.price})>"