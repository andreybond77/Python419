from datetime import datetime
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
import uuid
import random
import string

from models.order import Order, OrderItem, OrderStatus
from models.cart import Cart, CartItem
from models.potion import Potion
from schemas.order import (
    OrderCreate, 
    OrderUpdate, 
    OrderResponse,
    OrderFilter
)
from .base_service import BaseService


class OrderService(BaseService[Order, OrderCreate, OrderUpdate, OrderResponse]):
    def __init__(self):
        super().__init__(Order, OrderResponse)
    
    def _generate_order_number(self) -> str:
        """Generate unique order number."""
        timestamp = datetime.now().strftime("%Y%m%d")
        random_str = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        return f"DM-{timestamp}-{random_str}"
    
    async def create_from_cart(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        order_data: OrderCreate,
        cart_id: uuid.UUID
    ) -> OrderResponse:
        """Create order from cart contents."""
        # Get cart with items
        cart_query = (
            select(Cart)
            .where(Cart.id == cart_id, Cart.user_id == user_id)
            .options(selectinload(Cart.items))
        )
        cart_result = await session.execute(cart_query)
        cart = cart_result.scalar_one_or_none()
        
        if not cart:
            raise ValueError(f"Cart not found or doesn't belong to user")
        
        if cart.total_items == 0:
            raise ValueError("Cart is empty")
        
        # Calculate totals
        subtotal = cart.total_price
        shipping_cost = 0.0  # Calculate based on shipping method
        tax_amount = subtotal * 0.1  # 10% tax for example
        total_amount = subtotal + shipping_cost + tax_amount
        
        # Create order
        order = Order(
            user_id=user_id,
            order_number=self._generate_order_number(),
            status=OrderStatus.PENDING,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            tax_amount=tax_amount,
            total_amount=total_amount,
            shipping_method=order_data.shipping_method,
            shipping_address=order_data.shipping_address,
            shipping_city=order_data.shipping_city,
            shipping_zip=order_data.shipping_zip,
            shipping_country=order_data.shipping_country,
            customer_name=order_data.customer_name,
            customer_email=order_data.customer_email,
            customer_phone=order_data.customer_phone,
            notes=order_data.notes,
            payment_method=order_data.payment_method,
            payment_status="pending"
        )
        
        session.add(order)
        await session.flush()  # Get order ID
        
        # Create order items from cart items
        for cart_item in cart.items:
            # Get potion for current price
            potion_query = select(Potion).where(Potion.id == cart_item.potion_id)
            potion_result = await session.execute(potion_query)
            potion = potion_result.scalar_one_or_none()
            
            if not potion:
                raise ValueError(f"Potion with id {cart_item.potion_id} not found")
            
            # Check stock
            if potion.stock_quantity < cart_item.quantity:
                raise ValueError(f"Insufficient stock for {potion.name}")
            
            # Create order item
            order_item = OrderItem(
                order_id=order.id,
                potion_id=cart_item.potion_id,
                quantity=cart_item.quantity,
                unit_price=cart_item.price_per_unit,
                total_price=cart_item.total_price,
                potion_name=potion.name,
                potion_image=potion.image_url,
                potion_category=potion.category,
                potion_rarity=potion.rarity
            )
            
            session.add(order_item)
            
            # Update potion stock
            potion.stock_quantity -= cart_item.quantity
            if potion.stock_quantity <= 0:
                potion.in_stock = False
            
            # Update purchase count
            potion.purchase_count += cart_item.quantity
            potion.popularity_score += cart_item.quantity * 10
        
        # Clear cart
        delete_query = delete(CartItem).where(CartItem.cart_id == cart_id)
        await session.execute(delete_query)
        
        # Update cart totals
        cart.total_items = 0
        cart.total_price = 0.0
        
        await session.commit()
        await session.refresh(order, ["items"])
        
        return self._model_to_schema(order)
    
    async def get_user_orders(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID,
        filters: Optional[OrderFilter] = None
    ) -> tuple[List[OrderResponse], int]:
        """Get user's orders with filtering."""
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
        )
        
        # Apply filters
        if filters:
            if filters.status:
                query = query.where(Order.status == filters.status)
            
            if filters.start_date:
                query = query.where(Order.created_at >= filters.start_date)
            
            if filters.end_date:
                query = query.where(Order.created_at <= filters.end_date)
        
        # Count total
        count_query = select(func.count()).select_from(query.subquery())
        total = await session.scalar(count_query)
        
        # Apply pagination
        if filters:
            query = query.offset((filters.page - 1) * filters.limit).limit(filters.limit)
        
        result = await session.execute(query)
        orders = result.scalars().all()
        
        return [self._model_to_schema(order) for order in orders], total
    
    async def get_by_order_number(
        self, 
        session: AsyncSession, 
        order_number: str,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[OrderResponse]:
        """Get order by order number."""
        query = select(Order).where(Order.order_number == order_number)
        
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        query = query.options(selectinload(Order.items))
        
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        
        if order:
            return self._model_to_schema(order)
        return None
    
    async def update_status(
        self, 
        session: AsyncSession, 
        order_id: uuid.UUID,
        status: OrderStatus,
        tracking_number: Optional[str] = None,
        carrier: Optional[str] = None
    ) -> Optional[OrderResponse]:
        """Update order status."""
        update_data = {"status": status}
        
        if tracking_number:
            update_data["tracking_number"] = tracking_number
        
        if carrier:
            update_data["carrier"] = carrier
        
        if status == OrderStatus.DELIVERED:
            update_data["delivered_at"] = datetime.utcnow()
        
        query = (
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
            .returning(Order)
        )
        
        result = await session.execute(query)
        await session.commit()
        
        order = result.scalar_one_or_none()
        if order:
            return self._model_to_schema(order)
        return None
    
    async def cancel_order(
        self, 
        session: AsyncSession, 
        order_id: uuid.UUID,
        user_id: Optional[uuid.UUID] = None
    ) -> Optional[OrderResponse]:
        """Cancel order and restore stock."""
        # Get order with items
        query = select(Order).where(Order.id == order_id)
        
        if user_id:
            query = query.where(Order.user_id == user_id)
        
        query = query.options(selectinload(Order.items))
        
        result = await session.execute(query)
        order = result.scalar_one_or_none()
        
        if not order:
            return None
        
        # Check if order can be cancelled
        if order.status not in [OrderStatus.PENDING, OrderStatus.PROCESSING]:
            raise ValueError(f"Cannot cancel order with status {order.status.value}")
        
        # Restore stock for each item
        for item in order.items:
            potion_query = select(Potion).where(Potion.id == item.potion_id)
            potion_result = await session.execute(potion_query)
            potion = potion_result.scalar_one_or_none()
            
            if potion:
                potion.stock_quantity += item.quantity
                potion.in_stock = True
        
        # Update order status
        order.status = OrderStatus.CANCELLED
        order.payment_status = "refunded"
        
        await session.commit()
        await session.refresh(order)
        
        return self._model_to_schema(order)
    
    async def get_sales_stats(
        self, 
        session: AsyncSession, 
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Get sales statistics."""
        query = select(Order).where(Order.status == OrderStatus.DELIVERED)
        
        if start_date:
            query = query.where(Order.created_at >= start_date)
        
        if end_date:
            query = query.where(Order.created_at <= end_date)
        
        # Get total sales
        total_sales_query = select(func.sum(Order.total_amount)).select_from(query.subquery())
        total_sales = await session.scalar(total_sales_query) or 0.0
        
        # Get order count
        order_count_query = select(func.count(Order.id)).select_from(query.subquery())
        order_count = await session.scalar(order_count_query) or 0
        
        # Get average order value
        avg_order_value = total_sales / order_count if order_count > 0 else 0.0
        
        # Get sales by status
        status_query = (
            select(Order.status, func.count(Order.id).label("count"))
            .group_by(Order.status)
        )
        status_result = await session.execute(status_query)
        sales_by_status = {row[0].value: row[1] for row in status_result.all()}
        
        return {
            "total_sales": total_sales,
            "order_count": order_count,
            "avg_order_value": avg_order_value,
            "sales_by_status": sales_by_status
        }


order_service = OrderService()