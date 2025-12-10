"""
课堂互动模块 - 通用API
包含课堂互动模块需要的通用接口，如获取教师课程列表等
"""
from flask import jsonify, g
from flask_openapi3 import APIBlueprint, Tag
from app.models.course import Course
from app.utils.auth_decorators import login_required, role_required
from app.models.user import UserRole

interaction_common_tag = Tag(name='课堂互动-通用', description='课堂互动模块通用接口')
interaction_common_bp = APIBlueprint(
    'interaction_common', 
    __name__, 
    url_prefix='/api/v1/interaction/common', 
    abp_tags=[interaction_common_tag]
)


@interaction_common_bp.route('/teacher-courses', methods=['GET'])
@login_required
@role_required(UserRole.TEACHER, UserRole.ADMIN)
def get_teacher_courses():
    """
    获取当前教师的课程列表（用于课堂互动模块）
    """
    try:
        from flask import session
        user_id = session.get('user_id')
        
        # 查询该教师的所有课程
        courses = Course.query.filter_by(teacher_id=user_id).all()
        
        course_list = []
        for course in courses:
            course_list.append({
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'created_at': course.created_at.isoformat() if course.created_at else None
            })
        
        return jsonify({
            'code': 200,
            'message': '获取课程列表成功',
            'data': {
                'courses': course_list,
                'total': len(course_list)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取课程列表失败: {str(e)}'
        }), 500


@interaction_common_bp.route('/student-courses', methods=['GET'])
@login_required
@role_required(UserRole.STUDENT)
def get_student_courses():
    """
    获取当前学生的课程列表（用于课堂互动模块）
    通过学生所在班级获取课程
    """
    try:
        from flask import session
        from app.models.user import User
        
        user_id = session.get('user_id')
        
        # 获取学生信息
        student = User.query.get(user_id)
        if not student or not student.class_id:
            return jsonify({
                'code': 200,
                'message': '获取课程列表成功',
                'data': {
                    'courses': [],
                    'total': 0
                }
            }), 200
        
        # 通过学生的班级获取课程
        from app.models.class_model import Class
        student_class = Class.query.get(student.class_id)
        
        if not student_class:
            return jsonify({
                'code': 200,
                'message': '获取课程列表成功',
                'data': {
                    'courses': [],
                    'total': 0
                }
            }), 200
        
        # 获取该班级的所有课程
        courses = student_class.courses.all()
        
        course_list = []
        for course in courses:
            course_list.append({
                'id': course.id,
                'name': course.name,
                'description': course.description,
                'created_at': course.created_at.isoformat() if course.created_at else None
            })
        
        return jsonify({
            'code': 200,
            'message': '获取课程列表成功',
            'data': {
                'courses': course_list,
                'total': len(course_list)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取课程列表失败: {str(e)}'
        }), 500


@interaction_common_bp.route('/course/<int:course_id>/students', methods=['GET'])
@login_required
@role_required(UserRole.TEACHER, UserRole.ADMIN)
def get_course_students(course_id):
    """
    获取指定课程的学生列表（用于点名提问）
    """
    try:
        from app.models.user import User
        from app.models.class_model import Class
        
        # 查询课程
        course = Course.query.get(course_id)
        if not course:
            return jsonify({
                'code': 404,
                'message': '课程不存在'
            }), 404
        
        # 获取该课程关联的所有班级
        classes = course.classes.all()
        
        # 收集所有学生
        students_dict = {}  # 使用字典去重
        for class_obj in classes:
            # 获取班级的所有学生
            students = User.query.filter_by(
                class_id=class_obj.id,
                role=UserRole.STUDENT
            ).all()
            
            for student in students:
                if student.id not in students_dict:
                    students_dict[student.id] = {
                        'id': student.id,
                        'username': student.username,
                        'real_name': student.real_name,
                        'class_id': student.class_id,
                        'class_name': class_obj.name
                    }
        
        student_list = list(students_dict.values())
        
        return jsonify({
            'code': 200,
            'message': '获取学生列表成功',
            'data': {
                'students': student_list,
                'total': len(student_list)
            }
        }), 200
        
    except Exception as e:
        return jsonify({
            'code': 500,
            'message': f'获取学生列表失败: {str(e)}'
        }), 500
