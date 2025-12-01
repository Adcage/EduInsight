from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from .base import BaseModel

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # 关系
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def to_dict(self):
        """转换为字典，排除敏感信息"""
        data = super().to_dict()
        data.pop('password_hash', None)
        return data
    
    @classmethod
    def get_by_email(cls, email):
        """根据邮箱获取用户"""
        return cls.query.filter_by(email=email).first()
    
    def __repr__(self):
        return f'<User {self.name}>'
