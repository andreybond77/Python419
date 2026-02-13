from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user, get_current_active_user
from schemas.wishlist import WishlistCreate, WishlistResponse
from services.wishlist_service import wishlist_service

router = APIRouter(prefix="/wishlist", tags=["wishlist"])


@router.get("/", response_model=List[WishlistResponse])
async def get_wishlist(
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's wishlist.
    """
    wishlist = await wishlist_service.get_user_wishlist(db, current_user.id)
    return wishlist


@router.post("/", response_model=WishlistResponse, status_code=status.HTTP_201_CREATED)
async def add_to_wishlist(
    wishlist_data: WishlistCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add item to wishlist.
    
    If item already exists in wishlist, note will be updated if provided.
    """
    try:
        wishlist_item = await wishlist_service.add_to_wishlist(
            db, current_user.id, wishlist_data
        )
        return wishlist_item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{potion_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_wishlist(
    potion_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove item from wishlist.
    """
    success = await wishlist_service.remove_from_wishlist(db, current_user.id, potion_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in wishlist"
        )


@router.get("/check/{potion_id}")
async def check_in_wishlist(
    potion_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Check if potion is in user's wishlist.
    """
    in_wishlist = await wishlist_service.check_in_wishlist(db, current_user.id, potion_id)
    return {"in_wishlist": in_wishlist}