from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Float, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


def get_current_time():
    """
    获取当前时间，用于默认值
    """
    return datetime.now()


class Recommendation(Base):
    """
    推荐表模型
    """
    __tablename__ = "recommendations"
    
    id = Column(Integer, primary_key=True, index=True, comment="推荐ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    based_on_record_id = Column(Integer, ForeignKey("examination_records.id"), nullable=True, comment="基于的体检记录ID")
    recommended_items = Column(JSON, nullable=False, comment="推荐项目列表")
    reason = Column(String(1000), nullable=True, comment="推荐理由")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="recommendations")


class UserHealthProfile(Base):
    """
    用户健康画像表模型
    """
    __tablename__ = "user_health_profiles"
    
    id = Column(Integer, primary_key=True, index=True, comment="画像ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, comment="用户ID")
    health_risk = Column(String(20), nullable=False, default="低风险", comment="健康风险")
    recommended_frequency = Column(String(50), nullable=False, default="每年一次", comment="推荐频率")
    generated_at = Column(DateTime, default=get_current_time, comment="生成时间")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的一对一关系
    user = relationship("User", back_populates="user_health_profile")


class RecommendedPackage(Base):
    """
    推荐套餐表模型
    """
    __tablename__ = "recommended_packages"
    
    id = Column(Integer, primary_key=True, index=True, comment="套餐ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="用户ID")
    name = Column(String(100), nullable=False, comment="套餐名称")
    description = Column(String(500), nullable=True, comment="套餐描述")
    total_price = Column(Float, nullable=False, comment="套餐总价")
    recommended_reason = Column(String(1000), nullable=True, comment="推荐理由")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, comment="更新时间")
    
    # 关系：与用户表的多对一关系
    user = relationship("User", back_populates="recommended_packages")
    
    # 关系：一个套餐可以有多个项目
    package_items = relationship("PackageItem", back_populates="package", cascade="all, delete-orphan")


class PackageItem(Base):
    """
    套餐项目表模型
    """
    __tablename__ = "package_items"
    
    id = Column(Integer, primary_key=True, index=True, comment="套餐项目ID")
    package_id = Column(Integer, ForeignKey("recommended_packages.id"), nullable=False, comment="套餐ID")
    item_id = Column(Integer, ForeignKey("examination_items.id"), nullable=False, comment="体检项目ID")
    item_name = Column(String(100), nullable=False, comment="项目名称")
    item_price = Column(Float, nullable=False, comment="项目价格")
    created_at = Column(DateTime, default=get_current_time, comment="创建时间")
    
    # 关系：与推荐套餐表的多对一关系
    package = relationship("RecommendedPackage", back_populates="package_items")
    
    # 关系：与体检项目表的多对一关系
    examination_item = relationship("ExaminationItem")