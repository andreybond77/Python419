# schemas/product.py
from pydantic import BaseModel, Field
from typing import Optional

class ProductCreate(BaseModel):
    name: str = Field(..., min_length=1, description="Название товара")
    description: str = Field(..., min_length=5, description="Описание товара")
    price: float = Field(..., gt=0, description="Цена товара")
    stock: int = Field(default=0, description="Количество на складе")
    category_id: int = Field(..., description="ID категории")

class ProductResponse(BaseModel):
    id: int
    name: str
    description: str
    price: float
    stock: int
    category_id: int

    class Config:
        from_attributes = True