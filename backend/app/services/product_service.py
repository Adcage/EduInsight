from typing import List, Optional, Tuple
from sqlalchemy import and_, or_
from app.models.product import Product
from app.model.product_model import ProductCreateModel, ProductUpdateModel, ProductQueryModel
from app.extensions import db

class ProductService:
    """产品业务逻辑服务"""
    
    @staticmethod
    def get_all_products() -> List[Product]:
        """获取所有激活的产品"""
        return Product.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_product_by_id(product_id: int) -> Optional[Product]:
        """根据ID获取产品"""
        return Product.query.filter_by(id=product_id, is_active=True).first()
    
    @staticmethod
    def create_product(product_data: ProductCreateModel) -> Product:
        """创建新产品"""
        product = Product(
            name=product_data.name,
            description=product_data.description,
            price=product_data.price,
            stock=product_data.stock,
            category=product_data.category
        )
        
        db.session.add(product)
        db.session.commit()
        return product
    
    @staticmethod
    def update_product(product_id: int, product_data: ProductUpdateModel) -> Optional[Product]:
        """更新产品信息"""
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return None
        
        # 更新产品信息
        update_data = product_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(product, field, value)
        
        db.session.commit()
        return product
    
    @staticmethod
    def delete_product(product_id: int) -> bool:
        """软删除产品"""
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return False
        
        product.is_active = False
        db.session.commit()
        return True
    
    @staticmethod
    def search_products(query: ProductQueryModel) -> Tuple[List[Product], int]:
        """搜索产品"""
        filters = [Product.is_active == True]
        
        # 分类过滤
        if query.category:
            filters.append(Product.category == query.category)
        
        # 价格范围过滤
        if query.min_price is not None:
            filters.append(Product.price >= query.min_price)
        if query.max_price is not None:
            filters.append(Product.price <= query.max_price)
        
        # 库存过滤
        if query.in_stock_only:
            filters.append(Product.stock > 0)
        
        # 构建查询
        base_query = Product.query.filter(and_(*filters))
        
        # 分页
        total = base_query.count()
        products = base_query.offset((query.page - 1) * query.per_page).limit(query.per_page).all()
        
        return products, total
    
    @staticmethod
    def get_products_by_category(category: str) -> List[Product]:
        """根据分类获取产品"""
        return Product.query.filter_by(category=category, is_active=True).all()
    
    @staticmethod
    def update_stock(product_id: int, quantity: int) -> bool:
        """更新库存"""
        product = ProductService.get_product_by_id(product_id)
        if not product:
            return False
        
        if product.reduce_stock(quantity):
            db.session.commit()
            return True
        return False
    
    @staticmethod
    def get_low_stock_products(threshold: int = 10) -> List[Product]:
        """获取低库存产品"""
        return Product.query.filter(
            Product.is_active == True,
            Product.stock <= threshold
        ).all()
