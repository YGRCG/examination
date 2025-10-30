from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class PackageBase(BaseModel):
    """套餐基础模型"""
    name: str = Field(..., min_length=1, max_length=200, description="套餐名称")
    description: Optional[str] = Field(None, description="套餐描述")
    price: float = Field(..., gt=0, description="套餐价格")
    duration: int = Field(..., gt=0, description="体检预计时长（分钟）")
    items: List[str] = Field(default_factory=list, description="体检项目列表")
    suitable_for: List[str] = Field(default_factory=list, description="适合人群")
    is_active: bool = Field(default=True, description="是否激活")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外信息")


class PackageCreate(PackageBase):
    """套餐创建模型"""
    class Config:
        json_schema_extra = {
            "example": {
                "name": "基础体检套餐",
                "description": "适合一般健康检查的基础套餐",
                "price": 299.0,
                "duration": 60,
                "items": ["血常规", "尿常规", "肝功能", "肾功能", "胸片", "心电图"],
                "suitable_for": ["健康人群", "年度体检"],
                "is_active": True
            }
        }


class PackageUpdate(BaseModel):
    """套餐更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="套餐名称")
    description: Optional[str] = Field(None, description="套餐描述")
    price: Optional[float] = Field(None, gt=0, description="套餐价格")
    duration: Optional[int] = Field(None, gt=0, description="体检预计时长（分钟）")
    items: Optional[List[str]] = Field(None, description="体检项目列表")
    suitable_for: Optional[List[str]] = Field(None, description="适合人群")
    is_active: Optional[bool] = Field(None, description="是否激活")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外信息")


class PackageResponse(PackageBase):
    """套餐响应模型"""
    id: int = Field(..., description="套餐ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "基础体检套餐",
                "description": "适合一般健康检查的基础套餐",
                "price": 299.0,
                "duration": 60,
                "items": ["血常规", "尿常规", "肝功能", "肾功能", "胸片", "心电图"],
                "suitable_for": ["健康人群", "年度体检"],
                "is_active": True,
                "created_at": "2023-10-15T10:30:00Z",
                "updated_at": "2023-10-15T11:00:00Z"
            }
        }