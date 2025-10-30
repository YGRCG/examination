from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import Optional, List

from utils.database import get_db
from utils.security import get_current_user
from services import recommendation_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions

router = APIRouter(
    prefix="/api/v1/recommendations",
    tags=["智能推荐"]
)

@router.get("/packages", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_recommended_packages(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取推荐体检套餐接口
    """
    packages = await recommendation_service.get_recommended_packages(db, current_user.id)
    
    # 构造响应数据
    response_data = []
    for package in packages:
        # 获取套餐中的项目
        package_items = []
        for item in package.items:
            package_items.append({
                "id": item.id,
                "item_id": item.item_id,
                "item_name": item.item_name,
                "item_price": item.item_price
            })
        
        package_data = {
            "id": package.id,
            "name": package.name,
            "description": package.description,
            "total_price": package.total_price,
            "recommended_reason": package.recommended_reason,
            "created_at": package.created_at,
            "updated_at": package.updated_at,
            "items": package_items
        }
        response_data.append(package_data)
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取推荐套餐成功",
        data=response_data
    )

@router.post("/packages/{package_id}/adjust", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def adjust_recommended_items(
    package_id: int,
    add_items: Optional[List[int]] = None,
    remove_items: Optional[List[int]] = None,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    调整推荐套餐项目接口
    - **package_id**: 套餐ID
    - **add_items**: 要添加的项目ID列表
    - **remove_items**: 要移除的项目ID列表
    """
    package = await recommendation_service.adjust_recommended_items(
        db, package_id, add_items, remove_items
    )
    
    # 检查套餐是否属于当前用户
    if package.user_id != current_user.id:
        raise CustomException(
            status_code=403,
            message="您无权修改此套餐",
            error_type="Forbidden"
        )
    
    # 构造响应数据
    package_items = []
    for item in package.items:
        package_items.append({
            "id": item.id,
            "item_id": item.item_id,
            "item_name": item.item_name,
            "item_price": item.item_price
        })
    
    response_data = {
        "id": package.id,
        "name": package.name,
        "description": package.description,
        "total_price": package.total_price,
        "recommended_reason": package.recommended_reason,
        "created_at": package.created_at,
        "updated_at": package.updated_at,
        "items": package_items
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="调整套餐项目成功",
        data=response_data
    )

@router.get("/items", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_examination_items(
    category: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取体检项目列表接口
    - **category**: 项目分类（可选）
    - **keyword**: 关键词搜索（可选）
    - **limit**: 返回的记录数量，默认50
    - **offset**: 偏移量，默认0
    """
    items = await recommendation_service.get_examination_items(
        db, category, keyword, limit, offset
    )
    
    # 构造响应数据
    response_data = []
    for item in items:
        response_data.append({
            "id": item.id,
            "name": item.name,
            "description": item.description,
            "category": item.category,
            "price": item.price,
            "duration": item.duration,
            "is_active": item.is_active
        })
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取体检项目列表成功",
        data={
            "items": response_data,
            "total": len(response_data),
            "limit": limit,
            "offset": offset
        }
    )