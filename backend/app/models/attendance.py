"""
考勤管理模块模型

包含考勤任务、考勤记录、考勤统计等相关模型定义。
"""
from app.extensions import db
from .base import BaseModel
from enum import Enum


class AttendanceType(Enum):
    """考勤方式枚举"""
    QRCODE = 'qrcode'  # 二维码签到
    MANUAL = 'manual'  # 手动签到
    FACE = 'face'      # 人脸识别签到


class AttendanceStatus(Enum):
    """考勤状态枚举"""
    PENDING = 'pending'  # 待开始
    ACTIVE = 'active'    # 进行中
    ENDED = 'ended'      # 已结束


class CheckInStatus(Enum):
    """签到状态枚举"""
    PRESENT = 'present'  # 出勤
    LATE = 'late'        # 迟到
    ABSENT = 'absent'    # 缺勤
    LEAVE = 'leave'      # 请假


class Attendance(BaseModel):
    """考勤任务模型
    
    教师创建的考勤任务。
    """
    __tablename__ = 'attendances'
    
    # ==================== 字段定义 ====================
    # 基本信息
    title = db.Column(db.String(100), nullable=False)
    location = db.Column(db.String(100), nullable=True)
    
    # 外键关联
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)
    class_id = db.Column(db.Integer, nullable=True, index=True)  # FK→classes.id
    teacher_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 考勤设置
    attendance_type = db.Column(db.Enum(AttendanceType), nullable=False)
    qr_code = db.Column(db.String(255), nullable=True, index=True)
    require_location = db.Column(db.Boolean, default=False, nullable=False)
    
    # 时间
    start_time = db.Column(db.DateTime, nullable=False, index=True)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # 状态
    status = db.Column(db.Enum(AttendanceStatus), default=AttendanceStatus.PENDING, nullable=False)
    
    # ==================== 关系定义 ====================
    # 一对多：考勤记录
    records = db.relationship('AttendanceRecord', backref='attendance', lazy='dynamic', cascade='all, delete-orphan')
    
    # ==================== 实例方法 ====================
    def is_active(self):
        """检查考勤是否进行中"""
        return self.status == AttendanceStatus.ACTIVE
    
    def is_ended(self):
        """检查考勤是否已结束"""
        return self.status == AttendanceStatus.ENDED
    
    def is_teacher(self, user_id):
        """检查是否为创建教师"""
        return self.teacher_id == user_id
    
    def start(self):
        """开始考勤"""
        self.status = AttendanceStatus.ACTIVE
        db.session.commit()
    
    def end(self):
        """结束考勤"""
        self.status = AttendanceStatus.ENDED
        db.session.commit()
    
    def get_present_count(self):
        """获取出勤人数"""
        return self.records.filter_by(status=CheckInStatus.PRESENT).count()
    
    def get_late_count(self):
        """获取迟到人数"""
        return self.records.filter_by(status=CheckInStatus.LATE).count()
    
    def get_absent_count(self):
        """获取缺勤人数"""
        return self.records.filter_by(status=CheckInStatus.ABSENT).count()
    
    def get_leave_count(self):
        """获取请假人数"""
        return self.records.filter_by(status=CheckInStatus.LEAVE).count()
    
    def get_attendance_rate(self):
        """获取出勤率"""
        total = self.records.count()
        if total == 0:
            return 0
        present = self.get_present_count()
        return round((present / total) * 100, 2)
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id):
        """获取课程的所有考勤"""
        return cls.query.filter_by(course_id=course_id).order_by(cls.start_time.desc()).all()
    
    @classmethod
    def get_by_teacher(cls, teacher_id):
        """获取教师创建的所有考勤"""
        return cls.query.filter_by(teacher_id=teacher_id).order_by(cls.start_time.desc()).all()
    
    @classmethod
    def get_by_qr_code(cls, qr_code):
        """根据二维码获取考勤"""
        return cls.query.filter_by(qr_code=qr_code).first()
    
    def __repr__(self):
        return f'<Attendance {self.title}>'


class AttendanceRecord(BaseModel):
    """考勤记录模型
    
    学生的具体签到记录。
    """
    __tablename__ = 'attendance_records'
    
    # ==================== 字段定义 ====================
    # 外键关联
    attendance_id = db.Column(db.Integer, db.ForeignKey('attendances.id'), nullable=False, index=True)
    student_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 签到信息
    status = db.Column(db.Enum(CheckInStatus), nullable=False)
    check_in_time = db.Column(db.DateTime, nullable=True)
    check_in_method = db.Column(db.String(20), nullable=True)  # qrcode/manual/face/location
    
    # 位置信息
    latitude = db.Column(db.Numeric(10, 7), nullable=True)
    longitude = db.Column(db.Numeric(10, 7), nullable=True)
    
    # 人脸识别
    face_image_path = db.Column(db.String(255), nullable=True)
    
    # 备注
    remark = db.Column(db.String(255), nullable=True)
    
    # ==================== 实例方法 ====================
    def is_present(self):
        """检查是否出勤"""
        return self.status == CheckInStatus.PRESENT
    
    def is_late(self):
        """检查是否迟到"""
        return self.status == CheckInStatus.LATE
    
    def is_absent(self):
        """检查是否缺勤"""
        return self.status == CheckInStatus.ABSENT
    
    def is_leave(self):
        """检查是否请假"""
        return self.status == CheckInStatus.LEAVE
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_attendance(cls, attendance_id):
        """获取考勤任务的所有记录"""
        return cls.query.filter_by(attendance_id=attendance_id).all()
    
    @classmethod
    def get_by_student(cls, student_id, attendance_id):
        """获取学生在某次考勤的记录"""
        return cls.query.filter_by(student_id=student_id, attendance_id=attendance_id).first()
    
    def __repr__(self):
        return f'<AttendanceRecord student:{self.student_id} status:{self.status.value}>'


class AttendanceStatistics(BaseModel):
    """考勤统计模型
    
    按课程统计学生的考勤情况。
    """
    __tablename__ = 'attendance_statistics'
    
    # ==================== 字段定义 ====================
    # 外键关联
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    student_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 统计数据
    total_count = db.Column(db.Integer, default=0, nullable=False)
    present_count = db.Column(db.Integer, default=0, nullable=False)
    late_count = db.Column(db.Integer, default=0, nullable=False)
    absent_count = db.Column(db.Integer, default=0, nullable=False)
    leave_count = db.Column(db.Integer, default=0, nullable=False)
    attendance_rate = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    
    # ==================== 实例方法 ====================
    def update_statistics(self):
        """更新统计数据"""
        from .attendance import AttendanceRecord, CheckInStatus
        
        # 获取该学生在该课程的所有考勤记录
        records = db.session.query(AttendanceRecord).join(Attendance).filter(
            Attendance.course_id == self.course_id,
            AttendanceRecord.student_id == self.student_id
        ).all()
        
        self.total_count = len(records)
        self.present_count = sum(1 for r in records if r.status == CheckInStatus.PRESENT)
        self.late_count = sum(1 for r in records if r.status == CheckInStatus.LATE)
        self.absent_count = sum(1 for r in records if r.status == CheckInStatus.ABSENT)
        self.leave_count = sum(1 for r in records if r.status == CheckInStatus.LEAVE)
        
        if self.total_count > 0:
            self.attendance_rate = round((self.present_count / self.total_count) * 100, 2)
        else:
            self.attendance_rate = 0.00
        
        db.session.commit()
    
    # ==================== 类方法 ====================
    @classmethod
    def get_or_create(cls, course_id, student_id):
        """获取或创建统计记录"""
        stat = cls.query.filter_by(course_id=course_id, student_id=student_id).first()
        if not stat:
            stat = cls(course_id=course_id, student_id=student_id)
            stat.save()
        return stat
    
    @classmethod
    def get_by_course(cls, course_id):
        """获取课程的所有统计"""
        return cls.query.filter_by(course_id=course_id).all()
    
    @classmethod
    def get_by_student(cls, student_id):
        """获取学生的所有统计"""
        return cls.query.filter_by(student_id=student_id).all()
    
    def __repr__(self):
        return f'<AttendanceStatistics course:{self.course_id} student:{self.student_id}>'
