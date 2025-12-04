"""
成绩管理模块模型

包含成绩、成绩统计、成绩预测等相关模型定义。
"""
from app.extensions import db
from .base import BaseModel
from enum import Enum


class ExamType(Enum):
    """考试类型枚举"""
    DAILY = 'daily'        # 平时成绩
    MIDTERM = 'midterm'    # 期中考试
    FINAL = 'final'        # 期末考试
    HOMEWORK = 'homework'  # 作业


class RiskLevel(Enum):
    """风险等级枚举"""
    LOW = 'low'        # 低风险
    MEDIUM = 'medium'  # 中风险
    HIGH = 'high'      # 高风险


class Grade(BaseModel):
    """成绩模型
    
    存储学生的各类成绩记录。
    """
    __tablename__ = 'grades'
    
    # ==================== 字段定义 ====================
    # 外键关联
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    student_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 考试信息
    exam_type = db.Column(db.Enum(ExamType), nullable=False, index=True)
    exam_name = db.Column(db.String(100), nullable=True)
    exam_date = db.Column(db.Date, nullable=True)
    
    # 成绩信息
    score = db.Column(db.Numeric(5, 2), nullable=False)
    full_score = db.Column(db.Numeric(5, 2), default=100.00, nullable=False)
    weight = db.Column(db.Numeric(4, 2), default=1.00, nullable=False)
    
    # 备注
    remark = db.Column(db.String(255), nullable=True)
    
    # ==================== 实例方法 ====================
    def get_percentage(self):
        """获取百分比"""
        if self.full_score > 0:
            return round((self.score / self.full_score) * 100, 2)
        return 0.00
    
    def is_pass(self, pass_score=60):
        """检查是否及格"""
        percentage = self.get_percentage()
        return percentage >= pass_score
    
    def is_excellent(self, excellent_score=90):
        """检查是否优秀"""
        percentage = self.get_percentage()
        return percentage >= excellent_score
    
    def get_weighted_score(self):
        """获取加权分数"""
        return float(self.score) * float(self.weight)
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id, exam_type=None):
        """获取课程的成绩"""
        query = cls.query.filter_by(course_id=course_id)
        if exam_type:
            query = query.filter_by(exam_type=exam_type)
        return query.all()
    
    @classmethod
    def get_by_student(cls, student_id, course_id=None):
        """获取学生的成绩"""
        query = cls.query.filter_by(student_id=student_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        return query.all()
    
    @classmethod
    def get_by_exam(cls, course_id, exam_type, exam_name=None):
        """获取指定考试的成绩"""
        query = cls.query.filter_by(course_id=course_id, exam_type=exam_type)
        if exam_name:
            query = query.filter_by(exam_name=exam_name)
        return query.all()
    
    def __repr__(self):
        return f'<Grade student:{self.student_id} course:{self.course_id} score:{self.score}>'


class GradeStatistics(BaseModel):
    """成绩统计模型
    
    按课程和考试类型统计成绩分布。
    """
    __tablename__ = 'grade_statistics'
    
    # ==================== 字段定义 ====================
    # 外键关联
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    
    # 考试信息
    exam_type = db.Column(db.Enum(ExamType), nullable=False)
    exam_name = db.Column(db.String(100), nullable=True)
    
    # 统计数据
    total_students = db.Column(db.Integer, default=0, nullable=False)
    average_score = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    highest_score = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    lowest_score = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    std_deviation = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    median_score = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    pass_rate = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    excellent_rate = db.Column(db.Numeric(5, 2), default=0.00, nullable=False)
    score_distribution = db.Column(db.JSON, nullable=True)
    
    # ==================== 实例方法 ====================
    def calculate_statistics(self):
        """计算统计数据"""
        import numpy as np
        
        grades = Grade.get_by_exam(self.course_id, self.exam_type, self.exam_name)
        
        if not grades:
            return
        
        scores = [float(g.score) for g in grades]
        percentages = [g.get_percentage() for g in grades]
        
        self.total_students = len(scores)
        self.average_score = round(np.mean(scores), 2)
        self.highest_score = round(max(scores), 2)
        self.lowest_score = round(min(scores), 2)
        self.std_deviation = round(np.std(scores), 2)
        self.median_score = round(np.median(scores), 2)
        
        # 计算及格率和优秀率
        pass_count = sum(1 for p in percentages if p >= 60)
        excellent_count = sum(1 for p in percentages if p >= 90)
        
        self.pass_rate = round((pass_count / self.total_students) * 100, 2)
        self.excellent_rate = round((excellent_count / self.total_students) * 100, 2)
        
        # 计算分数段分布
        self.score_distribution = {
            '0-59': sum(1 for p in percentages if p < 60),
            '60-69': sum(1 for p in percentages if 60 <= p < 70),
            '70-79': sum(1 for p in percentages if 70 <= p < 80),
            '80-89': sum(1 for p in percentages if 80 <= p < 90),
            '90-100': sum(1 for p in percentages if p >= 90)
        }
        
        db.session.commit()
    
    # ==================== 类方法 ====================
    @classmethod
    def get_or_create(cls, course_id, exam_type, exam_name=None):
        """获取或创建统计记录"""
        stat = cls.query.filter_by(
            course_id=course_id,
            exam_type=exam_type,
            exam_name=exam_name
        ).first()
        
        if not stat:
            stat = cls(course_id=course_id, exam_type=exam_type, exam_name=exam_name)
            stat.save()
        
        return stat
    
    @classmethod
    def get_by_course(cls, course_id):
        """获取课程的所有统计"""
        return cls.query.filter_by(course_id=course_id).all()
    
    def __repr__(self):
        return f'<GradeStatistics course:{self.course_id} exam:{self.exam_type.value}>'


class GradePrediction(BaseModel):
    """成绩预测模型（智能模块）
    
    基于机器学习的成绩预测和预警。
    """
    __tablename__ = 'grade_predictions'
    
    # ==================== 字段定义 ====================
    # 外键关联
    student_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    
    # 预测结果
    predicted_score = db.Column(db.Numeric(5, 2), nullable=False)
    confidence = db.Column(db.Numeric(5, 4), nullable=True)
    risk_level = db.Column(db.Enum(RiskLevel), nullable=False)
    is_warning = db.Column(db.Boolean, default=False, nullable=False, index=True)
    
    # 预测信息
    prediction_date = db.Column(db.Date, nullable=False, index=True)
    model_version = db.Column(db.String(50), nullable=True)
    features_used = db.Column(db.JSON, nullable=True)
    recommendation = db.Column(db.Text, nullable=True)
    
    # ==================== 实例方法 ====================
    def is_high_risk(self):
        """检查是否高风险"""
        return self.risk_level == RiskLevel.HIGH
    
    def is_medium_risk(self):
        """检查是否中风险"""
        return self.risk_level == RiskLevel.MEDIUM
    
    def is_low_risk(self):
        """检查是否低风险"""
        return self.risk_level == RiskLevel.LOW
    
    def should_warn(self):
        """检查是否需要预警"""
        return self.is_warning
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_student(cls, student_id, course_id=None):
        """获取学生的预测"""
        query = cls.query.filter_by(student_id=student_id)
        if course_id:
            query = query.filter_by(course_id=course_id)
        return query.order_by(cls.prediction_date.desc()).all()
    
    @classmethod
    def get_by_course(cls, course_id):
        """获取课程的所有预测"""
        return cls.query.filter_by(course_id=course_id).all()
    
    @classmethod
    def get_warnings(cls, course_id=None):
        """获取所有预警"""
        query = cls.query.filter_by(is_warning=True)
        if course_id:
            query = query.filter_by(course_id=course_id)
        return query.order_by(cls.prediction_date.desc()).all()
    
    @classmethod
    def get_high_risk_students(cls, course_id):
        """获取高风险学生"""
        return cls.query.filter_by(
            course_id=course_id,
            risk_level=RiskLevel.HIGH
        ).all()
    
    def __repr__(self):
        return f'<GradePrediction student:{self.student_id} score:{self.predicted_score} risk:{self.risk_level.value}>'
