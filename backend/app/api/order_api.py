from flask_openapi3 import APIBlueprint, Tag
from app.model.order_model import (
    OrderCreateModel, OrderUpdateModel, OrderResponseModel,
    OrderListResponseModel, OrderPathModel, OrderQueryModel
)
from app.services.order_service import OrderService

order_api_bp = APIBlueprint('order_api', __name__, url_prefix='/api/v1/orders')
order_tag = Tag(name="OrderController", description="订单管理API")

class OrderAPI:
    """订单API类"""
    
    @staticmethod
    @order_api_bp.get(
        '/', 
        summary="获取订单列表", 
        tags=[order_tag]
    )
    def list_orders(query: OrderQueryModel):
        """获取订单列表"""
        try:
            orders, total = OrderService.search_orders(query)
            return {
                'orders': [OrderResponseModel.from_orm(o).dict() for o in orders],
                'total': total,
                'page': query.page,
                'per_page': query.per_page
            }
        except Exception as e:
            return {'message': str(e)}, 500
    
    @staticmethod
    @order_api_bp.post(
        '/', 
        summary="创建新订单", 
        tags=[order_tag]
    )
    def create_order(body: OrderCreateModel):
        """创建新订单"""
        try:
            # 需要在body中提供user_id
            order = OrderService.create_order(body.user_id, body)
            return {
                'message': 'Order created successfully',
                'order': OrderResponseModel.from_orm(order).dict()
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @order_api_bp.get(
        '/<int:order_id>', 
        summary="获取指定订单", 
        tags=[order_tag]
    )
    def get_order(path: OrderPathModel):
        """获取指定订单"""
        order = OrderService.get_order_by_id(path.order_id)
        
        if not order:
            return {'message': 'Order not found'}, 404
        
        return OrderResponseModel.from_orm(order).dict()
    
    @staticmethod
    @order_api_bp.put(
        '/<int:order_id>', 
        summary="更新订单信息", 
        tags=[order_tag]
    )
    def update_order(path: OrderPathModel, body: OrderUpdateModel):
        """更新订单信息"""
        try:
            order = OrderService.get_order_by_id(path.order_id)
            
            if not order:
                return {'message': 'Order not found'}, 404
            
            updated_order = OrderService.update_order(path.order_id, body)
            return {
                'message': 'Order updated successfully',
                'order': OrderResponseModel.from_orm(updated_order).dict()
            }
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @order_api_bp.delete(
        '/<int:order_id>/cancel', 
        summary="取消订单", 
        tags=[order_tag]
    )
    def cancel_order(path: OrderPathModel):
        """取消订单"""
        try:
            order = OrderService.get_order_by_id(path.order_id)
            
            if not order:
                return {'message': 'Order not found'}, 404
            
            if OrderService.cancel_order(path.order_id):
                return {'message': 'Order cancelled successfully'}
            else:
                return {'message': 'Failed to cancel order'}, 400
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @order_api_bp.get(
        '/statistics/<int:user_id>', 
        summary="获取订单统计", 
        tags=[order_tag]
    )
    def get_order_statistics(user_id: int):
        """获取用户的订单统计"""
        try:
            stats = OrderService.get_order_statistics(user_id)
            return stats
        except Exception as e:
            return {'message': str(e)}, 500
