from typing import List, Optional, Tuple
from sqlalchemy import and_
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product import Product
from app.model.order_model import OrderCreateModel, OrderUpdateModel, OrderQueryModel
from app.services.product_service import ProductService
from app.extensions import db

class OrderService:
    """订单业务逻辑服务"""
    
    @staticmethod
    def get_all_orders() -> List[Order]:
        """获取所有订单"""
        return Order.query.all()
    
    @staticmethod
    def get_order_by_id(order_id: int) -> Optional[Order]:
        """根据ID获取订单"""
        return Order.query.get(order_id)
    
    @staticmethod
    def get_user_orders(user_id: int) -> List[Order]:
        """获取用户的所有订单"""
        return Order.query.filter_by(user_id=user_id).all()
    
    @staticmethod
    def create_order(user_id: int, order_data: OrderCreateModel) -> Order:
        """创建新订单"""
        # 创建订单
        order = Order(
            user_id=user_id,
            total_amount=0,
            shipping_address=order_data.shipping_address,
            notes=order_data.notes
        )
        
        db.session.add(order)
        db.session.flush()  # 获取订单ID
        
        total_amount = 0
        
        # 创建订单项
        for item_data in order_data.items:
            product = ProductService.get_product_by_id(item_data.product_id)
            if not product:
                raise ValueError(f"产品ID {item_data.product_id} 不存在")
            
            if not product.is_in_stock or product.stock < item_data.quantity:
                raise ValueError(f"产品 {product.name} 库存不足")
            
            # 减少库存
            if not product.reduce_stock(item_data.quantity):
                raise ValueError(f"产品 {product.name} 库存不足")
            
            # 创建订单项
            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data.quantity,
                unit_price=product.price
            )
            
            db.session.add(order_item)
            total_amount += order_item.subtotal
        
        # 更新订单总金额
        order.total_amount = total_amount
        db.session.commit()
        
        return order
    
    @staticmethod
    def update_order(order_id: int, order_data: OrderUpdateModel) -> Optional[Order]:
        """更新订单信息"""
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return None
        
        # 更新订单信息
        update_data = order_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(order, field, value)
        
        db.session.commit()
        return order
    
    @staticmethod
    def cancel_order(order_id: int) -> bool:
        """取消订单"""
        order = OrderService.get_order_by_id(order_id)
        if not order:
            return False
        
        if order.status != OrderStatus.PENDING:
            raise ValueError("只能取消待处理状态的订单")
        
        # 恢复库存
        for item in order.items:
            product = ProductService.get_product_by_id(item.product_id)
            if product:
                product.stock += item.quantity
        
        order.status = OrderStatus.CANCELLED
        db.session.commit()
        return True
    
    @staticmethod
    def search_orders(query: OrderQueryModel) -> Tuple[List[Order], int]:
        """搜索订单"""
        filters = []
        
        # 状态过滤
        if query.status:
            filters.append(Order.status == query.status)
        
        # 用户过滤
        if query.user_id:
            filters.append(Order.user_id == query.user_id)
        
        # 日期范围过滤
        if query.start_date:
            filters.append(Order.created_at >= query.start_date)
        if query.end_date:
            filters.append(Order.created_at <= query.end_date)
        
        # 构建查询
        base_query = Order.query
        if filters:
            base_query = base_query.filter(and_(*filters))
        
        # 分页
        total = base_query.count()
        orders = base_query.offset((query.page - 1) * query.per_page).limit(query.per_page).all()
        
        return orders, total
    
    @staticmethod
    def get_order_statistics(user_id: Optional[int] = None) -> dict:
        """获取订单统计信息"""
        base_query = Order.query
        if user_id:
            base_query = base_query.filter_by(user_id=user_id)
        
        total_orders = base_query.count()
        pending_orders = base_query.filter_by(status=OrderStatus.PENDING).count()
        completed_orders = base_query.filter_by(status=OrderStatus.DELIVERED).count()
        cancelled_orders = base_query.filter_by(status=OrderStatus.CANCELLED).count()
        
        return {
            'total_orders': total_orders,
            'pending_orders': pending_orders,
            'completed_orders': completed_orders,
            'cancelled_orders': cancelled_orders
        }
