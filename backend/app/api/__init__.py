# API模块初始化文件
from app.api.user_api import user_api_bp
from app.api.auth_api import auth_api_bp

# 所有API蓝图列表
__all__ = [
    'user_api_bp',
    'auth_api_bp',
]

# 蓝图列表（用于批量注册）
api_blueprints = [
    user_api_bp,
    auth_api_bp,
]
