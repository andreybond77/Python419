from typing import Optional, List, Dict, Any
from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid

from models.cart import Cart, CartItem
from models.potion import Potion
from schemas.cart import (
    CartCreate, 
    CartUpdate, 
    CartResponse,
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse
)
from .base_service import BaseService


class CartService(BaseService[Cart, CartCreate, CartUpdate, CartResponse]):
    def __init__(self):
        super().__init__(Cart, CartResponse)
    
    async def get_or_create_cart(
        self, 
        session: AsyncSession, 
        user_id: Optional[uuid.UUID] = None,
        session_id: Optional[str] = None
    ) -> CartResponse:
        """
        Get existing cart or create new one.
        
        Args:
            session: Database session
            user_id: User ID for authenticated users (optional)
            session_id: Session ID for anonymous users (optional)
            
        Returns:
            CartResponse: Cart data
            
        Raises:
            ValueError: If neither user_id nor session_id is provided
        """
        if not user_id and not session_id:
            raise ValueError("Either user_id or session_id must be provided")
        
        # Поиск существующей корзины
        query = select(Cart)
        if user_id:
            query = query.where(Cart.user_id == user_id)
        elif session_id:
            query = query.where(Cart.session_id == session_id)
        
        result = await session.execute(query.options(selectinload(Cart.items)))
        cart = result.scalar_one_or_none()
        
        if cart:
            return self._model_to_schema(cart)
        
        # Создание новой корзины
        cart_data = {}
        if user_id:
            cart_data["user_id"] = user_id
        if session_id:
            cart_data["session_id"] = session_id
        
        new_cart = Cart(**cart_data)  # user_id может быть None для анонимных корзин!
        session.add(new_cart)
        await session.commit()
        await session.refresh(new_cart)
        
        return self._model_to_schema(new_cart)
    
    async def get_cart_by_id(
        self, 
        session: AsyncSession, 
        cart_id: uuid.UUID
    ) -> Optional[CartResponse]:
        """
        Get cart by ID with items preloaded.
        
        Args:
            session: Database session
            cart_id: Cart UUID
            
        Returns:
            Optional[CartResponse]: Cart data or None if not found
        """
        query = (
            select(Cart)
            .where(Cart.id == cart_id)
            .options(selectinload(Cart.items))
        )
        result = await session.execute(query)
        cart = result.scalar_one_or_none()
        
        if cart:
            return self._model_to_schema(cart)
        return None
    
    async def get_user_cart(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID
    ) -> Optional[CartResponse]:
        """
        Get user's cart with items preloaded.
        
        Args:
            session: Database session
            user_id: User UUID
            
        Returns:
            Optional[CartResponse]: Cart data or None if not found
        """
        query = (
            select(Cart)
            .where(Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        result = await session.execute(query)
        cart = result.scalar_one_or_none()
        
        if cart:
            return self._model_to_schema(cart)
        return None
    
    async def get_session_cart(
        self, 
        session: AsyncSession, 
        session_id: str
    ) -> Optional[CartResponse]:
        """
        Get session cart with items preloaded.
        
        Args:
            session: Database session
            session_id: Session ID for anonymous user
            
        Returns:
            Optional[CartResponse]: Cart data or None if not found
        """
        query = (
            select(Cart)
            .where(Cart.session_id == session_id)
            .options(selectinload(Cart.items))
        )
        result = await session.execute(query)
        cart = result.scalar_one_or_none()
        
        if cart:
            return self._model_to_schema(cart)
        return None
    
    async def add_item_to_cart(
        self, 
        session: AsyncSession, 
        cart_id: uuid.UUID,
        item_in: CartItemCreate
    ) -> CartItemResponse:
        """
        Add item to cart or update quantity if exists.
        
        Args:
            session: Database session
            cart_id: Cart UUID
            item_in: Cart item data
            
        Returns:
            CartItemResponse: Created/updated cart item
            
        Raises:
            ValueError: If cart or potion not found, or potion out of stock
        """
        # Get cart
        cart_query = select(Cart).where(Cart.id == cart_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise ValueError(f"Cart with id {cart_id} not found")
        
        # Get potion
        potion_query = select(Potion).where(Potion.id == item_in.potion_id)
        potion_result = await session.execute(potion_query)
        potion = potion_result.scalar_one_or_none()
        
        if not potion:
            raise ValueError(f"Potion with id {item_in.potion_id} not found")
        
        if not potion.in_stock:
            raise ValueError(f"Potion {potion.name} is out of stock")
        
        if potion.stock_quantity < item_in.quantity:
            raise ValueError(f"Insufficient stock for {potion.name}. Available: {potion.stock_quantity}")
        
        # Check if item already in cart
        item_query = (
            select(CartItem)
            .where(
                CartItem.cart_id == cart_id,
                CartItem.potion_id == item_in.potion_id
            )
        )
        item_result = await session.execute(item_query)
        existing_item = item_result.scalar_one_or_none()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item.quantity + item_in.quantity
            if new_quantity > 99:
                new_quantity = 99
            
            existing_item.quantity = new_quantity
            await session.commit()
            await session.refresh(existing_item)
            
            # Update cart totals
            await self._update_cart_totals(session, cart_id)
            
            return CartItemResponse.model_validate(existing_item, from_attributes=True)
        else:
            # Create new item
            cart_item = CartItem(
                cart_id=cart_id,
                potion_id=item_in.potion_id,
                quantity=item_in.quantity,
                price_per_unit=potion.price,
                potion_name=potion.name,
                potion_image=potion.image_url or "",
                potion_category=potion.category
            )
            
            session.add(cart_item)
            await session.commit()
            await session.refresh(cart_item)
            
            # Update cart totals
            await self._update_cart_totals(session, cart_id)
            
            return CartItemResponse.model_validate(cart_item, from_attributes=True)
    
    async def update_cart_item(
        self, 
        session: AsyncSession, 
        cart_id: uuid.UUID,
        item_id: uuid.UUID,
        item_update: CartItemUpdate
    ) -> Optional[CartItemResponse]:
        """
        Update cart item quantity.
        
        Args:
            session: Database session
            cart_id: Cart UUID
            item_id: Cart item UUID
            item_update: Update data
            
        Returns:
            Optional[CartItemResponse]: Updated item or None if not found
        """
        # Get item
        item_query = select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        )
        item_result = await session.execute(item_query)
        item = item_result.scalar_one_or_none()
        
        if not item:
            return None
        
        # Check stock if increasing quantity
        if item_update.quantity > item.quantity:
            potion_query = select(Potion).where(Potion.id == item.potion_id)
            potion_result = await session.execute(potion_query)
            potion = potion_result.scalar_one_or_none()
            
            if potion and potion.stock_quantity < (item_update.quantity - item.quantity):
                raise ValueError(f"Insufficient stock for {potion.name}")
        
        # Update quantity
        item.quantity = item_update.quantity
        await session.commit()
        await session.refresh(item)
        
        # Update cart totals
        await self._update_cart_totals(session, cart_id)
        
        return CartItemResponse.model_validate(item, from_attributes=True)
    
    async def remove_item_from_cart(
        self, 
        session: AsyncSession, 
        cart_id: uuid.UUID,
        item_id: uuid.UUID
    ) -> bool:
        """
        Remove item from cart.
        
        Args:
            session: Database session
            cart_id: Cart UUID
            item_id: Cart item UUID
            
        Returns:
            bool: True if item was removed, False otherwise
        """
        # Get item
        item_query = select(CartItem).where(
            CartItem.id == item_id,
            CartItem.cart_id == cart_id
        )
        item_result = await session.execute(item_query)
        item = item_result.scalar_one_or_none()
        
        if not item:
            return False
        
        # Delete item
        await session.delete(item)
        await session.commit()
        
        # Update cart totals
        await self._update_cart_totals(session, cart_id)
        
        return True
    
    async def clear_cart(
        self, 
        session: AsyncSession, 
        cart_id: uuid.UUID
    ) -> bool:
        """
        Clear all items from cart.
        
        Args:
            session: Database session
            cart_id: Cart UUID
            
        Returns:
            bool: Always returns True
        """
        # Delete all items
        delete_query = delete(CartItem).where(CartItem.cart_id == cart_id)
        await session.execute(delete_query)
        
        # Update cart totals
        await self._update_cart_totals(session, cart_id)
        
        return True
    
    async def _update_cart_totals(self, session: AsyncSession, cart_id: uuid.UUID) -> None:
        """
        Update cart totals (total_items and total_price).
        
        Args:
            session: Database session
            cart_id: Cart UUID
        """
        from sqlalchemy import func
        
        # Get cart to check if it exists
        cart_query = select(Cart).where(Cart.id == cart_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            return
        
        # Calculate totals
        items_query = (
            select(
                func.coalesce(func.sum(CartItem.quantity), 0).label("total_items"),
                func.coalesce(func.sum(CartItem.quantity * CartItem.price_per_unit), 0.0).label("total_price")
            )
            .where(CartItem.cart_id == cart_id)
        )
        
        items_result = await session.execute(items_query)
        row = items_result.first()
        
        if row:
            total_items = row[0] or 0
            total_price = float(row[1] or 0.0)
        else:
            total_items = 0
            total_price = 0.0
        
        # Update cart
        cart.total_items = total_items
        cart.total_price = total_price
        
        await session.commit()
    
    async def merge_carts(
        self, 
        session: AsyncSession, 
        source_cart_id: uuid.UUID,
        target_cart_id: uuid.UUID
    ) -> CartResponse:
        """
        Merge two carts (e.g., when user logs in).
        
        Args:
            session: Database session
            source_cart_id: Source cart UUID (usually anonymous cart)
            target_cart_id: Target cart UUID (usually user cart)
            
        Returns:
            CartResponse: Updated target cart
            
        Raises:
            ValueError: If one or both carts not found
        """
        # Get both carts with items
        source_query = (
            select(Cart)
            .where(Cart.id == source_cart_id)
            .options(selectinload(Cart.items))
        )
        source_result = await session.execute(source_query)
        source_cart = source_result.scalar_one_or_none()
        
        target_query = (
            select(Cart)
            .where(Cart.id == target_cart_id)
            .options(selectinload(Cart.items))
        )
        target_result = await session.execute(target_query)
        target_cart = target_result.scalar_one_or_none()
        
        if not source_cart or not target_cart:
            raise ValueError("One or both carts not found")
        
        # Don't merge if it's the same cart
        if source_cart_id == target_cart_id:
            return self._model_to_schema(target_cart)
        
        # Merge items
        for source_item in source_cart.items:
            # Check if item exists in target cart
            target_item = next(
                (item for item in target_cart.items if item.potion_id == source_item.potion_id),
                None
            )
            
            if target_item:
                # Update quantity
                new_quantity = target_item.quantity + source_item.quantity
                if new_quantity > 99:
                    new_quantity = 99
                target_item.quantity = new_quantity
            else:
                # Create new item in target cart
                new_item = CartItem(
                    cart_id=target_cart.id,
                    potion_id=source_item.potion_id,
                    quantity=source_item.quantity,
                    price_per_unit=source_item.price_per_unit,
                    potion_name=source_item.potion_name,
                    potion_image=source_item.potion_image,
                    potion_category=source_item.potion_category
                )
                session.add(new_item)
        
        # Delete source cart items
        delete_query = delete(CartItem).where(CartItem.cart_id == source_cart_id)
        await session.execute(delete_query)
        
        # Delete source cart
        await session.delete(source_cart)
        
        # Update target cart totals
        await self._update_cart_totals(session, target_cart_id)
        
        await session.commit()
        
        # Return updated target cart
        return await self.get_cart_by_id(session, target_cart_id)
    
    async def assign_cart_to_user(
        self,
        session: AsyncSession,
        cart_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> Optional[CartResponse]:
        """
        Assign anonymous cart to authenticated user.
        
        Args:
            session: Database session
            cart_id: Cart UUID
            user_id: User UUID
            
        Returns:
            Optional[CartResponse]: Updated cart or None if not found
        """
        # Get cart
        cart_query = select(Cart).where(Cart.id == cart_id)
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            return None
        
        # Check if user already has a cart
        user_cart_query = select(Cart).where(Cart.user_id == user_id)
        user_cart_result = await session.execute(user_cart_query)
        user_cart = user_cart_result.scalar_one_or_none()
        
        if user_cart:
            # User already has a cart, merge instead
            return await self.merge_carts(session, cart_id, user_cart.id)
        
        # Assign cart to user
        cart.user_id = user_id
        cart.session_id = None  # Clear session ID
        
        await session.commit()
        await session.refresh(cart)
        
        return self._model_to_schema(cart)
    
    async def get_or_create_cart_for_user(
        self,
        session: AsyncSession,
        user_id: uuid.UUID
    ) -> CartResponse:
        """
        Get or create cart for authenticated user.
        
        Args:
            session: Database session
            user_id: User UUID
            
        Returns:
            CartResponse: User's cart
        """
        cart = await self.get_user_cart(session, user_id)
        if cart:
            return cart
        
        # Create new cart for user
        return await self.get_or_create_cart(session, user_id=user_id)
    
    async def cleanup_abandoned_carts(
        self,
        session: AsyncSession,
        days_old: int = 30
    ) -> int:
        """
        Clean up abandoned anonymous carts older than specified days.
        
        Args:
            session: Database session
            days_old: Delete carts older than this many days
            
        Returns:
            int: Number of deleted carts
        """
        from datetime import datetime, timedelta
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_old)
        
        # Find abandoned anonymous carts
        query = select(Cart.id).where(
            Cart.user_id.is_(None),  # Only anonymous carts
            Cart.session_id.is_not(None),
            Cart.updated_at < cutoff_date
        )
        
        result = await session.execute(query)
        cart_ids = result.scalars().all()
        
        if not cart_ids:
            return 0
        
        # Delete carts
        delete_query = delete(Cart).where(Cart.id.in_(cart_ids))
        result = await session.execute(delete_query)
        await session.commit()
        
        return result.rowcount


# Singleton instance
cart_service = CartService()