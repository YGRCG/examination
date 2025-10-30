from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from utils.database import get_db
from schemas import user_schemas, common_schemas
from models import User
from services import admin_service, user_service
from utils.security import get_current_user, get_current_admin_user

router = APIRouter(
    prefix="/api/v1/admin",
    tags=["管理员功能"],
)

@router.get("/users", response_model=List[user_schemas.UserResponse])
async def get_all_users(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取所有用户列表（管理员权限）
    """
    users = await admin_service.get_all_users(db, skip=skip, limit=limit)
    return users

@router.put("/users/{user_id}/status", response_model=user_schemas.UserResponse)
async def update_user_status(
    user_id: int,
    status_update: common_schemas.StatusUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    更新用户状态（启用/禁用）
    """
    user = await admin_service.update_user_status(db, user_id, status_update.is_active)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="用户不存在"
        )
    return user

@router.get("/statistics", response_model=common_schemas.AdminStatistics)
async def get_admin_statistics(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user)
):
    """
    获取管理员统计信息
    """
    stats = await admin_service.get_statistics(db)
    return stats