from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime

class BaseResponseModel(BaseModel):
    """基础响应模型"""
    message: str
    success: bool = True
    timestamp: datetime = datetime.utcnow()

class PaginationModel(BaseModel):
    """分页模型"""
    page: int = 1
    per_page: int = 10
    total: int
    pages: int
    has_prev: bool
    has_next: bool

class ErrorResponseModel(BaseModel):
    """错误响应模型"""
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    success: bool = False
    timestamp: datetime = datetime.utcnow()

class SuccessResponseModel(BaseModel):
    """成功响应模型"""
    message: str = "操作成功"
    data: Optional[Any] = None
    success: bool = True
    timestamp: datetime = datetime.utcnow()
