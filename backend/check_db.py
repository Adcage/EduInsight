"""检查数据库状态"""
from app import create_app
from app.extensions import db
from sqlalchemy import inspect
import os

app = create_app()

with app.app_context():
    # 获取数据库URI
    db_uri = app.config['SQLALCHEMY_DATABASE_URI']
    print(f"📁 数据库URI: {db_uri}")
    
    # 检查数据库文件是否存在
    if 'sqlite:///' in db_uri:
        db_path = db_uri.replace('sqlite:///', '')
        if os.path.exists(db_path):
            print(f"✅ 数据库文件存在: {db_path}")
            print(f"📊 文件大小: {os.path.getsize(db_path)} bytes")
        else:
            print(f"❌ 数据库文件不存在: {db_path}")
    
    # 检查表
    inspector = inspect(db.engine)
    tables = inspector.get_table_names()
    
    if tables:
        print(f"\n✅ 找到 {len(tables)} 个数据表:")
        for table in sorted(tables):
            print(f"   - {table}")
    else:
        print("\n❌ 数据库中没有任何表!")
        print("请运行: python init_db.py")
