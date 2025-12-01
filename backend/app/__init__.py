from flask_openapi3 import OpenAPI, Info, SecurityScheme
from app.config import config
from app.extensions import init_extensions

def create_app(config_name='development'):
    """应用工厂函数"""
    # 定义JWT安全方案
    jwt_scheme = SecurityScheme(
        type="http",
        scheme="bearer",
        bearerFormat="JWT",
        description="JWT认证令牌"
    )
    
    # OpenAPI 信息配置
    info = Info(
        title="Flask Backend API", 
        version="1.0.0", 
        description="基于Flask-OpenAPI3的现代化RESTful API"
    )
    
    # 创建 OpenAPI 应用，添加安全方案
    app = OpenAPI(
        __name__, 
        info=info,
        security_schemes={"bearerAuth": jwt_scheme}
    )
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册API蓝图
    register_apis(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app

def register_apis(app):
    """注册所有API蓝图"""
    from app.api import api_blueprints
    
    # 注册所有API蓝图（前缀已在各蓝图中定义）
    for bp in api_blueprints:
        app.register_api(bp)

def register_error_handlers(app):
    """注册错误处理器"""
    from app.exceptions.handlers import register_handlers
    register_handlers(app)
