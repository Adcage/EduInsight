"""
测试课程API
"""
from app import create_app
from app.models.course import Course
from app.models.user import User, UserRole

app = create_app()

with app.app_context():
    # 查看所有教师
    teachers = User.query.filter_by(role=UserRole.TEACHER).all()
    print(f"\n找到 {len(teachers)} 个教师:")
    for teacher in teachers:
        print(f"  - ID: {teacher.id}, 姓名: {teacher.real_name}, 用户名: {teacher.username}")
    
    # 查看所有课程
    courses = Course.query.all()
    print(f"\n找到 {len(courses)} 个课程:")
    for course in courses:
        print(f"  - ID: {course.id}, 名称: {course.name}, 教师ID: {course.teacher_id}")
    
    # 查看教师ID为1的课程
    teacher_id = 1
    teacher_courses = Course.query.filter_by(teacher_id=teacher_id).all()
    print(f"\n教师ID {teacher_id} 的课程 ({len(teacher_courses)} 个):")
    for course in teacher_courses:
        print(f"  - ID: {course.id}, 名称: {course.name}, 学期: {course.semester}")
