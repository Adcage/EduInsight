from app.extensions import db
from .base import BaseModel

class Product(BaseModel):
    """产品模型"""
    __tablename__ = 'products'
    
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    stock = db.Column(db.Integer, default=0, nullable=False)
    category = db.Column(db.String(100), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # 关系
    order_items = db.relationship('OrderItem', backref='product', lazy='dynamic')
    
    @property
    def is_in_stock(self):
        """检查是否有库存"""
        return self.stock > 0
    
    def reduce_stock(self, quantity):
        """减少库存"""
        if self.stock >= quantity:
            self.stock -= quantity
            return True
        return False
    
    def __repr__(self):
        return f'<Product {self.name}>'
