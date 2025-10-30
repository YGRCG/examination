from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class Interaction(Base):
    """
    交互记录表模型
    """
    __tablename__ = "interactions"
    
    id = Column(Integer, primary_key=True, index=True, comment="交互ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    interaction_type = Column(String(50), nullable=False, comment="交互类型")
    content = Column(String(1000), nullable=False, comment="交互内容")
    response = Column(String(1000), nullable=True, comment="回复内容")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="interactions")


class QuestionnaireProgress(Base):
    """
    问卷进度表模型
    """
    __tablename__ = "questionnaire_progress"
    
    id = Column(Integer, primary_key=True, index=True, comment="进度ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    questionnaire_id = Column(Integer, nullable=False, comment="问卷ID")
    questionnaire_name = Column(String(100), nullable=False, comment="问卷名称")
    total_questions = Column(Integer, nullable=False, comment="总题数")
    answered_questions = Column(Integer, nullable=False, default=0, comment="已答题数")
    is_completed = Column(Boolean, default=False, comment="是否完成")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="questionnaire_progress")