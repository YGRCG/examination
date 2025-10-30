from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class HealthInfoBase(BaseModel):
    """健康信息基础模型"""
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    gender: Optional[str] = Field(None, pattern="^(male|female)$", description="性别")
    height: Optional[float] = Field(None, gt=0, description="身高（cm）")
    weight: Optional[float] = Field(None, gt=0, description="体重（kg）")
    blood_type: Optional[str] = Field(None, pattern="^[A|B|AB|O][+-]?$", description="血型")
    blood_pressure: Optional[str] = Field(None, description="血压")
    heart_rate: Optional[int] = Field(None, gt=0, description="心率")
    allergies: Optional[List[str]] = Field(default_factory=list, description="过敏史")
    chronic_diseases: Optional[List[str]] = Field(default_factory=list, description="慢性疾病史")
    medication: Optional[List[str]] = Field(default_factory=list, description="用药情况")
    other_info: Optional[Dict[str, Any]] = Field(None, description="其他健康信息")


class HealthInfoCreate(HealthInfoBase):
    """健康信息创建模型"""
    user_id: int = Field(..., description="用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "age": 35,
                "gender": "male",
                "height": 175.0,
                "weight": 70.0,
                "blood_type": "A+",
                "blood_pressure": "120/80",
                "heart_rate": 72,
                "allergies": ["青霉素"],
                "chronic_diseases": [],
                "medication": []
            }
        }


class HealthInfoUpdate(HealthInfoBase):
    """健康信息更新模型"""
    pass


class HealthInfoResponse(HealthInfoBase):
    """健康信息响应模型"""
    id: int = Field(..., description="健康信息ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "age": 35,
                "gender": "male",
                "height": 175.0,
                "weight": 70.0,
                "blood_type": "A+",
                "blood_pressure": "120/80",
                "heart_rate": 72,
                "allergies": ["青霉素"],
                "chronic_diseases": [],
                "medication": [],
                "created_at": "2023-10-15T10:30:00Z"
            }
        }