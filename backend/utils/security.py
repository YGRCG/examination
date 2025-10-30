from datetime import datetime, timedelta
import jwt
import os
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from models import User
from utils.database import get_db
from utils.error_handler import log_error, CustomException

# 从环境变量中获取JWT配置
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# OAuth2密码流程的token URL
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

def create_access_token(data: dict, expires_delta: timedelta = None) -> str:
    """
    创建访问令牌
    :param data: 要包含在令牌中的数据
    :param expires_delta: 过期时间增量
    :return: JWT令牌
    """
    try:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt
    except Exception as e:
        log_error("JWTTokenCreationError", f"创建JWT令牌失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="认证令牌创建失败",
            error_type="TokenCreationError"
        )

def verify_token(token: str, credentials_exception: HTTPException) -> dict:
    """
    验证JWT令牌
    :param token: JWT令牌
    :param credentials_exception: 验证失败时抛出的异常
    :return: 令牌中的数据
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        return payload
    except jwt.PyJWTError:
        raise credentials_exception
    except Exception as e:
        log_error("JWTTokenVerificationError", f"验证JWT令牌失败: {str(e)}")
        raise credentials_exception

async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    """
    获取当前认证的用户
    :param token: JWT令牌
    :param db: 数据库会话
    :return: 用户对象
    """
    credentials_exception = HTTPException(
        status_code=401,
        detail={
            "status": "error",
            "message": "认证失败",
            "error_code": "UNAUTHORIZED"
        },
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = verify_token(token, credentials_exception)
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = db.query(User).filter(User.username == username).first()
        if user is None:
            raise credentials_exception
        return user
    except Exception as e:
        if isinstance(e, HTTPException):
            raise
        log_error("GetCurrentUserError", f"获取当前用户失败: {str(e)}")
        raise credentials_exception

async def get_current_admin_user(current_user: User = Depends(get_current_user)) -> User:
    """
    获取当前认证的管理员用户
    :param current_user: 当前认证的用户
    :return: 管理员用户对象
    """
    if not hasattr(current_user, 'is_admin') or not current_user.is_admin:
        raise HTTPException(
            status_code=403,
            detail={
                "status": "error",
                "message": "权限不足，需要管理员权限",
                "error_code": "FORBIDDEN"
            }
        )
    return current_user