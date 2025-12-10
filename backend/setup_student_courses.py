"""
设置学生课程关联的测试脚本
将学生分配到班级，并将班级关联到课程
"""
import sys
import os

# 添加项目根目录到 Python 路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models.user import User
from app.models.class_model import Class
from app.models.course import Course

def setup_student_courses():
    """设置学生课程关联"""
    app = create_app()
    
    with app.app_context():
        print("=" * 60)
        print("开始设置学生课程关联...")
        print("=" * 60)
        
        # 1. 查找或创建班级
        print("\n1. 检查班级...")
        class1 = Class.query.filter_by(code='CS2021-1').first()
        if not class1:
            class1 = Class(
                name='计算机科学2021级1班',
                code='CS2021-1',
                description='计算机科学与技术专业2021级1班',
                grade='2021',
                major='计算机科学与技术'
            )
            db.session.add(class1)
            db.session.commit()
            print(f"   ✓ 创建班级: {class1.name} (ID: {class1.id})")
        else:
            print(f"   ✓ 班级已存在: {class1.name} (ID: {class1.id})")
        
        # 2. 将测试学生分配到班级
        print("\n2. 分配学生到班级...")
        student = User.query.filter_by(email='zhang@student.edu.com').first()
        if student:
            student.class_id = class1.id
            db.session.commit()
            print(f"   ✓ 学生 {student.real_name} (ID: {student.id}) 已分配到班级 {class1.name}")
        else:
            print("   ✗ 未找到测试学生 zhang@student.edu.com")
        
        # 3. 将班级关联到课程
        print("\n3. 关联班级到课程...")
        teacher = User.query.filter_by(email='teacher.test@edu.com').first()
        if not teacher:
            print("   ✗ 未找到教师 teacher.test@edu.com")
            return
        
        # 获取教师的所有课程
        courses = Course.query.filter_by(teacher_id=teacher.id).all()
        
        if not courses:
            print("   ✗ 教师没有课程")
            return
        
        for course in courses:
            # 检查班级是否已关联到课程
            if class1 not in course.classes:
                course.classes.append(class1)
                print(f"   ✓ 班级 {class1.name} 已关联到课程 {course.name} (ID: {course.id})")
            else:
                print(f"   - 班级 {class1.name} 已经关联到课程 {course.name}")
        
        db.session.commit()
        
        # 4. 验证设置
        print("\n4. 验证设置...")
        print(f"\n学生信息:")
        print(f"   姓名: {student.real_name}")
        print(f"   邮箱: {student.email}")
        print(f"   班级ID: {student.class_id}")
        print(f"   班级名称: {class1.name}")
        
        print(f"\n学生可以访问的课程:")
        student_courses = class1.courses.all()
        for idx, course in enumerate(student_courses, 1):
            print(f"   {idx}. {course.name} (ID: {course.id}) - 教师: {course.teacher_id}")
        
        print("\n" + "=" * 60)
        print("设置完成！")
        print("=" * 60)
        print("\n测试说明:")
        print("1. 使用 zhang@student.edu.com / test123456 登录学生端")
        print("2. 进入课堂提问页面")
        print("3. 应该能看到课程选择下拉框，显示上述课程")
        print("4. 选择课程后，只会收到该课程的问题通知")
        print("=" * 60)

if __name__ == '__main__':
    setup_student_courses()
