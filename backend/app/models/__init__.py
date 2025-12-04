"""
模型模块

导出所有数据库模型类。
"""

# 基础模型
from .base import BaseModel

# 用户和班级模块
from .user import User, UserRole
from .class_model import Class

# 资料中心模块
from .material import Material, MaterialCategory, MaterialTag, material_tag_relation

# 课程模块
from .course import Course, course_classes

# 考勤管理模块
from .attendance import (
    Attendance, AttendanceRecord, AttendanceStatistics,
    AttendanceType, AttendanceStatus, CheckInStatus
)

# 成绩管理模块
from .grade import (
    Grade, GradeStatistics, GradePrediction,
    ExamType, RiskLevel
)

# 课堂互动模块
from .interaction import (
    Poll, PollResponse, Question, QuestionAnswer, Barrage,
    PollType, PollStatus, QuestionStatus
)

# 智能模块
from .intelligence import DocumentKeyword, ClassificationLog

# 系统日志模块
from .system import (
    SystemLog, Notification,
    NotificationType, NotificationPriority
)

__all__ = [
    # 基础
    'BaseModel',
    
    # 用户和班级
    'User', 'UserRole', 'Class',
    
    # 资料中心
    'Material', 'MaterialCategory', 'MaterialTag', 'material_tag_relation',
    
    # 课程
    'Course', 'course_classes',
    
    # 考勤管理
    'Attendance', 'AttendanceRecord', 'AttendanceStatistics',
    'AttendanceType', 'AttendanceStatus', 'CheckInStatus',
    
    # 成绩管理
    'Grade', 'GradeStatistics', 'GradePrediction',
    'ExamType', 'RiskLevel',
    
    # 课堂互动
    'Poll', 'PollResponse', 'Question', 'QuestionAnswer', 'Barrage',
    'PollType', 'PollStatus', 'QuestionStatus',
    
    # 智能模块
    'DocumentKeyword', 'ClassificationLog',
    
    # 系统日志
    'SystemLog', 'Notification',
    'NotificationType', 'NotificationPriority',
]
