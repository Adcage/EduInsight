"""
系统日志模块Schema

包含系统日志、通知相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from enum import Enum
from app.schemas.base_schemas import CamelCaseModel


# ==================== 枚举 ====================

class NotificationTypeEnum(str, Enum):
    """通知类型枚举"""
    SYSTEM = 'system'
    ATTENDANCE = 'attendance'
    GRADE = 'grade'
    WARNING = 'warning'


class NotificationPriorityEnum(int, Enum):
    """通知优先级枚举"""
    NORMAL = 0
    IMPORTANT = 1
    URGENT = 2


# ==================== 系统日志 Schema ====================

class SystemLogCreateModel(CamelCaseModel):
    """系统日志创建模型"""
    user_id: Optional[int] = Field(None, description="用户ID", ge=1)
    action: str = Field(..., description="操作", max_length=50)
    module: str = Field(..., description="模块", max_length=50)
    ip_address: Optional[str] = Field(None, description="IP地址", max_length=50)
    user_agent: Optional[str] = Field(None, description="User Agent", max_length=255)
    request_data: Optional[dict] = Field(None, description="请求数据")
    response_status: Optional[int] = Field(None, description="响应状态码")
    error_message: Optional[str] = Field(None, description="错误信息")


class SystemLogResponseModel(CamelCaseModel):
    """系统日志响应模型"""
    id: int = Field(..., description="日志ID")
    user_id: Optional[int] = Field(None, description="用户ID")
    action: str = Field(..., description="操作")
    module: str = Field(..., description="模块")
    ip_address: Optional[str] = Field(None, description="IP地址")
    user_agent: Optional[str] = Field(None, description="User Agent")
    request_data: Optional[dict] = Field(None, description="请求数据")
    response_status: Optional[int] = Field(None, description="响应状态码")
    error_message: Optional[str] = Field(None, description="错误信息")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class SystemLogDetailResponseModel(SystemLogResponseModel):
    """系统日志详情响应模型"""
    user_name: Optional[str] = Field(None, description="用户姓名")


class SystemLogListResponseModel(CamelCaseModel):
    """系统日志列表响应模型"""
    logs: List[SystemLogDetailResponseModel] = Field(..., description="日志列表")
    total: int = Field(..., description="日志总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")


class SystemLogQueryModel(CamelCaseModel):
    """系统日志查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    user_id: Optional[int] = Field(None, description="用户ID筛选", ge=1)
    action: Optional[str] = Field(None, description="操作筛选", max_length=50)
    module: Optional[str] = Field(None, description="模块筛选", max_length=50)
    ip_address: Optional[str] = Field(None, description="IP地址筛选", max_length=50)
    error_only: bool = Field(False, description="只显示错误日志")


class SystemLogPathModel(CamelCaseModel):
    """系统日志路径参数模型"""
    log_id: int = Field(..., description="日志ID", ge=1)


# ==================== 通知 Schema ====================

class NotificationCreateModel(CamelCaseModel):
    """通知创建模型"""
    user_id: int = Field(..., description="接收者ID", ge=1)
    type: NotificationTypeEnum = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题", min_length=1, max_length=100)
    content: str = Field(..., description="通知内容", min_length=1)
    link: Optional[str] = Field(None, description="跳转链接", max_length=255)
    priority: int = Field(0, description="优先级(0:普通,1:重要,2:紧急)", ge=0, le=2)
    
    @validator('content')
    def validate_content(cls, v):
        """验证内容"""
        if len(v) > 1000:
            raise ValueError('通知内容不能超过1000字')
        return v.strip()


class NotificationBatchCreateModel(CamelCaseModel):
    """批量通知创建模型"""
    user_ids: List[int] = Field(..., description="接收者ID列表", min_items=1)
    type: NotificationTypeEnum = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题", min_length=1, max_length=100)
    content: str = Field(..., description="通知内容", min_length=1)
    link: Optional[str] = Field(None, description="跳转链接", max_length=255)
    priority: int = Field(0, description="优先级", ge=0, le=2)


class NotificationUpdateModel(CamelCaseModel):
    """通知更新模型"""
    is_read: bool = Field(..., description="是否已读")


class NotificationResponseModel(CamelCaseModel):
    """通知响应模型"""
    id: int = Field(..., description="通知ID")
    user_id: int = Field(..., description="接收者ID")
    type: str = Field(..., description="通知类型")
    title: str = Field(..., description="通知标题")
    content: str = Field(..., description="通知内容")
    link: Optional[str] = Field(None, description="跳转链接")
    is_read: bool = Field(..., description="是否已读")
    priority: int = Field(..., description="优先级")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class NotificationListResponseModel(CamelCaseModel):
    """通知列表响应模型"""
    notifications: List[NotificationResponseModel] = Field(..., description="通知列表")
    total: int = Field(..., description="通知总数")
    unread_count: int = Field(0, description="未读数量")


class NotificationQueryModel(CamelCaseModel):
    """通知查询参数模型"""
    is_read: Optional[bool] = Field(None, description="是否已读筛选")
    type: Optional[NotificationTypeEnum] = Field(None, description="通知类型筛选")
    priority: Optional[int] = Field(None, description="优先级筛选", ge=0, le=2)
    limit: int = Field(50, description="返回数量", ge=1, le=100)


class NotificationPathModel(CamelCaseModel):
    """通知路径参数模型"""
    notification_id: int = Field(..., description="通知ID", ge=1)


class NotificationStatsModel(CamelCaseModel):
    """通知统计模型"""
    total_notifications: int = Field(..., description="通知总数")
    unread_count: int = Field(..., description="未读数量")
    by_type: dict = Field(..., description="按类型统计")
    by_priority: dict = Field(..., description="按优先级统计")
    recent_notifications: List[NotificationResponseModel] = Field(..., description="最近通知")
