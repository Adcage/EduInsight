from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from decimal import Decimal

class ProductCreateModel(BaseModel):
    """产品创建模型"""
    name: str = Field(..., min_length=1, max_length=200, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    price: Decimal = Field(..., gt=0, description="产品价格")
    stock: int = Field(default=0, ge=0, description="库存数量")
    category: Optional[str] = Field(None, max_length=100, description="产品分类")

class ProductUpdateModel(BaseModel):
    """产品更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=200, description="产品名称")
    description: Optional[str] = Field(None, description="产品描述")
    price: Optional[Decimal] = Field(None, gt=0, description="产品价格")
    stock: Optional[int] = Field(None, ge=0, description="库存数量")
    category: Optional[str] = Field(None, max_length=100, description="产品分类")
    is_active: Optional[bool] = Field(None, description="是否激活")

class ProductResponseModel(BaseModel):
    """产品响应模型"""
    id: int
    name: str
    description: Optional[str] = None
    price: Decimal
    stock: int
    category: Optional[str] = None
    is_active: bool
    is_in_stock: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class ProductListResponseModel(BaseModel):
    """产品列表响应模型"""
    products: List[ProductResponseModel]
    total: int

class ProductPathModel(BaseModel):
    """产品路径参数模型"""
    product_id: int = Field(..., description="产品ID")

class ProductQueryModel(BaseModel):
    """产品查询模型"""
    category: Optional[str] = Field(None, description="产品分类")
    min_price: Optional[Decimal] = Field(None, ge=0, description="最低价格")
    max_price: Optional[Decimal] = Field(None, ge=0, description="最高价格")
    in_stock_only: Optional[bool] = Field(False, description="仅显示有库存商品")
    page: int = Field(1, ge=1, description="页码")
    per_page: int = Field(10, ge=1, le=100, description="每页数量")
