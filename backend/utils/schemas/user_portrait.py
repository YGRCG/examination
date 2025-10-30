from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional
from datetime import datetime


class QuestionnaireProgressResponse(BaseModel):
    """问卷进度响应模型"""
    current_step: str = Field(..., description="当前步骤")
    completed_steps: List[str] = Field(default_factory=list, description="已完成步骤列表")
    current_state: str = Field(default="normal", description="当前状态：normal 或 symptom_dynamic")

    class Config:
        json_schema_extra = {
            "example": {
                "current_step": "lifestyle",
                "completed_steps": ["basic_info", "health_history"],
                "current_state": "normal"
            }
        }


class StepRequest(BaseModel):
    """步骤处理请求模型"""
    step: str = Field(..., description="步骤名称")
    data: Dict[str, Any] = Field(..., description="步骤数据")

    class Config:
        json_schema_extra = {
            "example": {
                "step": "basic_info",
                "data": {
                    "age": 35,
                    "gender": "male",
                    "height": 175,
                    "weight": 70
                }
            }
        }


class StepResponse(BaseModel):
    """步骤处理响应模型"""
    next_action: str = Field(..., description="下一步动作：next_step, dynamic_question, complete")
    next_step: Optional[str] = Field(None, description="下一个主流程步骤")
    question: Optional[str] = Field(None, description="动态追问的问题")
    step: Optional[str] = Field(None, description="当前步骤")
    completed_steps: Optional[List[str]] = Field(None, description="已完成步骤列表")
    message: Optional[str] = Field(None, description="提示信息")
    portrait_id: Optional[int] = Field(None, description="用户画像ID")

    class Config:
        json_schema_extra = {
            "example": {
                "next_action": "next_step",
                "next_step": "lifestyle",
                "completed_steps": ["basic_info", "health_history"]
            }
        }


class DynamicQuestionRequest(BaseModel):
    """动态追问请求模型"""
    answer: str = Field(..., description="用户对动态问题的回答")

    class Config:
        json_schema_extra = {
            "example": {
                "answer": "是眩晕，感觉天旋地转"
            }
        }


class DynamicQuestionResponse(BaseModel):
    """动态追问响应模型"""
    next_action: str = Field(..., description="下一步动作：dynamic_question, next_step")
    question: Optional[str] = Field(None, description="下一个动态问题")
    next_step: Optional[str] = Field(None, description="下一个主流程步骤")
    step: Optional[str] = Field(None, description="当前步骤")
    completed_steps: Optional[List[str]] = Field(None, description="已完成步骤列表")

    class Config:
        json_schema_extra = {
            "example": {
                "next_action": "dynamic_question",
                "question": "这种情况持续多久了？",
                "step": "symptoms"
            }
        }


class SkipResponse(BaseModel):
    """跳过步骤响应模型"""
    next_action: str = Field(..., description="下一步动作：next_step, complete")
    next_step: Optional[str] = Field(None, description="下一个主流程步骤")
    completed_steps: List[str] = Field(default_factory=list, description="已完成步骤列表")
    message: Optional[str] = Field(None, description="提示信息")
    portrait_id: Optional[int] = Field(None, description="用户画像ID")

    class Config:
        json_schema_extra = {
            "example": {
                "next_action": "next_step",
                "next_step": "symptoms",
                "completed_steps": ["basic_info", "health_history", "lifestyle"]
            }
        }


class ResetResponse(BaseModel):
    """重置流程响应模型"""
    next_action: str = Field(..., description="下一步动作：reset")
    message: str = Field(..., description="提示信息")
    next_step: str = Field(..., description="重置后的起始步骤")

    class Config:
        json_schema_extra = {
            "example": {
                "next_action": "reset",
                "message": "流程已重置",
                "next_step": "basic_info"
            }
        }


class UserPortraitBase(BaseModel):
    """用户画像基础模型"""
    health_risk: str = Field(..., description="健康风险等级：低风险、中风险、高风险")
    recommended_frequency: str = Field(..., description="推荐体检频率")


class UserPortraitCreate(UserPortraitBase):
    """创建用户画像模型"""
    user_id: int = Field(..., description="用户ID")


class UserPortraitResponse(UserPortraitBase):
    """用户画像响应模型"""
    id: int = Field(..., description="用户画像ID")
    user_id: int = Field(..., description="用户ID")
    generated_at: datetime = Field(..., description="生成时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1001,
                "health_risk": "中风险",
                "recommended_frequency": "每年一次",
                "generated_at": "2023-10-15T10:30:00Z"
            }
        }


class UserSymptomBase(BaseModel):
    """用户症状基础模型"""
    symptom_name: str = Field(..., description="症状名称")
    frequency: Optional[str] = Field(None, description="频率")
    symptom_type: Optional[str] = Field(None, description="症状类型")
    duration: Optional[str] = Field(None, description="持续时间")
    triggers: Optional[str] = Field(None, description="诱发因素")
    severity: Optional[str] = Field(None, description="严重程度")
    additional_info: Optional[Dict[str, Any]] = Field(None, description="额外信息")


class UserSymptomCreate(UserSymptomBase):
    """创建用户症状模型"""
    user_id: int = Field(..., description="用户ID")


class UserSymptomResponse(UserSymptomBase):
    """用户症状响应模型"""
    id: int = Field(..., description="症状记录ID")
    user_id: int = Field(..., description="用户ID")
    created_at: datetime = Field(..., description="创建时间")

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "user_id": 1001,
                "symptom_name": "头晕",
                "frequency": "经常",
                "symptom_type": "眩晕",
                "duration": "两周",
                "triggers": "起床时",
                "severity": "中等",
                "additional_info": {},
                "created_at": "2023-10-15T10:30:00Z"
            }
        }


class HealthInfoBase(BaseModel):
    """健康信息基础模型"""
    # 这里可以根据需要添加健康信息相关字段
    pass


class HealthHistoryBase(BaseModel):
    """健康史基础模型"""
    chronic_diseases: List[str] = Field(default_factory=list, description="慢性疾病史")
    allergies: List[str] = Field(default_factory=list, description="过敏史")
    surgeries: List[str] = Field(default_factory=list, description="手术史")
    family_medical_history: List[str] = Field(default_factory=list, description="家族病史")

    class Config:
        json_schema_extra = {
            "example": {
                "chronic_diseases": ["高血压"],
                "allergies": ["青霉素"],
                "surgeries": ["阑尾切除"],
                "family_medical_history": ["糖尿病"]
            }
        }


class LifestyleBase(BaseModel):
    """生活习惯基础模型"""
    smoking: bool = Field(default=False, description="是否吸烟")
    alcohol: bool = Field(default=False, description="是否饮酒")
    exercise_frequency: str = Field(default="偶尔", description="运动频率：很少、偶尔、经常、每天")
    sleep_hours: float = Field(default=7.0, description="平均睡眠时间")
    diet_preference: str = Field(default="均衡", description="饮食偏好")

    class Config:
        json_schema_extra = {
            "example": {
                "smoking": False,
                "alcohol": True,
                "exercise_frequency": "偶尔",
                "sleep_hours": 7.5,
                "diet_preference": "清淡"
            }
        }


class SymptomsBase(BaseModel):
    """症状信息基础模型"""
    has_symptoms: bool = Field(default=False, description="是否有不适症状")
    description: Optional[str] = Field(None, description="症状描述")

    class Config:
        json_schema_extra = {
            "example": {
                "has_symptoms": True,
                "description": "最近经常头晕，特别是起床时"
            }
        }


class ConcernsBase(BaseModel):
    """重点关注基础模型"""
    health_concerns: List[str] = Field(default_factory=list, description="健康关注点")
    preferred_checkup_items: List[str] = Field(default_factory=list, description="偏好的体检项目")

    class Config:
        json_schema_extra = {
            "example": {
                "health_concerns": ["心脏健康", "血压"],
                "preferred_checkup_items": ["心电图", "血压监测"]
            }
        }