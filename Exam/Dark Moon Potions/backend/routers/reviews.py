from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user, get_current_active_user
from schemas.review import (
    ReviewCreate, 
    ReviewUpdate, 
    ReviewResponse
)
from services.review_service import review_service

router = APIRouter(prefix="/reviews", tags=["reviews"])


@router.post("/", response_model=ReviewResponse, status_code=status.HTTP_201_CREATED)
async def create_review(
    review_data: ReviewCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new review for a potion.
    
    User must have purchased the potion for review to be marked as verified.
    Reviews require moderation before being publicly visible.
    """
    try:
        review = await review_service.create(db, current_user.id, review_data)
        return review
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/potion/{potion_id}", response_model=Dict[str, Any])
async def get_potion_reviews(
    potion_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=50, description="Items per page"),
    approved_only: bool = Query(True, description="Show only approved reviews"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reviews for a specific potion.
    """
    skip = (page - 1) * limit
    reviews, total = await review_service.get_potion_reviews(
        db, potion_id, skip, limit, approved_only
    )
    
    # Get review statistics
    stats = await review_service.get_review_stats(db, potion_id)
    
    return {
        "reviews": reviews,
        "stats": stats,
        "total": total,
        "page": page,
        "limit": limit,
        "pages": (total + limit - 1) // limit
    }


@router.get("/user/me", response_model=List[ReviewResponse])
async def get_my_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's reviews.
    """
    skip = (page - 1) * limit
    reviews = await review_service.get_user_reviews(db, current_user.id, skip, limit)
    return reviews


@router.get("/user/{user_id}", response_model=List[ReviewResponse])
async def get_user_reviews(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    db: AsyncSession = Depends(get_db)
):
    """
    Get reviews by user ID.
    """
    skip = (page - 1) * limit
    reviews = await review_service.get_user_reviews(db, user_id, skip, limit)
    return reviews


@router.put("/{review_id}", response_model=ReviewResponse)
async def update_review(
    review_id: str,
    review_update: ReviewUpdate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update user's own review.
    """
    # Check if review belongs to user
    review = await review_service.get(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this review"
        )
    
    updated_review = await review_service.update(db, review_id, review_update)
    if not updated_review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return updated_review


@router.delete("/{review_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_review(
    review_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Delete user's own review.
    """
    # Check if review belongs to user
    review = await review_service.get(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    if review.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this review"
        )
    
    success = await review_service.delete(db, review_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )


@router.post("/{review_id}/helpful")
async def mark_review_helpful(
    review_id: str,
    helpful: bool = Query(True, description="Mark as helpful (True) or not helpful (False)"),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Mark review as helpful or not helpful.
    """
    review = await review_service.mark_helpful(db, review_id, current_user.id, helpful)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return {"message": "Thank you for your feedback!"}