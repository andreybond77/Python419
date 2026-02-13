from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user
from schemas.category import PotionCategoryCreate, PotionCategoryResponse
from services.category_service import category_service

router = APIRouter(prefix="/categories", tags=["categories"])


@router.get("/", response_model=List[PotionCategoryResponse])
async def get_all_categories(
    db: AsyncSession = Depends(get_db)
):
    """
    Get all potion categories.
    """
    categories = await category_service.get_all_with_counts(db)
    return categories


@router.get("/{category_id}", response_model=PotionCategoryResponse)
async def get_category_by_id(
    category_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get category by ID.
    """
    category = await category_service.get(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.get("/slug/{slug}", response_model=PotionCategoryResponse)
async def get_category_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get category by slug.
    """
    category = await category_service.get_by_slug(db, slug)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.post("/", response_model=PotionCategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: PotionCategoryCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new category (staff only).
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    try:
        category = await category_service.create_category(db, category_data)
        return category
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{category_id}", response_model=PotionCategoryResponse)
async def update_category(
    category_id: str,
    category_data: PotionCategoryCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update category (staff only).
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    category = await category_service.update(db, category_id, category_data)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete category (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    success = await category_service.delete(db, category_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )