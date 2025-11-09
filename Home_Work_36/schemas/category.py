# schemas/category.py
from pydantic import BaseModel
from pydantic.config import ConfigDict


class CategoryCreate(BaseModel):
    """
    Pydantic-схема для создания категории
    """
    name: str


class CategoryRead(BaseModel):
    """
    Pydantic-схема для представления категории
    """
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)