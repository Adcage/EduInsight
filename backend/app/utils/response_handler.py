"""
API 响应处理工具
提供统一的响应格式封装
"""
from typing import Any, Optional, Dict
from datetime import datetime
from pydantic import BaseModel
from app.schemas.common_schemas import (
    BaseResponseModel,
    PaginationModel,
)


class ResponseHandler:
    """API 响应处理类"""
    
    @staticmethod
    def success(data: Any = None, message: str = "操作成功") -> Dict[str, Any]:
        """
        返回成功响应
        
        Args:
            data: 响应数据
            message: 响应消息
            
        Returns:
            成功响应字典
        """
        response = BaseResponseModel(
            message=message,
            success=True,
            data=data
        )
        return response.model_dump(by_alias=True)
    
    @staticmethod
    def error(message: str, error_code: Optional[str] = None, details: Any = None) -> Dict[str, Any]:
        """
        返回错误响应
        
        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
            
        Returns:
            错误响应字典
        """
        response = BaseResponseModel(
            message=message,
            success=False,
            error_code=error_code,
            details=details
        )
        return response.model_dump(by_alias=True)
    
    @staticmethod
    def paginated(
        items: list,
        total: int,
        page: int,
        per_page: int,
        message: str = "获取成功"
    ) -> Dict[str, Any]:
        """
        返回分页数据响应
        
        Args:
            items: 数据列表
            total: 总记录数
            page: 当前页码
            per_page: 每页数量
            message: 响应消息
            
        Returns:
            包含分页信息的成功响应字典
        """
        # 计算总页数
        pages = (total + per_page - 1) // per_page if per_page > 0 else 0
        
        # 创建分页模型
        pagination = PaginationModel(
            page=page,
            per_page=per_page,
            total=total,
            pages=pages,
            has_prev=page > 1,
            has_next=page < pages
        )
        
        # 返回成功响应，包含分页数据和列表
        response = BaseResponseModel(
            message=message,
            success=True,
            data={
                'items': items,
                'pagination': pagination.model_dump(by_alias=True)
            }
        )
        return response.model_dump(by_alias=True)


# 工具函数
def _convert_datetime_to_string(obj: Any) -> Any:
    """
    递归转换对象中的 datetime 为字符串
    
    Args:
        obj: 要转换的对象（可以是字典、列表、datetime等）
        
    Returns:
        转换后的对象
    """
    if isinstance(obj, datetime):
        return obj.strftime('%a, %d %b %Y %H:%M:%S GMT')
    elif isinstance(obj, dict):
        return {key: _convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetime_to_string(item) for item in obj]
    elif isinstance(obj, BaseModel):
        # 如果是 Pydantic 模型，先转换为字典
        return _convert_datetime_to_string(obj.model_dump(by_alias=True))
    else:
        return obj


# 便捷函数别名
def success_response(data: Any = None, message: str = "操作成功", status_code: int = 200):
    """
    返回成功响应（便捷函数）
    
    自动处理：
    - datetime 对象转换为字符串
    - Pydantic 模型转换为驼峰命名的字典
    
    Args:
        data: 响应数据（支持字典、列表、Pydantic模型等）
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        (响应字典, 状态码) 元组
    """
    # 自动转换 datetime 和 Pydantic 模型
    processed_data = _convert_datetime_to_string(data)
    
    return {
        'code': status_code,
        'message': message,
        'data': processed_data
    }, status_code


def error_response(message: str, status_code: int = 400, error_code: Optional[str] = None):
    """
    返回错误响应（便捷函数）
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        error_code: 错误代码
        
    Returns:
        (响应字典, 状态码) 元组
    """
    return {
        'code': status_code,
        'message': message,
        'error_code': error_code
    }, status_code
