"""
学生端考勤业务逻辑服务
"""
from typing import Optional, Dict, Any
from datetime import datetime
from app.models.attendance import Attendance, AttendanceRecord, AttendanceStatus
from app.models.course import Course
from app.models.user import User
from app.extensions import db
import logging

logger = logging.getLogger(__name__)


class StudentAttendanceService:
    """学生端考勤业务逻辑服务"""
    
    @staticmethod
    def get_student_attendances(
        student_id: int,
        page: int = 1,
        per_page: int = 20,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        获取学生的考勤通知列表
        
        Args:
            student_id: 学生ID
            page: 页码
            per_page: 每页数量
            status: 状态筛选
            
        Returns:
            包含考勤列表和分页信息的字典
        """
        try:
            # 获取学生信息
            student = User.query.get(student_id)
            if not student or not student.class_id:
                return {
                    'attendances': [],
                    'total': 0,
                    'page': page,
                    'per_page': per_page,
                    'pages': 0
                }
            
            # 构建查询 - 查询学生所在班级的考勤
            query = Attendance.query.filter_by(class_id=student.class_id)
            
            # 状态筛选 - 将字符串转换为枚举
            if status:
                try:
                    # 将小写字符串转换为大写枚举值
                    status_enum = AttendanceStatus[status.upper()]
                    query = query.filter_by(status=status_enum)
                except (KeyError, AttributeError):
                    # 如果状态值无效，忽略筛选
                    logger.warning(f"Invalid status filter: {status}")
            
            # 按创建时间倒序排列
            query = query.order_by(Attendance.created_at.desc())
            
            # 分页
            pagination = query.paginate(
                page=page,
                per_page=per_page,
                error_out=False
            )
            
            # 转换为字典并添加额外信息
            attendances = []
            now = datetime.now()
            
            for attendance in pagination.items:
                # 自动更新考勤状态（根据当前时间）
                StudentAttendanceService._update_attendance_status(attendance, now)
                
                attendance_dict = attendance.to_dict()
                
                # 添加驼峰命名字段（兼容前端）
                attendance_dict['startTime'] = attendance_dict.get('start_time')
                attendance_dict['endTime'] = attendance_dict.get('end_time')
                attendance_dict['attendanceType'] = attendance_dict.get('attendance_type')
                attendance_dict['qrCode'] = attendance_dict.get('qr_code')
                attendance_dict['gesturePattern'] = attendance_dict.get('gesture_pattern')
                attendance_dict['locationName'] = attendance_dict.get('location_name')
                attendance_dict['locationLatitude'] = attendance_dict.get('location_latitude')
                attendance_dict['locationLongitude'] = attendance_dict.get('location_longitude')
                attendance_dict['locationRadius'] = attendance_dict.get('location_radius')
                attendance_dict['courseId'] = attendance_dict.get('course_id')
                attendance_dict['classId'] = attendance_dict.get('class_id')
                attendance_dict['teacherId'] = attendance_dict.get('teacher_id')
                attendance_dict['createdAt'] = attendance_dict.get('created_at')
                attendance_dict['updatedAt'] = attendance_dict.get('updated_at')
                
                # 添加课程名称
                if attendance.course_id:
                    course = Course.query.get(attendance.course_id)
                    if course:
                        attendance_dict['course_name'] = course.name
                        attendance_dict['courseName'] = course.name
                
                # 添加教师名称
                if attendance.teacher_id:
                    teacher = User.query.get(attendance.teacher_id)
                    if teacher:
                        attendance_dict['teacher_name'] = teacher.real_name
                        attendance_dict['teacherName'] = teacher.real_name
                
                # 获取学生的签到记录
                record = AttendanceRecord.query.filter_by(
                    attendance_id=attendance.id,
                    student_id=student_id
                ).first()
                
                if record:
                    record_dict = record.to_dict()
                    # 为记录也添加驼峰命名字段
                    record_dict['checkInTime'] = record_dict.get('check_in_time')
                    record_dict['studentId'] = record_dict.get('student_id')
                    record_dict['attendanceId'] = record_dict.get('attendance_id')
                    record_dict['createdAt'] = record_dict.get('created_at')
                    record_dict['updatedAt'] = record_dict.get('updated_at')
                    
                    attendance_dict['my_record'] = record_dict
                    attendance_dict['myRecord'] = record_dict
                    # 判断是否已签到
                    is_checked_in = record.status in ['present', 'late']
                    attendance_dict['is_checked_in'] = is_checked_in
                    attendance_dict['isCheckedIn'] = is_checked_in
                else:
                    attendance_dict['my_record'] = None
                    attendance_dict['myRecord'] = None
                    attendance_dict['is_checked_in'] = False
                    attendance_dict['isCheckedIn'] = False
                
                attendances.append(attendance_dict)
            
            return {
                'attendances': attendances,
                'total': pagination.total,
                'page': page,
                'per_page': per_page,
                'pages': pagination.pages
            }
            
        except Exception as e:
            logger.error(f"Error getting student attendances: {str(e)}")
            raise
    
    @staticmethod
    def get_student_attendance_detail(
        student_id: int,
        attendance_id: int
    ) -> Optional[Dict[str, Any]]:
        """
        获取学生的考勤详情
        
        Args:
            student_id: 学生ID
            attendance_id: 考勤ID
            
        Returns:
            考勤详情字典，如果不存在或无权访问则返回None
        """
        try:
            # 获取考勤
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤不存在")
            
            # 获取学生信息并验证是否在考勤范围内
            student = User.query.get(student_id)
            if not student or student.class_id != attendance.class_id:
                raise ValueError("您不在该考勤范围内")
            
            # 自动更新考勤状态
            now = datetime.now()
            StudentAttendanceService._update_attendance_status(attendance, now)
            
            # 转换为字典
            attendance_dict = attendance.to_dict()
            
            # 添加驼峰命名字段（兼容前端）
            attendance_dict['startTime'] = attendance_dict.get('start_time')
            attendance_dict['endTime'] = attendance_dict.get('end_time')
            attendance_dict['attendanceType'] = attendance_dict.get('attendance_type')
            attendance_dict['qrCode'] = attendance_dict.get('qr_code')
            attendance_dict['gesturePattern'] = attendance_dict.get('gesture_pattern')
            attendance_dict['locationName'] = attendance_dict.get('location_name')
            attendance_dict['locationLatitude'] = attendance_dict.get('location_latitude')
            attendance_dict['locationLongitude'] = attendance_dict.get('location_longitude')
            attendance_dict['locationRadius'] = attendance_dict.get('location_radius')
            attendance_dict['faceRecognitionThreshold'] = attendance_dict.get('face_recognition_threshold')
            attendance_dict['courseId'] = attendance_dict.get('course_id')
            attendance_dict['classId'] = attendance_dict.get('class_id')
            attendance_dict['teacherId'] = attendance_dict.get('teacher_id')
            attendance_dict['createdAt'] = attendance_dict.get('created_at')
            attendance_dict['updatedAt'] = attendance_dict.get('updated_at')
            
            # 添加课程名称
            if attendance.course_id:
                course = Course.query.get(attendance.course_id)
                if course:
                    attendance_dict['course_name'] = course.name
                    attendance_dict['courseName'] = course.name
            
            # 添加教师名称
            if attendance.teacher_id:
                teacher = User.query.get(attendance.teacher_id)
                if teacher:
                    attendance_dict['teacher_name'] = teacher.real_name
                    attendance_dict['teacherName'] = teacher.real_name
            
            # 获取学生的签到记录
            record = AttendanceRecord.query.filter_by(
                attendance_id=attendance_id,
                student_id=student_id
            ).first()
            
            if record:
                record_dict = record.to_dict()
                # 为记录也添加驼峰命名字段
                record_dict['checkInTime'] = record_dict.get('check_in_time')
                record_dict['studentId'] = record_dict.get('student_id')
                record_dict['attendanceId'] = record_dict.get('attendance_id')
                record_dict['createdAt'] = record_dict.get('created_at')
                record_dict['updatedAt'] = record_dict.get('updated_at')
                
                attendance_dict['my_record'] = record_dict
                attendance_dict['myRecord'] = record_dict
                # 判断是否已签到
                is_checked_in = record.status in ['present', 'late']
                attendance_dict['is_checked_in'] = is_checked_in
                attendance_dict['isCheckedIn'] = is_checked_in
            else:
                attendance_dict['my_record'] = None
                attendance_dict['myRecord'] = None
                attendance_dict['is_checked_in'] = False
                attendance_dict['isCheckedIn'] = False
            
            return attendance_dict
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error getting attendance detail: {str(e)}")
            raise
    
    @staticmethod
    def _update_attendance_status(attendance: Attendance, now: datetime) -> None:
        """
        根据当前时间自动更新考勤状态
        
        Args:
            attendance: 考勤对象
            now: 当前时间
        """
        try:
            # 如果考勤已手动结束，不再自动更新
            if attendance.status == AttendanceStatus.ENDED:
                return
            
            # 根据时间判断状态
            if now < attendance.start_time:
                # 还未开始
                if attendance.status != AttendanceStatus.PENDING:
                    attendance.status = AttendanceStatus.PENDING
                    db.session.commit()
                    logger.info(f"Attendance {attendance.id} status updated to PENDING")
            elif attendance.start_time <= now <= attendance.end_time:
                # 进行中
                if attendance.status != AttendanceStatus.ACTIVE:
                    attendance.status = AttendanceStatus.ACTIVE
                    db.session.commit()
                    logger.info(f"Attendance {attendance.id} status updated to ACTIVE")
            else:
                # 已结束
                if attendance.status != AttendanceStatus.ENDED:
                    attendance.status = AttendanceStatus.ENDED
                    db.session.commit()
                    logger.info(f"Attendance {attendance.id} status updated to ENDED")
        except Exception as e:
            logger.error(f"Error updating attendance status: {str(e)}")
            db.session.rollback()
