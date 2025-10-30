from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class HealthInfo(Base):
    """
    健康信息表模型
    """
    __tablename__ = "health_infos"
    
    id = Column(Integer, primary_key=True, index=True, comment="健康信息ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, comment="用户ID")
    age = Column(Integer, nullable=True, comment="年龄")
    gender = Column(String(10), nullable=True, comment="性别")
    height = Column(Float, nullable=True, comment="身高")
    weight = Column(Float, nullable=True, comment="体重")
    blood_type = Column(String(5), nullable=True, comment="血型")
    allergies = Column(String(500), nullable=True, comment="过敏情况")
    chronic_diseases = Column(String(500), nullable=True, comment="慢性疾病")
    family_medical_history = Column(String(500), nullable=True, comment="家族病史")
    lifestyle = Column(String(500), nullable=True, comment="生活方式")
    last_examination_date = Column(DateTime, nullable=True, comment="上次体检日期")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的一对一关系
    user = relationship("User", back_populates="health_info")


class HealthMetric(Base):
    """
    健康指标表模型
    """
    __tablename__ = "health_metrics"
    
    id = Column(Integer, primary_key=True, index=True, comment="指标ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    metric_name = Column(String(50), nullable=False, comment="指标名称")
    metric_value = Column(Float, nullable=False, comment="指标值")
    metric_unit = Column(String(20), nullable=True, comment="指标单位")
    recorded_at = Column(DateTime, default=get_current_time, comment="记录时间")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="health_metrics")


class UserSymptom(Base):
    """
    用户症状表模型
    """
    __tablename__ = "user_symptoms"
    
    id = Column(Integer, primary_key=True, index=True, comment="症状ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    symptom_name = Column(String(100), nullable=False, comment="症状名称")
    frequency = Column(String(50), nullable=True, comment="频率")
    symptom_type = Column(String(100), nullable=True, comment="症状类型")
    duration = Column(String(100), nullable=True, comment="持续时间")
    triggers = Column(String(200), nullable=True, comment="诱发因素")
    severity = Column(String(50), nullable=True, comment="严重程度")
    additional_info = Column(JSON, nullable=True, comment="额外信息")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="symptoms")