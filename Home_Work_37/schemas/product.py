# # schemas/product.py
# from pydantic import BaseModel, Field


# class Product(BaseModel):
#     """
#     Pydantic-схема для представления полного объекта продукта.
#     """
#     id: int
#     name: str = Field(..., description="Название товара", example="Plumbus")
#     description: str = Field(..., description="Детальное описание товара", example="Самый полезный прибор в галактике")
#     image_url: str = Field(..., description="Путь к изображению товара", example="/static/plumbus.jpg")
#     # Новые поля для цен
#     price_shmeckles: float = Field(..., description="Цена в шмекелях", example=10.0)
#     price_flurbos: float = Field(..., description="Цена в флурбо", example=7.5)
#     price_credits: float = Field(..., description="Цена в кредитах", example=12.3)



# schemas/product.py
from pydantic import BaseModel, Field
from pydantic.config import ConfigDict
from .category import CategoryRead


class Product(BaseModel):
    """
    Pydantic-схема для представления полного объекта продукта.
    """
    id: int
    name: str = Field(..., description="Название товара", example="Plumbus")
    description: str = Field(..., description="Детальное описание товара", example="Самый полезный прибор в галактике")
    image_url: str = Field(..., description="Путь к изображению товара", example="/static/plumbus.jpg")
    # Новые поля для цен
    price_shmeckles: float = Field(..., description="Цена в шмекелях", example=10.0)
    price_flurbos: float = Field(..., description="Цена в флурбо", example=7.5)
    price_credits: float = Field(..., description="Цена в кредитах", example=12.3)
    # Поле для связанной категории
    category: CategoryRead
    
    model_config = ConfigDict(from_attributes=True)