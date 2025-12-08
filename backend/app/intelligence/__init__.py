"""
智能模块 - 自动化资料归类功能

该模块提供文档内容分析、关键词提取、智能分类推荐和标签推荐能力。

主要组件:
- DocumentParser: 文档解析器，支持 PDF、Word、文本文件
- KeywordExtractor: 关键词提取器，使用 Jieba 分词和 TF-IDF 算法
- CategoryClassifier: 分类器，基于 Naive Bayes 进行文档分类
- TagRecommender: 标签推荐器，根据关键词推荐相关标签
"""

from .document_parser import DocumentParser, ParseResult
from .keyword_extractor import KeywordExtractor, KeywordResult
from .category_classifier import CategoryClassifier, ClassificationResult
from .tag_recommender import TagRecommender, TagSuggestion

__all__ = [
    'DocumentParser',
    'ParseResult',
    'KeywordExtractor',
    'KeywordResult',
    'CategoryClassifier',
    'ClassificationResult',
    'TagRecommender',
    'TagSuggestion',
]
