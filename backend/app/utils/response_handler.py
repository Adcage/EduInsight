"""
API 响应处理工具
提供统一的响应格式封装
"""
from typing import Any, Optional, Dict
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
