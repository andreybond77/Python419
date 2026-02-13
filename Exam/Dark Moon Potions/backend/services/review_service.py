from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from models.review import Review
from models.order import Order, OrderItem, OrderStatus
from schemas.review import ReviewCreate, ReviewUpdate, ReviewResponse
from .base_service import BaseService
from .potion_service import potion_service


class ReviewService(BaseService[Review, ReviewCreate, ReviewUpdate, ReviewResponse]):
    def __init__(self):
        super().__init__(Review, ReviewResponse)
    
    async def create(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        review_in: ReviewCreate
    ) -> ReviewResponse:
        """Create new review with validation."""
        # Check if user has purchased the potion
        purchase_query = (
            select(Order)
            .join(OrderItem, Order.id == OrderItem.order_id)
            .where(
                Order.user_id == user_id,
                Order.status == OrderStatus.DELIVERED,
                OrderItem.potion_id == review_in.potion_id
            )
        )
        result = await session.execute(purchase_query)
        has_purchased = result.scalar_one_or_none() is not None
        
        # Create review
        review_data = review_in.model_dump()
        review = Review(
            **review_data,
            user_id=user_id,
            is_verified_purchase=has_purchased,
            is_approved=False  # Require moderation
        )
        
        session.add(review)
        await session.commit()
        await session.refresh(review)
        
        # Update potion rating stats
        await potion_service.update_rating_stats(session, review_in.potion_id)
        
        return self._model_to_schema(review)
    
    async def get_potion_reviews(
        self, 
        session: AsyncSession, 
        potion_id: uuid.UUID,
        skip: int = 0,
        limit: int = 10,
        approved_only: bool = True
    ) -> tuple[List[ReviewResponse], int]:
        """Get reviews for a potion."""
        query = (
            select(Review)
            .where(Review.potion_id == potion_id)
        )
        
        if approved_only:
            query = query.where(Review.is_approved == True)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)
        
        # Get reviews with user info
        query = (
            query
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        # Convert to response with user info
        review_responses = []
        for review in reviews:
            review_dict = review.__dict__.copy()
            review_dict["user_username"] = review.user.username
            review_dict["user_avatar"] = review.user.avatar_url
            review_responses.append(ReviewResponse.model_validate(review_dict))
        
        return review_responses, total
    
    async def get_user_reviews(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        skip: int = 0,
        limit: int = 20
    ) -> List[ReviewResponse]:
        """Get reviews by user."""
        query = (
            select(Review)
            .where(Review.user_id == user_id)
            .options(selectinload(Review.user))
            .order_by(Review.created_at.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await session.execute(query)
        reviews = result.scalars().all()
        
        # Convert to response with user info
        review_responses = []
        for review in reviews:
            review_dict = review.__dict__.copy()
            review_dict["user_username"] = review.user.username
            review_dict["user_avatar"] = review.user.avatar_url
            review_responses.append(ReviewResponse.model_validate(review_dict))
        
        return review_responses
    
    async def mark_helpful(
        self, 
        session: AsyncSession, 
        review_id: uuid.UUID,
        user_id: uuid.UUID,
        helpful: bool = True
    ) -> Optional[ReviewResponse]:
        """Mark review as helpful or not helpful."""
        # TODO: Track which users have voted to prevent multiple votes
        
        query = select(Review).where(Review.id == review_id)
        result = await session.execute(query)
        review = result.scalar_one_or_none()
        
        if not review:
            return None
        
        if helpful:
            review.helpful_count += 1
        else:
            review.not_helpful_count += 1
        
        await session.commit()
        await session.refresh(review)
        
        return self._model_to_schema(review)
    
    async def approve_review(
        self, 
        session: AsyncSession, 
        review_id: uuid.UUID
    ) -> Optional[ReviewResponse]:
        """Approve a review (moderation)."""
        query = (
            update(Review)
            .where(Review.id == review_id)
            .values(is_approved=True)
            .returning(Review)
        )
        
        result = await session.execute(query)
        await session.commit()
        
        review = result.scalar_one_or_none()
        if review:
            # Update potion rating stats
            await potion_service.update_rating_stats(session, review.potion_id)
            return self._model_to_schema(review)
        return None
    
    async def reject_review(
        self, 
        session: AsyncSession, 
        review_id: uuid.UUID
    ) -> bool:
        """Reject a review (moderation)."""
        query = delete(Review).where(Review.id == review_id)
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
    
    async def get_review_stats(
        self, 
        session: AsyncSession, 
        potion_id: uuid.UUID
    ) -> Dict[str, Any]:
        """Get review statistics for a potion."""
        # Get rating distribution
        distribution_query = (
            select(
                Review.rating,
                func.count(Review.id).label("count")
            )
            .where(
                Review.potion_id == potion_id,
                Review.is_approved == True
            )
            .group_by(Review.rating)
            .order_by(Review.rating.desc())
        )
        
        result = await session.execute(distribution_query)
        rating_distribution = {row[0]: row[1] for row in result.all()}
        
        # Get average rating
        avg_query = (
            select(func.avg(Review.rating))
            .where(
                Review.potion_id == potion_id,
                Review.is_approved == True
            )
        )
        avg_rating = await session.scalar(avg_query) or 0.0
        
        # Get total count
        total_query = (
            select(func.count(Review.id))
            .where(
                Review.potion_id == potion_id,
                Review.is_approved == True
            )
        )
        total_reviews = await session.scalar(total_query) or 0
        
        return {
            "average_rating": round(avg_rating, 1),
            "total_reviews": total_reviews,
            "rating_distribution": rating_distribution
        }


review_service = ReviewService()