"""
分类智能模块Schema

包含分类、关键词提取、标签推荐相关的请求和响应模型。
"""
from pydantic import Field
from typing import Optional, List
from app.schemas.base_schemas import CamelCaseModel


# ==================== 关键词 Schema ====================

class KeywordResponseModel(CamelCaseModel):
    """关键词响应模型"""
    keyword: str = Field(..., description="关键词")
    weight: float = Field(..., description="权重 (0-1)", ge=0, le=1)


class KeywordQueryModel(CamelCaseModel):
    """关键词查询参数模型"""
    top_n: int = Field(10, description="返回的关键词数量", ge=1, le=50)


# ==================== 分类结果 Schema ====================

class ClassifyMaterialResponseModel(CamelCaseModel):
    """分类结果响应模型"""
    material_id: int = Field(..., description="资料ID")
    suggested_category_id: Optional[int] = Field(None, description="建议的分类ID")
    suggested_category_name: Optional[str] = Field(None, description="建议的分类名称")
    confidence: float = Field(..., description="置信度 (0-1)", ge=0, le=1)
    should_auto_apply: bool = Field(..., description="是否自动应用")
    needs_confirmation: bool = Field(..., description="是否需要确认")
    keywords: List[KeywordResponseModel] = Field(default_factory=list, description="提取的关键词列表")
    log_id: Optional[int] = Field(None, description="分类日志ID")
    error: Optional[str] = Field(None, description="错误信息")


# ==================== 标签建议 Schema ====================

class TagSuggestionResponseModel(CamelCaseModel):
    """标签建议响应模型"""
    tag_name: str = Field(..., description="标签名称")
    tag_id: Optional[int] = Field(None, description="标签ID (如果是现有标签)")
    is_existing: bool = Field(..., description="是否为现有标签")
    relevance: float = Field(..., description="相关度 (0-1)", ge=0, le=1)


# ==================== 分类日志 Schema ====================

class ClassificationLogPathModel(CamelCaseModel):
    """分类日志路径参数模型"""
    log_id: int = Field(..., description="分类日志ID", ge=1)


class ClassificationLogResponseModel(CamelCaseModel):
    """分类日志响应模型"""
    id: int = Field(..., description="日志ID")
    material_id: int = Field(..., description="资料ID")
    original_category_id: Optional[int] = Field(None, description="原分类ID")
    suggested_category_id: int = Field(..., description="建议分类ID")
    confidence: float = Field(..., description="置信度")
    is_accepted: Optional[bool] = Field(None, description="是否接受")
    algorithm_used: str = Field(..., description="使用的算法")
    created_at: str = Field(..., description="创建时间")


# ==================== 路径参数 Schema ====================

class MaterialClassifyPathModel(CamelCaseModel):
    """资料分类路径参数模型"""
    material_id: int = Field(..., description="资料ID", ge=1)
