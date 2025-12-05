"""
分类管理API

提供资料分类的创建、查询、更新、删除等功能。
"""
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.material_schemas import (
    MaterialCategoryCreateModel, MaterialCategoryUpdateModel,
    MaterialCategoryResponseModel, MaterialCategoryTreeModel,
    MaterialCategoryPathModel
)
from app.schemas.common_schemas import MessageResponseModel
from app.services.category_service import CategoryService
from app.utils.auth_decorators import login_required, role_required, log_user_action
from app.utils.response_handler import success_response, error_response
import logging

logger = logging.getLogger(__name__)

category_api_bp = APIBlueprint('category_api', __name__, url_prefix='/api/v1/material-categories')
category_tag = Tag(name="CategoryController", description="资料分类管理API")


class CategoryAPI:
    """
    分类管理API类 - 装饰器方式
    
    提供分类相关的完整功能，包括：
    - 创建分类
    - 获取分类（列表、树形结构、详情）
    - 更新分类
    - 删除分类
    """
    
    @staticmethod
    @category_api_bp.post('',
                         summary="创建分类",
                         tags=[category_tag],
                         responses={201: MaterialCategoryResponseModel, 400: MessageResponseModel})
    @login_required
    @role_required(['admin', 'teacher'])
    @log_user_action("创建资料分类")
    def create_category(body: MaterialCategoryCreateModel):
        """
        创建资料分类
        
        支持创建多级分类，可以指定父分类。
        只有管理员和教师可以创建分类。
        """
        try:
            category = CategoryService.create_category(
                name=body.name,
                description=body.description,
                parent_id=body.parent_id,
                sort_order=body.sort_order
            )
            
            return success_response(
                data=category.to_dict(),
                message="分类创建成功",
                status_code=201
            )
            
        except ValueError as e:
            logger.warning(f"分类创建失败: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"分类创建异常: {str(e)}")
            return error_response("分类创建失败", 500)
    
    @staticmethod
    @category_api_bp.get('',
                        summary="获取分类列表",
                        tags=[category_tag])
    @login_required
    def get_categories():
        """
        获取所有分类（平铺列表）
        
        返回所有分类的平铺列表，按排序序号排序。
        """
        try:
            categories = CategoryService.get_all_categories()
            categories_data = [category.to_dict() for category in categories]
            
            return success_response(data={'categories': categories_data})
            
        except Exception as e:
            logger.error(f"获取分类列表失败: {str(e)}")
            return error_response("获取分类列表失败", 500)
    
    @staticmethod
    @category_api_bp.get('/tree',
                        summary="获取分类树",
                        tags=[category_tag])
    @login_required
    def get_category_tree():
        """
        获取分类树形结构
        
        返回树形结构的分类数据，便于前端展示。
        """
        try:
            tree = CategoryService.get_category_tree()
            
            return success_response(data={'tree': tree})
            
        except Exception as e:
            logger.error(f"获取分类树失败: {str(e)}")
            return error_response("获取分类树失败", 500)
    
    @staticmethod
    @category_api_bp.get('/<int:categoryId>',
                        summary="获取分类详情",
                        tags=[category_tag],
                        responses={200: MaterialCategoryResponseModel, 404: MessageResponseModel})
    @login_required
    def get_category_detail(path: MaterialCategoryPathModel):
        """
        获取分类详情
        
        返回指定分类的详细信息。
        """
        try:
            category = CategoryService.get_category_by_id(path.category_id)
            
            if not category:
                return error_response("分类不存在", 404)
            
            return success_response(data=category.to_dict())
            
        except Exception as e:
            logger.error(f"获取分类详情失败: {str(e)}")
            return error_response("获取分类详情失败", 500)
    
    @staticmethod
    @category_api_bp.get('/<int:categoryId>/children',
                        summary="获取子分类",
                        tags=[category_tag])
    @login_required
    def get_children_categories(path: MaterialCategoryPathModel):
        """
        获取子分类
        
        返回指定分类的所有直接子分类。
        """
        try:
            children = CategoryService.get_children_categories(path.category_id)
            children_data = [child.to_dict() for child in children]
            
            return success_response(data={'children': children_data})
            
        except Exception as e:
            logger.error(f"获取子分类失败: {str(e)}")
            return error_response("获取子分类失败", 500)
    
    @staticmethod
    @category_api_bp.put('/<int:categoryId>',
                        summary="更新分类",
                        tags=[category_tag],
                        responses={200: MaterialCategoryResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @role_required(['admin', 'teacher'])
    @log_user_action("更新资料分类")
    def update_category(path: MaterialCategoryPathModel, body: MaterialCategoryUpdateModel):
        """
        更新分类信息
        
        可以更新分类名称、描述、父分类和排序序号。
        只有管理员和教师可以更新分类。
        """
        try:
            category = CategoryService.update_category(
                category_id=path.category_id,
                name=body.name,
                description=body.description,
                parent_id=body.parent_id,
                sort_order=body.sort_order
            )
            
            return success_response(
                data=category.to_dict(),
                message="分类更新成功"
            )
            
        except ValueError as e:
            logger.warning(f"分类更新失败: {str(e)}")
            return error_response(str(e), 400 if "不存在" not in str(e) else 404)
        except Exception as e:
            logger.error(f"分类更新异常: {str(e)}")
            return error_response("分类更新失败", 500)
    
    @staticmethod
    @category_api_bp.delete('/<int:categoryId>',
                           summary="删除分类",
                           tags=[category_tag],
                           responses={200: MessageResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @role_required(['admin', 'teacher'])
    @log_user_action("删除资料分类")
    def delete_category(path: MaterialCategoryPathModel):
        """
        删除分类
        
        只能删除没有子分类和关联资料的分类。
        只有管理员和教师可以删除分类。
        """
        try:
            CategoryService.delete_category(path.category_id)
            
            return success_response(message="分类删除成功")
            
        except ValueError as e:
            logger.warning(f"分类删除失败: {str(e)}")
            return error_response(str(e), 400 if "不存在" not in str(e) else 404)
        except Exception as e:
            logger.error(f"分类删除异常: {str(e)}")
            return error_response("分类删除失败", 500)
