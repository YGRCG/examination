from sqlalchemy.orm import Session
from pydantic import EmailStr
from passlib.context import CryptContext
import logging

from models import User
from schemas import user_schemas
from utils.error_handler import (
    CustomException,
    handle_database_error,
    log_error,
    db_transaction
)

# 密码哈希上下文
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

logger = logging.getLogger("app.services.user")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    验证密码是否匹配
    :param plain_password: 明文密码
    :param hashed_password: 哈希密码
    :return: 密码是否匹配
    """
    try:
        return pwd_context.verify(plain_password, hashed_password)
    except Exception as e:
        log_error("PasswordVerificationError", f"密码验证失败: {str(e)}")
        return False

def get_password_hash(password: str) -> str:
    """
    生成密码哈希
    :param password: 明文密码
    :return: 密码哈希
    """
    try:
        return pwd_context.hash(password)
    except Exception as e:
        log_error("PasswordHashingError", f"密码哈希生成失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="密码处理失败",
            error_type="PasswordProcessingError"
        )


async def create_user(
    db: Session,
    user_data: user_schemas.UserCreate
) -> User:
    """
    创建新用户
    :param db: 数据库会话
    :param user_data: 用户创建数据
    :return: 创建的用户对象
    """
    try:
        # 检查用户名是否已存在
        existing_user = db.query(User).filter(User.username == user_data.username).first()
        if existing_user:
            raise CustomException(
                status_code=400,
                message="用户名已被使用",
                error_type="UsernameAlreadyExists"
            )
        
        # 检查邮箱是否已存在
        existing_email = db.query(User).filter(User.email == user_data.email).first()
        if existing_email:
            raise CustomException(
                status_code=400,
                message="邮箱已被使用",
                error_type="EmailAlreadyExists"
            )
        
        # 生成密码哈希
        password_hash = get_password_hash(user_data.password)
        
        # 创建用户对象
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            password_hash=password_hash,
        )
        
        # 添加到数据库
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        logger.info(f"用户创建成功: {db_user.username} (ID: {db_user.id})")
        return db_user
        
    except CustomException as e:
        # 重新抛出自定义异常，让上层处理
        raise
    except Exception as e:
        # 处理其他异常
        handle_database_error(db, e)
        # 添加更详细的日志记录
        log_error("UserCreationError", f"创建用户失败: {str(e)}", exc_info=True)
        logger.error(f"详细错误信息: {type(e).__name__}: {str(e)}")
        logger.error(f"用户数据: username={user_data.username}, email={user_data.email}")
        raise CustomException(
            status_code=500,
            message="创建用户失败，请稍后重试",
            error_type="UserCreationError"
        )


async def get_user_by_username(db: Session, username: str) -> User:
    """
    根据用户名获取用户
    :param db: 数据库会话
    :param username: 用户名
    :return: 用户对象或None
    """
    try:
        user = db.query(User).filter(User.username == username).first()
        return user
    except Exception as e:
        log_error("GetUserByUsernameError", f"根据用户名获取用户失败: {str(e)}")
        raise CustomException(
            status_code=500,
            message="获取用户信息失败",
            error_type="DatabaseQueryError"
        )


async def update_user_profile(
    db: Session,
    user_id: int,
    profile_data: user_schemas.UserProfileUpdate
) -> User:
    """
    更新用户资料
    :param db: 数据库会话
    :param user_id: 用户ID
    :param profile_data: 用户资料更新数据
    :return: 更新后的用户对象
    """
    try:
        # 在事务中执行更新操作
        async with db_transaction(db):
            # 查找用户
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 更新用户资料
            update_data = profile_data.dict(exclude_unset=True)
            for key, value in update_data.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            
            # 如果有邮箱更新，检查新邮箱是否已被使用
            if "email" in update_data:
                existing_email = db.query(User).filter(
                    User.email == update_data["email"],
                    User.id != user_id
                ).first()
                if existing_email:
                    raise CustomException(
                        status_code=400,
                        message="邮箱已被使用",
                        error_type="EmailAlreadyExists"
                    )
            
            # 如果有密码更新，生成新的密码哈希
            if "password" in update_data:
                user.password_hash = get_password_hash(update_data["password"])
                # 删除密码字段，避免返回明文密码
                del update_data["password"]
            
            db.commit()
            db.refresh(user)
            
            logger.info(f"用户资料更新成功: {user.username} (ID: {user.id})")
            return user
            
    except CustomException as e:
        # 重新抛出自定义异常
        raise
    except Exception as e:
        # 处理其他异常
        handle_database_error(db, e)
        log_error("UpdateUserProfileError", f"更新用户资料失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="更新用户资料失败，请稍后重试",
            error_type="UserUpdateError"
        )


async def delete_user(db: Session, user_id: int) -> bool:
    """
    删除用户
    :param db: 数据库会话
    :param user_id: 用户ID
    :return: 是否删除成功
    """
    try:
        # 在事务中执行删除操作
        async with db_transaction(db):
            # 查找用户
            user = db.query(User).filter(User.id == user_id).first()
            if not user:
                raise CustomException(
                    status_code=404,
                    message="用户不存在",
                    error_type="UserNotFound"
                )
            
            # 删除用户
            db.delete(user)
            db.commit()
            
            logger.info(f"用户删除成功: {user.username} (ID: {user.id})")
            return True
            
    except CustomException as e:
        # 重新抛出自定义异常
        raise
    except Exception as e:
        # 处理其他异常
        handle_database_error(db, e)
        log_error("DeleteUserError", f"删除用户失败: {str(e)}", exc_info=True)
        raise CustomException(
            status_code=500,
            message="删除用户失败，请稍后重试",
            error_type="UserDeleteError"
        )


async def authenticate_user(db: Session, username: str, password: str) -> User or None:
    """
    验证用户身份
    :param db: 数据库会话
    :param username: 用户名
    :param password: 密码
    :return: 验证成功的用户对象或None
    """
    try:
        # 获取用户
        user = await get_user_by_username(db, username)
        if not user:
            return None
        
        # 验证密码
        if not verify_password(password, user.password_hash):
            return None
        
        return user
    except Exception as e:
        log_error("UserAuthenticationError", f"用户认证失败: {str(e)}")
        return None