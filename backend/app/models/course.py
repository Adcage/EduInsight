"""
课程模块模型

包含课程、课程班级关联等相关模型定义。
"""
from app.extensions import db
from sqlalchemy.orm import foreign
from .base import BaseModel


# ==================== 关联表 ====================
course_classes = db.Table(
    'course_classes',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True),
    db.Column('class_id', db.Integer, db.ForeignKey('classes.id'), nullable=False, index=True),
    db.Column('start_date', db.Date, nullable=True),
    db.Column('end_date', db.Date, nullable=True),
    db.Column('status', db.Boolean, default=True, nullable=False),
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp(), nullable=False),
    db.Column('updated_at', db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False),
    db.UniqueConstraint('course_id', 'class_id', name='uk_course_class')
)


class Course(BaseModel):
    """课程模型
    
    存储课程基本信息。
    """
    __tablename__ = 'courses'
    
    # ==================== 字段定义 ====================
    # 基本信息
    name = db.Column(db.String(100), nullable=False, index=True)
    code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # 教学信息
    semester = db.Column(db.String(20), nullable=False, index=True)  # 如:2024-2025-1
    academic_year = db.Column(db.String(20), nullable=False)  # 如:2024-2025
    credit = db.Column(db.Numeric(3, 1), nullable=True)
    total_hours = db.Column(db.Integer, nullable=True)
    
    # 外键关联
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    
    # 状态
    status = db.Column(db.Boolean, default=True, nullable=False)  # 1:进行中, 0:已结束
    
    # ==================== 关系定义 ====================
    # 多对多：课程和班级
    classes = db.relationship(
        'Class',
        secondary=course_classes,
        backref=db.backref('courses', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # 一对多：课程的资料
    materials = db.relationship('Material', backref='course', lazy='dynamic')
    
    # 一对多：课程的考勤
    attendances = db.relationship('Attendance', backref='course', lazy='dynamic', foreign_keys='Attendance.course_id', cascade='all, delete-orphan')
    
    # 一对多：课程的成绩（暂时注释，需要添加外键）
    # grades = db.relationship('Grade', backref='course', lazy='dynamic', foreign_keys='Grade.course_id', cascade='all, delete-orphan')
    
    # 一对多：课程的投票（暂时注释，需要添加外键）
    # polls = db.relationship('Poll', backref='course', lazy='dynamic', foreign_keys='Poll.course_id', cascade='all, delete-orphan')
    
    # 一对多：课程的提问（暂时注释，需要添加外键）
    # questions = db.relationship('Question', backref='course', lazy='dynamic', foreign_keys='Question.course_id', cascade='all, delete-orphan')
    
    # 一对多：课程的弹幕（暂时注释，需要添加外键）
    # barrages = db.relationship('Barrage', backref='course', lazy='dynamic', foreign_keys='Barrage.course_id', cascade='all, delete-orphan')
    
    # ==================== 实例方法 ====================
    def is_active(self):
        """检查课程是否进行中"""
        return self.status
    
    def is_teacher(self, user_id):
        """检查是否为授课教师"""
        return self.teacher_id == user_id
    
    def add_class(self, class_obj, start_date=None, end_date=None):
        """添加班级到课程"""
        if class_obj not in self.classes:
            self.classes.append(class_obj)
            db.session.commit()
    
    def remove_class(self, class_obj):
        """从课程中移除班级"""
        if class_obj in self.classes:
            self.classes.remove(class_obj)
            db.session.commit()
    
    def get_student_count(self):
        """获取选课学生总数"""
        count = 0
        for class_obj in self.classes:
            count += class_obj.student_count
        return count
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_teacher(cls, teacher_id, status=None):
        """获取教师的课程"""
        query = cls.query.filter_by(teacher_id=teacher_id)
        if status is not None:
            query = query.filter_by(status=status)
        return query.all()
    
    @classmethod
    def get_by_semester(cls, semester):
        """获取指定学期的课程"""
        return cls.query.filter_by(semester=semester).all()
    
    @classmethod
    def get_by_code(cls, code):
        """根据课程代码获取课程"""
        return cls.query.filter_by(code=code).first()
    
    @classmethod
    def search(cls, keyword):
        """搜索课程"""
        return cls.query.filter(
            db.or_(
                cls.name.like(f'%{keyword}%'),
                cls.code.like(f'%{keyword}%'),
                cls.description.like(f'%{keyword}%')
            )
        ).all()
    
    def __repr__(self):
        return f'<Course {self.code}: {self.name}>'
