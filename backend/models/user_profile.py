from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class UserPortrait(Base):
    """
    用户画像模型
    """
    __tablename__ = "user_portraits"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 基本信息
    basic_info = Column(JSON, nullable=True)  # 存储基本信息，如姓名、年龄、性别等
    
    # 健康史
    health_history = Column(JSON, nullable=True)  # 存储健康史信息
    
    # 生活习惯
    lifestyle = Column(JSON, nullable=True)  # 存储生活习惯信息
    
    # 不适症状
    symptoms = Column(JSON, nullable=True)  # 存储症状信息
    
    # 历史体检报告
    medical_reports = Column(JSON, nullable=True)  # 存储体检报告信息
    
    # 重点关注
    focus_areas = Column(JSON, nullable=True)  # 存储重点关注领域
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    user = relationship("User", back_populates="user_portrait")


class SymptomKnowledge(Base):
    """
    症状知识库模型
    """
    __tablename__ = "symptom_knowledge"

    id = Column(Integer, primary_key=True, index=True)
    symptom = Column(String(100), nullable=False, index=True)  # 症状名称
    
    # 追问问题集合
    follow_up_questions = Column(JSON, nullable=False)  # 存储追问问题列表
    
    # 症状分类
    category = Column(String(50), nullable=True)  # 症状分类，如"头部症状"、"消化系统症状"等
    
    # 相关检查项目
    related_examinations = Column(JSON, nullable=True)  # 相关检查项目列表
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class ConversationHistory(Base):
    """
    对话历史模型
    """
    __tablename__ = "conversation_history"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # 对话内容
    message = Column(Text, nullable=False)  # 消息内容
    sender = Column(String(20), nullable=False)  # 发送者：user或ai
    
    # 流程状态
    main_step = Column(String(50), nullable=True)  # 主流程步骤
    sub_step = Column(Integer, nullable=True)  # 子流程步骤
    is_ai_sub_process = Column(String(10), default=False)  # 是否在AI动态子流程中
    
    # 处理结果
    extracted_entities = Column(JSON, nullable=True)  # 提取的实体
    response_data = Column(JSON, nullable=True)  # 响应数据
    
    # 时间戳
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # 关联用户
    user = relationship("User")


class UserFlowState(Base):
    """
    用户流程状态模型
    """
    __tablename__ = "user_flow_states"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # 当前流程状态
    current_main_step = Column(String(50), nullable=False)  # 当前主流程步骤
    current_sub_step = Column(Integer, default=0)  # 当前子流程步骤
    is_ai_sub_process = Column(String(10), default=False)  # 是否在AI动态子流程中
    
    # 临时数据
    temp_data = Column(JSON, nullable=True)  # 临时存储的数据
    
    # 创建时间和更新时间
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联用户
    user = relationship("User")