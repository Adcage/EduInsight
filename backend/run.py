import os
from dotenv import load_dotenv
from app import create_app
from app.extensions import socketio

# 加载环境变量
# 1. 先加载 .env (团队共享的默认配置)
load_dotenv()
# 2. 再加载 .env.local (个人配置,会覆盖 .env 中的同名变量)
load_dotenv('.env.local', override=True)

# 从环境变量获取配置,默认使用开发环境
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # 使用socketio.run代替app.run，支持WebSocket
    socketio.run(
        app,
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5030)),
        debug=app.config.get('DEBUG', False),
        allow_unsafe_werkzeug=True  # 开发环境允许使用Werkzeug
    )
