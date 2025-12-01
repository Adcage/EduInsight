from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal
from enum import Enum

class OrderStatusEnum(str, Enum):
    """订单状态枚举"""
    PENDING = "pending"
    CONFIRMED = "confirmed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"

class OrderItemCreateModel(BaseModel):
    """订单项创建模型"""
    product_id: int = Field(..., description="产品ID")
    quantity: int = Field(..., gt=0, description="数量")

class OrderCreateModel(BaseModel):
    """订单创建模型"""
    items: List[OrderItemCreateModel] = Field(..., min_items=1, description="订单项列表")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    notes: Optional[str] = Field(None, description="订单备注")

class OrderUpdateModel(BaseModel):
    """订单更新模型"""
    status: Optional[OrderStatusEnum] = Field(None, description="订单状态")
    shipping_address: Optional[str] = Field(None, description="收货地址")
    notes: Optional[str] = Field(None, description="订单备注")

class OrderItemResponseModel(BaseModel):
    """订单项响应模型"""
    id: int
    product_id: int
    quantity: int
    unit_price: Decimal
    subtotal: Decimal
    product_name: Optional[str] = None
    
    class Config:
        from_attributes = True

class OrderResponseModel(BaseModel):
    """订单响应模型"""
    id: int
    user_id: int
    total_amount: Decimal
    status: OrderStatusEnum
    shipping_address: Optional[str] = None
    notes: Optional[str] = None
    item_count: int
    items: List[OrderItemResponseModel] = []
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class OrderListResponseModel(BaseModel):
    """订单列表响应模型"""
    orders: List[OrderResponseModel]
    total: int

class OrderPathModel(BaseModel):
    """订单路径参数模型"""
    order_id: int = Field(..., description="订单ID")

class OrderQueryModel(BaseModel):
    """订单查询模型"""
    status: Optional[OrderStatusEnum] = Field(None, description="订单状态")
    user_id: Optional[int] = Field(None, description="用户ID")
    start_date: Optional[datetime] = Field(None, description="开始日期")
    end_date: Optional[datetime] = Field(None, description="结束日期")
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(10, ge=1, le=100, description="每页数量")
