# schemas/product_create.py
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):
    """
    Pydantic-схема для создания или обновления продукта (без ID).
    """
    name: str = Field(..., min_length=1, description="Название товара", example="Plumbus")
    description: str = Field(..., min_length=5, description="Детальное описание товара", example="Самый полезный прибор в галактике")
    image_url: str = Field(..., description="Путь к изображению товара", example="/static/plumbus.jpg")
    # Новые поля для цен (теперь это отдельные поля)
    price_shmeckles: float = Field(..., gt=0, description="Цена в шмекелях", example=10.0)
    price_flurbos: float = Field(..., gt=0, description="Цена в флурбо", example=7.5)
    price_credits: float = Field(..., gt=0, description="Цена в кредитах", example=12.3)
    # Новое поле для связи с категорией
    category_id: int = Field(..., description="ID категории", example=1)