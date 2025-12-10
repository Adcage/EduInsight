"""
班级管理服务类
"""
import logging
from typing import Dict, Any, List, Optional
from app.extensions import db
from app.models.class_model import Class
from app.models.user import User, UserRole
from sqlalchemy import func

logger = logging.getLogger(__name__)


class ClassService:
    """班级管理服务类"""
    
    @staticmethod
    def get_class_students(class_id: int) -> Dict[str, Any]:
        """
        获取班级的学生列表
        
        Args:
            class_id: 班级ID
            
        Returns:
            包含班级信息和学生列表的字典
            
        Raises:
            ValueError: 班级不存在
        """
        # 验证班级是否存在
        class_obj = Class.query.get(class_id)
        if not class_obj:
            raise ValueError(f"班级不存在: {class_id}")
        
        # 查询该班级的所有学生
        students = User.query.filter(
            User.class_id == class_id,
            User.role == UserRole.STUDENT
        ).order_by(User.user_code).all()
        
        # 构建学生信息列表
        student_list = []
        for student in students:
            student_info = {
                'id': student.id,
                'user_code': student.user_code,
                'real_name': student.real_name,
                'username': student.username,
                'email': student.email,
                'phone': student.phone,
                'avatar': student.avatar,
                'status': student.status,
                'last_login_time': student.last_login_time,
                'created_at': student.created_at
            }
            student_list.append(student_info)
        
        logger.info(f"查询班级 {class_id}({class_obj.name}) 的学生信息，共 {len(student_list)} 名学生")
        
        return {
            'class_id': class_obj.id,
            'class_name': class_obj.name,
            'class_code': class_obj.code,
            'grade': class_obj.grade,
            'major': class_obj.major,
            'students': student_list,
            'total': len(student_list)
        }
    
    @staticmethod
    def get_class_by_id(class_id: int) -> Optional[Class]:
        """
        根据ID获取班级
        
        Args:
            class_id: 班级ID
            
        Returns:
            班级对象，不存在返回None
        """
        return Class.query.get(class_id)
    
    @staticmethod
    def get_all_classes(
        page: int = 1,
        per_page: int = 20,
        status: Optional[bool] = None,
        grade: Optional[str] = None,
        major: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取班级列表
        
        Args:
            page: 页码
            per_page: 每页数量
            status: 状态筛选
            grade: 年级筛选
            major: 专业筛选
            
        Returns:
            包含班级列表和分页信息的字典
        """
        query = Class.query
        
        # 应用筛选条件
        if status is not None:
            query = query.filter(Class.status == status)
        if grade:
            query = query.filter(Class.grade == grade)
        if major:
            query = query.filter(Class.major == major)
        
        # 分页查询
        pagination = query.order_by(Class.created_at.desc()).paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        # 构建班级列表，包含学生人数
        classes = []
        for class_obj in pagination.items:
            # 统计该班级的学生人数
            student_count = User.query.filter(
                User.class_id == class_obj.id,
                User.role == UserRole.STUDENT
            ).count()
            
            class_info = {
                'id': class_obj.id,
                'name': class_obj.name,
                'code': class_obj.code,
                'description': class_obj.description,
                'grade': class_obj.grade,
                'major': class_obj.major,
                'teacher_id': class_obj.teacher_id,
                'status': class_obj.status,
                'student_count': student_count,
                'created_at': class_obj.created_at,
                'updated_at': class_obj.updated_at
            }
            classes.append(class_info)
        
        logger.info(f"查询班级列表，第 {page} 页，共 {pagination.total} 个班级")
        
        return {
            'classes': classes,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
