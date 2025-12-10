from flask_openapi3 import OpenAPI, Info
from app.config import config
from app.extensions import init_extensions

def create_app(config_name='development'):
    """应用工厂函数"""
    # OpenAPI 信息配置
    info = Info(
        title="Flask Backend API", 
        version="1.0.0", 
        description="基于Flask-OpenAPI3的现代化RESTful API"
    )
    
    # 创建 OpenAPI 应用
    app = OpenAPI(
        __name__, 
        info=info
    )
    
    # 禁用严格的尾部斜杠检查，避免308重定向
    app.url_map.strict_slashes = False

    # 加载配置
    app.config.from_object(config[config_name])
    
    # 配置JSON输出,禁用ASCII转义以正确显示中文
    app.config['JSON_AS_ASCII'] = False
    app.json.ensure_ascii = False
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册API蓝图
    register_apis(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    # 注册WebSocket事件处理器
    register_websocket_events()
    
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

def register_websocket_events():
    """注册WebSocket事件处理器"""
    # 导入事件处理器模块，使装饰器生效
    from app.websocket import interaction_events
    import logging
    logger = logging.getLogger(__name__)
    logger.info("WebSocket事件处理器已注册")
