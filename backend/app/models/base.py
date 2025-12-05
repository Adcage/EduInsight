from datetime import datetime
from app.extensions import db

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """
        转换为字典
        
        自动将 datetime 对象转换为字符串格式
        """
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            # 自动转换 datetime 为字符串
            if isinstance(value, datetime):
                result[c.name] = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
            else:
                result[c.name] = value
        return result
    
    def save(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """获取所有记录"""
        return cls.query.all()
