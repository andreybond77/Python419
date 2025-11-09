# routes/categories.py
from fastapi import APIRouter, HTTPException
from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.database import AsyncSessionLocal
from models.category import Category as CategoryModel
from schemas.category import CategoryCreate, CategoryRead

router = APIRouter(
    prefix="/categories",
    tags=["Категории"]
)


@router.post(
    path="/",
    response_model=CategoryRead,
    status_code=201,
    summary="Создать новую категорию",
)
async def create_category(category_data: CategoryCreate):
    """
    Создаёт новую категорию и добавляет её в базу данных.
    """
    async with AsyncSessionLocal() as session:
        # Проверяем, существует ли уже категория с таким названием
        existing_category = await session.execute(
            select(CategoryModel).where(CategoryModel.name == category_data.name)
        )
        if existing_category.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")
        
        # Создаем ORM-объект из Pydantic-схемы
        new_category = CategoryModel(**category_data.model_dump())
        session.add(new_category)
        await session.commit()  # Сохраняем изменения
        await session.refresh(new_category)  # Обновляем объект, чтобы получить ID от БД

        # Преобразуем ORM-объект в Pydantic-модель для возврата
        return CategoryRead.model_validate(new_category)


@router.get(
    path="/",
    response_model=List[CategoryRead],
    status_code=200,
    summary="Получить все категории",
)
async def get_categories():
    """
    Возвращает список всех категорий из базы данных.
    """
    async with AsyncSessionLocal() as session:
        # Получаем все категории
        result = await session.execute(select(CategoryModel))
        categories = result.scalars().all()

        # Преобразуем ORM-объекты в Pydantic-модели для возврата
        return [CategoryRead.model_validate(c) for c in categories]


@router.get(
    path="/{category_id}",
    response_model=CategoryRead,
    status_code=200,
    summary="Получить категорию по ID",
)
async def get_category(category_id: int):
    """
    Возвращает одну категорию по её ID из базы данных.
    """
    async with AsyncSessionLocal() as session:
        # Получаем категорию по ID
        category = await session.get(CategoryModel, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")
        # Преобразуем ORM-объект в Pydantic-модель для возврата
        return CategoryRead.model_validate(category)


@router.put(
    path="/{category_id}",
    response_model=CategoryRead,
    status_code=200,
    summary="Обновить категорию",
)
async def update_category(category_id: int, category_data: CategoryCreate):
    """
    Обновляет существующую категорию по ID в базе данных.
    """
    async with AsyncSessionLocal() as session:
        # Получаем категорию по ID
        category = await session.get(CategoryModel, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")

        # Проверяем, существует ли уже другая категория с таким названием
        existing_category = await session.execute(
            select(CategoryModel).where(
                CategoryModel.name == category_data.name,
                CategoryModel.id != category_id
            )
        )
        if existing_category.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Категория с таким названием уже существует")

        # Обновляем поля категории данными из схемы
        for field, value in category_data.model_dump().items():
            setattr(category, field, value)

        await session.commit()  # Сохраняем изменения
        await session.refresh(category)  # Обновляем объект

        # Преобразуем ORM-объект в Pydantic-модель для возврата
        return CategoryRead.model_validate(category)


@router.delete(
    path="/{category_id}",
    status_code=204,
    summary="Удалить категорию",
)
async def delete_category(category_id: int):
    """
    Удаляет категорию по ID из базы данных.
    """
    async with AsyncSessionLocal() as session:
        # Получаем категорию по ID
        category = await session.get(CategoryModel, category_id)
        if category is None:
            raise HTTPException(status_code=404, detail="Категория не найдена")

        await session.delete(category)  # Удаляем объект
        await session.commit()  # Сохраняем изменения

        # Возвращаем 204 No Content
        return  # FastAPI автоматически установит статус 204, если функция возвращает None