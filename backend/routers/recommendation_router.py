from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import Optional, List, Dict, Any

from utils.database import get_db
from utils.security import get_current_user
from services import recommendation_service
from schemas import user_schemas
from utils.error_handler import handle_exceptions, CustomException

router = APIRouter(
    prefix="/recommendations",
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

@router.post("/create", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def create_recommendation(
    request: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    创建推荐记录接口
    - **portraits_id**: 用户画像ID
    - **recommended_package_id**: 推荐套餐ID
    - **recommendation_reason**: 推荐理由（可选）
    """
    # 验证请求参数
    portraits_id = request.get("portraits_id")
    recommended_package_id = request.get("recommended_package_id")
    recommendation_reason = request.get("recommendation_reason")
    
    if not portraits_id or not recommended_package_id:
        raise CustomException(
            status_code=400,
            message="用户画像ID和推荐套餐ID不能为空",
            error_type="InvalidParameters"
        )
    
    # 创建推荐记录
    recommendation = await recommendation_service.create_recommendation(
        db, current_user.id, portraits_id, recommended_package_id, recommendation_reason
    )
    
    # 构造响应数据
    response_data = {
        "id": recommendation.id,
        "user_id": recommendation.user_id,
        "portraits_id": recommendation.portraits_id,
        "recommended_package_id": recommendation.recommended_package_id,
        "recommendation_reason": recommendation.recommendation_reason,
        "recommended_at": recommendation.recommended_at,
        "created_at": recommendation.created_at,
        "updated_at": recommendation.updated_at
    }
    
    return user_schemas.ApiResponse(
        status="success",
        message="创建推荐记录成功",
        data=response_data
    )

@router.get("/list", response_model=user_schemas.ApiResponse)
@handle_exceptions
async def get_user_recommendations(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    获取用户推荐记录列表接口
    - **skip**: 跳过的记录数，默认0
    - **limit**: 返回的最大记录数，默认100
    """
    # 获取用户推荐记录
    recommendations = await recommendation_service.get_user_recommendations(
        db, current_user.id, skip, limit
    )
    
    # 构造响应数据
    response_data = []
    for recommendation in recommendations:
        response_data.append({
            "id": recommendation.id,
            "user_id": recommendation.user_id,
            "portraits_id": recommendation.portraits_id,
            "recommended_package_id": recommendation.recommended_package_id,
            "recommendation_reason": recommendation.recommendation_reason,
            "recommended_at": recommendation.recommended_at,
            "created_at": recommendation.created_at,
            "updated_at": recommendation.updated_at
        })
    
    return user_schemas.ApiResponse(
        status="success",
        message="获取用户推荐记录成功",
        data={
            "recommendations": response_data,
            "total": len(response_data),
            "skip": skip,
            "limit": limit
        }
    )