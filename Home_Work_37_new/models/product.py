# models/product.py
from sqlalchemy import Column, Integer, String, Text, Float, ForeignKey
from sqlalchemy.orm import relationship
from .base import Base

class ProductModel(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False, index=True)
    description = Column(Text)
    price = Column(Float, nullable=False)
    stock = Column(Integer, default=0)
    
    # Внешний ключ для категории
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    
    # Связь с категорией
    category = relationship("CategoryModel", back_populates="products")