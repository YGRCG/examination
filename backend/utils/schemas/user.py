from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    phone: Optional[str] = Field(None, pattern="^1[3-9]\d{9}$", description="手机号码")
    is_active: bool = Field(default=True, description="用户是否激活")


class UserCreate(UserBase):
    """用户创建模型"""
    password: str = Field(..., min_length=6, description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "password": "123456"
            }
        }


class UserUpdate(BaseModel):
    """用户更新模型"""
    username: Optional[str] = Field(None, min_length=3, max_length=50, description="用户名")
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    phone: Optional[str] = Field(None, pattern="^1[3-9]\d{9}$", description="手机号码")
    password: Optional[str] = Field(None, min_length=6, description="密码")
    is_active: Optional[bool] = Field(None, description="用户是否激活")


class UserResponse(UserBase):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "username": "张三",
                "email": "zhangsan@example.com",
                "phone": "13800138000",
                "is_active": True,
                "created_at": "2023-10-15T10:30:00Z"
            }
        }


class UserLogin(BaseModel):
    """用户登录模型"""
    email: EmailStr = Field(..., description="邮箱地址")
    password: str = Field(..., description="密码")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "zhangsan@example.com",
                "password": "123456"
            }
        }


class Token(BaseModel):
    """Token模型"""
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(default="bearer", description="令牌类型")

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer"
            }
        }


class TokenData(BaseModel):
    """Token数据模型"""
    user_id: Optional[int] = Field(None, description="用户ID")
    email: Optional[str] = Field(None, description="邮箱地址")