"""
分类服务模块

整合文档解析、关键词提取、分类和标签推荐功能。
"""

import logging
import os
from decimal import Decimal
from typing import Any, Dict, List, Optional

from app.extensions import db
from app.models.intelligence import ClassificationLog, DocumentKeyword
from app.models.material import Material, MaterialCategory, MaterialTag
from app.intelligence import (
    DocumentParser,
    KeywordExtractor,
    CategoryClassifier,
    TagRecommender,
    KeywordResult,
)

logger = logging.getLogger(__name__)


# 模型文件路径
MODEL_PATH = os.path.join(os.path.dirname(__file__), '..', 'intelligence', 'models', 'classifier.pkl')


class ClassificationService:
    """
    分类服务
    
    整合各智能组件，提供资料分类、关键词提取和标签推荐的业务逻辑。
    """

    # 单例模式的分类器实例
    _classifier: Optional[CategoryClassifier] = None
    _keyword_extractor: Optional[KeywordExtractor] = None
    _tag_recommender: Optional[TagRecommender] = None

    @classmethod
    def _get_classifier(cls) -> CategoryClassifier:
        """获取分类器实例（懒加载）"""
        if cls._classifier is None:
            cls._classifier = CategoryClassifier(model_path=MODEL_PATH)
        return cls._classifier

    @classmethod
    def _get_keyword_extractor(cls) -> KeywordExtractor:
        """获取关键词提取器实例（懒加载）"""
        if cls._keyword_extractor is None:
            cls._keyword_extractor = KeywordExtractor()
        return cls._keyword_extractor

    @classmethod
    def _get_tag_recommender(cls) -> TagRecommender:
        """获取标签推荐器实例（懒加载）"""
        if cls._tag_recommender is None:
            cls._tag_recommender = TagRecommender()
        return cls._tag_recommender

    @staticmethod
    def classify_material(material_id: int) -> Dict[str, Any]:
        """
        分析并分类资料
        
        Args:
            material_id: 资料 ID
            
        Returns:
            包含分类结果的字典
        """
        # 获取资料
        material = Material.query.get(material_id)
        if not material:
            raise ValueError(f"资料不存在: {material_id}")
        
        # 解析文档内容
        parse_result = DocumentParser.parse(material.file_path)
        if not parse_result.success or not parse_result.content.strip():
            logger.warning(f"文档解析失败或内容为空: {material.file_path}")
            return {
                'material_id': material_id,
                'suggested_category_id': None,
                'suggested_category_name': None,
                'confidence': 0.0,
                'should_auto_apply': False,
                'needs_confirmation': False,
                'keywords': [],
                'log_id': None,
                'error': parse_result.error_message or '文档内容为空'
            }
        
        # 提取关键词
        extractor = ClassificationService._get_keyword_extractor()
        keywords = extractor.extract(parse_result.content)
        
        # 保存关键词到数据库
        ClassificationService._save_keywords(material_id, keywords)
        
        # 进行分类预测
        classifier = ClassificationService._get_classifier()
        keyword_strings = [kw.keyword for kw in keywords]
        classification_result = classifier.predict(parse_result.content, keyword_strings)
        
        # 获取分类名称
        category_name = None
        if classification_result.category_id:
            category = MaterialCategory.query.get(classification_result.category_id)
            if category:
                category_name = category.name
        
        # 创建分类日志
        log_id = None
        if classification_result.category_id:
            log = ClassificationLog(
                material_id=material_id,
                original_category_id=material.category_id,
                suggested_category_id=classification_result.category_id,
                confidence=Decimal(str(classification_result.confidence)),
                algorithm_used='NaiveBayes',
                features={'keywords': keyword_strings[:10]}
            )
            log.save()
            log_id = log.id
            
            # 如果高置信度，自动应用分类
            if classification_result.should_auto_apply:
                material.category_id = classification_result.category_id
                material.auto_classified = True
                db.session.commit()
                log.is_accepted = True
                db.session.commit()
        
        return {
            'material_id': material_id,
            'suggested_category_id': classification_result.category_id,
            'suggested_category_name': category_name,
            'confidence': classification_result.confidence,
            'should_auto_apply': classification_result.should_auto_apply,
            'needs_confirmation': classification_result.needs_confirmation,
            'keywords': [{'keyword': kw.keyword, 'weight': kw.weight} for kw in keywords],
            'log_id': log_id
        }

    @staticmethod
    def _save_keywords(material_id: int, keywords: List[KeywordResult]) -> None:
        """保存关键词到数据库"""
        # 删除旧的关键词
        DocumentKeyword.query.filter_by(material_id=material_id).delete()
        
        # 保存新的关键词
        for kw in keywords:
            doc_keyword = DocumentKeyword(
                material_id=material_id,
                keyword=kw.keyword,
                weight=Decimal(str(kw.weight)),
                extraction_method='TF-IDF'
            )
            db.session.add(doc_keyword)
        
        db.session.commit()

    @staticmethod
    def extract_keywords(material_id: int, top_n: int = 10) -> List[Dict]:
        """
        提取资料关键词
        
        Args:
            material_id: 资料 ID
            top_n: 返回的关键词数量
            
        Returns:
            关键词列表
        """
        # 先检查数据库中是否已有关键词
        existing_keywords = DocumentKeyword.get_top_keywords(material_id, top_n)
        if existing_keywords:
            return [
                {'keyword': kw.keyword, 'weight': float(kw.weight)}
                for kw in existing_keywords
            ]
        
        # 如果没有，则提取并保存
        material = Material.query.get(material_id)
        if not material:
            raise ValueError(f"资料不存在: {material_id}")
        
        # 解析文档
        parse_result = DocumentParser.parse(material.file_path)
        if not parse_result.success or not parse_result.content.strip():
            return []
        
        # 提取关键词
        extractor = ClassificationService._get_keyword_extractor()
        keywords = extractor.extract(parse_result.content, top_n=top_n)
        
        # 保存到数据库
        ClassificationService._save_keywords(material_id, keywords)
        
        return [{'keyword': kw.keyword, 'weight': kw.weight} for kw in keywords]

    @staticmethod
    def suggest_tags(material_id: int) -> List[Dict]:
        """
        推荐标签
        
        Args:
            material_id: 资料 ID
            
        Returns:
            标签建议列表
        """
        # 获取关键词
        keywords_data = ClassificationService.extract_keywords(material_id)
        if not keywords_data:
            return []
        
        # 转换为 KeywordResult 对象
        keywords = [
            KeywordResult(keyword=kw['keyword'], weight=kw['weight'])
            for kw in keywords_data
        ]
        
        # 推荐标签
        recommender = ClassificationService._get_tag_recommender()
        suggestions = recommender.recommend(keywords)
        
        return [
            {
                'tag_name': s.tag_name,
                'tag_id': s.tag_id,
                'is_existing': s.is_existing,
                'relevance': s.relevance
            }
            for s in suggestions
        ]

    @staticmethod
    def accept_classification(log_id: int) -> bool:
        """
        接受分类建议
        
        Args:
            log_id: 分类日志 ID
            
        Returns:
            是否成功
        """
        log = ClassificationLog.query.get(log_id)
        if not log:
            raise ValueError(f"分类日志不存在: {log_id}")
        
        if log.is_accepted is not None:
            raise ValueError("该分类建议已被处理")
        
        log.accept()
        return True

    @staticmethod
    def reject_classification(log_id: int) -> bool:
        """
        拒绝分类建议
        
        Args:
            log_id: 分类日志 ID
            
        Returns:
            是否成功
        """
        log = ClassificationLog.query.get(log_id)
        if not log:
            raise ValueError(f"分类日志不存在: {log_id}")
        
        if log.is_accepted is not None:
            raise ValueError("该分类建议已被处理")
        
        log.reject()
        return True

    @staticmethod
    def train_classifier() -> Dict[str, Any]:
        """
        训练分类模型
        
        使用已分类的资料作为训练数据。
        
        Returns:
            训练结果
        """
        from app.intelligence.category_classifier import TrainingItem
        
        # 获取已分类的资料
        materials = Material.query.filter(Material.category_id.isnot(None)).all()
        
        if not materials:
            return {
                'success': False,
                'message': '没有可用的训练数据',
                'accuracy': 0.0
            }
        
        # 准备训练数据
        training_data = []
        category_names = {}
        
        for material in materials:
            # 解析文档内容
            parse_result = DocumentParser.parse(material.file_path)
            if parse_result.success and parse_result.content.strip():
                training_data.append(TrainingItem(
                    text=parse_result.content,
                    category_id=material.category_id
                ))
                
                # 记录分类名称
                if material.category_id not in category_names:
                    category = MaterialCategory.query.get(material.category_id)
                    if category:
                        category_names[material.category_id] = category.name
        
        if not training_data:
            return {
                'success': False,
                'message': '没有可解析的训练文档',
                'accuracy': 0.0
            }
        
        # 训练模型
        classifier = ClassificationService._get_classifier()
        result = classifier.train(training_data, category_names)
        
        # 保存模型
        if result.success:
            os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
            classifier.save_model(MODEL_PATH)
        
        return {
            'success': result.success,
            'message': result.message,
            'accuracy': result.accuracy
        }
