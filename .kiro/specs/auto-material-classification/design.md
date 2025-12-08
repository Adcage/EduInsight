# Design Document: 自动化资料归类

## Overview

自动化资料归类功能通过 NLP 和机器学习技术，为教师智能助手系统提供文档内容分析、关键词提取、智能分类推荐和标签推荐能力。该功能将集成到现有的资料中心模块中，在资料上传后自动触发分析流程。

核心技术栈：

- **中文分词**: Jieba
- **关键词提取**: TF-IDF (scikit-learn)
- **文本分类**: Naive Bayes / SVM (scikit-learn)
- **文档解析**: PyPDF2 (PDF), python-docx (Word)

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                        Frontend (Vue 3)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐  │
│  │ Upload View │  │ Detail View │  │ Classification Panel    │  │
│  └──────┬──────┘  └──────┬──────┘  └───────────┬─────────────┘  │
└─────────┼────────────────┼─────────────────────┼────────────────┘
          │                │                     │
          ▼                ▼                     ▼
┌─────────────────────────────────────────────────────────────────┐
│                    API Layer (Flask)                             │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              material_api.py (扩展)                          ││
│  │  POST /{id}/classify  GET /{id}/keywords  POST /{id}/suggest-tags │
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Service Layer                                  │
│  ┌─────────────────────────────────────────────────────────────┐│
│  │              classification_service.py                       ││
│  │  - classify_material()                                       ││
│  │  - extract_keywords()                                        ││
│  │  - suggest_tags()                                            ││
│  │  - accept_classification()                                   ││
│  │  - reject_classification()                                   ││
│  └─────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Intelligence Module                            │
│  ┌───────────────┐  ┌───────────────┐  ┌───────────────────────┐│
│  │DocumentParser │  │KeywordExtractor│  │CategoryClassifier    ││
│  │ - parse_pdf() │  │ - extract()    │  │ - predict()          ││
│  │ - parse_docx()│  │ - segment()    │  │ - train()            ││
│  │ - parse_txt() │  │ - filter()     │  │ - load_model()       ││
│  └───────────────┘  └───────────────┘  └───────────────────────┘│
│  ┌───────────────────────────────────────────────────────────────┐
│  │                    TagRecommender                             │
│  │  - recommend()  - match_existing()  - suggest_new()          │
│  └───────────────────────────────────────────────────────────────┘
└─────────────────────────────────────────────────────────────────┘
          │
          ▼
┌─────────────────────────────────────────────────────────────────┐
│                   Data Layer (SQLAlchemy)                        │
│  ┌─────────────┐  ┌─────────────────┐  ┌─────────────────────┐  │
│  │  Material   │  │ DocumentKeyword │  │ ClassificationLog   │  │
│  └─────────────┘  └─────────────────┘  └─────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
```

## Components and Interfaces

### 1. DocumentParser (文档解析器)

负责从不同格式的文件中提取文本内容。

```python
class DocumentParser:
    """文档解析器"""

    @staticmethod
    def parse(file_path: str) -> ParseResult:
        """根据文件类型自动选择解析方法"""
        pass

    @staticmethod
    def parse_pdf(file_path: str) -> str:
        """解析 PDF 文件"""
        pass

    @staticmethod
    def parse_docx(file_path: str) -> str:
        """解析 Word 文档"""
        pass

    @staticmethod
    def parse_txt(file_path: str) -> str:
        """解析文本文件"""
        pass

@dataclass
class ParseResult:
    """解析结果"""
    content: str                    # 提取的文本内容
    success: bool                   # 是否成功
    error_message: Optional[str]    # 错误信息
    file_type: str                  # 文件类型
    extraction_method: str          # 提取方法
    timestamp: datetime             # 提取时间

    def to_json(self) -> str:
        """序列化为 JSON"""
        pass

    @classmethod
    def from_json(cls, json_str: str) -> 'ParseResult':
        """从 JSON 反序列化"""
        pass
```

### 2. KeywordExtractor (关键词提取器)

使用 Jieba 分词和 TF-IDF 算法提取关键词。

```python
class KeywordExtractor:
    """关键词提取器"""

    def __init__(self, stop_words_path: Optional[str] = None):
        """初始化，加载停用词表"""
        pass

    def extract(self, text: str, top_n: int = 10) -> List[KeywordResult]:
        """提取关键词"""
        pass

    def segment(self, text: str) -> List[str]:
        """中文分词"""
        pass

    def filter_stop_words(self, words: List[str]) -> List[str]:
        """过滤停用词和单字"""
        pass

@dataclass
class KeywordResult:
    """关键词结果"""
    keyword: str      # 关键词
    weight: float     # 权重 (0-1)
```

### 3. CategoryClassifier (分类器)

基于机器学习模型进行文档分类。

```python
class CategoryClassifier:
    """分类分类器"""

    def __init__(self, model_path: Optional[str] = None):
        """初始化，加载预训练模型"""
        pass

    def predict(self, text: str, keywords: List[str]) -> ClassificationResult:
        """预测分类"""
        pass

    def train(self, training_data: List[TrainingItem]) -> TrainResult:
        """训练模型"""
        pass

    def save_model(self, path: str) -> bool:
        """保存模型"""
        pass

    def load_model(self, path: str) -> bool:
        """加载模型"""
        pass

@dataclass
class ClassificationResult:
    """分类结果"""
    category_id: Optional[int]      # 推荐的分类 ID
    category_name: Optional[str]    # 分类名称
    confidence: float               # 置信度 (0-1)
    should_auto_apply: bool         # 是否自动应用
    needs_confirmation: bool        # 是否需要确认

@dataclass
class TrainingItem:
    """训练数据项"""
    text: str           # 文本内容
    category_id: int    # 分类 ID
```

### 4. TagRecommender (标签推荐器)

根据关键词推荐相关标签。

```python
class TagRecommender:
    """标签推荐器"""

    def recommend(self, keywords: List[KeywordResult], max_tags: int = 5) -> List[TagSuggestion]:
        """推荐标签"""
        pass

    def match_existing_tags(self, keywords: List[str]) -> List[MaterialTag]:
        """匹配现有标签"""
        pass

    def suggest_new_tags(self, keywords: List[KeywordResult], count: int) -> List[str]:
        """建议新标签"""
        pass

@dataclass
class TagSuggestion:
    """标签建议"""
    tag_name: str           # 标签名称
    tag_id: Optional[int]   # 标签 ID (如果是现有标签)
    is_existing: bool       # 是否为现有标签
    relevance: float        # 相关度
```

### 5. ClassificationService (分类服务)

整合各组件，提供业务逻辑。

```python
class ClassificationService:
    """分类服务"""

    @staticmethod
    def classify_material(material_id: int) -> Dict[str, Any]:
        """分析并分类资料"""
        pass

    @staticmethod
    def extract_keywords(material_id: int, top_n: int = 10) -> List[Dict]:
        """提取资料关键词"""
        pass

    @staticmethod
    def suggest_tags(material_id: int) -> List[Dict]:
        """推荐标签"""
        pass

    @staticmethod
    def accept_classification(log_id: int) -> bool:
        """接受分类建议"""
        pass

    @staticmethod
    def reject_classification(log_id: int) -> bool:
        """拒绝分类建议"""
        pass

    @staticmethod
    def train_classifier() -> Dict[str, Any]:
        """训练分类模型"""
        pass
```

## Data Models

### 现有模型 (已实现)

**DocumentKeyword** - 文档关键词

```python
class DocumentKeyword(BaseModel):
    material_id: int          # 资料 ID (外键)
    keyword: str              # 关键词
    weight: Decimal(5,4)      # 权重 (0-1)
    extraction_method: str    # 提取方法 (TF-IDF/TextRank)
```

**ClassificationLog** - 分类日志

```python
class ClassificationLog(BaseModel):
    material_id: int              # 资料 ID (外键)
    original_category_id: int     # 原分类 ID
    suggested_category_id: int    # 建议分类 ID
    confidence: Decimal(5,4)      # 置信度 (0-1)
    is_accepted: bool             # 是否接受 (True/False/None)
    algorithm_used: str           # 使用的算法
    features: JSON                # 特征数据
```

### 新增 Schema

```python
# classification_schemas.py

class ClassifyMaterialResponseModel(CamelCaseModel):
    """分类结果响应"""
    material_id: int
    suggested_category_id: Optional[int]
    suggested_category_name: Optional[str]
    confidence: float
    should_auto_apply: bool
    needs_confirmation: bool
    keywords: List[KeywordResponseModel]
    log_id: int

class KeywordResponseModel(CamelCaseModel):
    """关键词响应"""
    keyword: str
    weight: float

class TagSuggestionResponseModel(CamelCaseModel):
    """标签建议响应"""
    tag_name: str
    tag_id: Optional[int]
    is_existing: bool
    relevance: float

class ClassificationLogPathModel(CamelCaseModel):
    """分类日志路径参数"""
    log_id: int = Field(..., description="分类日志ID", ge=1)
```

## 正确性属性

_属性是指在系统的所有有效执行中都应保持为真的特征或行为——本质上是关于系统应该做什么的形式化陈述。属性是人类可读规范与机器可验证正确性保证之间的桥梁。_

基于前期分析，已识别出以下正确性属性：

### 属性 1: 文档解析往返一致性

_对于任意_ 包含已知文本内容的有效文档文件（PDF、DOCX、TXT），解析文档应提取出包含原始内容的文本（允许格式差异）。
**验证需求: 1.1, 1.2, 1.3**

### 属性 2: 解析结果序列化往返一致性

_对于任意_ ParseResult 对象，序列化为 JSON 后再反序列化应产生等价的 ParseResult，所有字段保持不变。
**验证需求: 8.1, 8.2, 8.3**

### 属性 3: 关键词提取产生有效权重

_对于任意_ 非空文本输入，所有提取的关键词权重应在 [0, 1] 范围内。
**验证需求: 2.2**

### 属性 4: 关键词数量遵守限制

_对于任意_ 文本输入和 top_n 参数，提取的关键词数量应不超过 top_n。
**验证需求: 2.3**

### 属性 5: 关键词排除停用词和单字

_对于任意_ 提取的关键词列表，不应包含停用词或单个字符。
**验证需求: 2.5**

### 属性 6: 分类置信度在有效范围内

_对于任意_ 分类预测，置信度分数应在 [0, 1] 范围内。
**验证需求: 3.2**

### 属性 7: 高置信度触发自动应用

_对于任意_ 置信度 > 0.7 的分类，结果应指示启用自动应用。
**验证需求: 3.3**

### 属性 8: 中等置信度需要确认

_对于任意_ 0.5 <= 置信度 <= 0.7 的分类，结果应指示需要用户确认。
**验证需求: 3.4**

### 属性 9: 低置信度不产生建议

_对于任意_ 置信度 < 0.5 的分类，不应给出分类建议。
**验证需求: 3.5**

### 属性 10: 标签建议遵守最大数量限制

_对于任意_ 标签推荐请求，建议的标签数量应不超过 5 个。
**验证需求: 4.4**

### 属性 11: API 错误响应遵循标准格式

_对于任意_ 失败的 API 请求，响应应包含 code、message 和 data 字段。
**验证需求: 6.6**

## Error Handling

### 文档解析错误

- **文件不存在**: 返回 404 错误，提示文件未找到
- **不支持的格式**: 返回 400 错误，提示文件格式不支持
- **解析失败**: 记录错误日志，返回空内容，不影响其他功能

### 分类错误

- **模型未加载**: 使用基于规则的简单分类作为降级方案
- **分类失败**: 返回空分类建议，允许用户手动选择

### 数据库错误

- **保存失败**: 回滚事务，返回 500 错误
- **查询失败**: 返回 500 错误，记录详细日志

## 测试策略

### 测试框架

- **单元测试**: pytest
- **属性测试**: hypothesis (Python 属性测试库)

### 单元测试覆盖

1. DocumentParser 各格式解析
2. KeywordExtractor 分词和提取
3. CategoryClassifier 预测和训练
4. TagRecommender 推荐逻辑
5. API 端点响应

### 属性测试覆盖

每个正确性属性都将有对应的属性测试，使用 hypothesis 库生成随机输入进行验证。

测试文件结构：

```
backend/tests/
├── test_classification/
│   ├── test_document_parser.py      # 文档解析测试
│   ├── test_keyword_extractor.py    # 关键词提取测试
│   ├── test_category_classifier.py  # 分类器测试
│   ├── test_tag_recommender.py      # 标签推荐测试
│   ├── test_classification_service.py  # 服务层测试
│   └── test_classification_api.py   # API 测试
└── conftest.py                      # 测试配置和 fixtures
```

### 属性测试配置

- 每个属性测试运行至少 100 次迭代
- 使用 hypothesis 的 @given 装饰器生成测试数据
- 测试注释格式: `**Feature: auto-material-classification, 属性 {number}: {property_text}**`
