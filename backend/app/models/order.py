from enum import Enum
from app.extensions import db
from .base import BaseModel

class OrderStatus(Enum):
    """订单状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'
    
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(db.Enum(OrderStatus), default=OrderStatus.PENDING, nullable=False)
    shipping_address = db.Column(db.Text, nullable=True)
    notes = db.Column(db.Text, nullable=True)
    
    # 关系
    items = db.relationship('OrderItem', backref='order', lazy='dynamic', cascade='all, delete-orphan')
    
    @property
    def item_count(self):
        """获取订单项数量"""
        return self.items.count()
    
    def calculate_total(self):
        """计算订单总金额"""
        total = sum(item.subtotal for item in self.items)
        self.total_amount = total
        return total
    
    def __repr__(self):
        return f'<Order {self.id}>'

class OrderItem(BaseModel):
    """订单项模型"""
    __tablename__ = 'order_items'
    
    order_id = db.Column(db.Integer, db.ForeignKey('orders.id'), nullable=False)
    product_id = db.Column(db.Integer, db.ForeignKey('products.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    unit_price = db.Column(db.Numeric(10, 2), nullable=False)
    
    @property
    def subtotal(self):
        """计算小计"""
        return self.quantity * self.unit_price
    
    def __repr__(self):
        return f'<OrderItem {self.id}>'
