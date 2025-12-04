from app.extensions import db
from sqlalchemy.orm import foreign
from .base import BaseModel

class Class(BaseModel):
    """班级模型"""
    __tablename__ = 'classes'
    
    # 基本信息
    name = db.Column(db.String(100), nullable=False, unique=True, index=True)  # 班级名称
    code = db.Column(db.String(50), nullable=False, unique=True, index=True)   # 班级代码
    description = db.Column(db.String(255), nullable=True)                     # 班级描述
    
    # 班级信息
    grade = db.Column(db.String(50), nullable=True)  # 年级
    major = db.Column(db.String(100), nullable=True)  # 专业
    
    # 班主任
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    
    # 状态
    status = db.Column(db.Boolean, default=True, nullable=False)  # 1:正常, 0:禁用
    
    # 关系
    students = db.relationship('User', 
                              foreign_keys='User.class_id',
                              backref='class_rel', 
                              lazy='dynamic')
    
    def __repr__(self):
        return f'<Class {self.name}({self.code})>'
