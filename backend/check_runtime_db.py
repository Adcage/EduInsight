"""检查运行时数据库配置"""
import os
from dotenv import load_dotenv

# 模拟run.py的加载过程
load_dotenv()
load_dotenv('.env.local', override=True)

config_name = os.environ.get('FLASK_ENV', 'development')
print(f"🔧 FLASK_ENV: {config_name}")
print(f"🔧 DATABASE_URL: {os.environ.get('DATABASE_URL', 'Not set')}")
print(f"🔧 DEV_DATABASE_URL: {os.environ.get('DEV_DATABASE_URL', 'Not set')}")

# 创建应用并检查
from app import create_app
from app.extensions import db
from sqlalchemy import inspect

app = create_app(config_name)

with app.app_context():
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"\n📁 实际使用的数据库URI: {db_uri}")
    
    # 检查表
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if 'users' in tables:
        print(f"✅ users表存在!")
        # 检查users表中的数据
        from app.models.user import User
        user_count = User.query.count()
        print(f"📊 users表中有 {user_count} 条记录")
    else:
        print(f"❌ users表不存在!")
        print(f"当前数据库中的表: {tables}")
