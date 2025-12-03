import os
from app import create_app

# 从环境变量获取配置，默认使用开发环境
config_name = os.environ.get('FLASK_ENV', 'development')
app = create_app(config_name)

if __name__ == '__main__':
    # 开发服务器配置
    app.run(
        host='0.0.0.0',
        port=int(os.environ.get('PORT', 5001)),
        debug=app.config.get('DEBUG', False)
    )
