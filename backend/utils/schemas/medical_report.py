from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class MedicalReportBase(BaseModel):
    """体检报告基础模型"""
    report_date: datetime = Field(..., description="体检日期")
    hospital: Optional[str] = Field(None, description="体检医院")
    report_summary: Optional[str] = Field(None, description="报告摘要")
    abnormal_items: Optional[List[Dict[str, Any]]] = Field(None, description="异常项目")
    normal_items: Optional[List[str]] = Field(None, description="正常项目")
    doctor_advice: Optional[str] = Field(None, description="医生建议")
    attachments: Optional[List[str]] = Field(None, description="报告附件URL列表")
    metadata: Optional[Dict[str, Any]] = Field(None, description="额外信息")


class MedicalReportCreate(MedicalReportBase):
    """体检报告创建模型"""
    user_id: int = Field(..., description="用户ID")

    class Config:
        json_schema_extra = {
            "example": {
                "user_id": 1,
                "report_date": "2023-10-01T09:00:00Z",
                "hospital": "健康体检中心",
                "report_summary": "基本健康，建议加强运动",
                "abnormal_items": [
                    {
                        "item_name": "体重",
                        "value": "75kg",
                        "reference_range": "55-70kg",
                        "description": "超重"
                    }
                ],
                "normal_items": ["血常规", "尿常规", "肝功能", "肾功能"],
                "doctor_advice": "建议控制饮食，加强有氧运动",
                "attachments": ["https://example.com/reports/1.pdf"]
            }
        }


class MedicalReportResponse(MedicalReportBase):
    """体检报告响应模型"""
    id: int = Field(..., description="报告ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1,
                "report_date": "2023-10-01T09:00:00Z",
                "hospital": "健康体检中心",
                "report_summary": "基本健康，建议加强运动",
                "abnormal_items": [
                    {
                        "item_name": "体重",
                        "value": "75kg",
                        "reference_range": "55-70kg",
                        "description": "超重"
                    }
                ],
                "normal_items": ["血常规", "尿常规", "肝功能", "肾功能"],
                "doctor_advice": "建议控制饮食，加强有氧运动",
                "attachments": ["https://example.com/reports/1.pdf"],
                "created_at": "2023-10-15T10:30:00Z",
                "updated_at": "2023-10-15T11:00:00Z"
            }
        }