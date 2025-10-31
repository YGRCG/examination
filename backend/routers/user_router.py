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
    tags=["用户管理"],
)

@router.post("/register", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def register_user(user_data: user_schemas.UserCreate, db: Session = Depends(get_db)):
    """
    用户注册接口
    - **username**: 用户名
    - **email**: 邮箱地址
    - **password**: 密码
    """
    user = await user_service.create_user(db, user_data)
    user_response = user_schemas.UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        created_at=user.created_at,
        updated_at=user.updated_at
    )
    return user_schemas.ApiResponse(
        status="success",
        message="用户注册成功",
        data=user_response.model_dump()
    )

@router.post("/login", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """
    用户登录接口
    - **username**: 用户名
    - **password**: 密码
    """
    user = await user_service.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "status": "error",
                "message": "用户名或密码错误",
                "error_code": "INVALID_CREDENTIALS"
            },
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username},
        expires_delta=access_token_expires
    )
    token_response = user_schemas.Token(
        access_token=access_token,
        token_type="bearer"
    )
    return user_schemas.ApiResponse(
        status="success",
        message="登录成功",
        data=token_response
    )

@router.post("/reset-password", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def reset_password(
    reset_data: user_schemas.PasswordReset,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    重置密码接口
    - **current_password**: 当前密码
    - **new_password**: 新密码
    """
    # 验证当前密码
    if not user_service.verify_password(reset_data.current_password, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "status": "error",
                "message": "当前密码错误",
                "error_code": "INVALID_CURRENT_PASSWORD"
            }
        )
    # 更新密码
    await user_service.update_user_profile(
        db, 
        current_user.id, 
        user_schemas.UserProfileUpdate(password=reset_data.new_password)
    )
    return user_schemas.ApiResponse(
        status="success",
        message="密码重置成功"
    )

@router.get("/profile", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_user_profile(current_user = Depends(get_current_user)):
    """
    获取用户个人信息接口
    """
    user_response = user_schemas.UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        created_at=current_user.created_at,
        updated_at=current_user.updated_at
    )
    return user_schemas.ApiResponse(
        status="success",
        message="获取用户信息成功",
        data=user_response.model_dump()
    )

@router.put("/profile", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def update_user_profile(
    profile_data: user_schemas.UserProfileUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    更新用户个人信息接口
    - **email**: 邮箱地址（可选）
    - **password**: 密码（可选）
    """
    updated_user = await user_service.update_user_profile(db, current_user.id, profile_data)
    user_response = user_schemas.UserResponse(
        id=updated_user.id,
        username=updated_user.username,
        email=updated_user.email,
        created_at=updated_user.created_at,
        updated_at=updated_user.updated_at
    )
    return user_schemas.ApiResponse(
        status="success",
        message="用户信息更新成功",
        data=user_response.model_dump()
    )