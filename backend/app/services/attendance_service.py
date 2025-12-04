"""
考勤管理业务逻辑服务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.models.attendance import Attendance, AttendanceRecord, AttendanceStatistics, AttendanceType, AttendanceStatus, CheckInStatus
from app.models.course import Course
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.extensions import db
from app.utils.helpers import generate_random_string
import logging

logger = logging.getLogger(__name__)


class AttendanceService:
    """考勤业务逻辑服务"""
    
    @staticmethod
    def create_attendance(
        title: str,
        course_id: int,
        class_ids: List[int],
        teacher_id: int,
        attendance_type: str,
        start_time: datetime,
        end_time: datetime,
        student_ids: Optional[List[int]] = None,
        location: Optional[str] = None,
        require_location: bool = False
    ) -> Attendance:
        """
        创建考勤任务
        
        Args:
            title: 考勤标题
            course_id: 课程ID
            class_ids: 班级ID列表
            teacher_id: 教师ID
            attendance_type: 考勤方式
            start_time: 开始时间
            end_time: 结束时间
            student_ids: 指定学生ID列表（可选）
            location: 考勤地点
            require_location: 是否需要位置验证
            
        Returns:
            创建的考勤任务对象
        """
        try:
            # 验证课程是否存在
            course = Course.query.get(course_id)
            if not course:
                raise ValueError(f"课程ID {course_id} 不存在")
            
            # 验证教师权限
            if course.teacher_id != teacher_id:
                raise ValueError("只有课程教师可以创建考勤")
            
            # 验证班级是否存在且属于该课程
            classes = Class.query.filter(Class.id.in_(class_ids)).all()
            if len(classes) != len(class_ids):
                raise ValueError("部分班级ID不存在")
            
            # 验证班级是否属于该课程
            course_class_ids = [c.id for c in course.classes.all()]
            for class_id in class_ids:
                if class_id not in course_class_ids:
                    raise ValueError(f"班级ID {class_id} 不属于该课程")
            
            # 生成二维码token（如果是二维码签到）
            qr_code = None
            if attendance_type == AttendanceType.QRCODE.value:
                qr_code = generate_random_string(32)
            
            # 创建考勤任务（为每个班级创建一个考勤任务）
            attendances = []
            for class_id in class_ids:
                attendance = Attendance(
                    title=title,
                    course_id=course_id,
                    class_id=class_id,
                    teacher_id=teacher_id,
                    attendance_type=AttendanceType(attendance_type),
                    qr_code=qr_code,
                    location=location,
                    require_location=require_location,
                    start_time=start_time,
                    end_time=end_time,
                    status=AttendanceStatus.PENDING
                )
                db.session.add(attendance)
                attendances.append(attendance)
            
            db.session.flush()  # 获取考勤ID
            
            # 为每个考勤任务创建考勤记录
            for attendance in attendances:
                # 获取该班级的学生
                if student_ids:
                    # 如果指定了学生，只为这些学生创建记录
                    students = User.query.filter(
                        User.id.in_(student_ids),
                        User.class_id == attendance.class_id,
                        User.role == UserRole.STUDENT,
                        User.status == True
                    ).all()
                else:
                    # 否则为班级所有学生创建记录
                    students = User.query.filter_by(
                        class_id=attendance.class_id,
                        role=UserRole.STUDENT,
                        status=True
                    ).all()
                
                for student in students:
                    record = AttendanceRecord(
                        attendance_id=attendance.id,
                        student_id=student.id,
                        status=CheckInStatus.ABSENT  # 默认缺勤
                    )
                    db.session.add(record)
            
            db.session.commit()
            logger.info(f"Attendance created: {title} for course {course_id}, {len(attendances)} classes")
            
            # 返回第一个考勤任务（前端可以通过课程ID查询所有相关考勤）
            return attendances[0]
            
        except ValueError as e:
            db.session.rollback()
            logger.warning(f"Validation error creating attendance: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error creating attendance: {str(e)}")
            raise
    
    @staticmethod
    def get_attendance_by_id(attendance_id: int) -> Optional[Attendance]:
        """
        根据ID获取考勤任务
        
        Args:
            attendance_id: 考勤ID
            
        Returns:
            考勤任务对象，不存在返回None
        """
        return Attendance.query.get(attendance_id)
    
    @staticmethod
    def get_attendances_by_course(
        course_id: int,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取课程的考勤列表（分页）
        
        Args:
            course_id: 课程ID
            page: 页码
            per_page: 每页数量
            status: 状态筛选
            
        Returns:
            包含考勤列表和分页信息的字典
        """
        query = Attendance.query.filter_by(course_id=course_id)
        
        if status:
            query = query.filter_by(status=AttendanceStatus(status))
        
        query = query.order_by(Attendance.start_time.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'attendances': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_attendances_by_teacher(
        teacher_id: int,
        page: int = 1,
        per_page: int = 20,
        course_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取教师创建的考勤列表（分页）
        
        Args:
            teacher_id: 教师ID
            page: 页码
            per_page: 每页数量
            course_id: 课程ID筛选
            status: 状态筛选
            
        Returns:
            包含考勤列表和分页信息的字典
        """
        query = Attendance.query.filter_by(teacher_id=teacher_id)
        
        if course_id:
            query = query.filter_by(course_id=course_id)
        
        if status:
            query = query.filter_by(status=AttendanceStatus(status))
        
        query = query.order_by(Attendance.start_time.desc())
        
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'attendances': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def update_attendance(
        attendance_id: int,
        teacher_id: int,
        **kwargs
    ) -> Optional[Attendance]:
        """
        更新考勤任务
        
        Args:
            attendance_id: 考勤ID
            teacher_id: 教师ID（用于权限验证）
            **kwargs: 要更新的字段
            
        Returns:
            更新后的考勤任务对象，不存在或无权限返回None
        """
        try:
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                return None
            
            # 验证权限
            if attendance.teacher_id != teacher_id:
                raise ValueError("只有创建教师可以更新考勤")
            
            # 更新允许的字段
            allowed_fields = ['title', 'location', 'end_time', 'status']
            for field, value in kwargs.items():
                if field in allowed_fields and value is not None:
                    if field == 'status':
                        value = AttendanceStatus(value)
                    setattr(attendance, field, value)
            
            db.session.commit()
            logger.info(f"Attendance updated: {attendance_id}")
            return attendance
            
        except ValueError as e:
            db.session.rollback()
            logger.warning(f"Validation error updating attendance: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating attendance: {str(e)}")
            raise
    
    @staticmethod
    def delete_attendance(attendance_id: int, teacher_id: int) -> bool:
        """
        删除考勤任务
        
        Args:
            attendance_id: 考勤ID
            teacher_id: 教师ID（用于权限验证）
            
        Returns:
            删除成功返回True，失败返回False
        """
        try:
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                return False
            
            # 验证权限
            if attendance.teacher_id != teacher_id:
                raise ValueError("只有创建教师可以删除考勤")
            
            # 只能删除未开始的考勤
            if attendance.status != AttendanceStatus.PENDING:
                raise ValueError("只能删除未开始的考勤")
            
            db.session.delete(attendance)
            db.session.commit()
            logger.info(f"Attendance deleted: {attendance_id}")
            return True
            
        except ValueError as e:
            db.session.rollback()
            logger.warning(f"Validation error deleting attendance: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error deleting attendance: {str(e)}")
            raise
    
    @staticmethod
    def start_attendance(attendance_id: int, teacher_id: int) -> Optional[Attendance]:
        """
        开始考勤
        
        Args:
            attendance_id: 考勤ID
            teacher_id: 教师ID（用于权限验证）
            
        Returns:
            更新后的考勤任务对象
        """
        try:
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证权限
            if attendance.teacher_id != teacher_id:
                raise ValueError("只有创建教师可以开始考勤")
            
            # 验证状态
            if attendance.status != AttendanceStatus.PENDING:
                raise ValueError("考勤已开始或已结束")
            
            attendance.start()
            logger.info(f"Attendance started: {attendance_id}")
            return attendance
            
        except ValueError as e:
            logger.warning(f"Validation error starting attendance: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error starting attendance: {str(e)}")
            raise
    
    @staticmethod
    def end_attendance(attendance_id: int, teacher_id: int) -> Optional[Attendance]:
        """
        结束考勤
        
        Args:
            attendance_id: 考勤ID
            teacher_id: 教师ID（用于权限验证）
            
        Returns:
            更新后的考勤任务对象
        """
        try:
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证权限
            if attendance.teacher_id != teacher_id:
                raise ValueError("只有创建教师可以结束考勤")
            
            # 验证状态
            if attendance.status == AttendanceStatus.ENDED:
                raise ValueError("考勤已结束")
            
            attendance.end()
            logger.info(f"Attendance ended: {attendance_id}")
            return attendance
            
        except ValueError as e:
            logger.warning(f"Validation error ending attendance: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error ending attendance: {str(e)}")
            raise
    
    @staticmethod
    def get_attendance_detail(attendance_id: int) -> Optional[Dict[str, Any]]:
        """
        获取考勤详情（包含统计信息）
        
        Args:
            attendance_id: 考勤ID
            
        Returns:
            考勤详情字典
        """
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return None
        
        # 获取课程和教师信息
        course = Course.query.get(attendance.course_id)
        teacher = User.query.get(attendance.teacher_id)
        
        detail = attendance.to_dict()
        detail['course_name'] = course.name if course else None
        detail['teacher_name'] = teacher.real_name if teacher else None
        detail['present_count'] = attendance.get_present_count()
        detail['late_count'] = attendance.get_late_count()
        detail['absent_count'] = attendance.get_absent_count()
        detail['leave_count'] = attendance.get_leave_count()
        detail['attendance_rate'] = attendance.get_attendance_rate()
        
        return detail
