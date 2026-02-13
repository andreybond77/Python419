"""initial migration

Revision ID: 001
Revises: 
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table('users',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('username', sa.String(length=100), nullable=False),
        sa.Column('hashed_password', sa.String(length=255), nullable=False),
        sa.Column('full_name', sa.String(length=255), nullable=True),
        sa.Column('avatar_url', sa.String(length=500), nullable=True),
        sa.Column('bio', sa.Text(), nullable=True),
        sa.Column('address', sa.Text(), nullable=True),
        sa.Column('phone', sa.String(length=20), nullable=True),
        sa.Column('wizard_level', sa.String(length=20), nullable=False, default='novice'),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('is_verified', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_staff', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False, default=False),
        sa.Column('preferences', postgresql.JSON(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_username', 'users', ['username'], unique=True)
    
    # Create potion_categories table
    op.create_table('potion_categories',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    
    # Create potions table
    op.create_table('potions',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('category', sa.String(length=50), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('original_price', sa.Float(), nullable=True),
        sa.Column('discount_percent', sa.Integer(), nullable=False, default=0),
        sa.Column('in_stock', sa.Boolean(), nullable=False, default=True),
        sa.Column('stock_quantity', sa.Integer(), nullable=False, default=0),
        sa.Column('min_stock_level', sa.Integer(), nullable=False, default=10),
        sa.Column('rarity', sa.String(length=20), nullable=False, default='common'),
        sa.Column('brewing_time', sa.String(length=100), nullable=False),
        sa.Column('brewing_difficulty', sa.String(length=20), nullable=False, default='medium'),
        sa.Column('ingredients', postgresql.ARRAY(sa.String()), nullable=False, default=list),
        sa.Column('effects', postgresql.ARRAY(sa.String()), nullable=False, default=list),
        sa.Column('warnings', postgresql.ARRAY(sa.String()), nullable=False, default=list),
        sa.Column('image_url', sa.String(length=500), nullable=False),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('image_gallery', postgresql.ARRAY(sa.String()), nullable=False, default=list),
        sa.Column('popularity_score', sa.Integer(), nullable=False, default=0),
        sa.Column('purchase_count', sa.Integer(), nullable=False, default=0),
        sa.Column('review_count', sa.Integer(), nullable=False, default=0),
        sa.Column('average_rating', sa.Float(), nullable=False, default=0.0),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.CheckConstraint('price >= 0', name='check_price_positive'),
        sa.CheckConstraint('stock_quantity >= 0', name='check_stock_positive'),
        sa.CheckConstraint('discount_percent >= 0 AND discount_percent <= 100', name='check_discount_range'),
        sa.ForeignKeyConstraint(['category_id'], ['potion_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    op.create_index('ix_potions_name', 'potions', ['name'])
    op.create_index('ix_potions_slug', 'potions', ['slug'], unique=True)
    
    # Create carts table
    op.create_table('carts',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('total_items', sa.Integer(), nullable=False, default=0),
        sa.Column('total_price', sa.Float(), nullable=False, default=0.0),
        sa.Column('session_id', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
        sa.UniqueConstraint('session_id')
    )
    
    # Create cart_items table
    op.create_table('cart_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('cart_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('potion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('price_per_unit', sa.Float(), nullable=False),
        sa.Column('potion_name', sa.String(length=255), nullable=False),
        sa.Column('potion_image', sa.String(length=500), nullable=False),
        sa.Column('potion_category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.CheckConstraint('quantity > 0', name='check_quantity_positive'),
        sa.CheckConstraint('price_per_unit >= 0', name='check_price_positive'),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create order_status enum
    order_status_enum = postgresql.ENUM('pending', 'processing', 'shipped', 'delivered', 'cancelled', 'refunded', name='order_status')
    order_status_enum.create(op.get_bind())
    
    # Create orders table
    op.create_table('orders',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('status', order_status_enum, nullable=False, default='pending'),
        sa.Column('subtotal', sa.Float(), nullable=False),
        sa.Column('shipping_cost', sa.Float(), nullable=False, default=0.0),
        sa.Column('discount_amount', sa.Float(), nullable=False, default=0.0),
        sa.Column('tax_amount', sa.Float(), nullable=False, default=0.0),
        sa.Column('total_amount', sa.Float(), nullable=False),
        sa.Column('shipping_method', sa.String(length=50), nullable=False),
        sa.Column('shipping_address', sa.Text(), nullable=False),
        sa.Column('shipping_city', sa.String(length=100), nullable=False),
        sa.Column('shipping_zip', sa.String(length=20), nullable=False),
        sa.Column('shipping_country', sa.String(length=100), nullable=False),
        sa.Column('customer_name', sa.String(length=255), nullable=False),
        sa.Column('customer_email', sa.String(length=255), nullable=False),
        sa.Column('customer_phone', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('internal_notes', sa.Text(), nullable=True),
        sa.Column('tracking_number', sa.String(length=100), nullable=True),
        sa.Column('carrier', sa.String(length=50), nullable=True),
        sa.Column('estimated_delivery', sa.DateTime(), nullable=True),
        sa.Column('delivered_at', sa.DateTime(), nullable=True),
        sa.Column('payment_status', sa.String(length=20), nullable=False, default='pending'),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.CheckConstraint('subtotal >= 0', name='check_subtotal_positive'),
        sa.CheckConstraint('total_amount >= 0', name='check_total_positive'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    op.create_index('ix_orders_order_number', 'orders', ['order_number'], unique=True)
    
    # Create order_items table
    op.create_table('order_items',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('potion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False),
        sa.Column('unit_price', sa.Float(), nullable=False),
        sa.Column('total_price', sa.Float(), nullable=False),
        sa.Column('potion_name', sa.String(length=255), nullable=False),
        sa.Column('potion_image', sa.String(length=500), nullable=False),
        sa.Column('potion_category', sa.String(length=50), nullable=False),
        sa.Column('potion_rarity', sa.String(length=20), nullable=False),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create reviews table
    op.create_table('reviews',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('potion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified_purchase', sa.Boolean(), nullable=False, default=True),
        sa.Column('helpful_count', sa.Integer(), nullable=False, default=0),
        sa.Column('not_helpful_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.CheckConstraint('rating >= 1 AND rating <= 5', name='check_rating_range'),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create wishlist table
    op.create_table('wishlist',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('potion_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('note', sa.String(), nullable=False, default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'potion_id', name='unique_user_potion_wishlist')
    )
    
    # Create payment_status enum
    payment_status_enum = postgresql.ENUM('pending', 'processing', 'completed', 'failed', 'refunded', 'cancelled', name='payment_status')
    payment_status_enum.create(op.get_bind())
    
    # Create payments table
    op.create_table('payments',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('order_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('payment_id', sa.String(length=100), nullable=False),
        sa.Column('status', payment_status_enum, nullable=False, default='pending'),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False, default='USD'),
        sa.Column('payment_method', sa.String(length=50), nullable=False),
        sa.Column('payment_gateway', sa.String(length=50), nullable=False),
        sa.Column('transaction_id', sa.String(length=100), nullable=True),
        sa.Column('gateway_response', sa.Text(), nullable=True),
        sa.Column('card_last4', sa.String(length=4), nullable=True),
        sa.Column('card_brand', sa.String(length=20), nullable=True),
        sa.Column('billing_address', sa.Text(), nullable=True),
        sa.Column('billing_city', sa.String(length=100), nullable=True),
        sa.Column('billing_country', sa.String(length=100), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()'), onupdate=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_id')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('payments')
    op.drop_table('wishlist')
    op.drop_table('reviews')
    op.drop_table('order_items')
    op.drop_table('orders')
    op.drop_table('cart_items')
    op.drop_table('carts')
    op.drop_table('potions')
    op.drop_table('potion_categories')
    op.drop_table('users')
    
    # Drop enums
    op.execute("DROP TYPE IF EXISTS payment_status")
    op.execute("DROP TYPE IF EXISTS order_status")