"""
课堂互动模块模型

包含投票、提问、回答、弹幕等相关模型定义。
"""
from app.extensions import db
from .base import BaseModel
from enum import Enum


class PollType(Enum):
    """投票类型枚举"""
    SINGLE = 'single'      # 单选
    MULTIPLE = 'multiple'  # 多选


class PollStatus(Enum):
    """投票状态枚举"""
    ACTIVE = 'active'  # 进行中
    ENDED = 'ended'    # 已结束


class QuestionStatus(Enum):
    """问题状态枚举"""
    PENDING = 'pending'    # 待回答
    ANSWERED = 'answered'  # 已回答


class Poll(BaseModel):
    """投票模型
    
    课堂投票/问卷调查。
    """
    __tablename__ = 'polls'
    
    # ==================== 字段定义 ====================
    # 基本信息
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    
    # 外键关联
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    teacher_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 投票设置
    poll_type = db.Column(db.Enum(PollType), nullable=False)
    options = db.Column(db.JSON, nullable=False)  # JSON数组
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    
    # 时间
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)
    
    # 状态
    status = db.Column(db.Enum(PollStatus), default=PollStatus.ACTIVE, nullable=False)
    
    # ==================== 关系定义 ====================
    # 一对多：投票响应
    responses = db.relationship('PollResponse', backref='poll', lazy='dynamic', cascade='all, delete-orphan')
    
    # ==================== 实例方法 ====================
    def is_active(self):
        """检查投票是否进行中"""
        return self.status == PollStatus.ACTIVE
    
    def is_ended(self):
        """检查投票是否已结束"""
        return self.status == PollStatus.ENDED
    
    def is_teacher(self, user_id):
        """检查是否为创建教师"""
        return self.teacher_id == user_id
    
    def end_poll(self):
        """结束投票"""
        self.status = PollStatus.ENDED
        db.session.commit()
    
    def get_response_count(self):
        """获取投票人数"""
        return self.responses.count()
    
    def get_results(self):
        """获取投票结果"""
        results = {}
        for option in self.options:
            option_id = option.get('id')
            count = self.responses.filter(
                PollResponse.selected_options.contains([option_id])
            ).count()
            results[option_id] = {
                'text': option.get('text'),
                'count': count,
                'percentage': round((count / max(self.get_response_count(), 1)) * 100, 2)
            }
        return results
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id):
        """获取课程的所有投票"""
        return cls.query.filter_by(course_id=course_id).order_by(cls.start_time.desc()).all()
    
    @classmethod
    def get_by_teacher(cls, teacher_id):
        """获取教师创建的所有投票"""
        return cls.query.filter_by(teacher_id=teacher_id).order_by(cls.start_time.desc()).all()
    
    def __repr__(self):
        return f'<Poll {self.title}>'


class PollResponse(BaseModel):
    """投票响应模型
    
    学生的投票记录。
    """
    __tablename__ = 'poll_responses'
    
    # ==================== 字段定义 ====================
    # 外键关联
    poll_id = db.Column(db.Integer, nullable=False, index=True)  # FK→polls.id
    student_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 投票内容
    selected_options = db.Column(db.JSON, nullable=False)  # JSON数组
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_poll(cls, poll_id):
        """获取投票的所有响应"""
        return cls.query.filter_by(poll_id=poll_id).all()
    
    @classmethod
    def get_by_student(cls, student_id, poll_id):
        """获取学生的投票记录"""
        return cls.query.filter_by(student_id=student_id, poll_id=poll_id).first()
    
    @classmethod
    def has_voted(cls, student_id, poll_id):
        """检查学生是否已投票"""
        return cls.query.filter_by(student_id=student_id, poll_id=poll_id).first() is not None
    
    def __repr__(self):
        return f'<PollResponse poll:{self.poll_id} student:{self.student_id}>'


class Question(BaseModel):
    """提问模型
    
    课堂提问功能。
    """
    __tablename__ = 'questions'
    
    # ==================== 字段定义 ====================
    # 基本信息
    content = db.Column(db.Text, nullable=False)
    
    # 外键关联
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    user_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 设置
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    
    # 状态
    status = db.Column(db.Enum(QuestionStatus), default=QuestionStatus.PENDING, nullable=False, index=True)
    like_count = db.Column(db.Integer, default=0, nullable=False)
    
    # ==================== 关系定义 ====================
    # 一对多：问题的回答
    answers = db.relationship('QuestionAnswer', backref='question', lazy='dynamic', cascade='all, delete-orphan')
    
    # ==================== 实例方法 ====================
    def is_pending(self):
        """检查是否待回答"""
        return self.status == QuestionStatus.PENDING
    
    def is_answered(self):
        """检查是否已回答"""
        return self.status == QuestionStatus.ANSWERED
    
    def mark_as_answered(self):
        """标记为已回答"""
        self.status = QuestionStatus.ANSWERED
        db.session.commit()
    
    def increment_like(self):
        """增加点赞数"""
        self.like_count += 1
        db.session.commit()
    
    def decrement_like(self):
        """减少点赞数"""
        if self.like_count > 0:
            self.like_count -= 1
            db.session.commit()
    
    def get_answer_count(self):
        """获取回答数量"""
        return self.answers.count()
    
    def get_accepted_answer(self):
        """获取被采纳的回答"""
        return self.answers.filter_by(is_accepted=True).first()
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id, status=None):
        """获取课程的所有提问"""
        query = cls.query.filter_by(course_id=course_id)
        if status:
            query = query.filter_by(status=status)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_user(cls, user_id):
        """获取用户的所有提问"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_popular(cls, course_id, limit=10):
        """获取热门问题"""
        return cls.query.filter_by(course_id=course_id).order_by(
            cls.like_count.desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<Question {self.id}: {self.content[:50]}>'


class QuestionAnswer(BaseModel):
    """回答模型
    
    问题的回答记录。
    """
    __tablename__ = 'question_answers'
    
    # ==================== 字段定义 ====================
    # 基本信息
    content = db.Column(db.Text, nullable=False)
    
    # 外键关联
    question_id = db.Column(db.Integer, nullable=False, index=True)  # FK→questions.id
    user_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 状态
    is_accepted = db.Column(db.Boolean, default=False, nullable=False)
    like_count = db.Column(db.Integer, default=0, nullable=False)
    
    # ==================== 实例方法 ====================
    def accept(self):
        """采纳该回答"""
        # 取消该问题下其他回答的采纳状态
        QuestionAnswer.query.filter_by(question_id=self.question_id).update({'is_accepted': False})
        self.is_accepted = True
        
        # 标记问题为已回答
        question = Question.query.get(self.question_id)
        if question:
            question.mark_as_answered()
        
        db.session.commit()
    
    def increment_like(self):
        """增加点赞数"""
        self.like_count += 1
        db.session.commit()
    
    def decrement_like(self):
        """减少点赞数"""
        if self.like_count > 0:
            self.like_count -= 1
            db.session.commit()
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_question(cls, question_id):
        """获取问题的所有回答"""
        return cls.query.filter_by(question_id=question_id).order_by(
            cls.is_accepted.desc(), cls.like_count.desc(), cls.created_at.desc()
        ).all()
    
    @classmethod
    def get_by_user(cls, user_id):
        """获取用户的所有回答"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    def __repr__(self):
        return f'<QuestionAnswer question:{self.question_id} user:{self.user_id}>'


class Barrage(BaseModel):
    """弹幕模型
    
    课堂弹幕功能。
    """
    __tablename__ = 'barrages'
    
    # ==================== 字段定义 ====================
    # 基本信息
    content = db.Column(db.String(200), nullable=False)
    
    # 外键关联
    course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
    user_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 设置
    is_anonymous = db.Column(db.Boolean, default=False, nullable=False)
    
    # 状态
    status = db.Column(db.Boolean, default=True, nullable=False)  # 1:正常, 0:已删除
    
    # ==================== 实例方法 ====================
    def is_active(self):
        """检查是否正常"""
        return self.status
    
    def delete_barrage(self):
        """删除弹幕（软删除）"""
        self.status = False
        db.session.commit()
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id, include_deleted=False):
        """获取课程的所有弹幕"""
        query = cls.query.filter_by(course_id=course_id)
        if not include_deleted:
            query = query.filter_by(status=True)
        return query.order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_by_user(cls, user_id):
        """获取用户的所有弹幕"""
        return cls.query.filter_by(user_id=user_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_recent(cls, course_id, limit=50):
        """获取最近的弹幕"""
        return cls.query.filter_by(course_id=course_id, status=True).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<Barrage {self.content[:30]}>'
