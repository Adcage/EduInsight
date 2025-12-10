# API模块初始化文件
from app.api.user_api import user_api_bp
from app.api.auth_api import auth_api_bp
from app.api.material_api import material_api_bp
from app.api.category_api import category_api_bp
from app.api.tag_api import tag_api_bp
from app.api.chunked_upload_api import chunked_upload_api_bp
from app.api.grade_api import grade_api_bp
from app.api.statistics_api import statistics_api_bp
from .prediction_api import prediction_api_bp
from app.api.attendance_api import attendance_api_bp
from app.api.student_attendance_api import student_attendance_api_bp
from app.api.course_api import course_api_bp
from app.api.class_api import class_api_bp
from app.api.poll_api import poll_api_bp
from app.api.question_api import question_api_bp
from app.api.barrage_api import barrage_api_bp
from app.api.interaction_common_api import interaction_common_bp

# 所有API蓝图列表
__all__ = [
    'user_api_bp',
    'auth_api_bp',
    'material_api_bp',
    'category_api_bp',
    'tag_api_bp',
    'chunked_upload_api_bp',
    'grade_api_bp',
    'statistics_api_bp',
    'prediction_api_bp',
    'attendance_api_bp',
    'student_attendance_api_bp',
    'course_api_bp',
    'class_api_bp',
    'poll_api_bp',
    'question_api_bp',
    'barrage_api_bp',
    'interaction_common_bp',
]

# 蓝图列表（用于批量注册）
api_blueprints = [
    user_api_bp,
    auth_api_bp,
    material_api_bp,
    category_api_bp,
    tag_api_bp,
    chunked_upload_api_bp,
    grade_api_bp,
    statistics_api_bp,
    prediction_api_bp,
    attendance_api_bp,
    student_attendance_api_bp,
    course_api_bp,
    class_api_bp,
    poll_api_bp,
    question_api_bp,
    barrage_api_bp,
    interaction_common_bp,
]
