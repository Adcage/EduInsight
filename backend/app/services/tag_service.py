"""
标签管理服务层

处理资料标签相关的业务逻辑。
"""
from typing import List, Optional
from app.extensions import db
from app.models import MaterialTag
import logging

logger = logging.getLogger(__name__)


class TagService:
    """标签管理服务类"""
    
    @staticmethod
    def create_tag(name: str) -> MaterialTag:
        """
        创建标签
        
        Args:
            name: 标签名称
            
        Returns:
            MaterialTag: 创建的标签对象
            
        Raises:
            ValueError: 标签已存在
        """
        # 检查标签是否已存在
        existing_tag = MaterialTag.query.filter_by(name=name).first()
        if existing_tag:
            raise ValueError("标签已存在")
        
        tag = MaterialTag(name=name)
        tag.save()
        
        logger.info(f"标签创建成功: {tag.id} - {name}")
        return tag
    
    @staticmethod
    def get_tag_by_id(tag_id: int) -> Optional[MaterialTag]:
        """
        根据ID获取标签
        
        Args:
            tag_id: 标签ID
            
        Returns:
            Optional[MaterialTag]: 标签对象
        """
        return MaterialTag.query.get(tag_id)
    
    @staticmethod
    def get_tag_by_name(name: str) -> Optional[MaterialTag]:
        """
        根据名称获取标签
        
        Args:
            name: 标签名称
            
        Returns:
            Optional[MaterialTag]: 标签对象
        """
        return MaterialTag.query.filter_by(name=name).first()
    
    @staticmethod
    def get_all_tags(page: int = 1, per_page: int = 50) -> dict:
        """
        获取所有标签（分页）
        
        Args:
            page: 页码
            per_page: 每页数量
            
        Returns:
            dict: 包含标签列表和分页信息
        """
        pagination = MaterialTag.query.order_by(MaterialTag.usage_count.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )
        
        return {
            'tags': pagination.items,
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
    
    @staticmethod
    def get_popular_tags(limit: int = 20) -> List[MaterialTag]:
        """
        获取热门标签
        
        Args:
            limit: 返回数量
            
        Returns:
            List[MaterialTag]: 热门标签列表
        """
        return MaterialTag.get_popular_tags(limit=limit)
    
    @staticmethod
    def search_tags(keyword: str, limit: int = 20) -> List[MaterialTag]:
        """
        搜索标签
        
        Args:
            keyword: 搜索关键词
            limit: 返回数量
            
        Returns:
            List[MaterialTag]: 标签列表
        """
        return MaterialTag.query.filter(
            MaterialTag.name.like(f"%{keyword}%")
        ).order_by(MaterialTag.usage_count.desc()).limit(limit).all()
    
    @staticmethod
    def delete_tag(tag_id: int) -> bool:
        """
        删除标签
        
        Args:
            tag_id: 标签ID
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            ValueError: 标签不存在或正在使用中
        """
        tag = MaterialTag.query.get(tag_id)
        
        if not tag:
            raise ValueError("标签不存在")
        
        # 检查是否有资料使用该标签
        if tag.usage_count > 0:
            raise ValueError(f"该标签正在被 {tag.usage_count} 个资料使用，无法删除")
        
        tag.delete()
        
        logger.info(f"标签删除成功: {tag_id}")
        return True
    
    @staticmethod
    def get_or_create_tag(name: str) -> MaterialTag:
        """
        获取或创建标签
        
        Args:
            name: 标签名称
            
        Returns:
            MaterialTag: 标签对象
        """
        return MaterialTag.get_or_create(name)
