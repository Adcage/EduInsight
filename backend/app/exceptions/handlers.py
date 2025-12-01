from flask import jsonify
from werkzeug.exceptions import HTTPException
from pydantic import ValidationError as PydanticValidationError
from sqlalchemy.exc import IntegrityError
from app.exceptions.base import BaseAPIException

def register_handlers(app):
    """注册全局异常处理器"""
    
    @app.errorhandler(BaseAPIException)
    def handle_api_exception(error):
        """处理自定义API异常"""
        response = {
            'success': False,
            'message': error.message,
            'error_code': error.error_code,
            'timestamp': None  # 可以添加时间戳
        }
        return jsonify(response), error.status_code
    
    @app.errorhandler(PydanticValidationError)
    def handle_validation_error(error):
        """处理Pydantic验证异常"""
        errors = []
        for err in error.errors():
            field = '.'.join(str(x) for x in err['loc'])
            message = err['msg']
            errors.append(f"{field}: {message}")
        
        response = {
            'success': False,
            'message': '数据验证失败',
            'error_code': 'VALIDATION_ERROR',
            'details': errors
        }
        return jsonify(response), 400
    
    @app.errorhandler(IntegrityError)
    def handle_integrity_error(error):
        """处理数据库完整性异常"""
        response = {
            'success': False,
            'message': '数据库约束违反',
            'error_code': 'INTEGRITY_ERROR'
        }
        return jsonify(response), 400
    
    @app.errorhandler(HTTPException)
    def handle_http_exception(error):
        """处理HTTP异常"""
        response = {
            'success': False,
            'message': error.description,
            'error_code': f'HTTP_{error.code}'
        }
        return jsonify(response), error.code
    
    @app.errorhandler(Exception)
    def handle_generic_exception(error):
        """处理通用异常"""
        app.logger.error(f"Unhandled exception: {str(error)}")
        
        response = {
            'success': False,
            'message': '服务器内部错误',
            'error_code': 'INTERNAL_SERVER_ERROR'
        }
        
        # 在开发环境中显示详细错误信息
        if app.config.get('DEBUG'):
            response['details'] = str(error)
        
        return jsonify(response), 500
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        response = {
            'success': False,
            'message': '请求的资源不存在',
            'error_code': 'NOT_FOUND'
        }
        return jsonify(response), 404
    
    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """处理405错误"""
        response = {
            'success': False,
            'message': '请求方法不被允许',
            'error_code': 'METHOD_NOT_ALLOWED'
        }
        return jsonify(response), 405
