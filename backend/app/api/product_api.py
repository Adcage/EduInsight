from flask_openapi3 import APIBlueprint, Tag
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model.product_model import (
    ProductCreateModel, ProductUpdateModel, ProductResponseModel,
    ProductListResponseModel, ProductPathModel, ProductQueryModel
)
from app.services.product_service import ProductService

product_api_bp = APIBlueprint('product_api', __name__, url_prefix='/api/v1/products')
product_tag = Tag(name="ProductController", description="产品管理API")

class ProductAPI:
    """产品API类"""
    
    @staticmethod
    @product_api_bp.get('/', summary="获取产品列表", tags=[product_tag])
    def list_products(query: ProductQueryModel):
        """获取产品列表 - 支持搜索和分页"""
        try:
            products, total = ProductService.search_products(query)
            return {
                'products': [ProductResponseModel.from_orm(p).dict() for p in products],
                'total': total,
                'page': query.page,
                'per_page': query.per_page
            }
        except Exception as e:
            return {'message': str(e)}, 500
    
    @staticmethod
    @product_api_bp.post(
        '/', 
        summary="创建新产品", 
        tags=[product_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def create_product(body: ProductCreateModel):
        """创建新产品 - 需要JWT认证"""
        try:
            current_user_id = get_jwt_identity()
            product = ProductService.create_product(body)
            return {
                'message': 'Product created successfully',
                'product': ProductResponseModel.from_orm(product).dict(),
                'created_by': current_user_id
            }, 201
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @product_api_bp.get('/<int:product_id>', summary="获取指定产品", tags=[product_tag])
    def get_product(path: ProductPathModel):
        """获取指定产品 - 公开接口"""
        product = ProductService.get_product_by_id(path.product_id)
        if not product:
            return {'message': 'Product not found'}, 404
        return ProductResponseModel.from_orm(product).dict()
    
    @staticmethod
    @product_api_bp.put(
        '/<int:product_id>', 
        summary="更新产品信息", 
        tags=[product_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def update_product(path: ProductPathModel, body: ProductUpdateModel):
        """更新产品信息 - 需要JWT认证"""
        try:
            product = ProductService.update_product(path.product_id, body)
            if not product:
                return {'message': 'Product not found'}, 404
            return {
                'message': 'Product updated successfully',
                'product': ProductResponseModel.from_orm(product).dict()
            }
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @product_api_bp.delete(
        '/<int:product_id>', 
        summary="删除产品", 
        tags=[product_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def delete_product(path: ProductPathModel):
        """删除产品 - 需要JWT认证"""
        if not ProductService.delete_product(path.product_id):
            return {'message': 'Product not found'}, 404
        return {'message': 'Product deleted successfully'}, 204
    
    @staticmethod
    @product_api_bp.get('/categories/<string:category>', summary="根据分类获取产品", tags=[product_tag])
    def get_products_by_category(category: str):
        """根据分类获取产品 - 公开接口"""
        try:
            products = ProductService.get_products_by_category(category)
            return {
                'products': [ProductResponseModel.from_orm(p).dict() for p in products],
                'total': len(products),
                'category': category
            }
        except Exception as e:
            return {'message': str(e)}, 500
