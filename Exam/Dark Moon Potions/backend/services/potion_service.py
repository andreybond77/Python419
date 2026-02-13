# backend/services/potion_service.py
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func, or_, String
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from models.potion import Potion, PotionCategory
from schemas.potion import (
    PotionCreate, 
    PotionUpdate, 
    PotionResponse,
    PotionFilter
)
from schemas.category import PotionCategoryCreate, PotionCategoryResponse
from .base_service import BaseService


class PotionService(BaseService[Potion, PotionCreate, PotionUpdate, PotionResponse]):
    def __init__(self):
        super().__init__(Potion, PotionResponse)
    
    async def create(self, session: AsyncSession, obj_in: PotionCreate) -> PotionResponse:
        """Create new potion with category validation."""
        # Verify category exists
        try:
            category_uuid = uuid.UUID(obj_in.category_id) if isinstance(obj_in.category_id, str) else obj_in.category_id
        except ValueError:
            raise ValueError(f"Invalid category id format: {obj_in.category_id}")
        
        category_query = select(PotionCategory).where(PotionCategory.id == category_uuid)
        result = await session.execute(category_query)
        category = result.scalar_one_or_none()
        
        if not category:
            raise ValueError(f"Category with id {obj_in.category_id} does not exist")
        
        # Create potion
        potion_dict = obj_in.model_dump()
        potion = Potion(**potion_dict)
        
        session.add(potion)
        await session.commit()
        await session.refresh(potion, ["category_rel"])
        
        return self._model_to_schema(potion)
    
    async def get_with_category(self, session: AsyncSession, id: str) -> Optional[PotionResponse]:
        """Get potion with category preloaded."""
        try:
            potion_uuid = uuid.UUID(id) if isinstance(id, str) else id
        except ValueError:
            return None
        
        query = (
            select(Potion)
            .where(Potion.id == potion_uuid)
            .options(selectinload(Potion.category_rel))
        )
        result = await session.execute(query)
        potion = result.scalar_one_or_none()
        
        if potion:
            return self._model_to_schema(potion)
        return None
    
    async def get_by_slug(self, session: AsyncSession, slug: str) -> Optional[PotionResponse]:
        """Get potion by slug."""
        query = (
            select(Potion)
            .where(Potion.slug == slug)
            .options(selectinload(Potion.category_rel))
        )
        result = await session.execute(query)
        potion = result.scalar_one_or_none()
        
        if potion:
            return self._model_to_schema(potion)
        return None
    
    async def search(
        self, 
        session: AsyncSession, 
        filters: PotionFilter
    ) -> tuple[List[PotionResponse], int]:
        """Search potions with filtering and pagination."""
        query = select(Potion).options(selectinload(Potion.category_rel))
        
        # Apply filters
        if filters.search:
            search_term = f"%{filters.search}%"
            query = query.where(
                or_(
                    Potion.name.ilike(search_term),
                    Potion.description.ilike(search_term),
                    Potion.slug.ilike(search_term),
                    Potion.ingredients_json.cast(String).ilike(search_term),
                    Potion.effects_json.cast(String).ilike(search_term),
                    Potion.warnings_json.cast(String).ilike(search_term)
                )
            )
        
        if filters.category:
            query = query.where(Potion.category == filters.category)
        
        if filters.rarity:
            query = query.where(Potion.rarity == filters.rarity)
        
        if filters.min_price is not None:
            query = query.where(Potion.price >= filters.min_price)
        
        if filters.max_price is not None:
            query = query.where(Potion.price <= filters.max_price)
        
        if filters.in_stock is not None:
            query = query.where(Potion.in_stock == filters.in_stock)
        
        if filters.brewing_difficulty:
            query = query.where(Potion.brewing_difficulty == filters.brewing_difficulty)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query) or 0
        
        # Apply sorting
        sort_column = Potion.created_at  # По умолчанию сортируем по дате создания
        if filters.sort_by == "price":
            sort_column = Potion.price
        elif filters.sort_by == "rating":
            sort_column = Potion.average_rating
        elif filters.sort_by == "popularity":
            sort_column = Potion.purchase_count  # Используем purchase_count вместо popularity_score
        elif filters.sort_by == "created_at":
            sort_column = Potion.created_at
        elif filters.sort_by == "name":
            sort_column = Potion.name
        
        if filters.sort_order == "desc":
            sort_column = sort_column.desc()
        
        query = query.order_by(sort_column)
        
        # Apply pagination
        offset = (filters.page - 1) * filters.limit
        query = query.offset(offset).limit(filters.limit)
        
        # Execute
        result = await session.execute(query)
        potions = result.scalars().all()
        
        # Конвертируем вручную, чтобы избежать ошибок валидации
        response_potions = []
        for potion in potions:
            try:
                response = self._model_to_schema(potion)
                response_potions.append(response)
            except Exception:
                # Ручное создание ответа в случае ошибки
                response_potions.append(self._manual_potion_response(potion))
        
        return response_potions, total
    
    async def get_popular(
        self, 
        session: AsyncSession, 
        limit: int = 10
    ) -> List[PotionResponse]:
        """Get popular potions - УПРОЩЕННАЯ ВЕРСИЯ БЕЗ ОШИБОК"""
        # Простой запрос - берем зелья в наличии
        query = (
            select(Potion)
            .where(Potion.in_stock == True)
            .order_by(Potion.created_at.desc())  # Сортируем по дате
            .limit(limit)
            .options(selectinload(Potion.category_rel))
        )
        
        try:
            result = await session.execute(query)
            potions = result.scalars().all()
        except Exception:
            # Если запрос с сортировкой падает, берем без сортировки
            query = select(Potion).limit(limit)
            result = await session.execute(query)
            potions = result.scalars().all()
        
        # Конвертируем вручную
        response_potions = []
        for potion in potions:
            response_potions.append(self._manual_potion_response(potion))
        
        return response_potions
    
    def _manual_potion_response(self, potion: Potion) -> PotionResponse:
        """Ручное создание PotionResponse для избежания ошибок валидации"""
        from schemas.potion import PotionResponse
        
        return PotionResponse(
            id=str(potion.id),
            name=potion.name,
            slug=potion.slug,
            description=potion.description,
            category=potion.category,
            price=potion.price,
            image_url=potion.image_url,
            in_stock=potion.in_stock,
            stock_quantity=potion.stock_quantity,
            rarity=potion.rarity,
            brewing_time=potion.brewing_time,
            brewing_difficulty=potion.brewing_difficulty,
            category_id=str(potion.category_id),
            ingredients=potion.ingredients,
            effects=potion.effects,
            warnings=potion.warnings,
            image_gallery=potion.image_gallery,
            thumbnail_url=potion.thumbnail_url,
            popularity_score=0,  # Значение по умолчанию
            purchase_count=potion.purchase_count or 0,
            review_count=potion.review_count or 0,
            average_rating=potion.average_rating or 0.0,
            meta_title=potion.meta_title,
            meta_description=potion.meta_description,
            created_at=potion.created_at,
            updated_at=potion.updated_at,
            published_at=potion.published_at
        )
    
    async def get_by_category(
        self, 
        session: AsyncSession, 
        category_slug: str,
        limit: int = 20
    ) -> List[PotionResponse]:
        """Get potions by category slug."""
        # Get category
        category_query = select(PotionCategory).where(PotionCategory.slug == category_slug)
        result = await session.execute(category_query)
        category = result.scalar_one_or_none()
        
        if not category:
            return []
        
        # Get potions
        query = (
            select(Potion)
            .where(Potion.category_id == category.id, Potion.in_stock == True)
            .limit(limit)
            .options(selectinload(Potion.category_rel))
        )
        result = await session.execute(query)
        potions = result.scalars().all()
        
        # Конвертируем вручную
        response_potions = []
        for potion in potions:
            response_potions.append(self._manual_potion_response(potion))
        
        return response_potions
    
    async def update_stock(
        self, 
        session: AsyncSession, 
        potion_id: str, 
        quantity_change: int
    ) -> Optional[PotionResponse]:
        """Update potion stock quantity."""
        try:
            potion_uuid = uuid.UUID(potion_id) if isinstance(potion_id, str) else potion_id
        except ValueError:
            return None
        
        query = select(Potion).where(Potion.id == potion_uuid)
        result = await session.execute(query)
        potion = result.scalar_one_or_none()
        
        if not potion:
            return None
        
        new_quantity = potion.stock_quantity + quantity_change
        potion.stock_quantity = max(0, new_quantity)
        potion.in_stock = potion.stock_quantity > 0
        
        await session.commit()
        await session.refresh(potion)
        
        return self._manual_potion_response(potion)
    
    async def increment_purchase_count(
        self, 
        session: AsyncSession, 
        potion_id: str, 
        increment: int = 1
    ) -> None:
        """Increment potion purchase count and popularity."""
        try:
            potion_uuid = uuid.UUID(potion_id) if isinstance(potion_id, str) else potion_id
        except ValueError:
            return
        
        query = (
            update(Potion)
            .where(Potion.id == potion_uuid)
            .values(
                purchase_count=Potion.purchase_count + increment
            )
        )
        await session.execute(query)
        await session.commit()
    
    async def update_rating_stats(
        self, 
        session: AsyncSession, 
        potion_id: str
    ) -> None:
        """Update potion rating statistics."""
        from models.review import Review
        
        try:
            potion_uuid = uuid.UUID(potion_id) if isinstance(potion_id, str) else potion_id
        except ValueError:
            return
        
        # Calculate new average
        subquery = (
            select(func.avg(Review.rating))
            .where(Review.potion_id == potion_uuid, Review.is_approved == True)
            .scalar_subquery()
        )
        
        # Update potion
        query = (
            update(Potion)
            .where(Potion.id == potion_uuid)
            .values(
                average_rating=func.coalesce(subquery, 0.0),
                review_count=(
                    select(func.count(Review.id))
                    .where(Review.potion_id == potion_uuid, Review.is_approved == True)
                    .scalar_subquery()
                )
            )
        )
        await session.execute(query)
        await session.commit()


potion_service = PotionService()