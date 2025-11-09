# models/category.py
from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Category(Base):
    """
    ORM-модель категории товаров
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    
    # Обратная связь с продуктами - один ко многим
    products: Mapped[list["Product"]] = relationship(back_populates="category")

    def __repr__(self):
        """
        Строковое представление объекта Category.
        """
        return f"<Category id={self.id} name={self.name}>"