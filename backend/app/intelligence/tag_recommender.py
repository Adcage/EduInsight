"""
标签推荐器模块

根据关键词推荐相关标签。
"""

import logging
from dataclasses import dataclass
from typing import List, Optional

logger = logging.getLogger(__name__)


# 最大推荐标签数量
MAX_SUGGESTED_TAGS = 5


@dataclass
class KeywordResult:
    """关键词结果（从 keyword_extractor 导入时使用）"""
    keyword: str
    weight: float


@dataclass
class TagSuggestion:
    """标签建议"""
    tag_name: str           # 标签名称
    tag_id: Optional[int]   # 标签 ID (如果是现有标签)
    is_existing: bool       # 是否为现有标签
    relevance: float        # 相关度 (0-1)


class TagRecommender:
    """
    标签推荐器
    
    根据提取的关键词推荐相关标签。
    优先匹配现有标签，如果没有匹配则建议从关键词创建新标签。
    """

    def __init__(self, max_tags: int = MAX_SUGGESTED_TAGS):
        """
        初始化标签推荐器
        
        Args:
            max_tags: 最大推荐标签数量，默认为 5
        """
        self._max_tags = max_tags

    def recommend(
        self,
        keywords: List[KeywordResult],
        max_tags: Optional[int] = None
    ) -> List[TagSuggestion]:
        """
        推荐标签
        
        根据关键词推荐标签，优先匹配现有标签。
        
        Args:
            keywords: 关键词列表
            max_tags: 最大推荐数量，如果不指定则使用默认值
            
        Returns:
            标签建议列表，按相关度排序
        """
        if not keywords:
            return []
        
        limit = min(max_tags or self._max_tags, MAX_SUGGESTED_TAGS)
        
        # 提取关键词字符串列表
        keyword_strings = [kw.keyword for kw in keywords]
        
        # 1. 首先尝试匹配现有标签
        existing_suggestions = self._match_existing_tags(keywords)
        
        # 2. 如果现有标签不够，从关键词中建议新标签
        remaining_count = limit - len(existing_suggestions)
        if remaining_count > 0:
            # 过滤掉已经匹配的关键词
            matched_names = {s.tag_name.lower() for s in existing_suggestions}
            unmatched_keywords = [
                kw for kw in keywords 
                if kw.keyword.lower() not in matched_names
            ]
            new_suggestions = self._suggest_new_tags(unmatched_keywords, remaining_count)
            existing_suggestions.extend(new_suggestions)
        
        # 按相关度排序并限制数量
        suggestions = sorted(existing_suggestions, key=lambda x: x.relevance, reverse=True)
        return suggestions[:limit]

    def _match_existing_tags(self, keywords: List[KeywordResult]) -> List[TagSuggestion]:
        """
        匹配现有标签
        
        Args:
            keywords: 关键词列表
            
        Returns:
            匹配到的现有标签建议列表
        """
        suggestions = []
        
        try:
            # 延迟导入以避免循环依赖
            from app.models.material import MaterialTag
            
            # 获取所有现有标签
            existing_tags = MaterialTag.query.all()
            
            # 创建关键词到权重的映射
            keyword_weights = {kw.keyword.lower(): kw.weight for kw in keywords}
            
            for tag in existing_tags:
                tag_name_lower = tag.name.lower()
                
                # 检查标签名是否与任何关键词匹配
                for kw in keywords:
                    kw_lower = kw.keyword.lower()
                    
                    # 完全匹配或包含关系
                    if tag_name_lower == kw_lower or kw_lower in tag_name_lower or tag_name_lower in kw_lower:
                        suggestions.append(TagSuggestion(
                            tag_name=tag.name,
                            tag_id=tag.id,
                            is_existing=True,
                            relevance=kw.weight
                        ))
                        break
            
        except Exception as e:
            logger.warning(f"匹配现有标签时出错: {str(e)}")
        
        return suggestions

    def _suggest_new_tags(
        self,
        keywords: List[KeywordResult],
        count: int
    ) -> List[TagSuggestion]:
        """
        建议新标签
        
        从关键词中选择合适的作为新标签建议。
        
        Args:
            keywords: 未匹配的关键词列表
            count: 需要的新标签数量
            
        Returns:
            新标签建议列表
        """
        if not keywords or count <= 0:
            return []
        
        # 按权重排序，选择权重最高的关键词作为新标签
        sorted_keywords = sorted(keywords, key=lambda x: x.weight, reverse=True)
        
        suggestions = []
        for kw in sorted_keywords[:count]:
            # 过滤掉太短的关键词（少于2个字符）
            if len(kw.keyword) >= 2:
                suggestions.append(TagSuggestion(
                    tag_name=kw.keyword,
                    tag_id=None,
                    is_existing=False,
                    relevance=kw.weight * 0.8  # 新标签相关度略低于现有标签
                ))
        
        return suggestions

    def match_existing_tags(self, keywords: List[str]) -> List:
        """
        匹配现有标签（公开接口）
        
        Args:
            keywords: 关键词字符串列表
            
        Returns:
            匹配到的 MaterialTag 对象列表
        """
        try:
            from app.models.material import MaterialTag
            
            matched_tags = []
            existing_tags = MaterialTag.query.all()
            
            for tag in existing_tags:
                tag_name_lower = tag.name.lower()
                for kw in keywords:
                    kw_lower = kw.lower()
                    if tag_name_lower == kw_lower or kw_lower in tag_name_lower or tag_name_lower in kw_lower:
                        matched_tags.append(tag)
                        break
            
            return matched_tags
            
        except Exception as e:
            logger.warning(f"匹配现有标签时出错: {str(e)}")
            return []

    def suggest_new_tags(
        self,
        keywords: List[KeywordResult],
        count: int
    ) -> List[str]:
        """
        建议新标签名称（公开接口）
        
        Args:
            keywords: 关键词结果列表
            count: 需要的新标签数量
            
        Returns:
            新标签名称列表
        """
        suggestions = self._suggest_new_tags(keywords, count)
        return [s.tag_name for s in suggestions]
