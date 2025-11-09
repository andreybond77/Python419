# routes/products.py
from fastapi import APIRouter, HTTPException, Path, Query, BackgroundTasks
from typing import List, Optional
# Импорты схем
from schemas.product import Product
from schemas.product_create import ProductCreate
# Импорты SQLAlchemy
from sqlalchemy import select, or_, asc, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from core.database import AsyncSessionLocal
from models.product import Product as ProductModel  # Импортируем ORM-модель как ProductModel
from models.category import Category as CategoryModel  # Импортируем ORM-модель категории
# Импорт функции для отправки уведомлений
from utils.telegram import send_telegram_message

# Создаем экземпляр APIRouter с префиксом и тегами
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)

# --- READ (List) ---
@router.get(
    path="/",
    response_model=List[Product],
    status_code=200,
    summary="Получить все продукты",
)
async def get_products(
    search: Optional[str] = Query(None, description="Поиск по названию или описанию"),
    currency: Optional[str] = Query(None, description="Валюта для сортировки (shmeckles, credits, flurbos)"),
    sort_order: Optional[str] = Query(None, description="Направление сортировки (asc, desc)")
):
    """
    Возвращает список всех продуктов из базы данных.
    Поддерживает фильтрацию по тексту и сортировку по цене.
    """
    async with AsyncSessionLocal() as session:
        # Начинаем с базового запроса на выборку всех продуктов с загрузкой категории
        query = select(ProductModel).options(selectinload(ProductModel.category))

        # Фильтрация поиска
        if search:
            query = query.where(
                or_(
                    ProductModel.name.ilike(f"%{search}%"),
                    ProductModel.description.ilike(f"%{search}%")
                )
            )

        # Сортировка
        if currency and sort_order:
            # Проверяем, что валюта существует в модели (проверка на уровне БД)
            # SQLAlchemy сам проверит, существует ли поле, если использовать getattr
            try:
                price_column = getattr(ProductModel, f"price_{currency}")
                if sort_order.lower() == "desc":
                    query = query.order_by(price_column.desc())
                else:
                    query = query.order_by(price_column.asc())
            except AttributeError:
                # Если валюта не найдена в модели (например, price_undefined)
                raise HTTPException(status_code=400, detail=f"Неподдерживаемая валюта для сортировки: {currency}")

        # Выполняем запрос
        result = await session.execute(query)
        products = result.scalars().all()

        # Преобразуем ORM-объекты в Pydantic-модели для возврата
        return [Product.model_validate(p) for p in products]


# --- READ (One) ---
@router.get(
    path="/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Получить продукт по ID",
)
async def get_product(
    product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Возвращает один продукт по его ID из базы данных.
    """
    async with AsyncSessionLocal() as session:
        # Получаем продукт по ID с загрузкой категории
        product = await session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.category))
            .where(ProductModel.id == product_id)
        )
        product = product.scalar_one_or_none()
        if product is None:
            raise HTTPException(status_code=404, detail="Продукт не найден")
        # Преобразуем ORM-объект в Pydantic-модель для возврата
        return Product.model_validate(product)


# --- CREATE ---
@router.post(
    path="/",
    response_model=Product,
    status_code=201,
    summary="Создать новый продукт",
)
async def create_product(
    product_data: ProductCreate,
    background_tasks: BackgroundTasks
):
    """
    Создаёт новый продукт и добавляет его в базу данных.
    Также добавляет фоновую задачу для отправки уведомления в Telegram.
    """
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли категория с переданным category_id
        category = await session.get(CategoryModel, product_data.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        
        # Создаем ORM-объект из Pydantic-схемы
        new_product = ProductModel(**product_data.model_dump())
        session.add(new_product)
        await session.commit()  # Сохраняем изменения
        await session.refresh(new_product)  # Обновляем объект, чтобы получить ID от БД

        # Формируем сообщение для Telegram
        message = f"""🆕 *Создан новый продукт*

📦 *Название:* {new_product.name}
🆔 *ID:* {new_product.id}
📝 *Описание:* {new_product.description[:150]}...
🏷️ *Категория:* {new_product.category.name}

💰 *Цены:*
  • Шмекели: {new_product.price_shmeckles}
  • Флурбо: {new_product.price_flurbos}
  • Кредиты: {new_product.price_credits}
"""
        # Добавляем фоновую задачу для отправки уведомления
        background_tasks.add_task(send_telegram_message, message)

        # Преобразуем ORM-объект в Pydantic-модель для возврата
        # Загружаем категорию для полного ответа
        full_product = await session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.category))
            .where(ProductModel.id == new_product.id)
        )
        full_product = full_product.scalar_one()
        return Product.model_validate(full_product)


# --- UPDATE ---
@router.put(
    path="/{product_id}",
    response_model=Product,
    status_code=200,
    summary="Обновить продукт",
)
async def update_product(
    background_tasks: BackgroundTasks,
    product_id: int = Path(..., ge=1, description="ID продукта"),
    product_data: ProductCreate = None
):
    """
    Обновляет существующий продукт по ID в базе данных.
    Также добавляет фоновую задачу для отправки уведомления в Telegram.
    """
    async with AsyncSessionLocal() as session:
        # Получаем продукт по ID
        product = await session.get(ProductModel, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Продукт не найден")

        # Проверяем, существует ли категория с переданным category_id
        category = await session.get(CategoryModel, product_data.category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")

        # Обновляем поля продукта данными из схемы
        for field, value in product_data.model_dump().items():
            setattr(product, field, value)

        await session.commit()  # Сохраняем изменения
        await session.refresh(product)  # Обновляем объект

        # Формируем сообщение для Telegram
        message = f"""🔄 *Обновлён продукт*

📦 *Название:* {product.name}
🆔 *ID:* {product.id}
📝 *Описание:* {product.description[:150]}...
🏷️ *Категория:* {product.category.name}

💰 *Цены:*
  • Шмекели: {product.price_shmeckles}
  • Флурбо: {product.price_flurbos}
  • Кредиты: {product.price_credits}
"""
        # Добавляем фоновую задачу для отправки уведомления
        background_tasks.add_task(send_telegram_message, message)

        # Загружаем продукт с категорией для полного ответа
        full_product = await session.execute(
            select(ProductModel)
            .options(selectinload(ProductModel.category))
            .where(ProductModel.id == product.id)
        )
        full_product = full_product.scalar_one()
        # Преобразуем ORM-объект в Pydantic-модель для возврата
        return Product.model_validate(full_product)


# --- DELETE ---
@router.delete(
    path="/{product_id}",
    status_code=204,
    summary="Удалить продукт",
)
async def delete_product(
    product_id: int = Path(..., ge=1, description="ID продукта")
):
    """
    Удаляет продукт по ID из базы данных.
    """
    async with AsyncSessionLocal() as session:
        # Получаем продукт по ID
        product = await session.get(ProductModel, product_id)
        if product is None:
            raise HTTPException(status_code=404, detail="Продукт не найден")

        await session.delete(product)  # Удаляем объект
        await session.commit()  # Сохраняем изменения

        # Возвращаем 204 No Content
        return  # FastAPI автоматически установит статус 204, если функция возвращает None