from flask_openapi3 import APIBlueprint, Tag
from flask_jwt_extended import jwt_required, get_jwt_identity
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
        tags=[order_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def list_orders(query: OrderQueryModel):
        """获取订单列表 - 需要JWT认证"""
        try:
            current_user_id = get_jwt_identity()
            # 普通用户只能查看自己的订单
            query.user_id = current_user_id
            
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
        tags=[order_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def create_order(body: OrderCreateModel):
        """创建新订单 - 需要JWT认证"""
        try:
            current_user_id = get_jwt_identity()
            order = OrderService.create_order(current_user_id, body)
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
        tags=[order_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def get_order(path: OrderPathModel):
        """获取指定订单 - 需要JWT认证"""
        current_user_id = get_jwt_identity()
        order = OrderService.get_order_by_id(path.order_id)
        
        if not order:
            return {'message': 'Order not found'}, 404
        
        # 只能查看自己的订单
        if order.user_id != current_user_id:
            return {'message': 'Permission denied'}, 403
        
        return OrderResponseModel.from_orm(order).dict()
    
    @staticmethod
    @order_api_bp.put(
        '/<int:order_id>', 
        summary="更新订单信息", 
        tags=[order_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def update_order(path: OrderPathModel, body: OrderUpdateModel):
        """更新订单信息 - 需要JWT认证"""
        try:
            current_user_id = get_jwt_identity()
            order = OrderService.get_order_by_id(path.order_id)
            
            if not order:
                return {'message': 'Order not found'}, 404
            
            # 只能修改自己的订单
            if order.user_id != current_user_id:
                return {'message': 'Permission denied'}, 403
            
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
        tags=[order_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def cancel_order(path: OrderPathModel):
        """取消订单 - 需要JWT认证"""
        try:
            current_user_id = get_jwt_identity()
            order = OrderService.get_order_by_id(path.order_id)
            
            if not order:
                return {'message': 'Order not found'}, 404
            
            # 只能取消自己的订单
            if order.user_id != current_user_id:
                return {'message': 'Permission denied'}, 403
            
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
        '/statistics', 
        summary="获取订单统计", 
        tags=[order_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def get_order_statistics():
        """获取当前用户的订单统计 - 需要JWT认证"""
        try:
            current_user_id = get_jwt_identity()
            stats = OrderService.get_order_statistics(current_user_id)
            return stats
        except Exception as e:
            return {'message': str(e)}, 500
