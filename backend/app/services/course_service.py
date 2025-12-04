"""
课程管理业务逻辑服务
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime
from sqlalchemy import or_, and_, func
from app.extensions import db
from app.models.course import Course, course_classes
from app.models.class_model import Class
from app.models.user import User

logger = logging.getLogger(__name__)


class CourseService:
    """课程管理服务类"""
    
    @staticmethod
    def get_course_classes(course_id: int) -> Dict[str, Any]:
        """
        获取课程关联的班级信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            包含班级列表和统计信息的字典
            
        Raises:
            ValueError: 课程不存在
        """
        # 验证课程是否存在
        course = Course.query.get(course_id)
        if not course:
            raise ValueError(f"课程不存在: {course_id}")
        
        # 查询课程关联的班级信息
        query = db.session.query(
            Class.id.label('class_id'),
            Class.name.label('class_name'),
            Class.code.label('class_code'),
            Class.grade,
            Class.major,
            course_classes.c.start_date,
            course_classes.c.end_date,
            course_classes.c.status,
            func.count(User.id).label('student_count')
        ).join(
            course_classes,
            Class.id == course_classes.c.class_id
        ).outerjoin(
            User,
            and_(User.class_id == Class.id, User.role == 'student')
        ).filter(
            course_classes.c.course_id == course_id
        ).group_by(
            Class.id,
            Class.name,
            Class.code,
            Class.grade,
            Class.major,
            course_classes.c.start_date,
            course_classes.c.end_date,
            course_classes.c.status
        ).all()
        
        # 构建响应数据
        classes = []
        total_students = 0
        
        for row in query:
            class_info = {
                'class_id': row.class_id,
                'class_name': row.class_name,
                'class_code': row.class_code,
                'grade': row.grade,
                'major': row.major,
                'student_count': row.student_count,
                'start_date': row.start_date.strftime('%Y-%m-%d') if row.start_date else None,
                'end_date': row.end_date.strftime('%Y-%m-%d') if row.end_date else None,
                'status': bool(row.status)
            }
            classes.append(class_info)
            total_students += row.student_count
        
        logger.info(f"查询课程 {course_id} 的班级信息，共 {len(classes)} 个班级，{total_students} 名学生")
        
        return {
            'classes': classes,
            'total': len(classes),
            'total_students': total_students
        }
    
    @staticmethod
    def get_course_by_id(course_id: int) -> Optional[Course]:
        """
        根据ID获取课程
        
        Args:
            course_id: 课程ID
            
        Returns:
            课程对象，不存在返回None
        """
        return Course.query.get(course_id)
    
    @staticmethod
    def get_courses_by_teacher(
        teacher_id: int, 
        page: int = 1, 
        per_page: int = 20,
        include_stats: bool = True,
        semester: Optional[str] = None,
        status: Optional[bool] = None
    ) -> Dict[str, Any]:
        """
        获取教师的课程列表
        
        Args:
            teacher_id: 教师ID
            page: 页码
            per_page: 每页数量
            include_stats: 是否包含统计信息（班级数、学生数）
            semester: 学期筛选
            status: 状态筛选
            
        Returns:
            包含课程列表和分页信息的字典
        """
        query = Course.query.filter_by(teacher_id=teacher_id)
        
        # 添加筛选条件
        if semester:
            query = query.filter_by(semester=semester)
        if status is not None:
            query = query.filter_by(status=status)
        
        # 按更新时间倒序排列
        query = query.order_by(Course.updated_at.desc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        courses = []
        for course in pagination.items:
            course_data = {
                'id': course.id,
                'name': course.name,
                'code': course.code,
                'description': course.description,
                'semester': course.semester,
                'academic_year': course.academic_year,
                'credit': float(course.credit) if course.credit else None,
                'total_hours': course.total_hours,
                'teacher_id': course.teacher_id,
                'status': course.status,
                'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': course.updated_at.strftime('%Y-%m-%d %H:%M:%S')
            }
            
            # 如果需要统计信息，查询班级数和学生数
            if include_stats:
                # 查询班级数
                class_count = db.session.query(func.count(course_classes.c.class_id)).filter(
                    course_classes.c.course_id == course.id
                ).scalar() or 0
                
                # 查询学生数
                student_count = db.session.query(func.count(func.distinct(User.id))).select_from(
                    course_classes
                ).join(
                    User,
                    User.class_id == course_classes.c.class_id
                ).filter(
                    and_(
                        course_classes.c.course_id == course.id,
                        User.role == 'student'
                    )
                ).scalar() or 0
                
                course_data['class_count'] = class_count
                course_data['student_count'] = student_count
            
            courses.append(course_data)
        
        logger.info(f"查询教师 {teacher_id} 的课程列表，共 {pagination.total} 门课程")
        
        return {
            'courses': courses,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def add_classes_to_course(
        course_id: int,
        class_ids: List[int],
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> int:
        """
        为课程添加班级
        
        Args:
            course_id: 课程ID
            class_ids: 班级ID列表
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            添加的班级数量
            
        Raises:
            ValueError: 课程不存在或班级不存在
        """
        # 验证课程
        course = Course.query.get(course_id)
        if not course:
            raise ValueError(f"课程不存在: {course_id}")
        
        # 验证班级
        classes = Class.query.filter(Class.id.in_(class_ids)).all()
        if len(classes) != len(class_ids):
            raise ValueError("部分班级不存在")
        
        added_count = 0
        for class_id in class_ids:
            # 检查是否已存在关联
            existing = db.session.query(course_classes).filter_by(
                course_id=course_id,
                class_id=class_id
            ).first()
            
            if not existing:
                # 插入关联
                stmt = course_classes.insert().values(
                    course_id=course_id,
                    class_id=class_id,
                    start_date=start_date,
                    end_date=end_date,
                    status=True,
                    created_at=datetime.now(),
                    updated_at=datetime.now()
                )
                db.session.execute(stmt)
                added_count += 1
        
        db.session.commit()
        logger.info(f"为课程 {course_id} 添加了 {added_count} 个班级")
        
        return added_count
    
    @staticmethod
    def remove_class_from_course(course_id: int, class_id: int) -> bool:
        """
        从课程中移除班级
        
        Args:
            course_id: 课程ID
            class_id: 班级ID
            
        Returns:
            是否成功移除
        """
        result = db.session.query(course_classes).filter_by(
            course_id=course_id,
            class_id=class_id
        ).delete()
        
        db.session.commit()
        
        if result > 0:
            logger.info(f"从课程 {course_id} 中移除班级 {class_id}")
            return True
        return False
    
    @staticmethod
    def get_course_detail(course_id: int) -> Dict[str, Any]:
        """
        获取课程详细信息
        
        Args:
            course_id: 课程ID
            
        Returns:
            包含课程详细信息的字典
            
        Raises:
            ValueError: 课程不存在
        """
        course = Course.query.get(course_id)
        if not course:
            raise ValueError(f"课程不存在: {course_id}")
        
        # 基本信息
        course_data = {
            'id': course.id,
            'name': course.name,
            'code': course.code,
            'description': course.description,
            'semester': course.semester,
            'academic_year': course.academic_year,
            'credit': float(course.credit) if course.credit else None,
            'total_hours': course.total_hours,
            'teacher_id': course.teacher_id,
            'status': course.status,
            'created_at': course.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': course.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        # 获取教师信息
        teacher = User.query.get(course.teacher_id)
        if teacher:
            course_data['teacher_name'] = teacher.real_name
            course_data['teacher_email'] = teacher.email
        
        # 统计班级数
        class_count = db.session.query(func.count(course_classes.c.class_id)).filter(
            course_classes.c.course_id == course_id
        ).scalar() or 0
        course_data['class_count'] = class_count
        
        # 统计学生数
        student_count = db.session.query(func.count(func.distinct(User.id))).select_from(
            course_classes
        ).join(
            User,
            User.class_id == course_classes.c.class_id
        ).filter(
            and_(
                course_classes.c.course_id == course_id,
                User.role == 'student'
            )
        ).scalar() or 0
        course_data['student_count'] = student_count
        
        logger.info(f"查询课程 {course_id} 的详细信息")
        
        return course_data
