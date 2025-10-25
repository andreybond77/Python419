# schemas/product_create.py
from pydantic import BaseModel, Field
from typing import Dict

class ProductCreate(BaseModel):
    """
    Pydantic-схема для создания или обновления продукта (без ID).
    """
    name: str = Field(..., min_length=1, description="Название товара", example="Plumbus")
    description: str = Field(..., min_length=5, description="Детальное описание товара", example="Самый полезный прибор в галактике")
    prices: Dict[str, float] = Field(..., description="Цены в разных валютах", example={"USD": 100.0, "EUR": 90.0})
    image_url: str = Field(..., description="Путь к изображению товара", example="/static/plumbus.jpg")
