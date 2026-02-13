from typing import TypeVar, Generic, Type, Optional, List, Dict, Any
from sqlalchemy import select, update, delete, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from pydantic import BaseModel
import uuid

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)
ResponseSchemaType = TypeVar("ResponseSchemaType", bound=BaseModel)


class BaseService(Generic[ModelType, CreateSchemaType, UpdateSchemaType, ResponseSchemaType]):
    """Base service class with common CRUD operations."""
    
    def __init__(
        self, 
        model: Type[ModelType] = None,
        response_schema: Type[ResponseSchemaType] = None
    ):
        self.model = model
        self.response_schema = response_schema
    
    def _model_to_schema(self, obj: ModelType) -> ResponseSchemaType:
        """Convert SQLAlchemy model to Pydantic schema."""
        if self.response_schema:
            return self.response_schema.model_validate(obj, from_attributes=True)
        raise ValueError("Response schema not defined")
    
    async def get(self, session: AsyncSession, id: str) -> Optional[ResponseSchemaType]:
        """Get object by ID (string UUID)."""
        try:
            # Конвертируем строку в UUID для запроса к БД
            uuid_id = uuid.UUID(id) if isinstance(id, str) else id
            query = select(self.model).where(self.model.id == uuid_id)
            result = await session.execute(query)
            obj = result.scalar_one_or_none()
            
            if obj:
                return self._model_to_schema(obj)
            return None
        except ValueError:
            # Невалидный UUID
            return None
    
    async def get_multi(
        self, 
        session: AsyncSession, 
        skip: int = 0, 
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[ResponseSchemaType]:
        """Get multiple objects."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        objs = result.scalars().all()
        
        return [self._model_to_schema(obj) for obj in objs]
    
    async def create(
        self, 
        session: AsyncSession, 
        obj_in: CreateSchemaType
    ) -> ResponseSchemaType:
        """Create new object."""
        obj_dict = obj_in.model_dump()
        obj = self.model(**obj_dict)
        
        session.add(obj)
        await session.commit()
        await session.refresh(obj)
        
        return self._model_to_schema(obj)
    
    async def update(
        self, 
        session: AsyncSession, 
        id: str, 
        obj_in: UpdateSchemaType
    ) -> Optional[ResponseSchemaType]:
        """Update object."""
        try:
            uuid_id = uuid.UUID(id) if isinstance(id, str) else id
            
            # Get current object
            query = select(self.model).where(self.model.id == uuid_id)
            result = await session.execute(query)
            obj = result.scalar_one_or_none()
            
            if not obj:
                return None
            
            # Update fields
            update_data = obj_in.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(obj, field, value)
            
            await session.commit()
            await session.refresh(obj)
            
            return self._model_to_schema(obj)
        except ValueError:
            return None
    
    async def delete(self, session: AsyncSession, id: str) -> bool:
        """Delete object."""
        try:
            uuid_id = uuid.UUID(id) if isinstance(id, str) else id
            query = delete(self.model).where(self.model.id == uuid_id)
            result = await session.execute(query)
            await session.commit()
            
            return result.rowcount > 0
        except ValueError:
            return False
    
    async def exists(self, session: AsyncSession, id: str) -> bool:
        """Check if object exists."""
        try:
            uuid_id = uuid.UUID(id) if isinstance(id, str) else id
            query = select(self.model).where(self.model.id == uuid_id)
            result = await session.execute(query)
            obj = result.scalar_one_or_none()
            
            return obj is not None
        except ValueError:
            return False
    
    async def count(self, session: AsyncSession, filters: Optional[Dict[str, Any]] = None) -> int:
        """Count objects."""
        query = select(self.model)
        
        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    if isinstance(value, list):
                        query = query.where(getattr(self.model, key).in_(value))
                    else:
                        query = query.where(getattr(self.model, key) == value)
        
        result = await session.scalar(select(func.count()).select_from(query.subquery()))
        return result if result else 0