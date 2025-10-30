from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class AppointmentBase(BaseModel):
    """预约基础模型"""
    package_id: int = Field(..., description="套餐ID")
    appointment_time: datetime = Field(..., description="预约时间")
    status: str = Field(default="pending", description="预约状态：pending, confirmed, completed, cancelled")
    notes: Optional[str] = Field(None, description="备注")

    @validator('status')
    def validate_status(cls, v):
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"状态必须是以下之一: {', '.join(valid_statuses)}")
        return v


class AppointmentCreate(AppointmentBase):
    """预约创建模型"""
    user_id: int = Field(..., description="用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "package_id": 1,
                "appointment_time": "2023-11-01T09:00:00Z",
                "notes": "需要提前半小时到"
            }
        }


class AppointmentUpdate(BaseModel):
    """预约更新模型"""
    package_id: Optional[int] = Field(None, description="套餐ID")
    appointment_time: Optional[datetime] = Field(None, description="预约时间")
    status: Optional[str] = Field(None, description="预约状态")
    notes: Optional[str] = Field(None, description="备注")

    @validator('status')
    def validate_status(cls, v):
        if v is None:
            return v
        valid_statuses = ['pending', 'confirmed', 'completed', 'cancelled']
        if v not in valid_statuses:
            raise ValueError(f"状态必须是以下之一: {', '.join(valid_statuses)}")
        return v


class AppointmentResponse(AppointmentBase):
    """预约响应模型"""
    id: int = Field(..., description="预约ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "package_id": 1,
                "appointment_time": "2023-11-01T09:00:00Z",
                "status": "confirmed",
                "notes": "需要提前半小时到",
                "created_at": "2023-10-15T10:30:00Z",
                "updated_at": "2023-10-15T11:00:00Z"
            }
        }