from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user, get_optional_user
from schemas.potion import (
    PotionCreate, 
    PotionUpdate, 
    PotionResponse,
    PotionFilter
)
from services.potion_service import potion_service
from services.category_service import category_service

router = APIRouter(prefix="/potions", tags=["potions"])


@router.get("/", response_model=Dict[str, Any])
async def get_potions(
    search: str = Query(None, description="Search by name, description, ingredients, or effects"),
    category: str = Query(None, description="Filter by category"),
    rarity: str = Query(None, description="Filter by rarity"),
    min_price: float = Query(None, ge=0, description="Minimum price"),
    max_price: float = Query(None, ge=0, description="Maximum price"),
    in_stock: bool = Query(None, description="Filter by stock availability"),
    brewing_difficulty: str = Query(None, description="Filter by brewing difficulty"),
    sort_by: str = Query("popularity", description="Sort field"),
    sort_order: str = Query("desc", description="Sort order (asc/desc)"),
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get potions with filtering, sorting, and pagination.
    
    Available filters:
    - **search**: Search in name, description, ingredients, effects
    - **category**: Filter by category (physical, mental, healing, etc.)
    - **rarity**: Filter by rarity (common, rare, epic, legendary)
    - **min_price/max_price**: Price range
    - **in_stock**: Only show in-stock items
    - **brewing_difficulty**: Filter by difficulty (easy, medium, hard, expert)
    
    Sort options:
    - **popularity** (default)
    - **price**
    - **created_at**
    - **name**
    - **purchase_count**
    - **average_rating**
    """
    filters = PotionFilter(
        search=search,
        category=category,
        rarity=rarity,
        min_price=min_price,
        max_price=max_price,
        in_stock=in_stock,
        brewing_difficulty=brewing_difficulty,
        sort_by=sort_by,
        sort_order=sort_order,
        page=page,
        limit=limit
    )
    
    potions, total = await potion_service.search(db, filters)
    
    return {
        "potions": potions,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit  # ceil division
    }


@router.get("/popular", response_model=List[PotionResponse])
async def get_popular_potions(
    limit: int = Query(10, ge=1, le=50, description="Number of potions"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get popular potions (based on popularity score).
    """
    potions = await potion_service.get_popular(db, limit)
    return potions


@router.get("/{potion_id}", response_model=PotionResponse)
async def get_potion_by_id(
    potion_id: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get potion by ID.
    """
    potion = await potion_service.get_with_category(db, potion_id)
    if not potion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Potion not found"
        )
    return potion


@router.get("/slug/{slug}", response_model=PotionResponse)
async def get_potion_by_slug(
    slug: str,
    db: AsyncSession = Depends(get_db)
):
    """
    Get potion by slug (URL-friendly name).
    """
    potion = await potion_service.get_by_slug(db, slug)
    if not potion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Potion not found"
        )
    return potion


@router.post("/", response_model=PotionResponse, status_code=status.HTTP_201_CREATED)
async def create_potion(
    potion_data: PotionCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new potion (staff only).
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    try:
        potion = await potion_service.create(db, potion_data)
        return potion
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{potion_id}", response_model=PotionResponse)
async def update_potion(
    potion_id: str,
    potion_data: PotionUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update potion (staff only).
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    potion = await potion_service.update(db, potion_id, potion_data)
    if not potion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Potion not found"
        )
    
    return potion


@router.delete("/{potion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_potion(
    potion_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete potion (admin only).
    """
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin privileges required"
        )
    
    success = await potion_service.delete(db, potion_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Potion not found"
        )


@router.get("/category/{category_slug}", response_model=List[PotionResponse])
async def get_potions_by_category(
    category_slug: str,
    limit: int = Query(20, ge=1, le=100, description="Number of potions"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get potions by category slug.
    """
    potions = await potion_service.get_by_category(db, category_slug, limit)
    return potions