from typing import List, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from dependencies.database import get_db
from dependencies.auth import get_current_user
from schemas.order import (
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    OrderFilter,
    OrderFilterResponse,
    OrderStatus,
    OrderListResponse
)
from services.order_service import order_service
from services.cart_service import cart_service

router = APIRouter(prefix="/orders", tags=["orders"])


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_data: OrderCreate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create new order from current cart.
    
    The order will be created from items in the user's cart.
    Cart will be cleared after successful order creation.
    """
    # Get user's cart
    cart = await cart_service.get_user_cart(db, current_user.id)
    if not cart or cart.total_items == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cart is empty"
        )
    
    try:
        order = await order_service.create_from_cart(
            db, current_user.id, order_data, cart.id
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=OrderListResponse)
async def get_user_orders(
    status_filter: OrderStatus = Query(None, description="Filter by status"),
    date_from: str = Query(None, description="Filter by start date (YYYY-MM-DD)"),
    date_to: str = Query(None, description="Filter by end date (YYYY-MM-DD)"),
    min_amount: float = Query(None, ge=0, description="Minimum order amount"),
    max_amount: float = Query(None, ge=0, description="Maximum order amount"),
    delivery_method: str = Query(None, description="Filter by delivery method"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's orders with filtering and pagination.
    """
    # Parse dates
    parsed_date_from = None
    parsed_date_to = None
    
    if date_from:
        try:
            parsed_date_from = datetime.fromisoformat(date_from)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_from format. Use YYYY-MM-DD"
            )
    
    if date_to:
        try:
            parsed_date_to = datetime.fromisoformat(date_to)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid date_to format. Use YYYY-MM-DD"
            )
    
    # Create filter
    filters = OrderFilter(
        status=status_filter,
        date_from=parsed_date_from,
        date_to=parsed_date_to,
        min_amount=min_amount,
        max_amount=max_amount,
        delivery_method=delivery_method,
        page=page,
        page_size=page_size
    )
    
    # Get orders
    orders, total = await order_service.get_user_orders(db, current_user.id, filters)
    
    # Return paginated response
    return OrderListResponse(
        items=orders,
        total=total,
        page=page,
        size=page_size,
        pages=(total + page_size - 1) // page_size
    )


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_by_id(
    order_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get order by ID (user can only see their own orders).
    """
    order = await order_service.get(db, order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Check if order belongs to user
    if order.user_id != current_user.id and not getattr(current_user, 'is_staff', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this order"
        )
    
    return order


@router.get("/number/{order_number}", response_model=OrderResponse)
async def get_order_by_number(
    order_number: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get order by order number.
    """
    order = await order_service.get_by_order_number(db, order_number, current_user.id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
async def cancel_order(
    order_id: str,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Cancel order.
    
    Only orders with status 'pending' or 'processing' can be cancelled.
    Stock will be restored for cancelled items.
    """
    try:
        order = await order_service.cancel_order(db, order_id, current_user.id)
        if not order:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: str,
    status_update: OrderUpdate,
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Update order status (staff only).
    
    Can update:
    - Status
    - Tracking number
    - Carrier
    - Notes
    """
    if not getattr(current_user, 'is_staff', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    order = await order_service.update(db, order_id, status_update)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    return order


@router.get("/stats/summary", response_model=Dict[str, Any])
async def get_order_stats(
    current_user = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get order statistics (staff only).
    """
    if not getattr(current_user, 'is_staff', False):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    stats = await order_service.get_order_stats(db)
    return stats