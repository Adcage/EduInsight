from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from .base import BaseModel
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    # 基本信息
    username = db.Column(db.String(50), nullable=False)
    user_code = db.Column(db.String(50), unique=True, nullable=False, index=True)  # 工号/学号
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    real_name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    
    # 角色和权限
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False, index=True)
    
    # 班级关联（学生角色时使用）
    class_id = db.Column(db.Integer, db.ForeignKey('classes.id'), nullable=True, index=True)
    
    # 状态和时间
    status = db.Column(db.Boolean, default=True, nullable=False)  # 1:正常, 0:禁用
    last_login_time = db.Column(db.DateTime, nullable=True)
    
    # 关系
    # orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    # class_rel = db.relationship('Class', backref='students', lazy='select')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_time = datetime.utcnow()
        db.session.commit()
    
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == UserRole.ADMIN
    
    def is_teacher(self):
        """检查是否为教师"""
        return self.role == UserRole.TEACHER
    
    def is_student(self):
        """检查是否为学生"""
        return self.role == UserRole.STUDENT
    
    def has_permission(self, permission):
        """检查用户是否有指定权限"""
        # 管理员拥有所有权限
        if self.is_admin():
            return True
        
        # 根据角色和权限进行检查
        role_permissions = {
            UserRole.TEACHER: [
                'material:create', 'material:read', 'material:update', 'material:delete',
                'course:create', 'course:read', 'course:update',
                'attendance:create', 'attendance:read', 'attendance:update',
                'grade:create', 'grade:read', 'grade:update',
                'poll:create', 'poll:read', 'poll:update'
            ],
            UserRole.STUDENT: [
                'material:read',
                'course:read',
                'attendance:read', 'attendance:checkin',
                'grade:read',
                'poll:read', 'poll:vote',
                'question:create', 'question:read'
            ]
        }
        
        return permission in role_permissions.get(self.role, [])
    
    def to_dict(self):
        """转换为字典，排除敏感信息"""
        data = super().to_dict()
        data.pop('password_hash', None)
        data['role'] = self.role.value if self.role else None
        return data
    
    @classmethod
    def get_by_email(cls, email):
        """根据邮箱获取用户"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_user_code(cls, user_code):
        """根据工号/学号获取用户"""
        return cls.query.filter_by(user_code=user_code).first()
    
    @classmethod
    def get_by_username(cls, username):
        """根据用户名获取用户"""
        return cls.query.filter_by(username=username).first()
    
    def __repr__(self):
        return f'<User {self.username}({self.real_name})>'
