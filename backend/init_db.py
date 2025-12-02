"""
数据库初始化脚本
用于创建所有数据库表
"""
from app import create_app
from app.extensions import db

def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功!")
        print(f"📁 数据库位置: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 显示创建的表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"\n📊 已创建 {len(tables)} 个数据表:")
            for table in tables:
                print(f"   - {table}")
        else:
            print("\n⚠️  警告: 没有找到任何数据表!")

if __name__ == '__main__':
    init_database()
