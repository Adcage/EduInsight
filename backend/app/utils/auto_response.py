"""
自动响应处理装饰器
"""
from functools import wraps
from typing import Any, Tuple, Dict
from flask import jsonify
from app.utils.response_handler import ResponseHandler


def auto_response(success_message: str = "操作成功"):
    """
    自动响应处理装饰器
    
    Args:
        success_message: 成功时的默认消息
        
    使用方法:
        @auto_response("获取用户成功")
        def get_user():
            # 直接返回数据，装饰器会自动包装
            return user_data
            
        @auto_response("获取用户列表成功")  
        def list_users():
            # 返回元组 (data, total, page, per_page) 自动处理分页
            return users, total, page, per_page
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            try:
                result = func(*args, **kwargs)
                
                # 如果函数已经返回了完整的响应（包含状态码），直接返回
                if isinstance(result, tuple) and len(result) == 2 and isinstance(result[1], int):
                    return result
                
                # 如果返回的是分页数据元组 (items, total, page, per_page)
                if isinstance(result, tuple) and len(result) == 4:
                    items, total, page, per_page = result
                    response_data = ResponseHandler.paginated(
                        items=items,
                        total=total,
                        page=page,
                        per_page=per_page,
                        message=success_message
                    )
                    return jsonify(response_data), 200
                
                # 普通数据响应
                response_data = ResponseHandler.success(
                    data=result,
                    message=success_message
                )
                return jsonify(response_data), 200
                
            except ValueError as e:
                # 业务逻辑错误
                response_data = ResponseHandler.error(
                    message=str(e),
                    error_code="BUSINESS_ERROR"
                )
                return jsonify(response_data), 400
                
            except Exception as e:
                # 系统错误
                response_data = ResponseHandler.error(
                    message="系统内部错误",
                    error_code="INTERNAL_ERROR",
                    details=str(e)
                )
                return jsonify(response_data), 500
                
        return wrapper
    return decorator


def auto_error_response(func):
    """
    自动错误响应装饰器（只处理异常，不包装成功响应）
    
    使用方法:
        @auto_error_response
        def get_user():
            # 手动返回成功响应，装饰器只处理异常
            return ResponseHandler.success(user_data, "获取用户成功")
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            response_data = ResponseHandler.error(
                message=str(e),
                error_code="BUSINESS_ERROR"
            )
            return jsonify(response_data), 400
        except Exception as e:
            response_data = ResponseHandler.error(
                message="系统内部错误",
                error_code="INTERNAL_ERROR",
                details=str(e)
            )
            return jsonify(response_data), 500
    return wrapper
