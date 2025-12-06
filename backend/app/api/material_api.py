"""
资料管理API

提供资料上传、下载、查询、更新、删除等功能。
"""
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from flask import send_file, request, current_app, session
from app.schemas.material_schemas import (
    MaterialUploadModel, MaterialUpdateModel, MaterialResponseModel,
    MaterialDetailResponseModel, MaterialListResponseModel,
    MaterialQueryModel, MaterialPathModel, MaterialStatsModel
)
from app.schemas.common_schemas import BaseResponseModel, MessageResponseModel
from app.services.material_service import MaterialService
from app.utils.auth_decorators import login_required, log_user_action
from app.utils.response_handler import success_response, error_response
import logging
import os

logger = logging.getLogger(__name__)

material_api_bp = APIBlueprint('material_api', __name__, url_prefix='/api/v1/materials')
material_tag = Tag(name="MaterialController", description="资料管理API")


class MaterialAPI:
    """
    资料管理API类 - 装饰器方式
    
    提供资料相关的完整功能，包括：
    - 文件上传
    - 资料查询（列表、详情、搜索）
    - 资料更新
    - 资料删除
    - 文件下载
    - 统计信息
    """
    
    @staticmethod
    @material_api_bp.post('/upload',
                         summary="上传资料",
                         tags=[material_tag],
                         responses={201: MaterialResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("上传资料")
    def upload_material():
        """
        上传资料文件
        
        支持的文件类型：PDF、Word、PPT、Excel、图片、压缩包等。
        最大文件大小：100MB
        """
        try:
            # 获取当前用户ID
            user_id = session.get('user_id')
            
            # 获取上传的文件
            if 'file' not in request.files:
                return error_response("未找到上传文件", 400)
            
            file = request.files['file']
            
            if file.filename == '':
                return error_response("文件名为空", 400)
            
            # 获取表单数据
            title = request.form.get('title')
            description = request.form.get('description')
            course_id = request.form.get('course_id', type=int)
            category_id = request.form.get('category_id', type=int)
            tags_str = request.form.get('tags', '')
            
            # 解析标签
            tags = [tag.strip() for tag in tags_str.split(',') if tag.strip()] if tags_str else []
            
            if not title:
                return error_response("资料标题不能为空", 400)
            
            # 调用服务层上传资料
            material = MaterialService.upload_material(
                file=file,
                title=title,
                uploader_id=user_id,
                description=description,
                course_id=course_id,
                category_id=category_id,
                tags=tags
            )
            
            return success_response(
                data=material.to_dict(),
                message="资料上传成功",
                status_code=201
            )
            
        except ValueError as e:
            logger.warning(f"资料上传失败: {str(e)}")
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"资料上传异常: {str(e)}")
            return error_response("资料上传失败", 500)
    
    @staticmethod
    @material_api_bp.get('',
                        summary="获取资料列表",
                        tags=[material_tag],
                        responses={200: MaterialListResponseModel})
    @login_required
    def get_materials(query: MaterialQueryModel):
        """
        获取资料列表
        
        支持分页、筛选和排序：
        - 按课程筛选
        - 按分类筛选
        - 按上传者筛选
        - 按文件类型筛选
        - 关键词搜索
        """
        try:
            result = MaterialService.get_materials(
                page=query.page,
                per_page=query.per_page,
                course_id=query.course_id,
                category_id=query.category_id,
                uploader_id=query.uploader_id,
                file_type=query.file_type,
                search=query.search
            )
            
            # 使用 Pydantic 模型序列化每个资料（to_dict 已自动转换 datetime）
            materials_models = [
                MaterialResponseModel(**material.to_dict())
                for material in result['materials']
            ]
            
            # 使用 Pydantic 模型序列化列表响应，success_response 会自动处理
            response_model = MaterialListResponseModel(
                materials=materials_models,
                total=result['total'],
                page=result['page'],
                per_page=result['per_page'],
                pages=result['pages']
            )
            
            return success_response(data=response_model)
            
        except Exception as e:
            logger.error(f"获取资料列表失败: {str(e)}")
            return error_response("获取资料列表失败", 500)
    
    @staticmethod
    @material_api_bp.get('/<int:materialId>',
                        summary="获取资料详情",
                        tags=[material_tag],
                        responses={200: MaterialDetailResponseModel, 404: MessageResponseModel})
    @login_required
    def get_material_detail(path: MaterialPathModel):
        """
        获取资料详情
        
        返回资料的完整信息，包括关联的标签、分类、课程等。
        """
        try:
            material = MaterialService.get_material_by_id(
                path.material_id,
                increment_view=True
            )
            
            if not material:
                return error_response("资料不存在", 404)
            
            # 构建详细信息字典（to_dict 已自动转换 datetime）
            material_data = material.to_dict()
            
            # 添加标签信息
            material_data['tags'] = [tag.to_dict() for tag in material.tags.all()]
            
            # 添加分类名称
            if material.category:
                material_data['category_name'] = material.category.name
            
            # 添加上传者信息
            from app.models import User
            uploader = User.query.get(material.uploader_id)
            if uploader:
                material_data['uploader_name'] = uploader.real_name or uploader.username
            
            # 使用 Pydantic 模型序列化，success_response 会自动转换为驼峰命名
            response_model = MaterialDetailResponseModel(**material_data)
            
            return success_response(data=response_model)
            
        except Exception as e:
            logger.error(f"获取资料详情失败: {str(e)}")
            return error_response("获取资料详情失败", 500)
    
    @staticmethod
    @material_api_bp.put('/<int:materialId>',
                        summary="更新资料信息",
                        tags=[material_tag],
                        responses={200: MaterialResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @log_user_action("更新资料")
    def update_material(path: MaterialPathModel, body: MaterialUpdateModel):
        """
        更新资料信息
        
        只有资料的上传者可以更新。
        可以更新标题、描述、分类和标签。
        """
        try:
            user_id = session.get('user_id')
            
            material = MaterialService.update_material(
                material_id=path.material_id,
                user_id=user_id,
                title=body.title,
                description=body.description,
                category_id=body.category_id,
                tags=body.tags
            )
            
            return success_response(
                data=material.to_dict(),
                message="资料更新成功"
            )
            
        except ValueError as e:
            logger.warning(f"资料更新失败: {str(e)}")
            return error_response(str(e), 400 if "不存在" not in str(e) else 404)
        except Exception as e:
            logger.error(f"资料更新异常: {str(e)}")
            return error_response("资料更新失败", 500)
    
    @staticmethod
    @material_api_bp.delete('/<int:materialId>',
                           summary="删除资料",
                           tags=[material_tag],
                           responses={200: MessageResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @log_user_action("删除资料")
    def delete_material(path: MaterialPathModel):
        """
        删除资料
        
        只有资料的上传者可以删除。
        删除资料会同时删除文件和数据库记录。
        """
        try:
            user_id = session.get('user_id')
            
            MaterialService.delete_material(
                material_id=path.material_id,
                user_id=user_id
            )
            
            return success_response(message="资料删除成功")
            
        except ValueError as e:
            logger.warning(f"资料删除失败: {str(e)}")
            return error_response(str(e), 400 if "不存在" not in str(e) else 404)
        except Exception as e:
            logger.error(f"资料删除异常: {str(e)}")
            return error_response("资料删除失败", 500)
    
    @staticmethod
    @material_api_bp.get('/<int:materialId>/download',
                        summary="下载资料",
                        tags=[material_tag],
                        responses={404: MessageResponseModel})
    @login_required
    @log_user_action("下载资料")
    def download_material(path: MaterialPathModel):
        """
        下载资料文件
        
        返回文件流，浏览器会自动下载文件。
        """
        try:
            material = MaterialService.download_material(path.material_id)
            
            if not material:
                return error_response("资料不存在", 404)
            
            # 转换为绝对路径
            # 如果是相对路径，则相对于项目根目录（backend目录）
            if not os.path.isabs(material.file_path):
                # 获取项目根目录（backend目录）
                # __file__ 是 app/api/material_api.py
                # 需要向上两级到 app，再向上一级到 backend
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                file_path = os.path.join(base_dir, material.file_path)
            else:
                file_path = material.file_path
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return error_response("文件不存在", 404)
            
            # 发送文件
            return send_file(
                file_path,
                as_attachment=True,
                download_name=material.file_name
            )
            
        except Exception as e:
            logger.error(f"文件下载失败: {str(e)}")
            return error_response("文件下载失败", 500)
    
    @staticmethod
    @material_api_bp.get('/<int:materialId>/preview',
                        summary="预览资料",
                        tags=[material_tag],
                        responses={404: MessageResponseModel})
    @login_required
    @log_user_action("预览资料")
    def preview_material(path: MaterialPathModel):
        """
        预览资料文件
        
        返回文件流，浏览器会在线预览文件（不下载）。
        支持PDF、图片等可以在浏览器中直接显示的文件类型。
        """
        try:
            material = MaterialService.get_material_by_id(path.material_id)
            
            if not material:
                return error_response("资料不存在", 404)
            
            # 转换为绝对路径
            if not os.path.isabs(material.file_path):
                base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
                file_path = os.path.join(base_dir, material.file_path)
            else:
                file_path = material.file_path
            
            # 检查文件是否存在
            if not os.path.exists(file_path):
                logger.error(f"文件不存在: {file_path}")
                return error_response("文件不存在", 404)
            
            # 发送文件用于预览（不作为附件下载）
            return send_file(
                file_path,
                as_attachment=False,  # 关键：设置为False，浏览器会尝试在线预览
                download_name=material.file_name
            )
            
        except Exception as e:
            logger.error(f"文件预览失败: {str(e)}")
            return error_response("文件预览失败", 500)
    
    @staticmethod
    @material_api_bp.get('/search',
                        summary="搜索资料",
                        tags=[material_tag],
                        responses={200: MaterialListResponseModel})
    @login_required
    def search_materials():
        """
        搜索资料
        
        在资料标题、描述和关键词中搜索。
        """
        try:
            keyword = request.args.get('q', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            
            if not keyword:
                return error_response("搜索关键词不能为空", 400)
            
            result = MaterialService.search_materials(
                keyword=keyword,
                page=page,
                per_page=per_page
            )
            
            materials_data = [material.to_dict() for material in result['materials']]
            
            response_data = {
                'materials': materials_data,
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'pages': result['pages']
            }
            
            return success_response(data=response_data)
            
        except Exception as e:
            logger.error(f"搜索资料失败: {str(e)}")
            return error_response("搜索资料失败", 500)
    
    @staticmethod
    @material_api_bp.get('/statistics',
                        summary="获取资料统计信息",
                        tags=[material_tag],
                        responses={200: MaterialStatsModel})
    @login_required
    def get_statistics():
        """
        获取资料统计信息
        
        包括：
        - 资料总数
        - 总大小
        - 总下载次数
        - 总浏览次数
        - 按类型统计
        - 按分类统计
        - 最近上传
        - 热门资料
        """
        try:
            stats = MaterialService.get_material_statistics()
            
            # 转换资料列表为字典
            stats['recent_uploads'] = [m.to_dict() for m in stats['recent_uploads']]
            stats['popular_materials'] = [m.to_dict() for m in stats['popular_materials']]
            
            return success_response(data=stats)
            
        except Exception as e:
            logger.error(f"获取统计信息失败: {str(e)}")
            return error_response("获取统计信息失败", 500)
