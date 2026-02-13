from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from sqlalchemy.exc import IntegrityError
from jose import JWTError, jwt
from passlib.context import CryptContext
import uuid

from core.config import settings
from models.user import User
from schemas.user import UserCreate, UserUpdate, UserResponse, TokenData
from .base_service import BaseService


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class UserService(BaseService[User, UserCreate, UserUpdate, UserResponse]):
    def __init__(self):
        super().__init__(User, UserResponse)
    
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return pwd_context.verify(plain_password, hashed_password)
    
    @staticmethod
    def get_password_hash(password: str) -> str:
        """Generate password hash."""
        return pwd_context.hash(password)
    
    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """Create JWT access token."""
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        to_encode.update({"exp": expire, "type": "access"})
        encoded_jwt = jwt.encode(
            to_encode, 
            settings.SECRET_KEY, 
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def create_refresh_token(data: Dict[str, Any]) -> str:
        """Create JWT refresh token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
        to_encode.update({"exp": expire, "type": "refresh"})
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        return encoded_jwt
    
    @staticmethod
    def verify_token(token: str) -> Optional[TokenData]:
        """Verify and decode JWT token."""
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            user_id = payload.get("sub")
            email = payload.get("email")
            token_type = payload.get("type")
            
            if user_id is None or email is None or token_type != "access":
                return None
            
            return TokenData(
                user_id=uuid.UUID(user_id),
                email=email,
                exp=payload.get("exp")
            )
        except (JWTError, ValueError):
            return None
    
    async def authenticate_user(
        self, 
        session: AsyncSession, 
        email: str, 
        password: str
    ) -> Optional[User]:
        """Authenticate user by email and password."""
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return None
        if not self.verify_password(password, user.hashed_password):
            return None
        
        # Update last login
        user.last_login = datetime.utcnow()
        await session.commit()
        
        return user
    
    async def create(self, session: AsyncSession, obj_in: UserCreate) -> UserResponse:
        """Create new user with hashed password."""
        try:
            # Check if user exists
            query = select(User).where(
                (User.email == obj_in.email) | (User.username == obj_in.username)
            )
            result = await session.execute(query)
            existing_user = result.scalar_one_or_none()
            
            if existing_user:
                raise ValueError("User with this email or username already exists")
            
            # Create user
            hashed_password = self.get_password_hash(obj_in.password)
            user_data = obj_in.model_dump(exclude={"password"})
            user_data["hashed_password"] = hashed_password
            
            # Create user
            user = User(**user_data)
            session.add(user)
            await session.commit()
            await session.refresh(user)
            
            return self._model_to_schema(user)
        except IntegrityError as e:
            await session.rollback()
            raise ValueError("Database integrity error") from e
    
    async def get_by_email(self, session: AsyncSession, email: str) -> Optional[UserResponse]:
        """Get user by email."""
        query = select(User).where(User.email == email)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            return self._model_to_schema(user)
        return None
    
    async def get_by_username(self, session: AsyncSession, username: str) -> Optional[UserResponse]:
        """Get user by username."""
        query = select(User).where(User.username == username)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            return self._model_to_schema(user)
        return None
    
    async def update_last_login(self, session: AsyncSession, user_id: uuid.UUID) -> None:
        """Update user's last login time."""
        query = (
            update(User)
            .where(User.id == user_id)
            .values(last_login=datetime.utcnow())
        )
        await session.execute(query)
        await session.commit()
    
    async def change_password(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID, 
        current_password: str, 
        new_password: str
    ) -> bool:
        """Change user password."""
        # Get user
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if not user:
            return False
        
        # Verify current password
        if not self.verify_password(current_password, user.hashed_password):
            return False
        
        # Update password
        user.hashed_password = self.get_password_hash(new_password)
        await session.commit()
        
        return True
    
    async def deactivate_account(self, session: AsyncSession, user_id: uuid.UUID) -> bool:
        """Deactivate user account."""
        query = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=False)
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
    
    async def activate_account(self, session: AsyncSession, user_id: uuid.UUID) -> bool:
        """Activate user account."""
        query = (
            update(User)
            .where(User.id == user_id)
            .values(is_active=True)
        )
        result = await session.execute(query)
        await session.commit()
        
        return result.rowcount > 0
    
    async def get_with_orders(
        self, 
        session: AsyncSession, 
        user_id: uuid.UUID
    ) -> Optional[UserResponse]:
        """Get user with orders preloaded."""
        query = (
            select(User)
            .where(User.id == user_id)
            .options(selectinload(User.orders))
        )
        result = await session.execute(query)
        user = result.scalar_one_or_none()
        
        if user:
            return self._model_to_schema(user)
        return None


user_service = UserService()