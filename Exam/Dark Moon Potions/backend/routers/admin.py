from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime, timedelta

from dependencies.database import get_db
from dependencies.auth import require_admin, require_staff
from services.order_service import order_service
from services.user_service import user_service
from services.potion_service import potion_service
from services.review_service import review_service

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats/overview")
async def get_admin_stats(
    start_date: str = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: str = Query(None, description="End date (YYYY-MM-DD)"),
    current_user = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Get admin dashboard statistics.
    """
    # Parse dates
    start = datetime.fromisoformat(start_date) if start_date else None
    end = datetime.fromisoformat(end_date) if end_date else None
    
    # Get sales stats
    sales_stats = await order_service.get_sales_stats(db, start, end)
    
    # Get user stats
    from sqlalchemy import func, select
    from models.user import User
    
    total_users_query = select(func.count(User.id))
    total_users = await db.scalar(total_users_query)
    
    new_users_query = select(func.count(User.id)).where(
        User.created_at >= (datetime.utcnow() - timedelta(days=30))
    )
    new_users = await db.scalar(new_users_query)
    
    # Get potion stats
    from models.potion import Potion
    
    total_potions_query = select(func.count(Potion.id))
    total_potions = await db.scalar(total_potions_query)
    
    low_stock_query = select(func.count(Potion.id)).where(
        Potion.stock_quantity <= Potion.min_stock_level
    )
    low_stock = await db.scalar(low_stock_query)
    
    # Get pending reviews
    from models.review import Review
    
    pending_reviews_query = select(func.count(Review.id)).where(
        Review.is_approved == False
    )
    pending_reviews = await db.scalar(pending_reviews_query)
    
    return {
        "sales": sales_stats,
        "users": {
            "total": total_users or 0,
            "new_last_30_days": new_users or 0
        },
        "inventory": {
            "total_potions": total_potions or 0,
            "low_stock": low_stock or 0
        },
        "moderation": {
            "pending_reviews": pending_reviews or 0
        }
    }


@router.get("/reviews/pending")
async def get_pending_reviews(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Get pending reviews for moderation.
    """
    from sqlalchemy import select
    from models.review import Review
    from models.user import User
    from models.potion import Potion
    
    query = (
        select(Review, User.username, Potion.name)
        .join(User, Review.user_id == User.id)
        .join(Potion, Review.potion_id == Potion.id)
        .where(Review.is_approved == False)
        .order_by(Review.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )
    
    result = await db.execute(query)
    rows = result.all()
    
    reviews = []
    for review, username, potion_name in rows:
        review_dict = {
            "id": review.id,
            "user_id": review.user_id,
            "potion_id": review.potion_id,
            "rating": review.rating,
            "comment": review.comment,
            "is_approved": review.is_approved,
            "is_verified": review.is_verified,
            "helpful_count": review.helpful_count,
            "not_helpful_count": review.not_helpful_count,
            "created_at": review.created_at,
            "updated_at": review.updated_at,
            "user_username": username,
            "potion_name": potion_name
        }
        reviews.append(review_dict)
    
    return reviews


@router.post("/reviews/{review_id}/approve")
async def approve_review(
    review_id: str,
    current_user = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Approve a review.
    """
    review = await review_service.approve_review(db, review_id)
    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return {"message": "Review approved successfully"}


@router.post("/reviews/{review_id}/reject")
async def reject_review(
    review_id: str,
    current_user = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Reject a review.
    """
    success = await review_service.reject_review(db, review_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Review not found"
        )
    
    return {"message": "Review rejected successfully"}


@router.get("/users/{user_id}/orders")
async def get_user_orders_admin(
    user_id: str,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(20, ge=1, le=50, description="Items per page"),
    current_user = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Get all orders for a specific user (admin only).
    """
    from services.order_service import order_service
    from schemas.order import OrderFilter
    
    filters = OrderFilter(page=page, limit=limit)
    orders, total = await order_service.get_user_orders(db, user_id, filters)
    
    return {
        "orders": orders,
        "total": total,
        "page": page,
        "limit": limit
    }


@router.post("/users/{user_id}/verify")
async def verify_user(
    user_id: str,
    current_user = Depends(require_admin),
    db: AsyncSession = Depends(get_db)
):
    """
    Verify a user account (admin only).
    """
    from sqlalchemy import update
    from models.user import User
    
    query = (
        update(User)
        .where(User.id == user_id)
        .values(is_verified=True)
    )
    
    result = await db.execute(query)
    await db.commit()
    
    if result.rowcount == 0:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return {"message": "User verified successfully"}


@router.post("/inventory/{potion_id}/restock")
async def restock_potion(
    potion_id: str,
    quantity: int = Query(..., ge=1, description="Quantity to add"),
    current_user = Depends(require_staff),
    db: AsyncSession = Depends(get_db)
):
    """
    Restock a potion.
    """
    potion = await potion_service.update_stock(db, potion_id, quantity)
    if not potion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Potion not found"
        )
    
    return {"message": f"Restocked {quantity} units of {potion.name}"}