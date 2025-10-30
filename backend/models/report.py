from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class MedicalReport(Base):
    """
    医疗报告表模型
    """
    __tablename__ = "medical_reports"
    
    id = Column(Integer, primary_key=True, index=True, comment="报告ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    examination_record_id = Column(Integer, ForeignKey("examination_records.id"), nullable=False, comment="体检记录ID")
    report_type = Column(String(50), nullable=False, comment="报告类型")
    title = Column(String(200), nullable=False, comment="报告标题")
    content = Column(String(5000), nullable=False, comment="报告内容")
    file_path = Column(String(500), nullable=True, comment="文件路径")
    is_final = Column(Boolean, default=False, comment="是否最终版本")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="medical_reports")
    
    # 关系：与体检记录表的多对一关系
    examination_record = relationship("ExaminationRecord", back_populates="medical_reports")


class ExaminationReport(Base):
    """
    体检报告表模型
    """
    __tablename__ = "examination_reports"
    
    id = Column(Integer, primary_key=True, index=True, comment="报告ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    examination_record_id = Column(Integer, ForeignKey("examination_records.id"), nullable=False, comment="体检记录ID")
    title = Column(String(200), nullable=False, comment="报告标题")
    summary = Column(String(1000), nullable=False, comment="报告摘要")
    content = Column(String(5000), nullable=False, comment="报告内容")
    file_path = Column(String(500), nullable=True, comment="文件路径")
    is_final = Column(Boolean, default=False, comment="是否最终版本")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="examination_reports")
    
    # 关系：与体检记录表的多对一关系
    examination_record = relationship("ExaminationRecord", back_populates="examination_reports")


class ReportInterpretation(Base):
    """
    报告解读表模型
    """
    __tablename__ = "report_interpretations"
    
    id = Column(Integer, primary_key=True, index=True, comment="解读ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    report_id = Column(Integer, nullable=False, comment="报告ID")
    report_type = Column(String(50), nullable=False, comment="报告类型")
    interpretation = Column(String(2000), nullable=False, comment="解读内容")
    ai_interpretation = Column(String(2000), nullable=True, comment="AI解读内容")
    doctor_interpretation = Column(String(2000), nullable=True, comment="医生解读内容")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="report_interpretations")