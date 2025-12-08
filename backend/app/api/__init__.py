# API模块初始化文件
from app.api.user_api import user_api_bp
from app.api.auth_api import auth_api_bp
from app.api.material_api import material_api_bp
from app.api.category_api import category_api_bp
from app.api.tag_api import tag_api_bp
from app.api.grade_api import grade_api_bp
from app.api.statistics_api import statistics_api_bp
from .prediction_api import prediction_api_bp

# 所有API蓝图列表
__all__ = [
    'user_api_bp',
    'auth_api_bp',
    'material_api_bp',
    'category_api_bp',
    'tag_api_bp',
    'grade_api_bp',
    'statistics_api_bp',
    'prediction_api_bp',
]

# 蓝图列表（用于批量注册）
api_blueprints = [
    user_api_bp,
    auth_api_bp,
    material_api_bp,
    category_api_bp,
    tag_api_bp,
    grade_api_bp,
    statistics_api_bp,
    prediction_api_bp,
]
