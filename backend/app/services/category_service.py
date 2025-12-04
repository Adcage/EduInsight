"""
分类管理服务层

处理资料分类相关的业务逻辑。
"""
from typing import List, Optional, Dict, Any
from app.extensions import db
from app.models import MaterialCategory
import logging

logger = logging.getLogger(__name__)


class CategoryService:
    """分类管理服务类"""
    
    @staticmethod
    def create_category(
        name: str,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: int = 0
    ) -> MaterialCategory:
        """
        创建分类
        
        Args:
            name: 分类名称
            description: 分类描述
            parent_id: 父分类ID
            sort_order: 排序序号
            
        Returns:
            MaterialCategory: 创建的分类对象
            
        Raises:
            ValueError: 父分类不存在
        """
        # 如果指定了父分类，检查是否存在
        if parent_id:
            parent = MaterialCategory.query.get(parent_id)
            if not parent:
                raise ValueError("父分类不存在")
        
        category = MaterialCategory(
            name=name,
            description=description,
            parent_id=parent_id,
            sort_order=sort_order
        )
        
        category.save()
        
        logger.info(f"分类创建成功: {category.id} - {name}")
        return category
    
    @staticmethod
    def get_category_by_id(category_id: int) -> Optional[MaterialCategory]:
        """
        根据ID获取分类
        
        Args:
            category_id: 分类ID
            
        Returns:
            Optional[MaterialCategory]: 分类对象
        """
        return MaterialCategory.query.get(category_id)
    
    @staticmethod
    def get_all_categories() -> List[MaterialCategory]:
        """
        获取所有分类
        
        Returns:
            List[MaterialCategory]: 分类列表
        """
        return MaterialCategory.query.order_by(MaterialCategory.sort_order).all()
    
    @staticmethod
    def get_category_tree() -> List[Dict[str, Any]]:
        """
        获取分类树形结构
        
        Returns:
            List[Dict]: 树形结构的分类列表
        """
        def build_tree(categories: List[MaterialCategory], parent_id: Optional[int] = None) -> List[Dict[str, Any]]:
            """递归构建树形结构"""
            tree = []
            for category in categories:
                if category.parent_id == parent_id:
                    node = {
                        'id': category.id,
                        'name': category.name,
                        'description': category.description,
                        'parent_id': category.parent_id,
                        'sort_order': category.sort_order,
                        'created_at': category.created_at.isoformat() if category.created_at else None,
                        'updated_at': category.updated_at.isoformat() if category.updated_at else None,
                        'children': build_tree(categories, category.id)
                    }
                    tree.append(node)
            return tree
        
        all_categories = CategoryService.get_all_categories()
        return build_tree(all_categories)
    
    @staticmethod
    def get_top_level_categories() -> List[MaterialCategory]:
        """
        获取顶级分类
        
        Returns:
            List[MaterialCategory]: 顶级分类列表
        """
        return MaterialCategory.get_top_level_categories()
    
    @staticmethod
    def get_children_categories(parent_id: int) -> List[MaterialCategory]:
        """
        获取子分类
        
        Args:
            parent_id: 父分类ID
            
        Returns:
            List[MaterialCategory]: 子分类列表
        """
        return MaterialCategory.get_by_parent(parent_id)
    
    @staticmethod
    def update_category(
        category_id: int,
        name: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[int] = None,
        sort_order: Optional[int] = None
    ) -> MaterialCategory:
        """
        更新分类
        
        Args:
            category_id: 分类ID
            name: 分类名称
            description: 分类描述
            parent_id: 父分类ID
            sort_order: 排序序号
            
        Returns:
            MaterialCategory: 更新后的分类对象
            
        Raises:
            ValueError: 分类不存在或父分类不存在
        """
        category = MaterialCategory.query.get(category_id)
        
        if not category:
            raise ValueError("分类不存在")
        
        # 检查父分类
        if parent_id is not None:
            # 不能将分类设置为自己的子分类
            if parent_id == category_id:
                raise ValueError("不能将分类设置为自己的子分类")
            
            if parent_id != 0:  # 0表示设置为顶级分类
                parent = MaterialCategory.query.get(parent_id)
                if not parent:
                    raise ValueError("父分类不存在")
        
        # 更新字段
        if name is not None:
            category.name = name
        
        if description is not None:
            category.description = description
        
        if parent_id is not None:
            category.parent_id = parent_id if parent_id != 0 else None
        
        if sort_order is not None:
            category.sort_order = sort_order
        
        category.save()
        
        logger.info(f"分类更新成功: {category_id}")
        return category
    
    @staticmethod
    def delete_category(category_id: int, force: bool = False) -> bool:
        """
        删除分类
        
        Args:
            category_id: 分类ID
            force: 是否强制删除（包括子分类）
            
        Returns:
            bool: 是否成功删除
            
        Raises:
            ValueError: 分类不存在或有子分类/关联资料
        """
        category = MaterialCategory.query.get(category_id)
        
        if not category:
            raise ValueError("分类不存在")
        
        # 检查是否有子分类
        children = category.children.all()
        if children and not force:
            raise ValueError("该分类下有子分类，无法删除")
        
        # 检查是否有关联的资料
        materials_count = category.materials.count()
        if materials_count > 0:
            raise ValueError(f"该分类下有 {materials_count} 个资料，无法删除")
        
        # 如果强制删除，先删除子分类
        if force and children:
            for child in children:
                CategoryService.delete_category(child.id, force=True)
        
        # 删除分类
        category.delete()
        
        logger.info(f"分类删除成功: {category_id}")
        return True
