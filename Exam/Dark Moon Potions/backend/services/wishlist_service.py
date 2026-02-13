from typing import Optional, List
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from models.wishlist import Wishlist
from models.potion import Potion
from schemas.wishlist import WishlistCreate, WishlistResponse
from .base_service import BaseService


class WishlistService(BaseService[Wishlist, WishlistCreate, WishlistCreate, WishlistResponse]):
    def __init__(self):
        super().__init__(Wishlist, WishlistResponse)
    
    async def add_to_wishlist(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        wishlist_in: WishlistCreate
    ) -> WishlistResponse:
        """Add item to user's wishlist."""
        # Check if already in wishlist
        existing_query = select(Wishlist).where(
            Wishlist.user_id == user_id,
            Wishlist.potion_id == wishlist_in.potion_id
        )
        result = await session.execute(existing_query)
        existing = result.scalar_one_or_none()
        
        if existing:
            # Update note if provided
            if wishlist_in.note:
                existing.note = wishlist_in.note
                await session.commit()
                await session.refresh(existing)
            return WishlistResponse.model_validate(existing, from_attributes=True)
        
        # Get potion for info
        potion_query = select(Potion).where(Potion.id == wishlist_in.potion_id)
        potion_result = await session.execute(potion_query)
        potion = potion_result.scalar_one_or_none()
        
        if not potion:
            raise ValueError(f"Potion with id {wishlist_in.potion_id} not found")
        
        # Create wishlist item
        wishlist_dict = wishlist_in.model_dump()
        wishlist = Wishlist(**wishlist_dict, user_id=user_id)
        
        session.add(wishlist)
        await session.commit()
        await session.refresh(wishlist)
        
        # Add potion info to response
        response_dict = wishlist.__dict__.copy()
        response_dict.update({
            "potion_name": potion.name,
            "potion_price": potion.price,
            "potion_image": potion.image_url,
            "potion_category": potion.category
        })
        
        return WishlistResponse.model_validate(response_dict)
    
    async def get_user_wishlist(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID
    ) -> List[WishlistResponse]:
        """Get user's wishlist with potion info."""
        query = (
            select(Wishlist, Potion)
            .join(Potion, Wishlist.potion_id == Potion.id)
            .where(Wishlist.user_id == user_id)
            .order_by(Wishlist.created_at.desc())
        )
        
        result = await session.execute(query)
        items = result.all()
        
        wishlist_items = []
        for wishlist, potion in items:
            item_dict = wishlist.__dict__.copy()
            item_dict.update({
                "potion_name": potion.name,
                "potion_price": potion.price,
                "potion_image": potion.image_url,
                "potion_category": potion.category
            })
            wishlist_items.append(WishlistResponse.model_validate(item_dict))
        
        return wishlist_items
    
    async def remove_from_wishlist(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        potion_id: uuid.UUID
    ) -> bool:
        """Remove item from user's wishlist."""
        query = delete(Wishlist).where(
            Wishlist.user_id == user_id,
            Wishlist.potion_id == potion_id
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
    
    async def check_in_wishlist(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        potion_id: uuid.UUID
    ) -> bool:
        """Check if potion is in user's wishlist."""
        query = select(Wishlist).where(
            Wishlist.user_id == user_id,
            Wishlist.potion_id == potion_id
        )
        result = await session.execute(query)
        item = result.scalar_one_or_none()
        
        return item is not None


wishlist_service = WishlistService()