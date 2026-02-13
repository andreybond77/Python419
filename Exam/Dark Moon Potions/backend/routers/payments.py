from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from dependencies.auth import get_current_user, get_current_active_user
from schemas.payment import PaymentCreate, PaymentResponse, PaymentUpdate
from services.payment_service import payment_service

router = APIRouter(prefix="/payments", tags=["payments"])


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_data: PaymentCreate,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Create payment for an order.
    """
    # Verify order belongs to user
    from services.order_service import order_service
    order = await order_service.get(db, payment_data.order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create payment for this order"
        )
    
    try:
        payment = await payment_service.create_payment(db, current_user.id, payment_data)
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{payment_id}", response_model=PaymentResponse)
async def get_payment(
    payment_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get payment by ID.
    """
    payment = await payment_service.get(db, payment_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    # Check if payment belongs to user
    if payment.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    
    return payment


@router.get("/order/{order_id}", response_model=PaymentResponse)
async def get_payment_by_order(
    order_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get payment by order ID.
    """
    payment = await payment_service.get_payment_by_order(db, order_id)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found for this order"
        )
    
    # Check if payment belongs to user
    if payment.user_id != current_user.id and not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this payment"
        )
    
    return payment


@router.post("/{payment_id}/process", response_model=PaymentResponse)
async def process_payment(
    payment_id: str,
    transaction_data: Dict[str, Any] = Body(...),
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Process payment with gateway response (staff only).
    
    This endpoint would typically receive webhook calls from payment gateways.
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    payment = await payment_service.process_payment(db, payment_id, transaction_data)
    if not payment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    
    return payment


@router.post("/{payment_id}/refund", response_model=PaymentResponse)
async def refund_payment(
    payment_id: str,
    current_user = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Refund a payment (staff only).
    """
    if not current_user.is_staff:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Staff privileges required"
        )
    
    try:
        payment = await payment_service.refund_payment(db, payment_id)
        if not payment:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return payment
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )