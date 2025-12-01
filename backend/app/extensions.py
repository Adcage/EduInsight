from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 初始化扩展
db = SQLAlchemy()
cors = CORS()
jwt = JWTManager()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    cors.init_app(app, 
                  supports_credentials=True, 
                  origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
