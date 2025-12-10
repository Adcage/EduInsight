"""
分类器模块

基于机器学习模型（Naive Bayes）进行文档分类预测。
"""

import json
import logging
import os
import pickle
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

import jieba
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import Pipeline

logger = logging.getLogger(__name__)


# 置信度阈值常量
HIGH_CONFIDENCE_THRESHOLD = 0.5  # 降低到 50% 以便更早推荐分类
MEDIUM_CONFIDENCE_THRESHOLD = 0.3  # 相应调整中等置信度阈值


@dataclass
class ClassificationResult:
    """分类结果"""
    category_id: Optional[int]      # 推荐的分类 ID
    category_name: Optional[str]    # 分类名称
    confidence: float               # 置信度 (0-1)
    should_auto_apply: bool         # 是否自动应用
    needs_confirmation: bool        # 是否需要确认

    @classmethod
    def from_confidence(
        cls,
        confidence: float,
        category_id: Optional[int] = None,
        category_name: Optional[str] = None
    ) -> 'ClassificationResult':
        """
        根据置信度创建分类结果
        
        置信度阈值逻辑：
        - 高置信度 (≥0.5): 自动应用
        - 中等置信度 (0.3-0.5): 需要确认
        - 低置信度 (<0.3): 不建议
        
        Args:
            confidence: 置信度分数 (0-1)
            category_id: 分类 ID
            category_name: 分类名称
            
        Returns:
            ClassificationResult 实例
        """
        # 确保置信度在有效范围内
        confidence = max(0.0, min(1.0, float(confidence)))
        
        # 根据置信度确定行为
        if confidence > HIGH_CONFIDENCE_THRESHOLD:
            # 高置信度：自动应用
            return cls(
                category_id=category_id,
                category_name=category_name,
                confidence=confidence,
                should_auto_apply=True,
                needs_confirmation=False
            )
        elif confidence >= MEDIUM_CONFIDENCE_THRESHOLD:
            # 中等置信度：需要确认
            return cls(
                category_id=category_id,
                category_name=category_name,
                confidence=confidence,
                should_auto_apply=False,
                needs_confirmation=True
            )
        else:
            # 低置信度：不建议
            return cls(
                category_id=None,
                category_name=None,
                confidence=confidence,
                should_auto_apply=False,
                needs_confirmation=False
            )


@dataclass
class TrainingItem:
    """训练数据项"""
    text: str           # 文本内容
    category_id: int    # 分类 ID


@dataclass
class TrainResult:
    """训练结果"""
    success: bool
    accuracy: float
    message: str


class CategoryClassifier:
    """
    分类分类器
    
    基于 Naive Bayes 算法进行文档分类预测。
    使用 TF-IDF 向量化和多项式朴素贝叶斯分类器。
    """

    # 训练所需的最小样本数（每个分类）
    MIN_SAMPLES_PER_CATEGORY = 3  # 降低要求以适应测试环境

    def __init__(self, model_path: Optional[str] = None):
        """
        初始化分类器
        
        Args:
            model_path: 预训练模型文件路径，如果提供则加载模型
        """
        self._pipeline: Optional[Pipeline] = None
        self._category_mapping: Dict[int, str] = {}  # category_id -> category_name
        self._is_trained: bool = False
        
        # 如果提供了模型路径，尝试加载
        if model_path and os.path.exists(model_path):
            self.load_model(model_path)

    @property
    def is_trained(self) -> bool:
        """检查模型是否已训练"""
        return self._is_trained and self._pipeline is not None

    def _tokenize(self, text: str) -> str:
        """
        对文本进行分词
        
        Args:
            text: 输入文本
            
        Returns:
            分词后的文本（空格分隔）
        """
        if not text or not text.strip():
            return ""
        
        words = jieba.cut(text, cut_all=False)
        return " ".join(words)

    def predict(self, text: str, keywords: Optional[List[str]] = None) -> ClassificationResult:
        """
        预测文档分类
        
        Args:
            text: 文档文本内容
            keywords: 可选的关键词列表，用于增强分类
            
        Returns:
            ClassificationResult: 分类结果
        """
        # 如果模型未训练，返回低置信度结果
        if not self.is_trained:
            logger.warning("分类模型未训练，无法进行预测")
            return ClassificationResult.from_confidence(0.0)
        
        # 准备输入文本
        input_text = text
        if keywords:
            # 将关键词添加到文本中以增强特征
            input_text = f"{text} {' '.join(keywords)}"
        
        # 分词
        tokenized_text = self._tokenize(input_text)
        
        if not tokenized_text.strip():
            return ClassificationResult.from_confidence(0.0)
        
        try:
            # 预测分类
            predicted_category_id = self._pipeline.predict([tokenized_text])[0]
            
            # 获取预测概率
            probabilities = self._pipeline.predict_proba([tokenized_text])[0]
            confidence = float(max(probabilities))
            
            # 获取分类名称
            category_name = self._category_mapping.get(predicted_category_id)
            
            # 根据置信度创建结果
            return ClassificationResult.from_confidence(
                confidence=confidence,
                category_id=predicted_category_id,
                category_name=category_name
            )
            
        except Exception as e:
            logger.error(f"分类预测失败: {str(e)}")
            return ClassificationResult.from_confidence(0.0)

    def train(self, training_data: List[TrainingItem], category_names: Optional[Dict[int, str]] = None) -> TrainResult:
        """
        训练分类模型
        
        Args:
            training_data: 训练数据列表
            category_names: 分类 ID 到名称的映射
            
        Returns:
            TrainResult: 训练结果
        """
        if not training_data:
            return TrainResult(
                success=False,
                accuracy=0.0,
                message="训练数据为空"
            )
        
        # 统计每个分类的样本数
        category_counts: Dict[int, int] = {}
        for item in training_data:
            category_counts[item.category_id] = category_counts.get(item.category_id, 0) + 1
        
        # 检查是否有足够的训练数据
        insufficient_categories = [
            cat_id for cat_id, count in category_counts.items()
            if count < self.MIN_SAMPLES_PER_CATEGORY
        ]
        
        if insufficient_categories:
            return TrainResult(
                success=False,
                accuracy=0.0,
                message=f"以下分类的训练样本不足 {self.MIN_SAMPLES_PER_CATEGORY} 个: {insufficient_categories}"
            )
        
        try:
            # 准备训练数据
            texts = [self._tokenize(item.text) for item in training_data]
            labels = [item.category_id for item in training_data]
            
            # 过滤空文本
            valid_data = [(t, l) for t, l in zip(texts, labels) if t.strip()]
            if not valid_data:
                return TrainResult(
                    success=False,
                    accuracy=0.0,
                    message="所有训练文本分词后为空"
                )
            
            texts, labels = zip(*valid_data)
            texts = list(texts)
            labels = list(labels)
            
            # 创建并训练管道
            self._pipeline = Pipeline([
                ('tfidf', TfidfVectorizer(
                    max_features=5000,
                    ngram_range=(1, 2),
                    min_df=1,
                    max_df=0.95
                )),
                ('clf', MultinomialNB(alpha=0.1))
            ])
            
            self._pipeline.fit(texts, labels)
            
            # 计算训练准确率
            predictions = self._pipeline.predict(texts)
            accuracy = sum(p == l for p, l in zip(predictions, labels)) / len(labels)
            
            # 保存分类名称映射
            if category_names:
                self._category_mapping = category_names.copy()
            else:
                # 如果没有提供名称，使用 ID 作为名称
                self._category_mapping = {cat_id: str(cat_id) for cat_id in set(labels)}
            
            self._is_trained = True
            
            return TrainResult(
                success=True,
                accuracy=accuracy,
                message=f"模型训练成功，训练准确率: {accuracy:.2%}"
            )
            
        except Exception as e:
            logger.error(f"模型训练失败: {str(e)}")
            return TrainResult(
                success=False,
                accuracy=0.0,
                message=f"训练失败: {str(e)}"
            )

    def save_model(self, path: str) -> bool:
        """
        保存模型到文件
        
        Args:
            path: 保存路径
            
        Returns:
            bool: 是否保存成功
        """
        if not self.is_trained:
            logger.warning("模型未训练，无法保存")
            return False
        
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(path) if os.path.dirname(path) else '.', exist_ok=True)
            
            # 保存模型和映射
            model_data = {
                'pipeline': self._pipeline,
                'category_mapping': self._category_mapping
            }
            
            with open(path, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"模型已保存到: {path}")
            return True
            
        except Exception as e:
            logger.error(f"保存模型失败: {str(e)}")
            return False

    def load_model(self, path: str) -> bool:
        """
        从文件加载模型
        
        Args:
            path: 模型文件路径
            
        Returns:
            bool: 是否加载成功
        """
        if not os.path.exists(path):
            logger.warning(f"模型文件不存在: {path}")
            return False
        
        try:
            with open(path, 'rb') as f:
                model_data = pickle.load(f)
            
            self._pipeline = model_data['pipeline']
            self._category_mapping = model_data.get('category_mapping', {})
            self._is_trained = True
            
            logger.info(f"模型已从 {path} 加载")
            return True
            
        except Exception as e:
            logger.error(f"加载模型失败: {str(e)}")
            return False

    def get_category_name(self, category_id: int) -> Optional[str]:
        """
        获取分类名称
        
        Args:
            category_id: 分类 ID
            
        Returns:
            分类名称，如果不存在则返回 None
        """
        return self._category_mapping.get(category_id)

    def set_category_mapping(self, mapping: Dict[int, str]) -> None:
        """
        设置分类 ID 到名称的映射
        
        Args:
            mapping: 分类映射字典
        """
        self._category_mapping = mapping.copy()
