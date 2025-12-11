from datetime import datetime
from enum import Enum
from app.extensions import db

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    # 使用本地时间而不是UTC时间
    created_at = db.Column(db.DateTime, default=datetime.now, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, nullable=False)
    
    def to_dict(self):
        """
        转换为字典
        
        自动将 datetime 对象转换为字符串格式（不带时区信息）
        自动处理枚举类型、datetime 对象和 Decimal 类型
        """
        from decimal import Decimal
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            # 自动转换 datetime 为字符串（ISO格式，不带时区标记）
            if isinstance(value, datetime):
                result[c.name] = value.strftime('%Y-%m-%d %H:%M:%S')
            # 处理枚举类型 - 转换为枚举的值
            elif isinstance(value, Enum):
                result[c.name] = value.value
            # 处理 Decimal 类型 - 转换为 float
            elif isinstance(value, Decimal):
                result[c.name] = float(value)
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
