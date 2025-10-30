from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class Appointment(Base):
    """
    预约表模型
    """
    __tablename__ = "appointments"
    
    id = Column(Integer, primary_key=True, index=True, comment="预约ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    examination_center_id = Column(Integer, nullable=False, comment="体检中心ID")
    appointment_date = Column(DateTime, nullable=False, comment="预约日期")
    appointment_time = Column(String(20), nullable=False, comment="预约时间")
    status = Column(String(20), nullable=False, default="已预约", comment="预约状态")
    notes = Column(String(500), nullable=True, comment="备注")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="appointments")