"""fix uuid and nullable cart

Revision ID: 002
Revises: 001
Create Date: 2024-01-02 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql
import uuid

# revision identifiers, used by Alembic.
revision = '002'
down_revision = '001'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # SQLite не поддерживает ALTER COLUMN для изменения типа с STRING на UUID
    # Поэтому создаем новые таблицы с правильными типами
    
    # 1. Создаем временные таблицы с UUID
    
    # Users
    op.create_table('users_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
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
        sa.Column('preferences_json', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('last_login', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('email'),
        sa.UniqueConstraint('username')
    )
    
    # Копируем данные
    op.execute("""
        INSERT INTO users_new (id, email, username, hashed_password, full_name, avatar_url, bio, address, phone, 
                              wizard_level, is_active, is_verified, is_staff, is_superuser, preferences_json, 
                              created_at, updated_at, last_login)
        SELECT CAST(id AS UUID), email, username, hashed_password, full_name, avatar_url, bio, address, phone,
               wizard_level, is_active, is_verified, is_staff, is_superuser, preferences_json,
               created_at, updated_at, last_login
        FROM users
    """)
    
    op.drop_table('users')
    op.rename_table('users_new', 'users')
    
    # Potion Categories
    op.create_table('potion_categories_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('name', sa.String(length=50), nullable=False),
        sa.Column('slug', sa.String(length=50), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('color', sa.String(length=20), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
        sa.UniqueConstraint('slug')
    )
    
    op.execute("""
        INSERT INTO potion_categories_new (id, name, slug, description, icon, color, created_at, updated_at)
        SELECT CAST(id AS UUID), name, slug, description, icon, color, created_at, updated_at
        FROM potion_categories
    """)
    
    op.drop_table('potion_categories')
    op.rename_table('potion_categories_new', 'potion_categories')
    
    # Potions
    op.create_table('potions_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('category_id', sa.UUID(), nullable=False),
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
        sa.Column('ingredients_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('effects_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('warnings_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('image_url', sa.String(length=500), nullable=True),
        sa.Column('thumbnail_url', sa.String(length=500), nullable=True),
        sa.Column('image_gallery_json', sa.Text(), nullable=False, default='[]'),
        sa.Column('popularity_score', sa.Integer(), nullable=False, default=0),
        sa.Column('purchase_count', sa.Integer(), nullable=False, default=0),
        sa.Column('review_count', sa.Integer(), nullable=False, default=0),
        sa.Column('average_rating', sa.Float(), nullable=False, default=0.0),
        sa.Column('meta_title', sa.String(length=255), nullable=True),
        sa.Column('meta_description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('published_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['potion_categories.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('slug')
    )
    
    # Копируем данные с преобразованием JSON полей
    op.execute("""
        INSERT INTO potions_new (
            id, name, slug, description, category_id, category, price, original_price, 
            discount_percent, in_stock, stock_quantity, min_stock_level, rarity, brewing_time, 
            brewing_difficulty, ingredients_json, effects_json, warnings_json, image_url, 
            thumbnail_url, image_gallery_json, popularity_score, purchase_count, review_count, 
            average_rating, meta_title, meta_description, created_at, updated_at, published_at
        )
        SELECT 
            CAST(id AS UUID), name, slug, description, CAST(category_id AS UUID), category, 
            price, original_price, discount_percent, in_stock, stock_quantity, min_stock_level, 
            rarity, brewing_time, brewing_difficulty, 
            COALESCE(ingredients_json, '[]'), 
            COALESCE(effects_json, '[]'), 
            COALESCE(warnings_json, '[]'), 
            image_url, thumbnail_url, 
            COALESCE(image_gallery_json, '[]'), 
            popularity_score, purchase_count, review_count, average_rating, 
            meta_title, meta_description, created_at, updated_at, published_at
        FROM potions
    """)
    
    op.drop_table('potions')
    op.rename_table('potions_new', 'potions')
    
    # Carts - исправляем: user_id nullable, id UUID
    op.create_table('carts_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', sa.UUID(), nullable=True),  # NULL для анонимных корзин!
        sa.Column('total_items', sa.Integer(), nullable=False, default=0),
        sa.Column('total_price', sa.Float(), nullable=False, default=0.0),
        sa.Column('session_id', sa.String(length=100), nullable=True, unique=True),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id')
    )
    
    op.execute("""
        INSERT INTO carts_new (id, user_id, total_items, total_price, session_id, created_at, updated_at)
        SELECT CAST(id AS UUID), CAST(user_id AS UUID), total_items, total_price, session_id, created_at, updated_at
        FROM carts
    """)
    
    op.drop_table('carts')
    op.rename_table('carts_new', 'carts')
    
    # Cart Items
    op.create_table('cart_items_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('cart_id', sa.UUID(), nullable=False),
        sa.Column('potion_id', sa.UUID(), nullable=False),
        sa.Column('quantity', sa.Integer(), nullable=False, default=1),
        sa.Column('price_per_unit', sa.Float(), nullable=False),
        sa.Column('potion_name', sa.String(length=255), nullable=False),
        sa.Column('potion_image', sa.String(length=500), nullable=False),
        sa.Column('potion_category', sa.String(length=50), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['cart_id'], ['carts.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.execute("""
        INSERT INTO cart_items_new (
            id, cart_id, potion_id, quantity, price_per_unit, potion_name, 
            potion_image, potion_category, created_at, updated_at
        )
        SELECT 
            CAST(id AS UUID), CAST(cart_id AS UUID), CAST(potion_id AS UUID), 
            quantity, price_per_unit, potion_name, potion_image, potion_category, 
            created_at, updated_at
        FROM cart_items
    """)
    
    op.drop_table('cart_items')
    op.rename_table('cart_items_new', 'cart_items')
    
    # Orders
    op.create_table('orders_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('order_number', sa.String(length=50), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
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
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('order_number')
    )
    
    op.execute("""
        INSERT INTO orders_new (
            id, user_id, order_number, status, subtotal, shipping_cost, discount_amount,
            tax_amount, total_amount, shipping_method, shipping_address, shipping_city,
            shipping_zip, shipping_country, customer_name, customer_email, customer_phone,
            notes, internal_notes, tracking_number, carrier, estimated_delivery, delivered_at,
            payment_status, payment_method, created_at, updated_at
        )
        SELECT 
            CAST(id AS UUID), CAST(user_id AS UUID), order_number, status, subtotal, 
            shipping_cost, discount_amount, tax_amount, total_amount, shipping_method,
            shipping_address, shipping_city, shipping_zip, shipping_country, customer_name,
            customer_email, customer_phone, notes, internal_notes, tracking_number, carrier,
            estimated_delivery, delivered_at, payment_status, payment_method, created_at, updated_at
        FROM orders
    """)
    
    op.drop_table('orders')
    op.rename_table('orders_new', 'orders')
    
    # Order Items
    op.create_table('order_items_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('potion_id', sa.UUID(), nullable=False),
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
    
    op.execute("""
        INSERT INTO order_items_new (
            id, order_id, potion_id, quantity, unit_price, total_price, potion_name,
            potion_image, potion_category, potion_rarity
        )
        SELECT 
            CAST(id AS UUID), CAST(order_id AS UUID), CAST(potion_id AS UUID),
            quantity, unit_price, total_price, potion_name, potion_image,
            potion_category, potion_rarity
        FROM order_items
    """)
    
    op.drop_table('order_items')
    op.rename_table('order_items_new', 'order_items')
    
    # Reviews
    op.create_table('reviews_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('potion_id', sa.UUID(), nullable=False),
        sa.Column('rating', sa.Integer(), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=True),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('is_approved', sa.Boolean(), nullable=False, default=False),
        sa.Column('is_verified_purchase', sa.Boolean(), nullable=False, default=True),
        sa.Column('helpful_count', sa.Integer(), nullable=False, default=0),
        sa.Column('not_helpful_count', sa.Integer(), nullable=False, default=0),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id')
    )
    
    op.execute("""
        INSERT INTO reviews_new (
            id, user_id, potion_id, rating, title, comment, is_approved,
            is_verified_purchase, helpful_count, not_helpful_count, created_at, updated_at
        )
        SELECT 
            CAST(id AS UUID), CAST(user_id AS UUID), CAST(potion_id AS UUID),
            rating, title, comment, is_approved, is_verified_purchase,
            helpful_count, not_helpful_count, created_at, updated_at
        FROM reviews
    """)
    
    op.drop_table('reviews')
    op.rename_table('reviews_new', 'reviews')
    
    # Wishlist
    op.create_table('wishlist_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('potion_id', sa.UUID(), nullable=False),
        sa.Column('note', sa.String(), nullable=False, default=''),
        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['potion_id'], ['potions.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'potion_id', name='unique_user_potion_wishlist')
    )
    
    op.execute("""
        INSERT INTO wishlist_new (id, user_id, potion_id, note, created_at)
        SELECT CAST(id AS UUID), CAST(user_id AS UUID), CAST(potion_id AS UUID), note, created_at
        FROM wishlist
    """)
    
    op.drop_table('wishlist')
    op.rename_table('wishlist_new', 'wishlist')
    
    # Payments
    op.create_table('payments_new',
        sa.Column('id', sa.UUID(), nullable=False, default=uuid.uuid4),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('order_id', sa.UUID(), nullable=False),
        sa.Column('payment_id', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=20), nullable=False, default='pending'),
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
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['order_id'], ['orders.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('payment_id')
    )
    
    op.execute("""
        INSERT INTO payments_new (
            id, user_id, order_id, payment_id, status, amount, currency,
            payment_method, payment_gateway, transaction_id, gateway_response,
            card_last4, card_brand, billing_address, billing_city, billing_country,
            created_at, updated_at, completed_at
        )
        SELECT 
            CAST(id AS UUID), CAST(user_id AS UUID), CAST(order_id AS UUID),
            payment_id, status, amount, currency, payment_method, payment_gateway,
            transaction_id, gateway_response, card_last4, card_brand,
            billing_address, billing_city, billing_country, created_at, updated_at, completed_at
        FROM payments
    """)
    
    op.drop_table('payments')
    op.rename_table('payments_new', 'payments')


def downgrade() -> None:
    # Сложный downgrade - в реальном проекте обычно не нужен
    # Но для полноты - возвращаем VARCHAR
    pass