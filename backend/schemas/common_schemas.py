from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime


class ApiResponse(BaseModel):
    """
    API通用响应模型
    """
    status: str = Field(..., description="响应状态：success 或 error")
    message: str = Field(..., description="响应消息")
    data: Optional[Any] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误码")


class StatusUpdate(BaseModel):
    """
    状态更新模型
    """
    is_active: bool = Field(..., description="是否激活/启用")


class AdminStatistics(BaseModel):
    """
    管理员统计信息模型
    """
    total_users: int = Field(..., description="总用户数")
    active_users: int = Field(..., description="活跃用户数")
    total_reports: int = Field(..., description="总报告数")
    pending_interpretations: int = Field(..., description="待解读报告数")
    total_appointments: int = Field(..., description="总预约数")
    system_stats: dict = Field(default_factory=dict, description="系统统计信息")
    period_start: Optional[datetime] = Field(None, description="统计开始时间")
    period_end: Optional[datetime] = Field(None, description="统计结束时间")


class PaginationParams(BaseModel):
    """
    分页参数模型
    """
    page: int = Field(1, ge=1, description="页码，从1开始")
    page_size: int = Field(10, ge=1, le=100, description="每页大小，1-100")


class PaginatedResponse(BaseModel):
    """
    分页响应模型
    """
    items: list = Field(..., description="当前页的数据列表")
    total: int = Field(..., description="总记录数")
    page: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_pages: int = Field(..., description="总页数")
    has_next: bool = Field(..., description="是否有下一页")
    has_prev: bool = Field(..., description="是否有上一页")