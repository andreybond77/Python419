from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user, get_optional_user
from schemas.cart import (
    CartResponse,
    CartItemCreate,
    CartItemUpdate,
    CartItemResponse
)
from services.cart_service import cart_service

router = APIRouter(prefix="/cart", tags=["cart"])


@router.get("/", response_model=CartResponse)
async def get_cart(
    x_session_id: str = Header(None, description="Anonymous user session ID"),
    current_user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's cart.
    
    If user is authenticated: uses user ID.
    If user is anonymous: uses session ID from X-Session-ID header.
    """
    if current_user:
        # Authenticated user
        cart = await cart_service.get_or_create_cart(db, user_id=current_user.id)
        return cart
    elif x_session_id:
        # Anonymous user with session
        cart = await cart_service.get_or_create_cart(db, session_id=x_session_id)
        return cart
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication or session ID required"
        )


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    item_data: CartItemCreate,
    x_session_id: str = Header(None, description="Anonymous user session ID"),
    current_user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Add item to cart.
    
    If item already exists in cart, quantity will be increased.
    Maximum quantity per item: 99.
    """
    # Get or create cart
    if current_user:
        cart = await cart_service.get_or_create_cart(db, user_id=current_user.id)
    elif x_session_id:
        cart = await cart_service.get_or_create_cart(db, session_id=x_session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication or session ID required"
        )
    
    try:
        item = await cart_service.add_item_to_cart(db, cart.id, item_data)
        return item
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/items/{item_id}", response_model=CartItemResponse)
async def update_cart_item(
    item_id: str,
    item_update: CartItemUpdate,
    x_session_id: str = Header(None, description="Anonymous user session ID"),
    current_user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update cart item quantity.
    """
    # Get cart
    if current_user:
        cart = await cart_service.get_or_create_cart(db, user_id=current_user.id)
    elif x_session_id:
        cart = await cart_service.get_or_create_cart(db, session_id=x_session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication or session ID required"
        )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    item = await cart_service.update_cart_item(db, cart.id, item_id, item_update)
    if not item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )
    
    return item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    item_id: str,
    x_session_id: str = Header(None, description="Anonymous user session ID"),
    current_user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Remove item from cart.
    """
    # Get cart
    if current_user:
        cart = await cart_service.get_or_create_cart(db, user_id=current_user.id)
    elif x_session_id:
        cart = await cart_service.get_or_create_cart(db, session_id=x_session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication or session ID required"
        )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    success = await cart_service.remove_item_from_cart(db, cart.id, item_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item not found in cart"
        )


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    x_session_id: str = Header(None, description="Anonymous user session ID"),
    current_user = Depends(get_optional_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Clear all items from cart.
    """
    # Get cart
    if current_user:
        cart = await cart_service.get_or_create_cart(db, user_id=current_user.id)
    elif x_session_id:
        cart = await cart_service.get_or_create_cart(db, session_id=x_session_id)
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Either authentication or session ID required"
        )
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart not found"
        )
    
    await cart_service.clear_cart(db, cart.id)


@router.post("/merge", response_model=CartResponse)
async def merge_carts(
    session_cart_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Merge anonymous session cart with user cart after login.
    """
    # Get user cart
    user_cart = await cart_service.get_or_create_cart(db, user_id=current_user.id)
    
    try:
        merged_cart = await cart_service.merge_carts(db, session_cart_id, user_cart.id)
        return merged_cart
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )