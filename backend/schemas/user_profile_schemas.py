from pydantic import BaseModel, Field
from typing import Optional, Dict, List, Any, Union
from datetime import datetime


class BasicInfo(BaseModel):
    """
    基本信息模型
    """
    name: Optional[str] = Field(None, description="姓名")
    age: Optional[int] = Field(None, description="年龄")
    gender: Optional[str] = Field(None, description="性别")
    height: Optional[float] = Field(None, description="身高(cm)")
    weight: Optional[float] = Field(None, description="体重(kg)")
    occupation: Optional[str] = Field(None, description="职业")
    phone: Optional[str] = Field(None, description="联系电话")
    email: Optional[str] = Field(None, description="邮箱")


class HealthHistory(BaseModel):
    """
    健康史模型
    """
    disease_name: Optional[str] = Field(None, description="疾病名称")
    diagnosis_date: Optional[str] = Field(None, description="诊断日期")
    treatment_status: Optional[str] = Field(None, description="治疗状态")
    medication: Optional[List[str]] = Field(None, description="用药情况")


class Lifestyle(BaseModel):
    """
    生活习惯模型
    """
    smoking: Optional[str] = Field(None, description="吸烟情况")
    drinking: Optional[str] = Field(None, description="饮酒情况")
    exercise_frequency: Optional[str] = Field(None, description="运动频率")
    diet_habits: Optional[str] = Field(None, description="饮食习惯")
    sleep_pattern: Optional[str] = Field(None, description="睡眠模式")
    work_stress: Optional[str] = Field(None, description="工作压力")


class Symptom(BaseModel):
    """
    症状模型
    """
    symptom_name: str = Field(..., description="症状名称")
    symptom_type: Optional[str] = Field(None, description="症状类型")
    frequency: Optional[str] = Field(None, description="发生频率")
    duration: Optional[str] = Field(None, description="持续时间")
    triggers: Optional[str] = Field(None, description="诱因")
    severity: Optional[str] = Field(None, description="严重程度")
    additional_info: Optional[str] = Field(None, description="补充信息")


class MedicalReport(BaseModel):
    """
    体检报告模型
    """
    report_date: Optional[str] = Field(None, description="报告日期")
    institution: Optional[str] = Field(None, description="体检机构")
    abnormal_items: Optional[List[Dict[str, Any]]] = Field(None, description="异常项目")
    summary: Optional[str] = Field(None, description="报告摘要")


class FocusArea(BaseModel):
    """
    重点关注模型
    """
    area_name: str = Field(..., description="关注领域")
    reason: Optional[str] = Field(None, description="关注原因")
    priority: Optional[str] = Field(None, description="优先级")


class UserProfileCreate(BaseModel):
    """
    用户画像创建模型
    """
    user_id: int = Field(..., description="用户ID")
    basic_info: Optional[Dict[str, Any]] = Field(None, description="基本信息")
    health_history: Optional[List[Dict[str, Any]]] = Field(None, description="健康史")
    lifestyle: Optional[Dict[str, Any]] = Field(None, description="生活习惯")
    symptoms: Optional[List[Dict[str, Any]]] = Field(None, description="症状")
    medical_reports: Optional[List[Dict[str, Any]]] = Field(None, description="体检报告")
    focus_areas: Optional[List[Dict[str, Any]]] = Field(None, description="重点关注")


class UserProfileUpdate(BaseModel):
    """
    用户画像更新模型
    """
    basic_info: Optional[Dict[str, Any]] = Field(None, description="基本信息")
    health_history: Optional[List[Dict[str, Any]]] = Field(None, description="健康史")
    lifestyle: Optional[Dict[str, Any]] = Field(None, description="生活习惯")
    symptoms: Optional[List[Dict[str, Any]]] = Field(None, description="症状")
    medical_reports: Optional[List[Dict[str, Any]]] = Field(None, description="体检报告")
    focus_areas: Optional[List[Dict[str, Any]]] = Field(None, description="重点关注")


class UserProfileResponse(BaseModel):
    """
    用户画像响应模型
    """
    id: int = Field(..., description="画像ID")
    user_id: int = Field(..., description="用户ID")
    basic_info: Optional[Dict[str, Any]] = Field(None, description="基本信息")
    health_history: Optional[List[Dict[str, Any]]] = Field(None, description="健康史")
    lifestyle: Optional[Dict[str, Any]] = Field(None, description="生活习惯")
    symptoms: Optional[List[Dict[str, Any]]] = Field(None, description="症状")
    medical_reports: Optional[List[Dict[str, Any]]] = Field(None, description="体检报告")
    focus_areas: Optional[List[Dict[str, Any]]] = Field(None, description="重点关注")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class SymptomKnowledgeCreate(BaseModel):
    """
    症状知识库创建模型
    """
    symptom: str = Field(..., description="症状名称")
    follow_up_questions: List[Dict[str, Any]] = Field(..., description="追问问题列表")
    category: Optional[str] = Field(None, description="症状分类")
    related_examinations: Optional[List[str]] = Field(None, description="相关检查项目")


class SymptomKnowledgeResponse(BaseModel):
    """
    症状知识库响应模型
    """
    id: int = Field(..., description="知识ID")
    symptom: str = Field(..., description="症状名称")
    follow_up_questions: List[Dict[str, Any]] = Field(..., description="追问问题列表")
    category: Optional[str] = Field(None, description="症状分类")
    related_examinations: Optional[List[str]] = Field(None, description="相关检查项目")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ConversationMessage(BaseModel):
    """
    对话消息模型
    """
    id: int = Field(..., description="消息ID")
    user_id: int = Field(..., description="用户ID")
    message: str = Field(..., description="消息内容")
    sender: str = Field(..., description="发送者")
    main_step: Optional[str] = Field(None, description="主流程步骤")
    sub_step: Optional[int] = Field(None, description="子流程步骤")
    is_ai_sub_process: Optional[bool] = Field(None, description="是否在AI动态子流程中")
    extracted_entities: Optional[Dict[str, Any]] = Field(None, description="提取的实体")
    created_at: datetime = Field(..., description="创建时间")


class UserFlowStateCreate(BaseModel):
    """
    用户流程状态创建模型
    """
    user_id: int = Field(..., description="用户ID")
    current_main_step: str = Field(..., description="当前主流程步骤")
    current_sub_step: int = Field(0, description="当前子流程步骤")
    is_ai_sub_process: bool = Field(False, description="是否在AI动态子流程中")
    temp_data: Optional[Dict[str, Any]] = Field(None, description="临时数据")


class UserFlowStateUpdate(BaseModel):
    """
    用户流程状态更新模型
    """
    current_main_step: Optional[str] = Field(None, description="当前主流程步骤")
    current_sub_step: Optional[int] = Field(None, description="当前子流程步骤")
    is_ai_sub_process: Optional[bool] = Field(None, description="是否在AI动态子流程中")
    temp_data: Optional[Dict[str, Any]] = Field(None, description="临时数据")


class UserFlowStateResponse(BaseModel):
    """
    用户流程状态响应模型
    """
    id: int = Field(..., description="状态ID")
    user_id: int = Field(..., description="用户ID")
    current_main_step: str = Field(..., description="当前主流程步骤")
    current_sub_step: int = Field(..., description="当前子流程步骤")
    is_ai_sub_process: bool = Field(..., description="是否在AI动态子流程中")
    temp_data: Optional[Dict[str, Any]] = Field(None, description="临时数据")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class UserProfileProcessRequest(BaseModel):
    """
    用户画像处理请求模型
    """
    main_step: str = Field(..., description="主流程步骤")
    sub_step: int = Field(..., description="子流程步骤")
    is_ai_sub_process: bool = Field(..., description="是否在AI动态子流程中")
    user_input: str = Field(..., description="用户输入")
    current_profile: Dict[str, Any] = Field(..., description="当前用户画像数据")


class UserProfileProcessResponse(BaseModel):
    """
    用户画像处理响应模型
    """
    message: str = Field(..., description="AI回复消息")
    step_type: str = Field(..., description="下一步类型：text或multiple-choice")
    options: Optional[List[Dict[str, str]]] = Field(None, description="选项列表")
    next_step: Union[str, int] = Field(..., description="下一步：next_main、ai_sub_process、数字或complete")
    profile_update: Optional[Dict[str, Any]] = Field(None, description="用户画像更新数据")
    extracted_entities: Optional[Dict[str, Any]] = Field(None, description="提取的实体")


class UserProfileSaveRequest(BaseModel):
    """
    用户画像保存请求模型
    """
    basic_info: Optional[Dict[str, Any]] = Field(None, description="基本信息")
    health_history: Optional[List[Dict[str, Any]]] = Field(None, description="健康史")
    lifestyle: Optional[Dict[str, Any]] = Field(None, description="生活习惯")
    symptoms: Optional[List[Dict[str, Any]]] = Field(None, description="症状")
    medical_reports: Optional[List[Dict[str, Any]]] = Field(None, description="体检报告")
    focus_areas: Optional[List[Dict[str, Any]]] = Field(None, description="重点关注")


class UserProfileSaveResponse(BaseModel):
    """
    用户画像保存响应模型
    """
    success: bool = Field(..., description="保存是否成功")
    message: str = Field(..., description="响应消息")
    user_id: int = Field(..., description="用户ID")


class UserProfileInitializeRequest(BaseModel):
    """
    用户画像初始化请求模型
    """
    pass  # 初始化请求不需要任何字段，用户ID从认证中获取


class UserProfileInitializeResponse(BaseModel):
    """
    用户画像初始化响应模型
    """
    message: str = Field(..., description="初始欢迎消息")
    step_type: str = Field(..., description="第一步类型：text或multiple-choice")
    options: Optional[List[Dict[str, str]]] = Field(None, description="选项列表")


class UserProfileResponse(BaseModel):
    """用户画像响应模型"""
    user_id: int
    basic_info: Optional[Dict[str, Any]] = None
    health_history: Optional[List[Dict[str, Any]]] = None
    lifestyle: Optional[Dict[str, Any]] = None
    symptoms: Optional[List[Dict[str, Any]]] = None
    medical_reports: Optional[List[Dict[str, Any]]] = None
    focus_areas: Optional[List[Dict[str, Any]]] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class SymptomExtraction(BaseModel):
    """
    症状提取模型
    """
    symptom: str = Field(..., description="症状名称")
    frequency: Optional[str] = Field(None, description="频率")
    duration: Optional[str] = Field(None, description="持续时间")
    severity: Optional[str] = Field(None, description="严重程度")
    context: str = Field(..., description="上下文")


class SymptomFollowUp(BaseModel):
    """
    症状追问模型
    """
    question: str = Field(..., description="问题")
    key: str = Field(..., description="问题键")
    options: Optional[List[str]] = Field(None, description="选项")


class NLUExtractedEntity(BaseModel):
    """
    NLU提取实体模型
    """
    entity_type: str = Field(..., description="实体类型")
    entity_value: str = Field(..., description="实体值")
    confidence: float = Field(..., description="置信度")
    start_pos: Optional[int] = Field(None, description="开始位置")
    end_pos: Optional[int] = Field(None, description="结束位置")


class NLUResponse(BaseModel):
    """
    NLU响应模型
    """
    text: str = Field(..., description="原始文本")
    entities: List[NLUExtractedEntity] = Field(..., description="提取的实体")
    intent: Optional[str] = Field(None, description="意图")
    confidence: float = Field(..., description="整体置信度")