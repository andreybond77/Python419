# models/product.py
from sqlalchemy import String, Float, Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from models.base import Base


class Product(Base):
    """
    ORM-модель товара
    """
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), nullable=False)
    description: Mapped[str] = mapped_column(String(500), nullable=False)
    image_url: Mapped[str] = mapped_column(String(200), nullable=False)
    price_shmeckles: Mapped[float] = mapped_column(Float, nullable=False)
    price_flurbos: Mapped[float] = mapped_column(Float, nullable=False)
    price_credits: Mapped[float] = mapped_column(Float, nullable=False)
    
    # Внешний ключ, ссылающийся на таблицу категорий
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))
    # Связь с объектом категории
    category: Mapped["Category"] = relationship(back_populates="products")

    def __repr__(self):
        """
        Строковое представление объекта Product.
        """
        return f"<Product id={self.id} name={self.name}>"