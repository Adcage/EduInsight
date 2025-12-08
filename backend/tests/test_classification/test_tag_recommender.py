"""
标签推荐器属性测试

使用 hypothesis 进行属性测试，验证标签推荐器的正确性。
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from app.intelligence.tag_recommender import (
    TagRecommender,
    TagSuggestion,
    KeywordResult,
    MAX_SUGGESTED_TAGS
)


# ============================================================================
# 自定义策略
# ============================================================================

@st.composite
def keyword_result_strategy(draw):
    """生成有效的关键词结果"""
    chinese_words = [
        '机器学习', '深度学习', '人工智能', '神经网络', '数据分析',
        '自然语言处理', '计算机视觉', '算法', '模型', '训练',
        '教学', '课程', '学生', '教师', '知识', '学习', '教育',
        '数学', '物理', '化学', '生物', '历史', '地理', '语文',
        '编程', '软件', '开发', '系统', '设计', '测试', '部署',
    ]
    
    keyword = draw(st.sampled_from(chinese_words))
    weight = draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))
    
    return KeywordResult(keyword=keyword, weight=weight)


@st.composite
def keyword_list_strategy(draw, min_size=1, max_size=20):
    """生成关键词结果列表"""
    keywords = draw(st.lists(
        keyword_result_strategy(),
        min_size=min_size,
        max_size=max_size
    ))
    
    # 确保关键词唯一
    seen = set()
    unique_keywords = []
    for kw in keywords:
        if kw.keyword not in seen:
            seen.add(kw.keyword)
            unique_keywords.append(kw)
    
    assume(len(unique_keywords) >= min_size)
    return unique_keywords


# ============================================================================
# 属性测试：标签数量限制
# ============================================================================

class TestTagCountLimit:
    """标签数量限制测试"""

    @given(
        keywords=keyword_list_strategy(min_size=1, max_size=20),
        max_tags=st.integers(min_value=1, max_value=10)
    )
    @settings(max_examples=100, deadline=None)
    def test_tag_suggestions_respect_max_limit(self, keywords, max_tags):
        """
        **Feature: auto-material-classification, 属性 10: 标签建议遵守最大数量限制**
        
        对于任意标签推荐请求，建议的标签数量应不超过 5 个（MAX_SUGGESTED_TAGS）。
        
        **Validates: Requirements 4.4**
        """
        recommender = TagRecommender()
        
        # 推荐标签
        suggestions = recommender.recommend(keywords, max_tags=max_tags)
        
        # 验证数量不超过限制
        expected_limit = min(max_tags, MAX_SUGGESTED_TAGS)
        assert len(suggestions) <= expected_limit, \
            f"标签建议数量 ({len(suggestions)}) 超过限制 ({expected_limit})"

    @given(keywords=keyword_list_strategy(min_size=1, max_size=30))
    @settings(max_examples=100, deadline=None)
    def test_tag_suggestions_never_exceed_max_suggested_tags(self, keywords):
        """
        **Feature: auto-material-classification, 属性 10: 标签建议遵守最大数量限制**
        
        无论输入多少关键词，建议的标签数量都不应超过 MAX_SUGGESTED_TAGS (5)。
        
        **Validates: Requirements 4.4**
        """
        recommender = TagRecommender()
        
        # 不指定 max_tags，使用默认值
        suggestions = recommender.recommend(keywords)
        
        # 验证数量不超过全局最大限制
        assert len(suggestions) <= MAX_SUGGESTED_TAGS, \
            f"标签建议数量 ({len(suggestions)}) 超过全局限制 ({MAX_SUGGESTED_TAGS})"

    @given(keywords=keyword_list_strategy(min_size=1, max_size=20))
    @settings(max_examples=100, deadline=None)
    def test_all_suggestions_have_valid_structure(self, keywords):
        """
        **Feature: auto-material-classification, 属性 10: 标签建议遵守最大数量限制**
        
        所有返回的标签建议都应该有有效的结构。
        
        **Validates: Requirements 4.4**
        """
        recommender = TagRecommender()
        suggestions = recommender.recommend(keywords)
        
        for suggestion in suggestions:
            # 验证是 TagSuggestion 类型
            assert isinstance(suggestion, TagSuggestion), \
                f"建议类型错误: {type(suggestion)}"
            
            # 验证标签名称非空
            assert suggestion.tag_name, \
                "标签名称不能为空"
            
            # 验证相关度在有效范围内
            assert 0.0 <= suggestion.relevance <= 1.0, \
                f"相关度超出范围 [0, 1]: {suggestion.relevance}"
            
            # 验证 is_existing 是布尔值
            assert isinstance(suggestion.is_existing, bool), \
                f"is_existing 类型错误: {type(suggestion.is_existing)}"


class TestTagRecommenderBehavior:
    """标签推荐器行为测试"""

    def test_empty_keywords_returns_empty_list(self):
        """空关键词列表应返回空建议列表"""
        recommender = TagRecommender()
        suggestions = recommender.recommend([])
        
        assert suggestions == [], \
            f"空关键词应返回空列表，实际返回: {suggestions}"

    @given(keywords=keyword_list_strategy(min_size=1, max_size=10))
    @settings(max_examples=50, deadline=None)
    def test_suggestions_sorted_by_relevance(self, keywords):
        """标签建议应按相关度降序排列"""
        recommender = TagRecommender()
        suggestions = recommender.recommend(keywords)
        
        if len(suggestions) > 1:
            for i in range(len(suggestions) - 1):
                assert suggestions[i].relevance >= suggestions[i + 1].relevance, \
                    f"标签建议未按相关度排序: {suggestions[i].relevance} < {suggestions[i + 1].relevance}"
