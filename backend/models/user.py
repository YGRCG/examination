from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class User(Base):
    """
    用户表模型
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True, comment="用户ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="邮箱")
    password_hash = Column(String(255), nullable=False, comment="密码哈希值")
    is_active = Column(Boolean, default=True, comment="用户是否激活")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：一个用户可以有一个用户资料
    profile = relationship("UserProfile", back_populates="user", uselist=False)
    
    # 关系：一个用户可以有多个体检记录
    examination_records = relationship("ExaminationRecord", back_populates="user")
    
    # 关系：一个用户可以有多个体检项目
    examination_items = relationship("UserExaminationItem", back_populates="user")
    
    # 关系：一个用户可以有多个推荐结果
    recommendations = relationship("Recommendation", back_populates="user")
    
    # 关系：一个用户可以有多个交互记录
    interactions = relationship("Interaction", back_populates="user")
    
    # 关系：一个用户可以有一个健康信息记录
    health_info = relationship("HealthInfo", back_populates="user", uselist=False)
    
    # 关系：一个用户可以有多个健康指标
    health_metrics = relationship("HealthMetric", back_populates="user")
    
    # 关系：一个用户可以有多个体检报告
    medical_reports = relationship("MedicalReport", back_populates="user")
    
    # 关系：一个用户可以有多个体检报告
    examination_reports = relationship("ExaminationReport", back_populates="user")
    
    # 关系：一个用户可以有多个报告解读
    report_interpretations = relationship("ReportInterpretation", back_populates="user")
    
    # 关系：一个用户可以有一个用户画像
    user_portrait = relationship("UserPortrait", back_populates="user", uselist=False)
    
    # 关系：一个用户可以有一个健康画像
    user_health_profile = relationship("UserHealthProfile", back_populates="user", uselist=False)
    
    # 关系：一个用户可以有多个推荐套餐
    recommended_packages = relationship("RecommendedPackage", back_populates="user")
    
    # 关系：一个用户可以有多个预约记录
    appointments = relationship("Appointment", back_populates="user")
    
    # 关系：一个用户可以有多个症状记录
    symptoms = relationship("UserSymptom", back_populates="user")
    
    # 关系：一个用户可以有一个问卷进度记录
    questionnaire_progress = relationship("QuestionnaireProgress", back_populates="user", uselist=False)


class UserProfile(Base):
    """
    用户资料表模型
    """
    __tablename__ = "user_profiles"
    
    id = Column(Integer, primary_key=True, index=True, comment="资料ID")
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False, comment="用户ID")
    full_name = Column(String(100), nullable=True, comment="姓名")
    gender = Column(String(10), nullable=True, comment="性别")
    age = Column(Integer, nullable=True, comment="年龄")
    height = Column(Integer, nullable=True, comment="身高")
    weight = Column(Integer, nullable=True, comment="体重")
    blood_type = Column(String(5), nullable=True, comment="血型")
    medical_history = Column(String(500), nullable=True, comment="病史")
    allergies = Column(String(500), nullable=True, comment="过敏史")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的一对一关系
    user = relationship("User", back_populates="profile")