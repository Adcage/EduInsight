"""
为测试教师添加课程
"""
from app import create_app
from app.models.course import Course
from app.extensions import db

app = create_app()

with app.app_context():
    teacher_id = 12  # teacher.test@edu.com
    
    # 检查是否已有课程
    existing = Course.query.filter_by(teacher_id=teacher_id).all()
    if existing:
        print(f"教师 {teacher_id} 已有 {len(existing)} 个课程")
        for c in existing:
            print(f"  - {c.name}")
    else:
        # 创建测试课程
        courses = [
            {
                'name': '软件工程',
                'code': 'SE2024001',
                'description': '软件工程基础课程',
                'semester': '2024-2025-1',
                'academic_year': '2024-2025',
                'credit': 3.0,
                'total_hours': 48,
                'teacher_id': teacher_id,
                'status': True
            },
            {
                'name': '计算机网络',
                'code': 'CN2024001',
                'description': '计算机网络原理与应用',
                'semester': '2024-2025-1',
                'academic_year': '2024-2025',
                'credit': 4.0,
                'total_hours': 64,
                'teacher_id': teacher_id,
                'status': True
            },
            {
                'name': '操作系统',
                'code': 'OS2024001',
                'description': '操作系统原理与实践',
                'semester': '2024-2025-1',
                'academic_year': '2024-2025',
                'credit': 3.5,
                'total_hours': 56,
                'teacher_id': teacher_id,
                'status': True
            }
        ]
        
        for course_data in courses:
            course = Course(**course_data)
            db.session.add(course)
        
        db.session.commit()
        print(f"成功为教师 {teacher_id} 创建了 {len(courses)} 个课程")
        
        # 验证
        created = Course.query.filter_by(teacher_id=teacher_id).all()
        for c in created:
            print(f"  - ID: {c.id}, 名称: {c.name}, 代码: {c.code}")
