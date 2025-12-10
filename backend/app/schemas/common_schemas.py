"""
通用响应模型和分页模型
"""
from typing import Optional, Any
from datetime import datetime
from pydantic import Field
from app.schemas.base_schemas import CamelCaseModel


class MessageResponseModel(CamelCaseModel):
    """消息响应模型"""
    message: str = Field(..., description="响应消息")


class BaseResponseModel(CamelCaseModel):
    """基础响应模型"""
    message: str = Field(..., description="响应消息")
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Any] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")


class MessageResponseModel(CamelCaseModel):
    """消息响应模型（用于简单的成功/失败响应）"""
    message: str = Field(..., description="响应消息")


class PaginationModel(CamelCaseModel):
    """分页模型"""
    page: int = Field(1, description="当前页码", ge=1)
    per_page: int = Field(10, description="每页数量", ge=1, le=100)
    total: int = Field(..., description="总记录数", ge=0)
    pages: int = Field(..., description="总页数", ge=0)
    has_prev: bool = Field(..., description="是否有上一页")
    has_next: bool = Field(..., description="是否有下一页")


class QueryModel(CamelCaseModel):
    """通用查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    course_id: Optional[int] = Field(None, description="课程ID")
    question_id: Optional[int] = Field(None, description="问题ID")
    status: Optional[str] = Field(None, description="状态")
    type: Optional[str] = Field(None, description="类型")
    limit: Optional[int] = Field(None, description="限制数量", ge=1, le=1000)
    minutes: Optional[int] = Field(10, description="最近N分钟", ge=1, le=1440)  # 最多24小时
    start_time: Optional[datetime] = Field(None, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
