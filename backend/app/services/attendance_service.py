"""
考勤管理业务逻辑服务
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from app.models.attendance import Attendance, AttendanceRecord, AttendanceStatistics, AttendanceType, AttendanceStatus, CheckInStatus
from app.models.course import Course
from app.models.class_model import Class
from app.models.user import User, UserRole
from app.extensions import db
from app.utils.helpers import generate_random_string
import json
import logging
import hashlib

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
        description: Optional[str] = None,
        gesture_pattern: Optional[Dict[str, Any]] = None,
        location_config: Optional[Dict[str, Any]] = None,
        face_recognition_threshold: Optional[float] = None
    ) -> Attendance:
        """
        创建考勤任务
        
        Args:
            title: 考勤标题
            course_id: 课程ID
            class_ids: 班级ID列表
            teacher_id: 教师ID
            attendance_type: 考勤方式（qrcode/gesture/location/face/manual）
            start_time: 开始时间
            end_time: 结束时间
            student_ids: 指定学生ID列表（可选）
            description: 考勤描述
            gesture_pattern: 手势路径数据（手势签到时必填）
            location_config: 位置配置（位置签到时必填）
            face_recognition_threshold: 人脸识别阈值（人脸签到时可选）
            
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
            
            # 根据考勤方式验证必填参数
            if attendance_type == AttendanceType.GESTURE.value:
                if not gesture_pattern:
                    raise ValueError("手势签到需要提供手势路径数据")
            elif attendance_type == AttendanceType.LOCATION.value:
                if not location_config:
                    raise ValueError("位置签到需要提供位置配置")
            
            # 生成二维码token（如果是二维码签到）
            qr_code = None
            if attendance_type == AttendanceType.QRCODE.value:
                qr_code = generate_random_string(32)
            
            # 处理手势数据（转换为JSON字符串）
            gesture_pattern_json = None
            if gesture_pattern:
                gesture_pattern_json = json.dumps(gesture_pattern)
            
            # 处理位置配置
            location_name = None
            location_latitude = None
            location_longitude = None
            location_radius = 100  # 默认100米
            if location_config:
                location_name = location_config.get('name')
                location_latitude = location_config.get('latitude')
                location_longitude = location_config.get('longitude')
                location_radius = location_config.get('radius', 100)
            
            # 创建考勤任务（为每个班级创建一个考勤任务）
            attendances = []
            for class_id in class_ids:
                attendance = Attendance(
                    title=title,
                    description=description,
                    course_id=course_id,
                    class_id=class_id,
                    teacher_id=teacher_id,
                    attendance_type=AttendanceType(attendance_type),
                    qr_code=qr_code,
                    gesture_pattern=gesture_pattern_json,
                    location_name=location_name,
                    location_latitude=location_latitude,
                    location_longitude=location_longitude,
                    location_radius=location_radius,
                    face_recognition_threshold=face_recognition_threshold,
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
            
            # WebSocket通知：考勤创建
            try:
                from app.websocket.attendance_events import notify_attendance_created
                for attendance in attendances:
                    attendance_dict = attendance.to_dict()
                    # 添加课程和教师信息
                    attendance_dict['course_name'] = course.name
                    attendance_dict['courseName'] = course.name
                    teacher = User.query.get(teacher_id)
                    if teacher:
                        attendance_dict['teacher_name'] = teacher.real_name
                        attendance_dict['teacherName'] = teacher.real_name
                    notify_attendance_created(attendance_dict, attendance.class_id)
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {str(e)}")
            
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
    
    @staticmethod
    def get_attendance_records(attendance_id: int) -> Optional[Dict[str, Any]]:
        """
        获取考勤记录列表
        
        Args:
            attendance_id: 考勤ID
            
        Returns:
            包含记录列表和总数的字典，考勤不存在返回None
        """
        # 验证考勤是否存在
        attendance = Attendance.query.get(attendance_id)
        if not attendance:
            return None
        
        # 获取所有考勤记录
        records = AttendanceRecord.query.filter_by(
            attendance_id=attendance_id
        ).all()
        
        # 转换为字典并添加学生信息
        records_data = []
        for record in records:
            record_dict = record.to_dict()
            # 获取学生信息
            student = User.query.get(record.student_id)
            if student:
                record_dict['student_name'] = student.real_name
                record_dict['student_code'] = student.user_code
                record_dict['student_avatar'] = student.avatar
            else:
                # 学生不存在的情况（可能被删除）
                logger.warning(f"考勤记录 {record.id} 关联的学生 {record.student_id} 不存在")
                record_dict['student_name'] = f'[已删除学生-ID:{record.student_id}]'
                record_dict['student_code'] = 'N/A'
                record_dict['student_avatar'] = None
            records_data.append(record_dict)
        
        return {
            'records': records_data,
            'total': len(records_data)
        }
    
    @staticmethod
    def update_attendance_record(
        attendance_id: int,
        record_id: int,
        teacher_id: int,
        status: str,
        remark: Optional[str] = None
    ) -> Optional[AttendanceRecord]:
        """
        更新考勤记录（教师手动标记）
        
        Args:
            attendance_id: 考勤ID
            record_id: 记录ID
            teacher_id: 教师ID
            status: 新的签到状态
            remark: 备注
            
        Returns:
            更新后的考勤记录，失败返回None
        """
        try:
            # 验证考勤任务是否存在且属于该教师
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                return None
            
            if attendance.teacher_id != teacher_id:
                raise ValueError("只有创建考勤的教师可以修改记录")
            
            # 获取考勤记录
            record = AttendanceRecord.query.filter_by(
                id=record_id,
                attendance_id=attendance_id
            ).first()
            
            if not record:
                return None
            
            # 更新状态
            record.status = CheckInStatus(status)
            if remark is not None:
                record.remark = remark
            
            # 如果标记为出勤或迟到，记录签到时间
            if status in ['present', 'late'] and not record.check_in_time:
                from datetime import datetime
                record.check_in_time = datetime.now()
                record.check_in_method = 'manual'  # 手动标记
            
            db.session.commit()
            logger.info(f"Record {record_id} updated to {status} by teacher {teacher_id}")
            
            return record
            
        except ValueError as e:
            db.session.rollback()
            logger.warning(f"Validation error updating record: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error updating record: {str(e)}")
            raise
    
    @staticmethod
    def generate_qrcode_token(attendance_id: int, teacher_id: int, token: str = None) -> Dict[str, Any]:
        """
        生成二维码令牌
        
        Args:
            attendance_id: 考勤ID
            teacher_id: 教师ID（用于权限验证）
            token: 前端生成的token（可选，如果不提供则后端生成）
            
        Returns:
            包含二维码令牌和过期时间的字典
        """
        try:
            # 验证考勤任务是否存在
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证权限
            if attendance.teacher_id != teacher_id:
                raise ValueError("只有创建教师可以生成二维码")
            
            # 验证考勤类型
            if attendance.attendance_type != AttendanceType.QRCODE:
                raise ValueError("只有二维码签到方式才能生成二维码")
            
            # 使用前端传来的token，或者后端生成
            if token:
                qr_code_token = token
                logger.info(f"使用前端生成的token: {qr_code_token}")
            else:
                # 生成新的二维码令牌（包含时间戳）
                import time
                timestamp = int(time.time())
                random_part = generate_random_string(24)
                qr_code_token = f"{timestamp}_{random_part}"
                logger.info(f"后端生成token: {qr_code_token}")
            
            # 计算过期时间（30分钟，延长有效期避免扫码后过期）
            valid_duration = 1800  # 30分钟
            expires_at = datetime.now() + timedelta(seconds=valid_duration)
            
            # 更新考勤任务的二维码令牌
            attendance.qr_code = qr_code_token
            db.session.commit()
            logger.info(f"已更新数据库中的token: {qr_code_token}")
            
            # 生成二维码数据（JSON格式）
            qr_code_data = json.dumps({
                'type': 'attendance_qrcode',
                'attendance_id': attendance_id,
                'token': qr_code_token,
                'timestamp': datetime.now().isoformat(),
                'expires_at': expires_at.isoformat()
            })
            
            logger.info(f"QR code generated for attendance {attendance_id}")
            
            return {
                'qr_code_token': qr_code_token,
                'qr_code_data': qr_code_data,
                'expires_at': expires_at.isoformat(),
                'valid_duration': valid_duration
            }
            
        except ValueError as e:
            logger.warning(f"Validation error generating QR code: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error generating QR code: {str(e)}")
            raise
    
    @staticmethod
    def refresh_qrcode_token(attendance_id: int, teacher_id: int) -> Dict[str, Any]:
        """
        刷新二维码令牌（使旧令牌失效）
        
        Args:
            attendance_id: 考勤ID
            teacher_id: 教师ID
            
        Returns:
            新的二维码令牌信息
        """
        # 刷新实际上就是重新生成
        return AttendanceService.generate_qrcode_token(attendance_id, teacher_id)
    
    @staticmethod
    def verify_qrcode_and_checkin(
        student_id: int,
        attendance_id: int,
        qr_code_token: str
    ) -> AttendanceRecord:
        """
        验证二维码并完成签到
        
        Args:
            student_id: 学生ID
            attendance_id: 考勤ID
            qr_code_token: 二维码令牌
            
        Returns:
            更新后的考勤记录
        """
        try:
            # 验证考勤任务是否存在
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证考勤时间（使用本地时间）
            from datetime import datetime
            import pytz
            
            # 获取当前本地时间
            local_tz = pytz.timezone('Asia/Shanghai')  # 中国时区
            now = datetime.now(local_tz)
            
            # 确保考勤时间也是本地时区
            start_time = attendance.start_time
            end_time = attendance.end_time
            
            # 如果数据库时间是naive（无时区），假设为本地时间
            if start_time.tzinfo is None:
                start_time = local_tz.localize(start_time)
            if end_time.tzinfo is None:
                end_time = local_tz.localize(end_time)
            
            # 验证考勤时间
            if now < start_time:
                raise ValueError(f"考勤未开始，开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if now > end_time:
                raise ValueError(f"考勤已结束，结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            logger.info(f"时间验证通过 - 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}, 开始: {start_time.strftime('%Y-%m-%d %H:%M:%S')}, 结束: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 验证考勤类型
            if attendance.attendance_type != AttendanceType.QRCODE:
                raise ValueError("该考勤不是二维码签到方式")
            
            # 验证二维码令牌
            logger.info(f"=== 二维码验证 ===")
            logger.info(f"数据库中的token: {attendance.qr_code}")
            logger.info(f"提交的token: {qr_code_token}")
            logger.info(f"token是否匹配: {attendance.qr_code == qr_code_token}")
            
            if not attendance.qr_code:
                raise ValueError("考勤任务未生成二维码，请教师先生成二维码")
            
            if attendance.qr_code != qr_code_token:
                raise ValueError(f"二维码token不匹配。数据库token长度:{len(attendance.qr_code)}, 提交token长度:{len(qr_code_token)}")
            
            # 【临时禁用】验证二维码是否过期（检查token中的时间戳）
            # 注释原因：跳过过期验证，允许所有二维码通过
            logger.info(f"二维码验证通过（已禁用过期检查）")
            
            # import time
            # token_parts = qr_code_token.split('_')
            # if len(token_parts) >= 2:
            #     try:
            #         token_timestamp = int(token_parts[0])
            #         current_timestamp = int(time.time())
            #         token_age = current_timestamp - token_timestamp
            #         
            #         logger.info(f"二维码时间验证 - 生成于{token_age}秒前（{token_age//60}分钟前）")
            #         
            #         # 30分钟有效期
            #         if token_age > 1800:
            #             raise ValueError(f"二维码已过期（生成于{token_age//60}分钟前）")
            #         
            #         logger.info(f"二维码时间验证通过")
            #     except ValueError as e:
            #         # 如果是时间戳格式错误，记录警告但继续
            #         if "二维码已过期" in str(e):
            #             # 这是真正的过期错误，需要抛出
            #             raise
            #         else:
            #             # 时间戳格式错误，跳过时间验证
            #             logger.warning(f"无法解析二维码时间戳: {e}")
            # else:
            #     # 旧格式的token（没有时间戳），跳过时间验证
            #     logger.info(f"使用旧格式二维码（无时间戳），跳过时间验证")
            
            # 验证学生是否存在
            student = User.query.get(student_id)
            if not student or student.role != UserRole.STUDENT:
                raise ValueError("学生不存在")
            
            # 获取考勤记录
            record = AttendanceRecord.query.filter_by(
                attendance_id=attendance_id,
                student_id=student_id
            ).first()
            
            if not record:
                raise ValueError("未找到该学生的考勤记录，请确认是否在考勤范围内")
            
            # 检查是否已经签到
            if record.status in [CheckInStatus.PRESENT, CheckInStatus.LATE]:
                raise ValueError("已经签到，请勿重复签到")
            
            # 判断是否迟到（开始时间后15分钟为迟到）
            now = datetime.now()
            late_threshold = attendance.start_time + timedelta(minutes=15)
            
            if now <= late_threshold:
                record.status = CheckInStatus.PRESENT
            else:
                record.status = CheckInStatus.LATE
            
            # 记录签到信息
            record.check_in_time = now
            record.check_in_method = 'qrcode'
            
            db.session.commit()
            logger.info(f"Student {student_id} checked in for attendance {attendance_id} via QR code")
            
            # WebSocket通知：学生签到成功
            try:
                from app.websocket.attendance_events import notify_student_checked_in
                student = User.query.get(student_id)
                if student:
                    student_data = {
                        'id': student.id,
                        'real_name': student.real_name,
                        'user_code': student.user_code
                    }
                    record_data = record.to_dict()
                    notify_student_checked_in(attendance_id, student_data, record_data)
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {str(e)}")
            
            return record
            
        except ValueError as e:
            logger.warning(f"Validation error in QR code check-in: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in QR code check-in: {str(e)}")
            raise
    
    @staticmethod
    def verify_gesture_and_checkin(
        student_id: int,
        attendance_id: int,
        gesture_code: str,
        gesture_pattern: Optional[Dict[str, Any]] = None
    ) -> AttendanceRecord:
        """
        验证手势码并完成签到
        
        Args:
            student_id: 学生ID
            attendance_id: 考勤ID
            gesture_code: 手势码
            
        Returns:
            更新后的考勤记录
        """
        try:
            # 验证考勤任务是否存在
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证考勤状态
            if attendance.status != AttendanceStatus.ACTIVE:
                raise ValueError("考勤未开始或已结束")
            
            # 验证考勤类型
            if attendance.attendance_type != AttendanceType.GESTURE:
                raise ValueError("该考勤不是手势签到方式")
            
            # 验证手势码
            if not attendance.gesture_pattern:
                raise ValueError("该考勤未设置手势码")
            
            # 解析数据库中的手势数据（JSON格式）
            try:
                import json
                stored_gesture_data = json.loads(attendance.gesture_pattern)
                stored_points = stored_gesture_data.get('points', [])
                
                logger.info(f"Database stored_points: {stored_points}, type: {type(stored_points)}")
                logger.info(f"Student gesture_pattern: {gesture_pattern}")
                logger.info(f"Student gesture_code: {gesture_code}")
                
                # 优先使用完整的gesture_pattern进行比较
                if gesture_pattern and 'points' in gesture_pattern:
                    student_points = gesture_pattern['points']
                    logger.info(f"Student points: {student_points}, type: {type(student_points)}")
                    
                    # 检查stored_points是坐标对象还是索引
                    if stored_points and isinstance(stored_points[0], dict) and 'x' in stored_points[0]:
                        # 数据库存储的是坐标对象，需要转换为索引
                        # 3x3网格的坐标映射
                        coord_to_index = {}
                        positions = [50, 150, 250]
                        index = 0
                        for row in positions:
                            for col in positions:
                                coord_to_index[f"{col},{row}"] = index
                                index += 1
                        
                        # 将坐标转换为索引
                        stored_indices = []
                        for point in stored_points:
                            key = f"{int(point['x'])},{int(point['y'])}"
                            if key in coord_to_index:
                                stored_indices.append(coord_to_index[key])
                        
                        logger.info(f"Converted stored coords to indices: {stored_indices}")
                        stored_list = stored_indices
                    else:
                        # 数据库存储的就是索引
                        stored_list = list(stored_points) if not isinstance(stored_points, list) else stored_points
                    
                    # 学生端发送的是索引
                    student_list = list(student_points) if not isinstance(student_points, list) else student_points
                    
                    logger.info(f"Final comparison: {stored_list} vs {student_list}")
                    
                    if stored_list != student_list:
                        raise ValueError(f"手势不匹配。数据库：{stored_list}，学生：{student_list}")
                else:
                    # 降级方案：使用gesture_code字符串比较
                    if stored_points and isinstance(stored_points[0], (int, float)):
                        stored_code = '-'.join(map(str, map(int, stored_points)))
                    else:
                        stored_code = '-'.join(map(str, stored_points))
                    
                    logger.info(f"Comparing codes: {stored_code} vs {gesture_code}")
                    
                    if stored_code != gesture_code:
                        raise ValueError(f"手势码不匹配")
                        
            except json.JSONDecodeError as e:
                logger.error(f"JSON decode error: {str(e)}")
                raise ValueError("手势数据格式错误")
            
            # 验证学生是否存在
            student = User.query.get(student_id)
            if not student or student.role != UserRole.STUDENT:
                raise ValueError("学生不存在")
            
            # 获取考勤记录
            record = AttendanceRecord.query.filter_by(
                attendance_id=attendance_id,
                student_id=student_id
            ).first()
            
            if not record:
                raise ValueError("未找到该学生的考勤记录，请确认是否在考勤范围内")
            
            # 检查是否已经签到
            if record.status in [CheckInStatus.PRESENT, CheckInStatus.LATE]:
                raise ValueError("已经签到，请勿重复签到")
            
            # 判断是否迟到（开始时间后15分钟为迟到）
            now = datetime.now()
            late_threshold = attendance.start_time + timedelta(minutes=15)
            
            if now <= late_threshold:
                record.status = CheckInStatus.PRESENT
            else:
                record.status = CheckInStatus.LATE
            
            # 记录签到信息
            record.check_in_time = now
            record.check_in_method = 'gesture'
            
            db.session.commit()
            logger.info(f"Student {student_id} checked in for attendance {attendance_id} via gesture")
            
            # WebSocket通知：学生签到成功
            try:
                from app.websocket.attendance_events import notify_student_checked_in
                student = User.query.get(student_id)
                if student:
                    student_data = {
                        'id': student.id,
                        'real_name': student.real_name,
                        'user_code': student.user_code
                    }
                    record_data = record.to_dict()
                    notify_student_checked_in(attendance_id, student_data, record_data)
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {str(e)}")
            
            return record
            
        except ValueError as e:
            logger.warning(f"Validation error in gesture check-in: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in gesture check-in: {str(e)}")
            raise
    
    @staticmethod
    def verify_location_and_checkin(
        student_id: int,
        attendance_id: int,
        latitude: float,
        longitude: float
    ) -> AttendanceRecord:
        """
        验证位置并完成签到
        
        Args:
            student_id: 学生ID
            attendance_id: 考勤ID
            latitude: 纬度
            longitude: 经度
            
        Returns:
            更新后的考勤记录
        """
        try:
            # 验证考勤任务是否存在
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证考勤状态
            if attendance.status != AttendanceStatus.ACTIVE:
                raise ValueError("考勤未开始或已结束")
            
            # 验证考勤类型
            if attendance.attendance_type != AttendanceType.LOCATION:
                raise ValueError("该考勤不是位置签到方式")
            
            # 验证位置范围
            if not attendance.location_latitude or not attendance.location_longitude:
                raise ValueError("考勤未设置位置信息")
            
            # 计算距离（使用Haversine公式）
            # 将Decimal类型转换为float
            target_lat = float(attendance.location_latitude)
            target_lon = float(attendance.location_longitude)
            
            distance = AttendanceService._calculate_distance(
                latitude, longitude,
                target_lat, target_lon
            )
            
            # 验证是否在允许范围内（默认100米）
            allowed_range = int(attendance.location_radius) if attendance.location_radius else 100
            if distance > allowed_range:
                raise ValueError(f"您不在签到范围内（距离: {distance:.0f}米，要求: {allowed_range}米）")
            
            # 验证学生是否存在
            student = User.query.get(student_id)
            if not student or student.role != UserRole.STUDENT:
                raise ValueError("学生不存在")
            
            # 获取考勤记录
            record = AttendanceRecord.query.filter_by(
                attendance_id=attendance_id,
                student_id=student_id
            ).first()
            
            if not record:
                raise ValueError("未找到该学生的考勤记录，请确认是否在考勤范围内")
            
            # 检查是否已经签到
            if record.status in [CheckInStatus.PRESENT, CheckInStatus.LATE]:
                raise ValueError("已经签到，请勿重复签到")
            
            # 判断是否迟到（开始时间后15分钟为迟到）
            now = datetime.now()
            late_threshold = attendance.start_time + timedelta(minutes=15)
            
            if now <= late_threshold:
                record.status = CheckInStatus.PRESENT
            else:
                record.status = CheckInStatus.LATE
            
            # 记录签到信息
            from decimal import Decimal
            record.check_in_time = now
            record.check_in_method = 'location'
            record.latitude = Decimal(str(latitude))  # 转换为Decimal
            record.longitude = Decimal(str(longitude))  # 转换为Decimal
            record.distance = int(distance)  # 记录距离（米）
            
            db.session.commit()
            logger.info(f"Student {student_id} checked in for attendance {attendance_id} via location (distance: {distance:.2f}m)")
            
            # WebSocket通知：学生签到成功
            try:
                from app.websocket.attendance_events import notify_student_checked_in
                student = User.query.get(student_id)
                if student:
                    student_data = {
                        'id': student.id,
                        'real_name': student.real_name,
                        'user_code': student.user_code
                    }
                    record_data = record.to_dict()
                    record_data['distance'] = round(distance, 2)
                    notify_student_checked_in(attendance_id, student_data, record_data)
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {str(e)}")
            
            return record
            
        except ValueError as e:
            logger.warning(f"Validation error in location check-in: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in location check-in: {str(e)}")
            logger.error(f"Error type: {type(e).__name__}")
            logger.error(f"Attendance ID: {attendance_id}, Student ID: {student_id}")
            logger.error(f"Location: lat={latitude}, lon={longitude}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
            raise
    
    @staticmethod
    def _calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        使用Haversine公式计算两个经纬度坐标之间的距离（单位：米）
        
        Args:
            lat1: 第一个点的纬度
            lon1: 第一个点的经度
            lat2: 第二个点的纬度
            lon2: 第二个点的经度
            
        Returns:
            距离（米）
        """
        from math import radians, sin, cos, sqrt, atan2
        
        # 地球半径（米）
        R = 6371000
        
        # 转换为弧度
        lat1_rad = radians(lat1)
        lat2_rad = radians(lat2)
        delta_lat = radians(lat2 - lat1)
        delta_lon = radians(lon2 - lon1)
        
        # Haversine公式
        a = sin(delta_lat / 2) ** 2 + cos(lat1_rad) * cos(lat2_rad) * sin(delta_lon / 2) ** 2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))
        distance = R * c
        
        return distance
    
    @staticmethod
    def student_checkin(
        student_id: int,
        attendance_id: int,
        face_image: Optional[str] = None,
        face_similarity: Optional[float] = None
    ) -> AttendanceRecord:
        """
        学生签到（人脸验证签到）
        
        Args:
            student_id: 学生ID
            attendance_id: 考勤ID
            face_image: 人脸图片Base64（可选）
            face_similarity: 人脸相似度（可选）
            
        Returns:
            更新后的考勤记录
        """
        try:
            # 验证考勤任务是否存在
            attendance = Attendance.query.get(attendance_id)
            if not attendance:
                raise ValueError("考勤任务不存在")
            
            # 验证考勤时间
            from datetime import datetime
            import pytz
            
            # 获取当前本地时间
            local_tz = pytz.timezone('Asia/Shanghai')
            now = datetime.now(local_tz)
            
            # 确保考勤时间也是本地时区
            start_time = attendance.start_time
            end_time = attendance.end_time
            
            if start_time.tzinfo is None:
                start_time = local_tz.localize(start_time)
            if end_time.tzinfo is None:
                end_time = local_tz.localize(end_time)
            
            # 验证考勤时间
            if now < start_time:
                raise ValueError(f"考勤未开始，开始时间: {start_time.strftime('%Y-%m-%d %H:%M:%S')}")
            if now > end_time:
                raise ValueError(f"考勤已结束，结束时间: {end_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            logger.info(f"时间验证通过 - 当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # 验证学生是否存在
            student = User.query.get(student_id)
            if not student or student.role != UserRole.STUDENT:
                raise ValueError("学生不存在")
            
            # 获取考勤记录
            record = AttendanceRecord.query.filter_by(
                attendance_id=attendance_id,
                student_id=student_id
            ).first()
            
            if not record:
                raise ValueError("未找到该学生的考勤记录，请确认是否在考勤范围内")
            
            # 检查是否已经签到
            if record.status in [CheckInStatus.PRESENT, CheckInStatus.LATE]:
                raise ValueError("已经签到，请勿重复签到")
            
            # 判断是否迟到（开始时间后15分钟为迟到）
            now_naive = datetime.now()
            late_threshold = attendance.start_time + timedelta(minutes=15)
            
            if now_naive <= late_threshold:
                record.status = CheckInStatus.PRESENT
            else:
                record.status = CheckInStatus.LATE
            
            # 记录签到信息
            from decimal import Decimal
            record.check_in_time = now_naive
            record.check_in_method = 'face'
            
            # 保存人脸相似度信息
            if face_similarity is not None:
                # 将相似度转换为Decimal类型（百分比形式，如90.00）
                record.face_similarity = Decimal(str(face_similarity * 100))
                record.remark = f"人脸相似度: {face_similarity:.1%}"
            
            # 保存人脸图片路径（如果有）
            if face_image:
                # 这里可以保存图片，但由于临时禁用验证，暂不处理
                pass
            
            db.session.commit()
            logger.info(f"Student {student_id} checked in for attendance {attendance_id} via face recognition (similarity: {face_similarity:.1%} [临时固定])")
            
            # WebSocket通知：学生签到成功
            try:
                from app.websocket.attendance_events import notify_student_checked_in
                student_data = {
                    'id': student.id,
                    'real_name': student.real_name,
                    'user_code': student.user_code
                }
                record_data = record.to_dict()
                notify_student_checked_in(attendance_id, student_data, record_data)
            except Exception as e:
                logger.error(f"Error sending WebSocket notification: {str(e)}")
            
            return record
            
        except ValueError as e:
            logger.warning(f"Validation error in face check-in: {str(e)}")
            raise
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error in face check-in: {str(e)}")
            raise
    
    @staticmethod
    def get_course_statistics(course_id: int) -> dict:
        """
        获取指定课程的考勤统计数据
        
        Args:
            course_id: 课程ID
            
        Returns:
            统计数据字典
        """
        from app.models.course import Course
        from sqlalchemy import func
        from datetime import datetime, timedelta
        
        try:
            # 验证课程是否存在
            course = Course.query.get(course_id)
            if not course:
                raise ValueError("课程不存在")
            
            # 获取该课程的所有考勤任务
            attendances = Attendance.query.filter_by(course_id=course_id).all()
            
            if not attendances:
                # 返回空统计数据
                return {
                    'total_check_ins': 0,
                    'present_count': 0,
                    'late_count': 0,
                    'absent_count': 0,
                    'perfect_attendance_count': 0,
                    'warning_count': 0,
                    'attendance_rate': 0.0,
                    'total_tasks': 0,
                    'total_students': 0,
                    'date_statistics': [],
                    'type_statistics': {},
                    'perfect_attendance_students': [],
                    'warning_students': []
                }
            
            attendance_ids = [a.id for a in attendances]
            
            # 1. 总体统计
            total_records = AttendanceRecord.query.filter(
                AttendanceRecord.attendance_id.in_(attendance_ids)
            ).all()
            
            present_count = sum(1 for r in total_records if r.status == CheckInStatus.PRESENT)
            late_count = sum(1 for r in total_records if r.status == CheckInStatus.LATE)
            absent_count = sum(1 for r in total_records if r.status == CheckInStatus.ABSENT)
            total_check_ins = present_count + late_count
            
            # 计算平均出勤率
            total_expected = len(total_records)
            attendance_rate = (total_check_ins / total_expected * 100) if total_expected > 0 else 0.0
            
            # 2. 学生统计
            # 获取所有学生的考勤记录
            from collections import defaultdict
            student_stats = defaultdict(lambda: {'present': 0, 'late': 0, 'absent': 0, 'total': 0})
            
            for record in total_records:
                student_id = record.student_id
                student_stats[student_id]['total'] += 1
                if record.status == CheckInStatus.PRESENT:
                    student_stats[student_id]['present'] += 1
                elif record.status == CheckInStatus.LATE:
                    student_stats[student_id]['late'] += 1
                elif record.status == CheckInStatus.ABSENT:
                    student_stats[student_id]['absent'] += 1
            
            # 全勤学生（出勤+迟到=总次数）
            perfect_students = []
            warning_students = []
            
            for student_id, stats in student_stats.items():
                student = User.query.get(student_id)
                if not student:
                    continue
                
                # 全勤：缺勤次数为0
                if stats['absent'] == 0 and stats['total'] > 0:
                    perfect_students.append({
                        'id': student.id,
                        'name': student.real_name,
                        'user_code': student.user_code
                    })
                
                # 预警：缺勤次数>=3
                if stats['absent'] >= 3:
                    warning_students.append({
                        'id': student.id,
                        'name': student.real_name,
                        'user_code': student.user_code,
                        'absent_count': stats['absent']
                    })
            
            # 3. 日期统计（最近7天）
            today = datetime.now().date()
            date_stats = []
            
            for i in range(6, -1, -1):
                target_date = today - timedelta(days=i)
                
                # 获取该日期的考勤记录
                day_records = [
                    r for r in total_records
                    if r.check_in_time and r.check_in_time.date() == target_date
                ]
                
                day_present = sum(1 for r in day_records if r.status == CheckInStatus.PRESENT)
                day_late = sum(1 for r in day_records if r.status == CheckInStatus.LATE)
                day_absent = sum(1 for r in day_records if r.status == CheckInStatus.ABSENT)
                
                date_stats.append({
                    'date': target_date.isoformat(),
                    'date_display': target_date.strftime('%m/%d'),
                    'present': day_present,
                    'late': day_late,
                    'absent': day_absent
                })
            
            # 4. 考勤方式统计
            type_stats = defaultdict(lambda: {'name': '', 'count': 0})
            
            for record in total_records:
                if record.check_in_method:
                    method = record.check_in_method
                    type_stats[method]['name'] = method
                    type_stats[method]['count'] += 1
            
            # 转换为字典
            type_statistics = {k: v for k, v in type_stats.items()}
            
            # 获取总学生数
            total_students = len(student_stats)
            
            return {
                'total_check_ins': total_check_ins,
                'present_count': present_count,
                'late_count': late_count,
                'absent_count': absent_count,
                'perfect_attendance_count': len(perfect_students),
                'warning_count': len(warning_students),
                'attendance_rate': round(attendance_rate, 2),
                'total_tasks': len(attendances),
                'total_students': total_students,
                'date_statistics': date_stats,
                'type_statistics': type_statistics,
                'perfect_attendance_students': perfect_students,
                'warning_students': warning_students
            }
            
        except ValueError as e:
            logger.warning(f"Validation error in get_course_statistics: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in get_course_statistics: {str(e)}")
            raise
    
    @staticmethod
    def get_student_statistics(student_id: int) -> dict:
        """
        获取学生的考勤统计数据
        
        Args:
            student_id: 学生ID
            
        Returns:
            统计数据字典
        """
        from app.models.course import Course
        from datetime import datetime, timedelta
        from collections import defaultdict
        
        try:
            # 验证学生是否存在
            student = User.query.get(student_id)
            if not student or student.role != UserRole.STUDENT:
                raise ValueError("学生不存在")
            
            # 获取该学生的所有考勤记录
            all_records = AttendanceRecord.query.filter_by(student_id=student_id).all()
            
            if not all_records:
                # 返回空统计数据
                return {
                    'total_records': 0,
                    'present_count': 0,
                    'late_count': 0,
                    'absent_count': 0,
                    'leave_count': 0,
                    'attendance_rate': 0.0,
                    'date_statistics': [],
                    'course_statistics': [],
                    'recent_records': []
                }
            
            # 1. 总体统计
            present_count = sum(1 for r in all_records if r.status == CheckInStatus.PRESENT)
            late_count = sum(1 for r in all_records if r.status == CheckInStatus.LATE)
            absent_count = sum(1 for r in all_records if r.status == CheckInStatus.ABSENT)
            leave_count = sum(1 for r in all_records if r.status == CheckInStatus.LEAVE)
            
            # 计算出勤率（出勤+迟到）/总数
            total_records = len(all_records)
            attendance_rate = ((present_count + late_count) / total_records * 100) if total_records > 0 else 0.0
            
            # 2. 日期统计（最近30天）
            today = datetime.now().date()
            date_stats = []
            
            for i in range(29, -1, -1):
                target_date = today - timedelta(days=i)
                
                # 获取该日期的考勤记录
                day_records = [
                    r for r in all_records
                    if r.check_in_time and r.check_in_time.date() == target_date
                ]
                
                day_present = sum(1 for r in day_records if r.status == CheckInStatus.PRESENT)
                day_late = sum(1 for r in day_records if r.status == CheckInStatus.LATE)
                day_absent = sum(1 for r in day_records if r.status == CheckInStatus.ABSENT)
                
                date_stats.append({
                    'date': target_date.isoformat(),
                    'date_display': target_date.strftime('%m/%d'),
                    'present': day_present,
                    'late': day_late,
                    'absent': day_absent
                })
            
            # 3. 按课程统计
            course_stats_dict = defaultdict(lambda: {'present': 0, 'late': 0, 'absent': 0, 'total': 0})
            
            for record in all_records:
                attendance = Attendance.query.get(record.attendance_id)
                if not attendance:
                    continue
                
                course_id = attendance.course_id
                course_stats_dict[course_id]['total'] += 1
                
                if record.status == CheckInStatus.PRESENT:
                    course_stats_dict[course_id]['present'] += 1
                elif record.status == CheckInStatus.LATE:
                    course_stats_dict[course_id]['late'] += 1
                elif record.status == CheckInStatus.ABSENT:
                    course_stats_dict[course_id]['absent'] += 1
            
            # 转换为列表并添加课程信息
            course_statistics = []
            for course_id, stats in course_stats_dict.items():
                course = Course.query.get(course_id)
                if not course:
                    continue
                
                total = stats['total']
                attendance_count = stats['present'] + stats['late']
                course_rate = (attendance_count / total * 100) if total > 0 else 0.0
                
                course_statistics.append({
                    'course_id': course_id,
                    'course_name': course.name,
                    'present': stats['present'],
                    'late': stats['late'],
                    'absent': stats['absent'],
                    'total': total,
                    'attendance_rate': round(course_rate, 2)
                })
            
            # 按出勤率排序
            course_statistics.sort(key=lambda x: x['attendance_rate'], reverse=True)
            
            # 4. 最近10条考勤记录
            recent_records_data = sorted(all_records, key=lambda x: x.created_at, reverse=True)[:10]
            recent_records = []
            
            for record in recent_records_data:
                attendance = Attendance.query.get(record.attendance_id)
                if not attendance:
                    continue
                
                course = Course.query.get(attendance.course_id)
                
                recent_records.append({
                    'id': record.id,
                    'title': attendance.title,
                    'course_name': course.name if course else '未知课程',
                    'status': record.status.value if hasattr(record.status, 'value') else record.status,
                    'check_in_time': record.check_in_time.isoformat() if record.check_in_time else None,
                    'created_at': record.created_at.isoformat() if record.created_at else None
                })
            
            return {
                'total_records': total_records,
                'present_count': present_count,
                'late_count': late_count,
                'absent_count': absent_count,
                'leave_count': leave_count,
                'attendance_rate': round(attendance_rate, 2),
                'date_statistics': date_stats,
                'course_statistics': course_statistics,
                'recent_records': recent_records
            }
            
        except ValueError as e:
            logger.warning(f"Validation error in get_student_statistics: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error in get_student_statistics: {str(e)}")
            raise
