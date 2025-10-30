from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta

from utils.database import get_db
from schemas import user_schemas
from services import user_service
from utils.security import create_access_token, get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES
from utils.error_handler import handle_exceptions

router = APIRouter(
    prefix="/auth",
    tags=["认证管理"],
)

@router.post("/token", response_model=user_schemas.Token)
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    """
    用户登录接口，使用OAuth2密码模式
    - **username**: 用户名
    - **password**: 密码
    """
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="用户名或密码错误",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer", "user_id": user.id, "username": user.username}

@router.post("/register", response_model=user_schemas.UserResponse)
@handle_exceptions
async def register(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    - **username**: 用户名
    - **email**: 邮箱地址
    - **password**: 密码
    """
    # 这里可以复用 user_router 中的注册逻辑
    # 或者直接调用 user_service
    user = await user_service.create_user(db, user_data)
    return user_schemas.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at
    )