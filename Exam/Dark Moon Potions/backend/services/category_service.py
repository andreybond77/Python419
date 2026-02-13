from typing import Optional, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid
from uuid import UUID

from models.potion import PotionCategory, Potion
from schemas.category import (
    PotionCategoryCreate, 
    PotionCategoryUpdate,  # ✅ Добавлен недостающий импорт
    PotionCategoryResponse
)
from .base_service import BaseService


class CategoryService(BaseService[
    PotionCategory, 
    PotionCategoryCreate, 
    PotionCategoryUpdate,  # ✅ Исправлено: второй параметр должен быть PotionCategoryUpdate
    PotionCategoryResponse
]):
    def __init__(self):
        super().__init__(PotionCategory, PotionCategoryResponse)
    
    def _convert_id(self, id_value: any) -> Optional[UUID]:
        """Конвертирует строку или UUID в UUID для запросов к БД"""
        if id_value is None:
            return None
        if isinstance(id_value, UUID):
            return id_value
        try:
            return UUID(str(id_value))
        except (ValueError, AttributeError):
            return None
    
    async def get_by_slug(self, session: AsyncSession, slug: str) -> Optional[PotionCategoryResponse]:
        """Get category by slug."""
        query = (
            select(PotionCategory)
            .where(PotionCategory.slug == slug)
            .options(selectinload(PotionCategory.potions))
        )
        result = await session.execute(query)
        category = result.scalar_one_or_none()
        
        if category:
            return self._model_to_schema(category)
        return None
    
    async def get_all_with_counts(
        self, 
        session: AsyncSession
    ) -> List[PotionCategoryResponse]:
        """Get all categories with potion counts."""
        # Get categories with potion counts
        query = (
            select(
                PotionCategory,
                func.count(Potion.id).label('potion_count')
            )
            .outerjoin(Potion, Potion.category_id == PotionCategory.id)
            .group_by(PotionCategory.id)
            .order_by(PotionCategory.name)
        )
        result = await session.execute(query)
        
        categories = []
        for row in result.all():
            category, count = row
            
            # ✅ Исправлено: конвертируем UUID в строку
            category_dict = {
                'id': str(category.id),
                'name': category.name,
                'slug': category.slug,
                'description': category.description,
                'icon': category.icon,
                'color': category.color,
                'created_at': category.created_at,
                'updated_at': category.updated_at,
                'potion_count': count or 0
            }
            
            # ✅ Исправлено: безопасная валидация
            try:
                category_response = PotionCategoryResponse.model_validate(category_dict)
                categories.append(category_response)
            except Exception as e:
                # Fallback - создаем вручную
                from pydantic import ValidationError
                category_response = PotionCategoryResponse(
                    id=str(category.id),
                    name=category.name,
                    slug=category.slug,
                    description=category.description,
                    icon=category.icon,
                    color=category.color,
                    created_at=category.created_at,
                    updated_at=category.updated_at,
                    potion_count=count or 0
                )
                categories.append(category_response)
        
        return categories
    
    async def get(self, session: AsyncSession, id: str) -> Optional[PotionCategoryResponse]:
        """Get category by ID (override base method)."""
        # ✅ Конвертируем строку в UUID
        try:
            category_uuid = uuid.UUID(id) if isinstance(id, str) else id
        except ValueError:
            return None
        
        query = select(PotionCategory).where(PotionCategory.id == category_uuid)
        result = await session.execute(query)
        category = result.scalar_one_or_none()
        
        if category:
            return self._model_to_schema(category)
        return None
    
    async def create_category(
        self, 
        session: AsyncSession, 
        obj_in: PotionCategoryCreate
    ) -> PotionCategoryResponse:
        """Create new category."""
        # Проверяем уникальность slug
        existing = await self.get_by_slug(session, obj_in.slug)
        if existing:
            raise ValueError(f"Category with slug '{obj_in.slug}' already exists")
        
        # Создаем категорию
        category_dict = obj_in.model_dump()
        category = PotionCategory(**category_dict)
        
        session.add(category)
        await session.commit()
        await session.refresh(category)
        
        return self._model_to_schema(category)


category_service = CategoryService()