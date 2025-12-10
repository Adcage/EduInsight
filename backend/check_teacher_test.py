"""
查找测试教师账号
"""
from app import create_app
from app.models.user import User, UserRole

app = create_app()

with app.app_context():
    # 查找 teacher.test@edu.com
    teacher = User.query.filter_by(email='teacher.test@edu.com').first()
    if teacher:
        print(f"\n找到测试教师:")
        print(f"  - ID: {teacher.id}")
        print(f"  - 姓名: {teacher.real_name}")
        print(f"  - 用户名: {teacher.username}")
        print(f"  - 邮箱: {teacher.email}")
        print(f"  - 角色: {teacher.role}")
    else:
        print("\n未找到 teacher.test@edu.com 账号")
    
    # 查找所有教师
    print("\n所有教师账号:")
    teachers = User.query.filter_by(role=UserRole.TEACHER).all()
    for t in teachers:
        print(f"  - ID: {t.id}, 姓名: {t.real_name}, 邮箱: {t.email}")
