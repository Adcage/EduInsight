"""
关键词提取器属性测试

使用 hypothesis 进行属性测试，验证关键词提取器的正确性。
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from app.intelligence.keyword_extractor import KeywordExtractor, KeywordResult

# 预先初始化 jieba，避免首次加载时超时
import jieba
jieba.initialize()


# 创建全局的 KeywordExtractor 实例用于测试
@pytest.fixture(scope="module")
def extractor():
    """创建关键词提取器实例"""
    return KeywordExtractor()


# 自定义策略：生成有效的中文文本
@st.composite
def chinese_text_strategy(draw):
    """生成包含中文的有效文本
    
    生成的文本应该：
    - 包含足够的中文内容以便提取关键词
    - 避免纯空白或纯标点
    """
    # 中文词汇库 - 包含多种主题的词汇
    chinese_words = [
        '机器学习', '深度学习', '人工智能', '神经网络', '数据分析',
        '自然语言处理', '计算机视觉', '算法', '模型', '训练',
        '教学', '课程', '学生', '教师', '知识', '学习', '教育',
        '数学', '物理', '化学', '生物', '历史', '地理', '语文',
        '编程', '软件', '开发', '系统', '设计', '测试', '部署',
        '研究', '实验', '分析', '结果', '方法', '技术', '应用',
        '文档', '资料', '内容', '信息', '数据', '处理', '管理',
    ]
    
    # 随机选择词汇数量
    num_words = draw(st.integers(min_value=5, max_value=30))
    
    # 随机选择词汇
    selected_words = draw(st.lists(
        st.sampled_from(chinese_words),
        min_size=num_words,
        max_size=num_words
    ))
    
    # 添加一些连接词和标点
    connectors = ['的', '和', '与', '是', '在', '中', '有', '为', '了', '。', '，']
    
    # 构建文本
    text_parts = []
    for i, word in enumerate(selected_words):
        text_parts.append(word)
        if i < len(selected_words) - 1:
            connector = draw(st.sampled_from(connectors))
            text_parts.append(connector)
    
    text = ''.join(text_parts)
    
    # 确保文本非空
    assume(text.strip())
    assume(len(text.strip()) >= 10)
    
    return text


# 自定义策略：生成 top_n 参数
@st.composite
def top_n_strategy(draw):
    """生成有效的 top_n 参数"""
    return draw(st.integers(min_value=1, max_value=50))


class TestKeywordWeightValidity:
    """关键词权重有效性测试"""

    @given(text=chinese_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_keyword_weights_in_valid_range(self, text: str):
        """
        **Feature: auto-material-classification, 属性 3: 关键词提取产生有效权重**
        
        对于任意非空文本输入，所有提取的关键词权重应在 [0, 1] 范围内。
        
        **Validates: Requirements 2.2**
        """
        extractor = KeywordExtractor()
        
        # 提取关键词
        keywords = extractor.extract(text, top_n=10)
        
        # 验证每个关键词的权重都在有效范围内
        for kw in keywords:
            assert isinstance(kw, KeywordResult), \
                f"返回类型错误: {type(kw)}"
            assert isinstance(kw.weight, float), \
                f"权重类型错误: {type(kw.weight)}"
            assert 0.0 <= kw.weight <= 1.0, \
                f"权重超出范围 [0, 1]: keyword={kw.keyword!r}, weight={kw.weight}"


class TestKeywordCountLimit:
    """关键词数量限制测试"""

    @given(text=chinese_text_strategy(), top_n=top_n_strategy())
    @settings(max_examples=100, deadline=None)
    def test_keyword_count_respects_limit(self, text: str, top_n: int):
        """
        **Feature: auto-material-classification, 属性 4: 关键词数量遵守限制**
        
        对于任意文本输入和 top_n 参数，提取的关键词数量应不超过 top_n。
        
        **Validates: Requirements 2.3**
        """
        extractor = KeywordExtractor()
        
        # 提取关键词
        keywords = extractor.extract(text, top_n=top_n)
        
        # 验证关键词数量不超过 top_n
        assert len(keywords) <= top_n, \
            f"关键词数量 {len(keywords)} 超过限制 {top_n}"


class TestKeywordStopWordFiltering:
    """关键词停用词过滤测试"""

    @given(text=chinese_text_strategy())
    @settings(max_examples=100, deadline=None)
    def test_keywords_exclude_stop_words_and_single_chars(self, text: str):
        """
        **Feature: auto-material-classification, 属性 5: 关键词排除停用词和单字**
        
        对于任意提取的关键词列表，不应包含停用词或单个字符。
        
        **Validates: Requirements 2.5**
        """
        extractor = KeywordExtractor()
        stop_words = extractor.stop_words
        
        # 提取关键词
        keywords = extractor.extract(text, top_n=20)
        
        # 验证每个关键词都不是停用词且不是单字
        for kw in keywords:
            # 验证不是单字
            assert len(kw.keyword) > 1, \
                f"关键词是单字: {kw.keyword!r}"
            
            # 验证不是停用词
            assert kw.keyword not in stop_words, \
                f"关键词是停用词: {kw.keyword!r}"
