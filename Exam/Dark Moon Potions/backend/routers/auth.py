from datetime import timedelta
from typing import Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession

from dependencies.database import get_db
from schemas.user import UserCreate, UserResponse, Token, UserLogin
from services.user_service import user_service

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    """
    Register new user.
    
    - **email**: User's email address
    - **username**: Unique username
    - **password**: Password (min 6 characters)
    - **wizard_level**: Magical expertise level (novice, apprentice, adept, master, archmage)
    """
    try:
        user = await user_service.create(db, user_data)
        return user
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=Token)
async def login(
    form_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    """
    Login user and get access token.
    
    - **email**: User's email
    - **password**: User's password
    """
    user = await user_service.authenticate_user(db, form_data.email, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create tokens
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = user_service.create_access_token(token_data)
    refresh_token = user_service.create_refresh_token(token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/login/form", response_model=Token)
async def login_form(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Login using OAuth2 form (for Swagger UI).
    """
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token_data = {"sub": str(user.id), "email": user.email}
    access_token = user_service.create_access_token(token_data)
    refresh_token = user_service.create_refresh_token(token_data)
    
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer"
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    refresh_token: str = Body(..., embed=True),
    db: AsyncSession = Depends(get_db)
):
    """
    Refresh access token using refresh token.
    """
    try:
        from jose import jwt
        from core.config import settings
        
        payload = jwt.decode(
            refresh_token,
            settings.secret_key,
            algorithms=[settings.algorithm]
        )
        
        token_type = payload.get("type")
        if token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token type"
            )
        
        user_id = payload.get("sub")
        email = payload.get("email")
        
        if not user_id or not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token"
            )
        
        # Verify user exists and is active
        user = await user_service.get(db, user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )
        
        # Create new tokens
        token_data = {"sub": str(user.id), "email": user.email}
        new_access_token = user_service.create_access_token(token_data)
        new_refresh_token = user_service.create_refresh_token(token_data)
        
        return Token(
            access_token=new_access_token,
            refresh_token=new_refresh_token,
            token_type="bearer"
        )
    
    except jwt.JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token"
        )


@router.post("/logout")
async def logout():
    """
    Logout user (client should delete tokens).
    In a real application, you might want to blacklist the token.
    """
    return {"message": "Successfully logged out"}