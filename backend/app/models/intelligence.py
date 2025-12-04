"""
智能模块模型

包含文档关键词、分类日志等相关模型定义。
"""
from app.extensions import db
from .base import BaseModel


class DocumentKeyword(BaseModel):
    """文档关键词模型（智能归类）
    
    NLP提取的文档关键词，用于自动分类。
    """
    __tablename__ = 'document_keywords'
    
    # ==================== 字段定义 ====================
    # 外键关联
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    
    # 关键词信息
    keyword = db.Column(db.String(100), nullable=False, index=True)
    weight = db.Column(db.Numeric(5, 4), default=0.0000, nullable=False)
    extraction_method = db.Column(db.String(50), nullable=True)  # TF-IDF/TextRank/BERT等
    
    # ==================== 实例方法 ====================
    def get_weight_percentage(self):
        """获取权重百分比"""
        return round(float(self.weight) * 100, 2)
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_material(cls, material_id, limit=None):
        """获取资料的所有关键词"""
        query = cls.query.filter_by(material_id=material_id).order_by(cls.weight.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_top_keywords(cls, material_id, top_n=10):
        """获取资料的Top N关键词"""
        return cls.get_by_material(material_id, limit=top_n)
    
    @classmethod
    def search_by_keyword(cls, keyword):
        """根据关键词搜索资料"""
        return cls.query.filter(cls.keyword.like(f'%{keyword}%')).all()
    
    @classmethod
    def get_popular_keywords(cls, limit=20):
        """获取热门关键词"""
        from sqlalchemy import func
        return db.session.query(
            cls.keyword,
            func.count(cls.id).label('count'),
            func.avg(cls.weight).label('avg_weight')
        ).group_by(cls.keyword).order_by(
            func.count(cls.id).desc()
        ).limit(limit).all()
    
    def __repr__(self):
        return f'<DocumentKeyword {self.keyword} weight:{self.weight}>'


class ClassificationLog(BaseModel):
    """分类日志模型
    
    记录自动分类的过程和结果。
    """
    __tablename__ = 'classification_logs'
    
    # ==================== 字段定义 ====================
    # 外键关联
    material_id = db.Column(db.Integer, db.ForeignKey('materials.id'), nullable=False, index=True)
    original_category_id = db.Column(db.Integer, db.ForeignKey('material_categories.id'), nullable=True, index=True)
    suggested_category_id = db.Column(db.Integer, db.ForeignKey('material_categories.id'), nullable=False, index=True)
    
    # 分类信息
    confidence = db.Column(db.Numeric(5, 4), nullable=True)  # 置信度(0-1)
    is_accepted = db.Column(db.Boolean, nullable=True, index=True)  # 1:是, 0:否, NULL:待处理
    algorithm_used = db.Column(db.String(50), nullable=True)  # NaiveBayes/SVM/BERT等
    features = db.Column(db.JSON, nullable=True)  # 特征数据(JSON格式)
    
    # ==================== 实例方法 ====================
    def is_pending(self):
        """检查是否待处理"""
        return self.is_accepted is None
    
    def is_accepted_classification(self):
        """检查是否接受建议"""
        return self.is_accepted is True
    
    def is_rejected(self):
        """检查是否拒绝建议"""
        return self.is_accepted is False
    
    def accept(self):
        """接受分类建议"""
        self.is_accepted = True
        
        # 更新资料的分类
        from .material import Material
        material = Material.query.get(self.material_id)
        if material:
            material.category_id = self.suggested_category_id
            material.auto_classified = True
            db.session.commit()
    
    def reject(self):
        """拒绝分类建议"""
        self.is_accepted = False
        db.session.commit()
    
    def get_confidence_percentage(self):
        """获取置信度百分比"""
        if self.confidence:
            return round(float(self.confidence) * 100, 2)
        return 0.00
    
    def is_high_confidence(self, threshold=0.8):
        """检查是否高置信度"""
        return self.confidence and float(self.confidence) >= threshold
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_material(cls, material_id):
        """获取资料的所有分类日志"""
        return cls.query.filter_by(material_id=material_id).order_by(cls.created_at.desc()).all()
    
    @classmethod
    def get_pending(cls, limit=None):
        """获取所有待处理的分类建议"""
        query = cls.query.filter_by(is_accepted=None).order_by(cls.created_at.desc())
        if limit:
            query = query.limit(limit)
        return query.all()
    
    @classmethod
    def get_accepted(cls):
        """获取所有已接受的分类"""
        return cls.query.filter_by(is_accepted=True).all()
    
    @classmethod
    def get_rejected(cls):
        """获取所有已拒绝的分类"""
        return cls.query.filter_by(is_accepted=False).all()
    
    @classmethod
    def get_accuracy_rate(cls):
        """获取分类准确率"""
        total = cls.query.filter(cls.is_accepted.isnot(None)).count()
        if total == 0:
            return 0.00
        
        accepted = cls.query.filter_by(is_accepted=True).count()
        return round((accepted / total) * 100, 2)
    
    @classmethod
    def get_by_algorithm(cls, algorithm):
        """获取指定算法的分类日志"""
        return cls.query.filter_by(algorithm_used=algorithm).all()
    
    def __repr__(self):
        return f'<ClassificationLog material:{self.material_id} confidence:{self.confidence}>'
