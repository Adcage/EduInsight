"""
系统日志模块模型

包含系统日志、通知等相关模型定义。
"""
from app.extensions import db
from .base import BaseModel
from enum import Enum


class NotificationType(Enum):
    """通知类型枚举"""
    SYSTEM = 'system'          # 系统通知
    ATTENDANCE = 'attendance'  # 考勤通知
    GRADE = 'grade'            # 成绩通知
    WARNING = 'warning'        # 预警通知


class NotificationPriority(Enum):
    """通知优先级枚举"""
    NORMAL = 0    # 普通
    IMPORTANT = 1  # 重要
    URGENT = 2     # 紧急


class SystemLog(BaseModel):
    """系统日志模型
    
    记录用户操作和系统事件。
    """
    __tablename__ = 'system_logs'
    
    # ==================== 字段定义 ====================
    # 外键关联
    user_id = db.Column(db.Integer, nullable=True, index=True)  # FK→users.id
    
    # 操作信息
    action = db.Column(db.String(50), nullable=False, index=True)  # login/upload/delete等
    module = db.Column(db.String(50), nullable=False, index=True)  # user/material/grade等
    
    # 请求信息
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(255), nullable=True)
    request_data = db.Column(db.JSON, nullable=True)  # JSON格式
    
    # 响应信息
    response_status = db.Column(db.Integer, nullable=True)
    error_message = db.Column(db.Text, nullable=True)
    
    # ==================== 实例方法 ====================
    def is_success(self):
        """检查操作是否成功"""
        return self.response_status and 200 <= self.response_status < 300
    
    def is_error(self):
        """检查是否有错误"""
        return self.response_status and self.response_status >= 400
    
    def is_client_error(self):
        """检查是否客户端错误(4xx)"""
        return self.response_status and 400 <= self.response_status < 500
    
    def is_server_error(self):
        """检查是否服务器错误(5xx)"""
        return self.response_status and self.response_status >= 500
    
    # ==================== 类方法 ====================
    @classmethod
    def log(cls, user_id, action, module, ip_address=None, user_agent=None, 
            request_data=None, response_status=None, error_message=None):
        """记录日志"""
        log = cls(
            user_id=user_id,
            action=action,
            module=module,
            ip_address=ip_address,
            user_agent=user_agent,
            request_data=request_data,
            response_status=response_status,
            error_message=error_message
        )
        log.save()
        return log
    
    @classmethod
    def get_by_user(cls, user_id, limit=100):
        """获取用户的操作日志"""
        return cls.query.filter_by(user_id=user_id).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_action(cls, action, limit=100):
        """获取指定操作的日志"""
        return cls.query.filter_by(action=action).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_module(cls, module, limit=100):
        """获取指定模块的日志"""
        return cls.query.filter_by(module=module).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_errors(cls, limit=100):
        """获取错误日志"""
        return cls.query.filter(cls.response_status >= 400).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_by_ip(cls, ip_address, limit=100):
        """获取指定IP的日志"""
        return cls.query.filter_by(ip_address=ip_address).order_by(
            cls.created_at.desc()
        ).limit(limit).all()
    
    @classmethod
    def get_recent(cls, limit=100):
        """获取最近的日志"""
        return cls.query.order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def clean_old_logs(cls, days=30):
        """清理旧日志"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cls.query.filter(cls.created_at < cutoff_date).delete()
        db.session.commit()
    
    def __repr__(self):
        return f'<SystemLog {self.action} by user:{self.user_id}>'


class Notification(BaseModel):
    """通知模型
    
    系统通知和消息推送。
    """
    __tablename__ = 'notifications'
    
    # ==================== 字段定义 ====================
    # 外键关联
    user_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    
    # 通知信息
    type = db.Column(db.Enum(NotificationType), nullable=False, index=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    link = db.Column(db.String(255), nullable=True)
    
    # 状态
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    priority = db.Column(db.Integer, default=0, nullable=False)  # 0:普通, 1:重要, 2:紧急
    
    # ==================== 实例方法 ====================
    def mark_as_read(self):
        """标记为已读"""
        self.is_read = True
        db.session.commit()
    
    def mark_as_unread(self):
        """标记为未读"""
        self.is_read = False
        db.session.commit()
    
    def is_unread(self):
        """检查是否未读"""
        return not self.is_read
    
    def is_normal(self):
        """检查是否普通优先级"""
        return self.priority == NotificationPriority.NORMAL.value
    
    def is_important(self):
        """检查是否重要"""
        return self.priority == NotificationPriority.IMPORTANT.value
    
    def is_urgent(self):
        """检查是否紧急"""
        return self.priority == NotificationPriority.URGENT.value
    
    def is_system(self):
        """检查是否系统通知"""
        return self.type == NotificationType.SYSTEM
    
    def is_attendance(self):
        """检查是否考勤通知"""
        return self.type == NotificationType.ATTENDANCE
    
    def is_grade(self):
        """检查是否成绩通知"""
        return self.type == NotificationType.GRADE
    
    def is_warning(self):
        """检查是否预警通知"""
        return self.type == NotificationType.WARNING
    
    # ==================== 类方法 ====================
    @classmethod
    def create_notification(cls, user_id, notification_type, title, content, 
                          link=None, priority=0):
        """创建通知"""
        notification = cls(
            user_id=user_id,
            type=notification_type,
            title=title,
            content=content,
            link=link,
            priority=priority
        )
        notification.save()
        return notification
    
    @classmethod
    def get_by_user(cls, user_id, is_read=None, limit=None):
        """获取用户的通知"""
        query = cls.query.filter_by(user_id=user_id)
        if is_read is not None:
            query = query.filter_by(is_read=is_read)
        query = query.order_by(cls.priority.desc(), cls.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_unread(cls, user_id):
        """获取用户的未读通知"""
        return cls.get_by_user(user_id, is_read=False)
    
    @classmethod
    def get_unread_count(cls, user_id):
        """获取未读通知数量"""
        return cls.query.filter_by(user_id=user_id, is_read=False).count()
    
    @classmethod
    def get_by_type(cls, user_id, notification_type):
        """获取指定类型的通知"""
        return cls.query.filter_by(
            user_id=user_id,
            type=notification_type
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_urgent(cls, user_id):
        """获取紧急通知"""
        return cls.query.filter_by(
            user_id=user_id,
            priority=NotificationPriority.URGENT.value,
            is_read=False
        ).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def mark_all_as_read(cls, user_id):
        """标记所有通知为已读"""
        cls.query.filter_by(user_id=user_id, is_read=False).update({'is_read': True})
        db.session.commit()
    
    @classmethod
    def delete_old_notifications(cls, user_id, days=30):
        """删除旧通知"""
        from datetime import datetime, timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        cls.query.filter(
            cls.user_id == user_id,
            cls.is_read == True,
            cls.created_at < cutoff_date
        ).delete()
        db.session.commit()
    
    def __repr__(self):
        return f'<Notification {self.title} to user:{self.user_id}>'
