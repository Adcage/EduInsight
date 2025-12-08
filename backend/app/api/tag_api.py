"""
标签管理API

提供资料标签的创建、查询、删除等功能。
"""
from flask_openapi3 import APIBlueprint, Tag
from flask import request
from app.schemas.material_schemas import (
    MaterialTagCreateModel, MaterialTagResponseModel,
    TagPathModel
)
from app.schemas.common_schemas import MessageResponseModel
from app.services.tag_service import TagService
from app.models.user import UserRole
from app.utils.auth_decorators import login_required, role_required, log_user_action
from app.utils.response_handler import success_response, error_response
import logging

logger = logging.getLogger(__name__)

tag_api_bp = APIBlueprint('tag_api', __name__, url_prefix='/api/v1/material-tags')
tag_tag = Tag(name="TagController", description="资料标签管理API")


class TagAPI:
    """
    标签管理API类 - 装饰器方式
    
    提供标签相关的完整功能，包括：
    - 创建标签
    - 获取标签（列表、热门标签）
    - 搜索标签
    - 删除标签
    """
    
    @staticmethod
    @tag_api_bp.post('',
                    summary="创建标签",
                    tags=[tag_tag],
                    responses={201: MaterialTagResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("创建资料标签")
    def create_tag(body: MaterialTagCreateModel):
        """
        创建资料标签
        
        标签名称必须唯一。
        """
        try:
            tag = TagService.create_tag(name=body.name)
            
            return success_response(
                data=tag.to_dict(),
                message="标签创建成功",
                status_code=201
            )
            
        except ValueError as e:
            logger.warning(f"标签创建失败: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"标签创建异常: {str(e)}")
            return error_response("标签创建失败", 500)
    
    @staticmethod
    @tag_api_bp.get('',
                   summary="获取标签列表",
                   tags=[tag_tag])
    @login_required
    def get_tags():
        """
        获取标签列表
        
        支持分页，按使用次数降序排序。
        """
        try:
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 50, type=int)
            
            result = TagService.get_all_tags(page=page, per_page=per_page)
            
            tags_data = [tag.to_dict() for tag in result['tags']]
            
            response_data = {
                'tags': tags_data,
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'pages': result['pages']
            }
            
            return success_response(data=response_data)
            
        except Exception as e:
            logger.error(f"获取标签列表失败: {str(e)}")
            return error_response("获取标签列表失败", 500)
    
    @staticmethod
    @tag_api_bp.get('/popular',
                   summary="获取热门标签",
                   tags=[tag_tag])
    @login_required
    def get_popular_tags():
        """
        获取热门标签
        
        返回使用次数最多的标签。
        """
        try:
            limit = request.args.get('limit', 20, type=int)
            
            tags = TagService.get_popular_tags(limit=limit)
            tags_data = [tag.to_dict() for tag in tags]
            
            return success_response(data={'tags': tags_data})
            
        except Exception as e:
            logger.error(f"获取热门标签失败: {str(e)}")
            return error_response("获取热门标签失败", 500)
    
    @staticmethod
    @tag_api_bp.get('/search',
                   summary="搜索标签",
                   tags=[tag_tag])
    @login_required
    def search_tags():
        """
        搜索标签
        
        根据关键词模糊搜索标签名称。
        """
        try:
            keyword = request.args.get('q', '')
            limit = request.args.get('limit', 20, type=int)
            
            if not keyword:
                return error_response("搜索关键词不能为空", 400)
            
            tags = TagService.search_tags(keyword=keyword, limit=limit)
            tags_data = [tag.to_dict() for tag in tags]
            
            return success_response(data={'tags': tags_data})
            
        except Exception as e:
            logger.error(f"搜索标签失败: {str(e)}")
            return error_response("搜索标签失败", 500)
    
    @staticmethod
    @tag_api_bp.get('/<int:tagId>',
                   summary="获取标签详情",
                   tags=[tag_tag],
                   responses={200: MaterialTagResponseModel, 404: MessageResponseModel})
    @login_required
    def get_tag_detail(path: TagPathModel):
        """
        获取标签详情
        
        返回指定标签的详细信息。
        """
        try:
            tag = TagService.get_tag_by_id(path.tag_id)
            
            if not tag:
                return error_response("标签不存在", 404)
            
            return success_response(data=tag.to_dict())
            
        except Exception as e:
            logger.error(f"获取标签详情失败: {str(e)}")
            return error_response("获取标签详情失败", 500)
    
    @staticmethod
    @tag_api_bp.delete('/<int:tagId>',
                      summary="删除标签",
                      tags=[tag_tag],
                      responses={200: MessageResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @role_required(UserRole.ADMIN, UserRole.TEACHER)
    @log_user_action("删除资料标签")
    def delete_tag(path: TagPathModel):
        """
        删除标签
        
        只能删除未被使用的标签。
        只有管理员和教师可以删除标签。
        """
        try:
            TagService.delete_tag(path.tag_id)
            
            return success_response(message="标签删除成功")
            
        except ValueError as e:
            logger.warning(f"标签删除失败: {str(e)}")
            return error_response(str(e), 400 if "不存在" not in str(e) else 404)
        except Exception as e:
            logger.error(f"标签删除异常: {str(e)}")
            return error_response("标签删除失败", 500)
