"""
资料管理服务层

处理资料相关的业务逻辑。
"""
from typing import List, Optional, Dict, Any
from werkzeug.datastructures import FileStorage
from sqlalchemy import or_, and_, func
from app.extensions import db
from app.models import Material, MaterialCategory, MaterialTag, Course
from app.utils.file_utils import (
    save_uploaded_file, delete_file, get_file_type,
    get_file_size_mb, validate_file
)
import logging

logger = logging.getLogger(__name__)


class MaterialService:
    """资料管理服务类"""
    
    @staticmethod
    def upload_material(
        file: FileStorage,
        title: str,
        uploader_id: int,
        description: Optional[str] = None,
        course_id: Optional[int] = None,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Material:
        """
        上传资料
        
        Args:
            file: 上传的文件
            title: 资料标题
            uploader_id: 上传者ID
            description: 资料描述
            course_id: 课程ID
            category_id: 分类ID
            tags: 标签列表
            
        Returns:
            Material: 创建的资料对象
            
        Raises:
            ValueError: 文件验证失败或参数错误
        """
        try:
            # 验证文件
            is_valid, error_msg = validate_file(file)
            if not is_valid:
                raise ValueError(error_msg)
            
            # 保存文件
            file_path, unique_filename, file_size = save_uploaded_file(file)
            
            # 获取文件类型
            file_type = get_file_type(file.filename)
            
            # 创建资料记录
            material = Material(
                title=title,
                description=description,
                file_name=file.filename,
                file_path=file_path,
                file_size=file_size,
                file_type=file_type,
                course_id=course_id,
                uploader_id=uploader_id,
                category_id=category_id
            )
            
            material.save()
            
            # 添加标签
            if tags:
                for tag_name in tags:
                    if tag_name.strip():
                        material.add_tag(tag_name.strip())
            
            logger.info(f"资料上传成功: {material.id} - {title}")
            return material
            
        except Exception as e:
            logger.error(f"资料上传失败: {str(e)}")
            # 如果创建记录失败，删除已上传的文件
            if 'file_path' in locals():
                delete_file(file_path)
            raise
    
    @staticmethod
    def get_material_by_id(material_id: int, increment_view: bool = False) -> Optional[Material]:
        """
        根据ID获取资料
        
        Args:
            material_id: 资料ID
            increment_view: 是否增加浏览次数
            
        Returns:
            Optional[Material]: 资料对象
        """
        material = Material.query.get(material_id)
        
        if material and increment_view:
            material.increment_view_count()
        
        return material
    
    @staticmethod
    def get_materials(
        page: int = 1,
        per_page: int = 20,
        course_id: Optional[int] = None,
        category_id: Optional[int] = None,
        uploader_id: Optional[int] = None,
        file_type: Optional[str] = None,
        search: Optional[str] = None,
        sort_by: str = 'created_at',
        order: str = 'desc'
    ) -> Dict[str, Any]:
        """
        获取资料列表（分页、筛选、排序）
        
        Args:
            page: 页码
            per_page: 每页数量
            course_id: 课程ID筛选
            category_id: 分类ID筛选
            uploader_id: 上传者ID筛选
            file_type: 文件类型筛选
            search: 搜索关键词
            sort_by: 排序字段
            order: 排序方向
            
        Returns:
            Dict: 包含资料列表和分页信息
        """
        # 构建查询
        query = Material.query
        
        # 应用筛选条件
        if course_id:
            query = query.filter(Material.course_id == course_id)
        
        if category_id:
            query = query.filter(Material.category_id == category_id)
        
        if uploader_id:
            query = query.filter(Material.uploader_id == uploader_id)
        
        if file_type:
            query = query.filter(Material.file_type == file_type)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Material.title.like(search_pattern),
                    Material.description.like(search_pattern),
                    Material.keywords.like(search_pattern)
                )
            )
        
        # 应用排序
        sort_column = getattr(Material, sort_by, Material.created_at)
        if order.lower() == 'desc':
            query = query.order_by(sort_column.desc())
        else:
            query = query.order_by(sort_column.asc())
        
        # 分页
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)
        
        return {
            'materials': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def update_material(
        material_id: int,
        user_id: int,
        title: Optional[str] = None,
        description: Optional[str] = None,
        category_id: Optional[int] = None,
        tags: Optional[List[str]] = None
    ) -> Material:
        """
        更新资料信息
        
        Args:
            material_id: 资料ID
            user_id: 当前用户ID
            title: 资料标题
            description: 资料描述
            category_id: 分类ID
            tags: 标签列表
            
        Returns:
            Material: 更新后的资料对象
            
        Raises:
            ValueError: 资料不存在或无权限
        """
        material = Material.query.get(material_id)
        
        if not material:
            raise ValueError("资料不存在")
        
        # 检查权限（只有上传者可以修改）
        if not material.is_owner(user_id):
            raise ValueError("无权限修改此资料")
        
        # 更新字段
        if title is not None:
            material.title = title
        
        if description is not None:
            material.description = description
        
        if category_id is not None:
            material.category_id = category_id
        
        # 更新标签
        if tags is not None:
            # 移除所有现有标签
            for tag in material.tags.all():
                material.remove_tag(tag.name)
            
            # 添加新标签
            for tag_name in tags:
                if tag_name.strip():
                    material.add_tag(tag_name.strip())
        
        material.save()
        
        logger.info(f"资料更新成功: {material_id}")
        return material
    
    @staticmethod
    def delete_material(material_id: int, user_id: int) -> bool:
        """
        删除资料
        
        Args:
            material_id: 资料ID
            user_id: 当前用户ID
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            ValueError: 资料不存在或无权限
        """
        material = Material.query.get(material_id)
        
        if not material:
            raise ValueError("资料不存在")
        
        # 检查权限（只有上传者可以删除）
        if not material.is_owner(user_id):
            raise ValueError("无权限删除此资料")
        
        # 删除文件
        file_deleted = delete_file(material.file_path)
        if not file_deleted:
            logger.warning(f"文件删除失败: {material.file_path}")
        
        # 删除数据库记录
        material.delete()
        
        logger.info(f"资料删除成功: {material_id}")
        return True
    
    @staticmethod
    def download_material(material_id: int) -> Optional[Material]:
        """
        下载资料（增加下载次数）
        
        Args:
            material_id: 资料ID
            
        Returns:
            Optional[Material]: 资料对象
        """
        material = Material.query.get(material_id)
        
        if material:
            material.increment_download_count()
        
        return material
    
    @staticmethod
    def search_materials(keyword: str, page: int = 1, per_page: int = 20) -> Dict[str, Any]:
        """
        搜索资料
        
        Args:
            keyword: 搜索关键词
            page: 页码
            per_page: 每页数量
            
        Returns:
            Dict: 包含搜索结果和分页信息
        """
        pagination = Material.search(keyword, page=page, per_page=per_page)
        
        return {
            'materials': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_material_statistics() -> Dict[str, Any]:
        """
        获取资料统计信息
        
        Returns:
            Dict: 统计信息
        """
        # 总资料数
        total_materials = Material.query.count()
        
        # 总大小
        total_size = db.session.query(func.sum(Material.file_size)).scalar() or 0
        
        # 总下载次数
        total_downloads = db.session.query(func.sum(Material.download_count)).scalar() or 0
        
        # 总浏览次数
        total_views = db.session.query(func.sum(Material.view_count)).scalar() or 0
        
        # 按文件类型统计
        by_type = db.session.query(
            Material.file_type,
            func.count(Material.id).label('count')
        ).group_by(Material.file_type).all()
        
        by_type_dict = {item[0]: item[1] for item in by_type}
        
        # 按分类统计
        by_category = db.session.query(
            MaterialCategory.name,
            func.count(Material.id).label('count')
        ).join(Material, Material.category_id == MaterialCategory.id, isouter=True)\
         .group_by(MaterialCategory.name).all()
        
        by_category_dict = {item[0]: item[1] for item in by_category if item[0]}
        
        # 最近上传
        recent_uploads = Material.query.order_by(Material.created_at.desc()).limit(10).all()
        
        # 热门资料（按下载次数）
        popular_materials = Material.query.order_by(Material.download_count.desc()).limit(10).all()
        
        return {
            'total_materials': total_materials,
            'total_size': total_size,
            'total_downloads': total_downloads,
            'total_views': total_views,
            'by_type': by_type_dict,
            'by_category': by_category_dict,
            'recent_uploads': recent_uploads,
            'popular_materials': popular_materials
        }
