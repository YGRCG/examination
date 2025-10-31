from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON, text
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class ExaminationItem(Base):
    """
    体检项目表模型
    """
    __tablename__ = "examination_items"
    
    id = Column(Integer, primary_key=True, index=True, comment="项目ID")
    name = Column(String(100), nullable=False, comment="项目名称")
    description = Column(String(500), nullable=True, comment="项目描述")
    category = Column(String(50), nullable=False, comment="项目类别")
    price = Column(Float, nullable=False, comment="项目价格")
    duration = Column(Integer, nullable=True, comment="检查时长(分钟)")
    is_active = Column(Boolean, default=True, comment="是否启用")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：一个体检项目可以属于多个用户体检项目
    user_examination_items = relationship("UserExaminationItem", back_populates="examination_item")


class UserExaminationItem(Base):
    """
    用户体检项目关联表模型
    """
    __tablename__ = "user_examination_items"
    
    id = Column(Integer, primary_key=True, index=True, comment="关联ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    examination_item_id = Column(Integer, ForeignKey("examination_items.id"), nullable=False, comment="体检项目ID")
    status = Column(String(20), default="pending", comment="状态(pending/completed/recommended)")
    scheduled_at = Column(DateTime, nullable=True, comment="预约时间")
    completed_at = Column(DateTime, nullable=True, comment="完成时间")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="examination_items")
    
    # 关系：与体检项目表的多对一关系
    examination_item = relationship("ExaminationItem", back_populates="user_examination_items")


class ExaminationRecord(Base):
    """
    体检记录表模型
    """
    __tablename__ = "examination_records"
    
    id = Column(Integer, primary_key=True, index=True, comment="记录ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    record_date = Column(DateTime, default=get_current_time, comment="体检日期")
    doctor_id = Column(Integer, nullable=True, comment="医生ID")
    summary = Column(String(1000), nullable=True, comment="体检总结")
    status = Column(String(20), default="pending", comment="状态(pending/completed/reviewed)")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="examination_records")
    
    # 关系：一个体检记录可以有多个体检结果
    results = relationship("ExaminationResult", back_populates="record")
    
    # 关系：一个体检记录可以有多个医疗报告
    medical_reports = relationship("MedicalReport", back_populates="examination_record")
    
    # 关系：一个体检记录可以有多个体检报告
    examination_reports = relationship("ExaminationReport", back_populates="examination_record")


class ExaminationResult(Base):
    """
    体检结果表模型
    """
    __tablename__ = "examination_results"
    
    id = Column(Integer, primary_key=True, index=True, comment="结果ID")
    record_id = Column(Integer, ForeignKey("examination_records.id"), nullable=False, comment="体检记录ID")
    examination_item_id = Column(Integer, ForeignKey("examination_items.id"), nullable=False, comment="体检项目ID")
    result_value = Column(String(255), nullable=False, comment="结果值")
    reference_range = Column(String(255), nullable=True, comment="参考范围")
    is_abnormal = Column(Boolean, default=False, comment="是否异常")
    comments = Column(String(500), nullable=True, comment="医生备注")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与体检记录表的多对一关系
    record = relationship("ExaminationRecord", back_populates="results")


class ExaminationPackage(Base):
    """
    体检套餐表模型
    """
    __tablename__ = "examination_packages"
    
    id = Column(Integer, primary_key=True, index=True, comment="套餐ID")
    name = Column(String(100), nullable=False, comment="套餐名称")
    description = Column(String(1000), nullable=True, comment="套餐描述")
    price = Column(Float, nullable=False, comment="套餐价格")
    target_group = Column(String(100), nullable=True, comment="目标人群")
    recommended_frequency = Column(String(50), nullable=True, comment="推荐频率")
    created_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=True, comment="创建时间")
    updated_at = Column(DateTime, server_default=text('CURRENT_TIMESTAMP'), nullable=True, comment="更新时间")
    
    # 关系：一个套餐可以有多个推荐记录
    recommendations = relationship("Recommendation", back_populates="package")