"""
资料中心模块Schema

包含资料、分类、标签相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from app.schemas.base_schemas import CamelCaseModel


# ==================== 资料分类 Schema ====================

class MaterialCategoryCreateModel(CamelCaseModel):
    """资料分类创建模型"""
    name: str = Field(..., description="分类名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="分类描述", max_length=255)
    parent_id: Optional[int] = Field(None, description="父分类ID", ge=1)
    sort_order: int = Field(0, description="排序顺序", ge=0)


class MaterialCategoryUpdateModel(CamelCaseModel):
    """资料分类更新模型"""
    name: Optional[str] = Field(None, description="分类名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="分类描述", max_length=255)
    parent_id: Optional[int] = Field(None, description="父分类ID", ge=1)
    sort_order: Optional[int] = Field(None, description="排序顺序", ge=0)


class MaterialCategoryResponseModel(CamelCaseModel):
    """资料分类响应模型"""
    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(..., description="排序顺序")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class MaterialCategoryTreeModel(CamelCaseModel):
    """资料分类树形结构模型"""
    id: int = Field(..., description="分类ID")
    name: str = Field(..., description="分类名称")
    description: Optional[str] = Field(None, description="分类描述")
    parent_id: Optional[int] = Field(None, description="父分类ID")
    sort_order: int = Field(..., description="排序顺序")
    children: List['MaterialCategoryTreeModel'] = Field(default_factory=list, description="子分类列表")


# ==================== 资料标签 Schema ====================

class MaterialTagCreateModel(CamelCaseModel):
    """资料标签创建模型"""
    name: str = Field(..., description="标签名称", min_length=1, max_length=50)
    
    @validator('name')
    def validate_name(cls, v):
        """验证标签名称"""
        if not v.strip():
            raise ValueError('标签名称不能为空白')
        return v.strip()


class MaterialTagResponseModel(CamelCaseModel):
    """资料标签响应模型"""
    id: int = Field(..., description="标签ID")
    name: str = Field(..., description="标签名称")
    usage_count: int = Field(..., description="使用次数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


# ==================== 资料 Schema ====================

class MaterialUploadModel(CamelCaseModel):
    """资料上传请求模型"""
    title: str = Field(..., description="资料标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="资料描述")
    course_id: Optional[int] = Field(None, description="课程ID", ge=1)
    category_id: Optional[int] = Field(None, description="分类ID", ge=1)
    tags: List[str] = Field(default_factory=list, description="标签列表")
    
    @validator('title')
    def validate_title(cls, v):
        """验证标题不能为空白"""
        if not v.strip():
            raise ValueError('标题不能为空白')
        return v.strip()
    
    @validator('tags')
    def validate_tags(cls, v):
        """验证标签列表"""
        if v and len(v) > 10:
            raise ValueError('标签数量不能超过10个')
        return [tag.strip() for tag in v if tag.strip()]


class MaterialUpdateModel(CamelCaseModel):
    """资料更新模型"""
    title: Optional[str] = Field(None, description="资料标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="资料描述")
    category_id: Optional[int] = Field(None, description="分类ID", ge=1)
    tags: Optional[List[str]] = Field(None, description="标签列表")
    
    @validator('title')
    def validate_title(cls, v):
        """验证标题"""
        if v is not None and not v.strip():
            raise ValueError('标题不能为空白')
        return v.strip() if v else v


class MaterialResponseModel(CamelCaseModel):
    """资料响应模型"""
    id: int = Field(..., description="资料ID")
    title: str = Field(..., description="资料标题")
    description: Optional[str] = Field(None, description="资料描述")
    file_name: str = Field(..., description="文件名")
    file_path: str = Field(..., description="文件路径")
    file_size: int = Field(..., description="文件大小(字节)")
    file_type: str = Field(..., description="文件类型")
    course_id: Optional[int] = Field(None, description="课程ID")
    uploader_id: int = Field(..., description="上传者ID")
    category_id: Optional[int] = Field(None, description="分类ID")
    download_count: int = Field(..., description="下载次数")
    view_count: int = Field(..., description="浏览次数")
    keywords: Optional[str] = Field(None, description="关键词")
    auto_classified: bool = Field(..., description="是否自动分类")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class MaterialDetailResponseModel(MaterialResponseModel):
    """资料详情响应模型（包含关联信息）"""
    tags: List[MaterialTagResponseModel] = Field(default_factory=list, description="标签列表")
    category_name: Optional[str] = Field(None, description="分类名称")
    uploader_name: Optional[str] = Field(None, description="上传者姓名")


class MaterialListResponseModel(CamelCaseModel):
    """资料列表响应模型"""
    materials: List[MaterialResponseModel] = Field(..., description="资料列表")
    total: int = Field(..., description="资料总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")


class MaterialQueryModel(CamelCaseModel):
    """资料查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    course_id: Optional[int] = Field(None, description="课程ID筛选", ge=1)
    category_id: Optional[int] = Field(None, description="分类ID筛选", ge=1)
    uploader_id: Optional[int] = Field(None, description="上传者ID筛选", ge=1)
    file_type: Optional[str] = Field(None, description="文件类型筛选", max_length=50)
    search: Optional[str] = Field(None, description="搜索关键词（标题、描述、关键词）", max_length=100)


class MaterialPathModel(CamelCaseModel):
    """资料路径参数模型"""
    material_id: int = Field(..., description="资料ID", ge=1)


class MaterialTagPathModel(CamelCaseModel):
    """资料标签路径参数模型"""
    material_id: int = Field(..., description="资料ID", ge=1)
    tag_id: int = Field(..., description="标签ID", ge=1)


class TagPathModel(CamelCaseModel):
    """标签路径参数模型（仅tag_id）"""
    tag_id: int = Field(..., description="标签ID", ge=1)


class MaterialCategoryPathModel(CamelCaseModel):
    """资料分类路径参数模型"""
    category_id: int = Field(..., description="分类ID", ge=1)


class MaterialTagAddModel(CamelCaseModel):
    """添加标签模型"""
    tag_names: List[str] = Field(..., description="标签名称列表", min_items=1, max_items=10)
    
    @validator('tag_names')
    def validate_tag_names(cls, v):
        """验证标签名称"""
        return [tag.strip() for tag in v if tag.strip()]


class MaterialStatsModel(CamelCaseModel):
    """资料统计模型"""
    total_materials: int = Field(..., description="资料总数")
    total_size: int = Field(..., description="总大小(字节)")
    total_downloads: int = Field(..., description="总下载次数")
    total_views: int = Field(..., description="总浏览次数")
    by_type: dict = Field(..., description="按文件类型统计")
    by_category: dict = Field(..., description="按分类统计")
    recent_uploads: List[MaterialResponseModel] = Field(..., description="最近上传")
    popular_materials: List[MaterialResponseModel] = Field(..., description="热门资料")
