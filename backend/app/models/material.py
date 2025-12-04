"""
资料中心模块模型

包含资料、分类、标签等相关模型定义。
"""
from app.extensions import db
from .base import BaseModel


# ==================== 关联表 ====================
material_tag_relation = db.Table(
    'material_tag_relation',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('material_id', db.Integer, nullable=False, index=True),  # FK→materials.id
    db.Column('tag_id', db.Integer, nullable=False, index=True),  # FK→material_tags.id
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp(), nullable=False),
    db.Column('updated_at', db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp(), nullable=False),
    db.UniqueConstraint('material_id', 'tag_id', name='uk_material_tag')
)


class MaterialCategory(BaseModel):
    """资料分类模型
    
    支持多级分类的资料分类体系。
    """
    __tablename__ = 'material_categories'
    
    # ==================== 字段定义 ====================
    # 基本信息
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255), nullable=True)
    sort_order = db.Column(db.Integer, default=0, nullable=False)
    
    # 父分类（支持多级分类）
    parent_id = db.Column(db.Integer, nullable=True, index=True)  # FK→material_categories.id
    
    # ==================== 关系定义 ====================
    # 自引用关系：父子分类
    children = db.relationship(
        'MaterialCategory',
        backref=db.backref('parent', remote_side='MaterialCategory.id'),
        lazy='dynamic'
    )
    
    # 一对多：分类下的资料
    materials = db.relationship('Material', backref='category', lazy='dynamic')
    
    # ==================== 实例方法 ====================
    def is_top_level(self):
        """检查是否为顶级分类"""
        return self.parent_id is None
    
    def get_full_path(self):
        """获取完整分类路径"""
        if self.parent_id is None:
            return self.name
        parent = MaterialCategory.query.get(self.parent_id)
        if parent:
            return f"{parent.get_full_path()} > {self.name}"
        return self.name
    
    # ==================== 类方法 ====================
    @classmethod
    def get_top_level_categories(cls):
        """获取所有顶级分类"""
        return cls.query.filter_by(parent_id=None).order_by(cls.sort_order).all()
    
    @classmethod
    def get_by_parent(cls, parent_id):
        """获取指定父分类下的所有子分类"""
        return cls.query.filter_by(parent_id=parent_id).order_by(cls.sort_order).all()
    
    def __repr__(self):
        return f'<MaterialCategory {self.name}>'


class MaterialTag(BaseModel):
    """资料标签模型
    
    用于资料的标签管理。
    """
    __tablename__ = 'material_tags'
    
    # ==================== 字段定义 ====================
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    usage_count = db.Column(db.Integer, default=0, nullable=False)
    
    # ==================== 关系定义 ====================
    # 多对多：标签关联的资料
    # materials = db.relationship('Material', secondary=material_tag_relation, backref='tags', lazy='dynamic')
    
    # ==================== 实例方法 ====================
    def increment_usage(self):
        """增加使用次数"""
        self.usage_count += 1
        db.session.commit()
    
    def decrement_usage(self):
        """减少使用次数"""
        if self.usage_count > 0:
            self.usage_count -= 1
            db.session.commit()
    
    # ==================== 类方法 ====================
    @classmethod
    def get_or_create(cls, tag_name):
        """获取或创建标签"""
        tag = cls.query.filter_by(name=tag_name).first()
        if not tag:
            tag = cls(name=tag_name)
            tag.save()
        return tag
    
    @classmethod
    def get_popular_tags(cls, limit=10):
        """获取热门标签"""
        return cls.query.order_by(cls.usage_count.desc()).limit(limit).all()
    
    def __repr__(self):
        return f'<MaterialTag {self.name}>'


class Material(BaseModel):
    """资料模型
    
    存储所有教学资料的元数据和文件信息。
    """
    __tablename__ = 'materials'
    
    # ==================== 字段定义 ====================
    # 基本信息
    title = db.Column(db.String(200), nullable=False, index=True)
    description = db.Column(db.Text, nullable=True)
    
    # 文件信息
    file_name = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(500), nullable=False)
    file_size = db.Column(db.BigInteger, nullable=False)
    file_type = db.Column(db.String(50), nullable=False)
    
    # 外键关联
    course_id = db.Column(db.Integer, nullable=True, index=True)  # FK→courses.id
    uploader_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
    category_id = db.Column(db.Integer, nullable=True, index=True)  # FK→material_categories.id
    
    # 统计信息
    download_count = db.Column(db.Integer, default=0, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    # 智能归类
    keywords = db.Column(db.Text, nullable=True)
    auto_classified = db.Column(db.Boolean, default=False, nullable=False)
    
    # ==================== 关系定义 ====================
    # 多对多：资料和标签
    tags = db.relationship(
        'MaterialTag',
        secondary=material_tag_relation,
        backref=db.backref('materials', lazy='dynamic'),
        lazy='dynamic'
    )
    
    # 一对多：资料的关键词
    document_keywords = db.relationship('DocumentKeyword', backref='material', lazy='dynamic', cascade='all, delete-orphan')
    
    # 一对多：分类日志
    classification_logs = db.relationship('ClassificationLog', backref='material', lazy='dynamic', cascade='all, delete-orphan')
    
    # ==================== 实例方法 ====================
    def increment_download_count(self):
        """增加下载次数"""
        self.download_count += 1
        db.session.commit()
    
    def increment_view_count(self):
        """增加浏览次数"""
        self.view_count += 1
        db.session.commit()
    
    def is_owner(self, user_id):
        """检查是否为上传者"""
        return self.uploader_id == user_id
    
    def add_tag(self, tag_name):
        """添加标签"""
        tag = MaterialTag.get_or_create(tag_name)
        if tag not in self.tags:
            self.tags.append(tag)
            tag.increment_usage()
            db.session.commit()
    
    def remove_tag(self, tag_name):
        """移除标签"""
        tag = MaterialTag.query.filter_by(name=tag_name).first()
        if tag and tag in self.tags:
            self.tags.remove(tag)
            tag.decrement_usage()
            db.session.commit()
    
    def get_file_size_mb(self):
        """获取文件大小(MB)"""
        return round(self.file_size / (1024 * 1024), 2)
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id, page=1, per_page=20):
        """获取指定课程的资料（分页）"""
        return cls.query.filter_by(course_id=course_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @classmethod
    def get_by_uploader(cls, uploader_id, page=1, per_page=20):
        """获取指定用户上传的资料（分页）"""
        return cls.query.filter_by(uploader_id=uploader_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @classmethod
    def get_by_category(cls, category_id, page=1, per_page=20):
        """获取指定分类的资料（分页）"""
        return cls.query.filter_by(category_id=category_id).paginate(
            page=page, per_page=per_page, error_out=False
        )
    
    @classmethod
    def search(cls, keyword, page=1, per_page=20):
        """搜索资料"""
        return cls.query.filter(
            db.or_(
                cls.title.like(f'%{keyword}%'),
                cls.description.like(f'%{keyword}%'),
                cls.keywords.like(f'%{keyword}%')
            )
        ).paginate(page=page, per_page=per_page, error_out=False)
    
    def __repr__(self):
        return f'<Material {self.title}>'
