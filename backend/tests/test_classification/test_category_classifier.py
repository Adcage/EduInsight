"""
分类器属性测试

使用 hypothesis 进行属性测试，验证分类器的正确性。
"""

import pytest
from hypothesis import given, strategies as st, settings, assume

from app.intelligence.category_classifier import (
    CategoryClassifier,
    ClassificationResult,
    TrainingItem,
    HIGH_CONFIDENCE_THRESHOLD,
    MEDIUM_CONFIDENCE_THRESHOLD
)

# 预先初始化 jieba，避免首次加载时超时
import jieba
jieba.initialize()


# ============================================================================
# 自定义策略
# ============================================================================

@st.composite
def chinese_text_strategy(draw):
    """生成包含中文的有效文本"""
    chinese_words = [
        '机器学习', '深度学习', '人工智能', '神经网络', '数据分析',
        '自然语言处理', '计算机视觉', '算法', '模型', '训练',
        '教学', '课程', '学生', '教师', '知识', '学习', '教育',
        '数学', '物理', '化学', '生物', '历史', '地理', '语文',
        '编程', '软件', '开发', '系统', '设计', '测试', '部署',
        '研究', '实验', '分析', '结果', '方法', '技术', '应用',
    ]
    
    num_words = draw(st.integers(min_value=5, max_value=20))
    selected_words = draw(st.lists(
        st.sampled_from(chinese_words),
        min_size=num_words,
        max_size=num_words
    ))
    
    connectors = ['的', '和', '与', '是', '在', '中', '有', '为', '了', '。', '，']
    
    text_parts = []
    for i, word in enumerate(selected_words):
        text_parts.append(word)
        if i < len(selected_words) - 1:
            connector = draw(st.sampled_from(connectors))
            text_parts.append(connector)
    
    text = ''.join(text_parts)
    assume(text.strip())
    assume(len(text.strip()) >= 10)
    
    return text


@st.composite
def training_data_strategy(draw):
    """生成有效的训练数据集"""
    # 定义分类主题词汇
    category_words = {
        1: ['机器学习', '深度学习', '人工智能', '神经网络', '算法', '模型', '训练', '数据'],
        2: ['教学', '课程', '学生', '教师', '知识', '学习', '教育', '考试'],
        3: ['编程', '软件', '开发', '系统', '设计', '测试', '代码', '程序'],
    }
    
    training_items = []
    
    # 为每个分类生成足够的训练样本
    for category_id, words in category_words.items():
        num_samples = draw(st.integers(min_value=10, max_value=15))
        
        for _ in range(num_samples):
            num_words = draw(st.integers(min_value=5, max_value=15))
            selected_words = draw(st.lists(
                st.sampled_from(words),
                min_size=num_words,
                max_size=num_words
            ))
            text = ' '.join(selected_words)
            training_items.append(TrainingItem(text=text, category_id=category_id))
    
    return training_items


@st.composite
def confidence_strategy(draw):
    """生成有效的置信度值 (0-1)"""
    return draw(st.floats(min_value=0.0, max_value=1.0, allow_nan=False, allow_infinity=False))


# ============================================================================
# 属性测试：分类置信度范围
# ============================================================================

class TestConfidenceRange:
    """分类置信度范围测试"""

    @given(confidence=confidence_strategy())
    @settings(max_examples=100, deadline=None)
    def test_confidence_in_valid_range(self, confidence: float):
        """
        **Feature: auto-material-classification, 属性 6: 分类置信度在有效范围内**
        
        对于任意分类预测，置信度分数应在 [0, 1] 范围内。
        
        **Validates: Requirements 3.2**
        """
        # 使用 from_confidence 创建结果
        result = ClassificationResult.from_confidence(
            confidence=confidence,
            category_id=1,
            category_name="测试分类"
        )
        
        # 验证置信度在有效范围内
        assert isinstance(result.confidence, float), \
            f"置信度类型错误: {type(result.confidence)}"
        assert 0.0 <= result.confidence <= 1.0, \
            f"置信度超出范围 [0, 1]: {result.confidence}"

    @given(confidence=st.floats(min_value=-100.0, max_value=100.0, allow_nan=False, allow_infinity=False))
    @settings(max_examples=100, deadline=None)
    def test_confidence_clamped_to_valid_range(self, confidence: float):
        """
        **Feature: auto-material-classification, 属性 6: 分类置信度在有效范围内**
        
        即使输入超出范围的置信度，结果也应被限制在 [0, 1] 范围内。
        
        **Validates: Requirements 3.2**
        """
        result = ClassificationResult.from_confidence(
            confidence=confidence,
            category_id=1,
            category_name="测试分类"
        )
        
        # 验证置信度被限制在有效范围内
        assert 0.0 <= result.confidence <= 1.0, \
            f"置信度未被正确限制: 输入={confidence}, 输出={result.confidence}"


# ============================================================================
# 属性测试：置信度阈值行为
# ============================================================================

class TestConfidenceThresholdBehavior:
    """置信度阈值行为测试"""

    @given(confidence=st.floats(
        min_value=HIGH_CONFIDENCE_THRESHOLD + 0.001,
        max_value=1.0,
        allow_nan=False,
        allow_infinity=False
    ))
    @settings(max_examples=100, deadline=None)
    def test_high_confidence_triggers_auto_apply(self, confidence: float):
        """
        **Feature: auto-material-classification, 属性 7: 高置信度触发自动应用**
        
        对于任意置信度 > 0.7 的分类，结果应指示启用自动应用。
        
        **Validates: Requirements 3.3**
        """
        result = ClassificationResult.from_confidence(
            confidence=confidence,
            category_id=1,
            category_name="测试分类"
        )
        
        # 高置信度应该自动应用
        assert result.should_auto_apply is True, \
            f"高置信度 ({confidence}) 应该启用自动应用"
        assert result.needs_confirmation is False, \
            f"高置信度 ({confidence}) 不应该需要确认"
        # 高置信度应该保留分类信息
        assert result.category_id is not None, \
            f"高置信度 ({confidence}) 应该保留分类 ID"

    @given(confidence=st.floats(
        min_value=MEDIUM_CONFIDENCE_THRESHOLD,
        max_value=HIGH_CONFIDENCE_THRESHOLD,
        allow_nan=False,
        allow_infinity=False
    ))
    @settings(max_examples=100, deadline=None)
    def test_medium_confidence_needs_confirmation(self, confidence: float):
        """
        **Feature: auto-material-classification, 属性 8: 中等置信度需要确认**
        
        对于任意 0.5 <= 置信度 <= 0.7 的分类，结果应指示需要用户确认。
        
        **Validates: Requirements 3.4**
        """
        result = ClassificationResult.from_confidence(
            confidence=confidence,
            category_id=1,
            category_name="测试分类"
        )
        
        # 中等置信度应该需要确认
        assert result.needs_confirmation is True, \
            f"中等置信度 ({confidence}) 应该需要确认"
        assert result.should_auto_apply is False, \
            f"中等置信度 ({confidence}) 不应该自动应用"
        # 中等置信度应该保留分类信息
        assert result.category_id is not None, \
            f"中等置信度 ({confidence}) 应该保留分类 ID"

    @given(confidence=st.floats(
        min_value=0.0,
        max_value=MEDIUM_CONFIDENCE_THRESHOLD - 0.001,
        allow_nan=False,
        allow_infinity=False
    ))
    @settings(max_examples=100, deadline=None)
    def test_low_confidence_no_suggestion(self, confidence: float):
        """
        **Feature: auto-material-classification, 属性 9: 低置信度不产生建议**
        
        对于任意置信度 < 0.5 的分类，不应给出分类建议。
        
        **Validates: Requirements 3.5**
        """
        result = ClassificationResult.from_confidence(
            confidence=confidence,
            category_id=1,
            category_name="测试分类"
        )
        
        # 低置信度不应该给出建议
        assert result.category_id is None, \
            f"低置信度 ({confidence}) 不应该给出分类建议"
        assert result.category_name is None, \
            f"低置信度 ({confidence}) 不应该给出分类名称"
        assert result.should_auto_apply is False, \
            f"低置信度 ({confidence}) 不应该自动应用"
        assert result.needs_confirmation is False, \
            f"低置信度 ({confidence}) 不应该需要确认"
