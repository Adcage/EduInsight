"""
智能模块Schema

包含文档关键词、分类日志相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from app.schemas.base_schemas import CamelCaseModel


# ==================== 文档关键词 Schema ====================

class DocumentKeywordResponseModel(CamelCaseModel):
    """文档关键词响应模型"""
    id: int = Field(..., description="关键词ID")
    material_id: int = Field(..., description="资料ID")
    keyword: str = Field(..., description="关键词")
    weight: float = Field(..., description="权重")
    extraction_method: Optional[str] = Field(None, description="提取方法")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class DocumentKeywordListResponseModel(CamelCaseModel):
    """文档关键词列表响应模型"""
    keywords: List[DocumentKeywordResponseModel] = Field(..., description="关键词列表")
    total: int = Field(..., description="关键词总数")


class PopularKeywordModel(CamelCaseModel):
    """热门关键词模型"""
    keyword: str = Field(..., description="关键词")
    count: int = Field(..., description="出现次数")
    avg_weight: float = Field(..., description="平均权重")


class PopularKeywordListModel(CamelCaseModel):
    """热门关键词列表模型"""
    keywords: List[PopularKeywordModel] = Field(..., description="热门关键词列表")


# ==================== 分类日志 Schema ====================

class ClassificationLogCreateModel(CamelCaseModel):
    """分类日志创建模型"""
    material_id: int = Field(..., description="资料ID", ge=1)
    suggested_category_id: int = Field(..., description="建议分类ID", ge=1)
    confidence: Optional[float] = Field(None, description="置信度", ge=0, le=1)
    algorithm_used: Optional[str] = Field(None, description="使用的算法", max_length=50)
    features: Optional[dict] = Field(None, description="特征数据")


class ClassificationLogUpdateModel(CamelCaseModel):
    """分类日志更新模型"""
    is_accepted: bool = Field(..., description="是否接受建议")


class ClassificationLogResponseModel(CamelCaseModel):
    """分类日志响应模型"""
    id: int = Field(..., description="日志ID")
    material_id: int = Field(..., description="资料ID")
    original_category_id: Optional[int] = Field(None, description="原分类ID")
    suggested_category_id: int = Field(..., description="建议分类ID")
    confidence: Optional[float] = Field(None, description="置信度")
    is_accepted: Optional[bool] = Field(None, description="是否接受")
    algorithm_used: Optional[str] = Field(None, description="使用的算法")
    features: Optional[dict] = Field(None, description="特征数据")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class ClassificationLogDetailResponseModel(ClassificationLogResponseModel):
    """分类日志详情响应模型"""
    material_title: Optional[str] = Field(None, description="资料标题")
    original_category_name: Optional[str] = Field(None, description="原分类名称")
    suggested_category_name: Optional[str] = Field(None, description="建议分类名称")
    confidence_percentage: float = Field(..., description="置信度百分比")


class ClassificationLogListResponseModel(CamelCaseModel):
    """分类日志列表响应模型"""
    logs: List[ClassificationLogDetailResponseModel] = Field(..., description="日志列表")
    total: int = Field(..., description="日志总数")
    pending_count: int = Field(0, description="待处理数量")
    accuracy_rate: float = Field(0.0, description="准确率(%)")


class ClassificationLogPathModel(CamelCaseModel):
    """分类日志路径参数模型"""
    log_id: int = Field(..., description="日志ID", ge=1)


# ==================== 智能分类 Schema ====================

class MaterialClassifyRequestModel(CamelCaseModel):
    """资料分类请求模型"""
    material_id: int = Field(..., description="资料ID", ge=1)
    algorithm: Optional[str] = Field('TF-IDF', description="使用的算法")


class MaterialClassifyResponseModel(CamelCaseModel):
    """资料分类响应模型"""
    material_id: int = Field(..., description="资料ID")
    suggested_category_id: int = Field(..., description="建议分类ID")
    suggested_category_name: str = Field(..., description="建议分类名称")
    confidence: float = Field(..., description="置信度")
    keywords: List[str] = Field(..., description="提取的关键词")
    suggested_tags: List[str] = Field(..., description="建议的标签")


class KeywordExtractionRequestModel(CamelCaseModel):
    """关键词提取请求模型"""
    material_id: int = Field(..., description="资料ID", ge=1)
    top_k: int = Field(10, description="提取关键词数量", ge=1, le=50)
    method: Optional[str] = Field('TF-IDF', description="提取方法")


class KeywordExtractionResponseModel(CamelCaseModel):
    """关键词提取响应模型"""
    material_id: int = Field(..., description="资料ID")
    keywords: List[DocumentKeywordResponseModel] = Field(..., description="关键词列表")
    extraction_method: str = Field(..., description="提取方法")
