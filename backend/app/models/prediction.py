"""
预警预测模块数据模型
"""
from app.extensions import db
from datetime import datetime
from enum import Enum


class RiskLevel(Enum):
    """风险等级枚举"""
    HIGH = 'high'      # 高风险: 预测分数 < 60
    MEDIUM = 'medium'  # 中风险: 60 <= 预测分数 < 70
    LOW = 'low'        # 低风险: 70 <= 预测分数 < 80
    NONE = 'none'      # 无风险: 预测分数 >= 80


class InterventionType(Enum):
    """干预方式枚举"""
    TALK = 'talk'           # 谈话
    TUTORING = 'tutoring'   # 辅导
    HOMEWORK = 'homework'   # 作业
    OTHER = 'other'         # 其他


class PredictFrequency(Enum):
    """预测频率枚举"""
    DAILY = 'daily'      # 每天
    WEEKLY = 'weekly'    # 每周
    MONTHLY = 'monthly'  # 每月


class PredictTrigger(Enum):
    """预测触发时机枚举"""
    AFTER_GRADE = 'after_grade'  # 录入成绩后
    SCHEDULED = 'scheduled'      # 定时触发


class Prediction(db.Model):
    """预警记录模型"""
    __tablename__ = 'predictions'
    
    id = db.Column(db.Integer, primary_key=True, comment='预警ID')
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='学生ID')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, comment='课程ID')
    predicted_score = db.Column(db.Float, nullable=False, comment='预测分数')
    confidence = db.Column(db.Float, nullable=False, comment='置信度(%)')
    risk_level = db.Column(db.Enum(RiskLevel), nullable=False, comment='风险等级')
    prediction_date = db.Column(db.Date, nullable=False, comment='预测日期')
    is_sent = db.Column(db.Boolean, default=False, comment='是否已发送通知')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    student = db.relationship('User', foreign_keys=[student_id], backref='predictions')
    course = db.relationship('Course', backref='predictions')
    interventions = db.relationship('Intervention', backref='prediction', lazy='dynamic', cascade='all, delete-orphan')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'student_id': self.student_id,
            'course_id': self.course_id,
            'predicted_score': self.predicted_score,
            'confidence': self.confidence,
            'risk_level': self.risk_level.value if isinstance(self.risk_level, RiskLevel) else self.risk_level,
            'prediction_date': self.prediction_date.isoformat() if self.prediction_date else None,
            'is_sent': self.is_sent,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class Intervention(db.Model):
    """干预记录模型"""
    __tablename__ = 'interventions'
    
    id = db.Column(db.Integer, primary_key=True, comment='干预ID')
    prediction_id = db.Column(db.Integer, db.ForeignKey('predictions.id'), nullable=False, comment='关联预警记录ID')
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='教师ID')
    intervention_date = db.Column(db.Date, nullable=False, comment='干预日期')
    intervention_type = db.Column(db.Enum(InterventionType), nullable=False, comment='干预方式')
    description = db.Column(db.Text, nullable=False, comment='干预内容描述')
    expected_effect = db.Column(db.String(500), comment='预期效果')
    actual_effect = db.Column(db.String(500), comment='实际效果')
    student_feedback = db.Column(db.Text, comment='学生反馈')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='interventions')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'prediction_id': self.prediction_id,
            'teacher_id': self.teacher_id,
            'intervention_date': self.intervention_date.isoformat() if self.intervention_date else None,
            'intervention_type': self.intervention_type.value if isinstance(self.intervention_type, InterventionType) else self.intervention_type,
            'description': self.description,
            'expected_effect': self.expected_effect,
            'actual_effect': self.actual_effect,
            'student_feedback': self.student_feedback,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }


class PredictionConfig(db.Model):
    """预测配置模型"""
    __tablename__ = 'prediction_configs'
    
    id = db.Column(db.Integer, primary_key=True, comment='配置ID')
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, unique=True, comment='课程ID')
    teacher_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, comment='教师ID')
    auto_predict_enabled = db.Column(db.Boolean, default=False, comment='是否启用自动预测')
    predict_frequency = db.Column(db.Enum(PredictFrequency), default=PredictFrequency.WEEKLY, comment='预测频率')
    predict_trigger = db.Column(db.Enum(PredictTrigger), default=PredictTrigger.SCHEDULED, comment='触发时机')
    min_grades_required = db.Column(db.Integer, default=2, comment='最少需要几次成绩才预测')
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    # 关系
    course = db.relationship('Course', backref='prediction_config', uselist=False)
    teacher = db.relationship('User', foreign_keys=[teacher_id], backref='prediction_configs')
    
    def to_dict(self):
        """转换为字典"""
        return {
            'id': self.id,
            'course_id': self.course_id,
            'teacher_id': self.teacher_id,
            'auto_predict_enabled': self.auto_predict_enabled,
            'predict_frequency': self.predict_frequency.value if isinstance(self.predict_frequency, PredictFrequency) else self.predict_frequency,
            'predict_trigger': self.predict_trigger.value if isinstance(self.predict_trigger, PredictTrigger) else self.predict_trigger,
            'min_grades_required': self.min_grades_required,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }
