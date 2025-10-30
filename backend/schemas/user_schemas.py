from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """
    用户基础模型
    """
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="用户邮箱")


class UserCreate(UserBase):
    """
    用户创建模型
    """
    password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="用户密码，至少6位"
    )


class UserProfileUpdate(BaseModel):
    """
    用户资料更新模型
    """
    username: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=50, 
        description="用户名"
    )
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    password: Optional[str] = Field(
        None, 
        min_length=6, 
        max_length=100, 
        description="用户密码，至少6位"
    )


class UserResponse(UserBase):
    """
    用户响应模型
    """
    id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """
    用户登录模型
    """
    username: str = Field(..., description="用户名")
    password: str = Field(..., description="用户密码")


class Token(BaseModel):
    """
    JWT令牌模型
    """
    access_token: str = Field(..., description="访问令牌")
    token_type: str = Field(..., description="令牌类型")
    user_id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")


class TokenData(BaseModel):
    """
    令牌数据模型
    """
    username: Optional[str] = None


class PasswordReset(BaseModel):
    """
    密码重置模型
    """
    email: EmailStr = Field(..., description="用户邮箱")
    new_password: str = Field(
        ...,
        min_length=6,
        max_length=100,
        description="新密码，至少6位"
    )
    confirm_password: str = Field(
        ...,
        description="确认新密码"
    )

    def check_password_match(self):
        """
        检查两次输入的密码是否匹配
        """
        if self.new_password != self.confirm_password:
            raise ValueError("两次输入的密码不匹配")


class ApiResponse(BaseModel):
    """
    API统一响应模型
    """
    status: str = Field(..., description="请求状态")
    message: str = Field(..., description="状态消息")
    data: Optional[dict] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")

    @classmethod
    def success(cls, message: str = "操作成功", data: dict = None) -> "ApiResponse":
        """
        创建成功响应
        """
        return cls(status="success", message=message, data=data)

    @classmethod
    def error(cls, message: str = "操作失败", error_code: str = None, data: dict = None) -> "ApiResponse":
        """
        创建错误响应
        """
        return cls(status="error", message=message, error_code=error_code, data=data)