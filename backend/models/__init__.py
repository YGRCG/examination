# 导入基础模型
from .base import Base

# 导入用户相关模型
from .user import User, UserProfile

# 导入用户画像相关模型
from .user_profile import UserPortrait, SymptomKnowledge, ConversationHistory, UserFlowState

# 导入体检相关模型
from .examination import (
    ExaminationItem, 
    UserExaminationItem, 
    ExaminationRecord, 
    ExaminationResult,
    ExaminationPackage
)

# 导入健康相关模型
from .health import HealthInfo, HealthMetric, UserSymptom

# 导入推荐相关模型
from .recommendation import (
    Recommendation, 
    UserHealthProfile, 
    RecommendedPackage, 
    PackageItem
)

# 导入报告相关模型
from .report import (
    MedicalReport, 
    ExaminationReport, 
    ReportInterpretation
)

# 导入预约相关模型
from .appointment import Appointment

# 导入交互相关模型
from .interaction import Interaction, QuestionnaireProgress

# 导出所有模型
__all__ = [
    # 基础模型
    "Base",
    
    # 用户相关模型
    "User",
    "UserProfile",
    
    # 用户画像相关模型
    "UserPortrait",
    "SymptomKnowledge",
    "ConversationHistory",
    "UserFlowState",
    
    # 体检相关模型
    "ExaminationItem",
    "UserExaminationItem",
    "ExaminationRecord",
    "ExaminationResult",
    "ExaminationPackage",
    
    # 健康相关模型
    "HealthInfo",
    "HealthMetric",
    "UserSymptom",
    
    # 推荐相关模型
    "Recommendation",
    "UserHealthProfile",
    "RecommendedPackage",
    "PackageItem",
    
    # 报告相关模型
    "MedicalReport",
    "ExaminationReport",
    "ReportInterpretation",
    
    # 预约相关模型
    "Appointment",
    
    # 交互相关模型
    "Interaction",
    "QuestionnaireProgress",
]