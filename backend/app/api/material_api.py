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
from app.schemas.classification_schemas import (
    ClassifyMaterialResponseModel, KeywordResponseModel, KeywordQueryModel,
    TagSuggestionResponseModel, ClassificationLogPathModel,
    MaterialClassifyPathModel
)
from app.schemas.common_schemas import BaseResponseModel, MessageResponseModel
from app.services.material_service import MaterialService
from app.services.classification_service import ClassificationService
from app.utils.auth_decorators import login_required, log_user_action
from app.utils.response_handler import success_response, error_response
import logging
import os

logger = logging.getLogger(__name__)

material_api_bp = APIBlueprint('material_api', __name__, url_prefix='/api/v1/materials')
material_tag = Tag(name="MaterialController", description="资料管理API")
classification_tag = Tag(name="ClassificationController", description="智能分类API")


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
        - 按标签筛选
        - 关键词搜索
        """
        try:
            # 手动从 request.args 获取参数（作为备用方案）
            # 优先使用 request.args 中的值，如果不存在则使用 query 对象的默认值
            page = request.args.get('page', type=int) or query.page
            
            # per_page 可能来自 page_size 或 perPage
            per_page_raw = request.args.get('page_size') or request.args.get('perPage')
            per_page = int(per_page_raw) if per_page_raw else query.per_page
            
            # 其他参数
            course_id_raw = request.args.get('course_id') or request.args.get('courseId')
            course_id = int(course_id_raw) if course_id_raw else query.course_id
            
            category_id_raw = request.args.get('category_id') or request.args.get('categoryId')
            category_id = int(category_id_raw) if category_id_raw else query.category_id
            
            uploader_id_raw = request.args.get('uploader_id') or request.args.get('uploaderId')
            uploader_id = int(uploader_id_raw) if uploader_id_raw else query.uploader_id
            
            file_type = request.args.get('file_type') or request.args.get('fileType') or query.file_type
            search = request.args.get('search') or query.search
            sort_by = request.args.get('sort_by') or request.args.get('sortBy') or query.sort_by
            order = request.args.get('order') or query.order
            
            # 处理标签ID列表
            tag_ids = None
            tag_ids_raw = request.args.get('tag_ids') or request.args.get('tagIds')
            if tag_ids_raw:
                try:
                    # 支持逗号分隔的字符串或JSON数组
                    if isinstance(tag_ids_raw, str):
                        if tag_ids_raw.startswith('['):
                            import json
                            tag_ids = json.loads(tag_ids_raw)
                        else:
                            tag_ids = [int(x.strip()) for x in tag_ids_raw.split(',') if x.strip()]
                    else:
                        tag_ids = [int(tag_ids_raw)]
                except (ValueError, json.JSONDecodeError) as e:
                    print(f"解析 tag_ids 失败: {e}")
                    tag_ids = None
            elif query.tag_ids:
                tag_ids = query.tag_ids
            
            # 处理日期范围
            start_date = request.args.get('start_date') or request.args.get('startDate') or query.start_date
            end_date = request.args.get('end_date') or request.args.get('endDate') or query.end_date
            
            result = MaterialService.get_materials(
                page=page,
                per_page=per_page,
                course_id=course_id,
                category_id=category_id,
                uploader_id=uploader_id,
                file_type=file_type,
                search=search,
                tag_ids=tag_ids,
                start_date=start_date,
                end_date=end_date,
                sort_by=sort_by,
                order=order
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
        
        在资料标题、描述、关键词和文件名中搜索。
        支持按分类、文件类型筛选，支持多种排序方式。
        """
        try:
            keyword = request.args.get('q', '')
            page = request.args.get('page', 1, type=int)
            per_page = request.args.get('per_page', 20, type=int)
            category_id = request.args.get('category_id', type=int)
            file_type = request.args.get('file_type')
            sort_by = request.args.get('sort_by', 'relevance')
            
            if not keyword:
                return error_response("搜索关键词不能为空", 400)
            
            result = MaterialService.search_materials(
                keyword=keyword,
                page=page,
                per_page=per_page,
                category_id=category_id,
                file_type=file_type,
                sort_by=sort_by
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


class ClassificationAPI:
    """
    智能分类API类
    
    提供资料智能分类相关功能，包括：
    - 分析并分类资料
    - 提取关键词
    - 推荐标签
    - 分类日志管理
    """
    
    @staticmethod
    @material_api_bp.post('/<int:materialId>/classify',
                         summary="分析并分类资料",
                         tags=[classification_tag],
                         responses={200: ClassifyMaterialResponseModel, 404: MessageResponseModel})
    @login_required
    @log_user_action("分析分类资料")
    def classify_material(path: MaterialClassifyPathModel):
        """
        分析并分类资料
        
        对指定资料进行内容分析，提取关键词并推荐分类。
        - 高置信度 (>0.7): 自动应用分类
        - 中等置信度 (0.5-0.7): 需要用户确认
        - 低置信度 (<0.5): 不推荐分类
        """
        try:
            result = ClassificationService.classify_material(path.material_id)
            
            # 转换关键词为响应模型
            keywords = [
                KeywordResponseModel(keyword=kw['keyword'], weight=kw['weight'])
                for kw in result.get('keywords', [])
            ]
            
            response = ClassifyMaterialResponseModel(
                material_id=result['material_id'],
                suggested_category_id=result.get('suggested_category_id'),
                suggested_category_name=result.get('suggested_category_name'),
                confidence=result['confidence'],
                should_auto_apply=result['should_auto_apply'],
                needs_confirmation=result['needs_confirmation'],
                keywords=keywords,
                log_id=result.get('log_id'),
                error=result.get('error')
            )
            
            return success_response(data=response, message="分类分析完成")
            
        except ValueError as e:
            logger.warning(f"分类分析失败: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            logger.error(f"分类分析异常: {str(e)}")
            return error_response("分类分析失败", 500)
    
    @staticmethod
    @material_api_bp.get('/<int:materialId>/keywords',
                        summary="获取资料关键词",
                        tags=[classification_tag],
                        responses={200: KeywordResponseModel, 404: MessageResponseModel})
    @login_required
    def get_keywords(path: MaterialClassifyPathModel, query: KeywordQueryModel):
        """
        获取资料关键词
        
        返回资料的关键词列表，包含关键词和权重。
        如果关键词尚未提取，会自动进行提取。
        """
        try:
            # 从请求参数获取 top_n
            top_n = request.args.get('top_n', type=int) or request.args.get('topN', type=int) or query.top_n
            
            keywords = ClassificationService.extract_keywords(path.material_id, top_n=top_n)
            
            # 转换为响应模型
            keyword_models = [
                KeywordResponseModel(keyword=kw['keyword'], weight=kw['weight'])
                for kw in keywords
            ]
            
            return success_response(data=keyword_models, message="获取关键词成功")
            
        except ValueError as e:
            logger.warning(f"获取关键词失败: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            logger.error(f"获取关键词异常: {str(e)}")
            return error_response("获取关键词失败", 500)
    
    @staticmethod
    @material_api_bp.post('/<int:materialId>/suggest-tags',
                         summary="获取标签建议",
                         tags=[classification_tag],
                         responses={200: TagSuggestionResponseModel, 404: MessageResponseModel})
    @login_required
    def suggest_tags(path: MaterialClassifyPathModel):
        """
        获取标签建议
        
        根据资料内容和关键词推荐相关标签。
        返回最多5个标签建议，包括现有标签和新建议的标签。
        """
        try:
            suggestions = ClassificationService.suggest_tags(path.material_id)
            
            # 转换为响应模型
            suggestion_models = [
                TagSuggestionResponseModel(
                    tag_name=s['tag_name'],
                    tag_id=s.get('tag_id'),
                    is_existing=s['is_existing'],
                    relevance=s['relevance']
                )
                for s in suggestions
            ]
            
            return success_response(data=suggestion_models, message="获取标签建议成功")
            
        except ValueError as e:
            logger.warning(f"获取标签建议失败: {str(e)}")
            return error_response(str(e), 404)
        except Exception as e:
            logger.error(f"获取标签建议异常: {str(e)}")
            return error_response("获取标签建议失败", 500)
    
    @staticmethod
    @material_api_bp.post('/classification-logs/<int:logId>/accept',
                         summary="接受分类建议",
                         tags=[classification_tag],
                         responses={200: MessageResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @log_user_action("接受分类建议")
    def accept_classification(path: ClassificationLogPathModel):
        """
        接受分类建议
        
        接受指定的分类建议，将建议的分类应用到资料。
        """
        try:
            ClassificationService.accept_classification(path.log_id)
            return success_response(message="已接受分类建议")
            
        except ValueError as e:
            logger.warning(f"接受分类建议失败: {str(e)}")
            if "不存在" in str(e):
                return error_response(str(e), 404)
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"接受分类建议异常: {str(e)}")
            return error_response("接受分类建议失败", 500)
    
    @staticmethod
    @material_api_bp.post('/classification-logs/<int:logId>/reject',
                         summary="拒绝分类建议",
                         tags=[classification_tag],
                         responses={200: MessageResponseModel, 400: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    @log_user_action("拒绝分类建议")
    def reject_classification(path: ClassificationLogPathModel):
        """
        拒绝分类建议
        
        拒绝指定的分类建议，保持资料原有分类不变。
        """
        try:
            ClassificationService.reject_classification(path.log_id)
            return success_response(message="已拒绝分类建议")
            
        except ValueError as e:
            logger.warning(f"拒绝分类建议失败: {str(e)}")
            if "不存在" in str(e):
                return error_response(str(e), 404)
            return error_response(str(e), 400)
        except Exception as e:
            logger.error(f"拒绝分类建议异常: {str(e)}")
            return error_response("拒绝分类建议失败", 500)
