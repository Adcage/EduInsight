class BaseAPIException(Exception):
    """API基础异常类"""
    
    def __init__(self, message: str, status_code: int = 500, error_code: str = None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.error_code = error_code or self.__class__.__name__

class ValidationError(BaseAPIException):
    """数据验证异常"""
    
    def __init__(self, message: str = "数据验证失败"):
        super().__init__(message, status_code=400, error_code="VALIDATION_ERROR")

class AuthenticationError(BaseAPIException):
    """认证异常"""
    
    def __init__(self, message: str = "认证失败"):
        super().__init__(message, status_code=401, error_code="AUTHENTICATION_ERROR")

class AuthorizationError(BaseAPIException):
    """授权异常"""
    
    def __init__(self, message: str = "权限不足"):
        super().__init__(message, status_code=403, error_code="AUTHORIZATION_ERROR")

class NotFoundError(BaseAPIException):
    """资源不存在异常"""
    
    def __init__(self, message: str = "资源不存在"):
        super().__init__(message, status_code=404, error_code="NOT_FOUND_ERROR")

class ConflictError(BaseAPIException):
    """资源冲突异常"""
    
    def __init__(self, message: str = "资源冲突"):
        super().__init__(message, status_code=409, error_code="CONFLICT_ERROR")

class BusinessLogicError(BaseAPIException):
    """业务逻辑异常"""
    
    def __init__(self, message: str = "业务逻辑错误"):
        super().__init__(message, status_code=422, error_code="BUSINESS_LOGIC_ERROR")

class ExternalServiceError(BaseAPIException):
    """外部服务异常"""
    
    def __init__(self, message: str = "外部服务错误"):
        super().__init__(message, status_code=502, error_code="EXTERNAL_SERVICE_ERROR")

class RateLimitError(BaseAPIException):
    """速率限制异常"""
    
    def __init__(self, message: str = "请求过于频繁"):
        super().__init__(message, status_code=429, error_code="RATE_LIMIT_ERROR")
