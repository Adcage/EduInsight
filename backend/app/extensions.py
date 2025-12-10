from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_socketio import SocketIO

# 初始化扩展
db = SQLAlchemy()
cors = CORS()
socketio = SocketIO()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    cors.init_app(app, 
                  supports_credentials=True, 
                  origins=app.config['CORS_ORIGINS'])
    socketio.init_app(app, 
                     cors_allowed_origins=app.config['CORS_ORIGINS'],
                     async_mode='eventlet')
