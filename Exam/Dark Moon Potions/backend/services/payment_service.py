from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
import uuid
import secrets

from models.payment import Payment, PaymentStatus
from schemas.payment import PaymentCreate, PaymentUpdate, PaymentResponse
from .base_service import BaseService


class PaymentService(BaseService[Payment, PaymentCreate, PaymentUpdate, PaymentResponse]):
    def __init__(self):
        super().__init__(Payment, PaymentResponse)
    
    def _generate_payment_id(self) -> str:
        """Generate unique payment ID."""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        random_str = secrets.token_hex(4).upper()
        return f"PAY-{timestamp}-{random_str}"
    
    async def create_payment(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        payment_in: PaymentCreate
    ) -> PaymentResponse:
        """Create new payment."""
        payment_data = payment_in.model_dump()
        payment = Payment(
            **payment_data,
            user_id=user_id,
            payment_id=self._generate_payment_id(),
            status=PaymentStatus.PENDING
        )
        
        session.add(payment)
        await session.commit()
        await session.refresh(payment)
        
        return self._model_to_schema(payment)
    
    async def process_payment(
        self, 
        session: AsyncSession, 
        payment_id: str,
        transaction_data: Dict[str, Any]
    ) -> Optional[PaymentResponse]:
        """Process payment with gateway response."""
        # Get payment
        query = select(Payment).where(Payment.payment_id == payment_id)
        result = await session.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
        
        # Update payment status based on gateway response
        # This is a simplified example - in reality, you would verify with gateway
        if transaction_data.get("success"):
            payment.status = PaymentStatus.COMPLETED
            payment.transaction_id = transaction_data.get("transaction_id")
            payment.gateway_response = transaction_data
            payment.completed_at = datetime.utcnow()
            payment.card_last4 = transaction_data.get("card_last4")
            payment.card_brand = transaction_data.get("card_brand")
        else:
            payment.status = PaymentStatus.FAILED
            payment.gateway_response = transaction_data
        
        await session.commit()
        await session.refresh(payment)
        
        return self._model_to_schema(payment)
    
    async def get_payment_by_order(
        self, 
        session: AsyncSession, 
        order_id: uuid.UUID
    ) -> Optional[PaymentResponse]:
        """Get payment by order ID."""
        query = select(Payment).where(Payment.order_id == order_id)
        result = await session.execute(query)
        payment = result.scalar_one_or_none()
        
        if payment:
            return self._model_to_schema(payment)
        return None
    
    async def refund_payment(
        self, 
        session: AsyncSession, 
        payment_id: str
    ) -> Optional[PaymentResponse]:
        """Refund a payment."""
        query = select(Payment).where(Payment.payment_id == payment_id)
        result = await session.execute(query)
        payment = result.scalar_one_or_none()
        
        if not payment:
            return None
        
        if payment.status != PaymentStatus.COMPLETED:
            raise ValueError(f"Cannot refund payment with status {payment.status.value}")
        
        payment.status = PaymentStatus.REFUNDED
        
        await session.commit()
        await session.refresh(payment)
        
        return self._model_to_schema(payment)


payment_service = PaymentService()