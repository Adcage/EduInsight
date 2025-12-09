# 设计文档：智能问答助手

## 概述

智能问答助手是一个基于课程资料库的智能问答系统，能够自动回答学生关于课程安排、作业要求、考试信息等常见问题。系统通过自然语言处理技术理解学生提问，并从课程知识库中检索相关信息提供准确答案。

**核心设计目标：**

- 减轻教师重复回答常见问题的负担
- 提升学生获取信息的效率
- 维护对话上下文以支持追问
- 提供透明的答案来源和置信度分数
- 通过反馈收集实现持续改进

**技术栈：**

- 后端：Python with FastAPI
- 自然语言处理：TF-IDF 向量化与余弦相似度
- 数据库：PostgreSQL 用于结构化数据，向量存储用于嵌入
- 文本处理：中文分词（jieba）
- 文件处理：从各种文档格式提取文本

## 架构

系统采用分层架构，实现关注点清晰分离：

```
┌─────────────────────────────────────────────────────────┐
│                      表示层                              │
│              (API 端点, 请求/响应)                       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                      应用层                              │
│         (问答服务, 意图识别, 上下文管理)                 │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                      领域层                              │
│    (知识检索, 相似度匹配, FAQ管理)                       │
└─────────────────────────────────────────────────────────┘
                            │
┌─────────────────────────────────────────────────────────┐
│                    基础设施层                            │
│        (数据库, 资料索引, 文本处理)                      │
└─────────────────────────────────────────────────────────┘
```

**设计理由：**

- 分层架构使每个组件能够独立测试和修改
- 意图识别、检索和排序之间的清晰边界允许算法改进而不影响其他部分
- FAQ 管理与通用检索的分离使得可以优先返回精选答案

## 组件和接口

### 1. 问题处理组件

**职责：**

- 验证问题输入（长度、内容）
- 执行中文分词
- 提取关键词
- 识别问题意图

**接口：**

```python
class QuestionProcessor:
    def validate_question(self, text: str) -> ValidationResult
    def segment_text(self, text: str) -> List[str]
    def extract_keywords(self, text: str) -> List[str]
    def recognize_intent(self, text: str, keywords: List[str]) -> Intent
```

**设计理由：**

- 在入口点进行验证可防止无效数据在系统中传播
- 关键词提取使相似度匹配更高效
- 意图识别允许从特定知识源进行针对性检索

### 2. 知识检索组件

**职责：**

- 根据意图从不同知识源检索信息
- 访问课程安排、作业、考试和资料
- 查询 FAQ 数据库
- 搜索资料内容索引

**接口：**

```python
class KnowledgeRetriever:
    def retrieve_by_intent(self, intent: Intent, keywords: List[str],
                          course_id: Optional[str]) -> List[KnowledgeItem]
    def retrieve_course_info(self, keywords: List[str], course_id: Optional[str]) -> List[KnowledgeItem]
    def retrieve_assignment_info(self, keywords: List[str], course_id: Optional[str]) -> List[KnowledgeItem]
    def retrieve_exam_info(self, keywords: List[str], course_id: Optional[str]) -> List[KnowledgeItem]
    def retrieve_material_info(self, keywords: List[str], course_id: Optional[str]) -> List[KnowledgeItem]
    def search_faq(self, question: str, course_id: Optional[str]) -> List[FAQItem]
```

**设计理由：**

- 基于意图的路由确保查询针对最相关的知识源
- 课程范围的检索提高答案相关性
- FAQ 优先级使常见问题能够返回精选答案

### 3. 相似度匹配组件

**职责：**

- 使用 TF-IDF 对问题和知识条目进行向量化
- 计算余弦相似度分数
- 按相关性对结果排序
- 分类相关性级别（高/中/低）

**接口：**

```python
class SimilarityMatcher:
    def vectorize(self, text: str) -> Vector
    def calculate_similarity(self, query_vector: Vector, item_vector: Vector) -> float
    def rank_items(self, query: str, items: List[KnowledgeItem]) -> List[RankedItem]
    def classify_relevance(self, score: float) -> RelevanceLevel
```

**设计理由：**

- TF-IDF 为中文文本提供良好的基线性能，无需大型训练数据集
- 余弦相似度计算高效且可解释
- 三级相关性分类（高 ≥0.6，中 0.3-0.6，低 <0.3）支持灵活的答案策略

### 4. 答案生成组件

**职责：**

- 从检索到的知识条目格式化答案
- 包含来源信息和置信度分数
- 处理多个高相关性结果
- 在未找到良好匹配时生成后备响应

**接口：**

```python
class AnswerGenerator:
    def generate_answer(self, ranked_items: List[RankedItem],
                       question: str) -> Answer
    def format_material_answer(self, item: MaterialItem) -> str
    def format_structured_answer(self, item: StructuredItem) -> str
    def generate_fallback(self, question: str,
                         medium_items: List[RankedItem]) -> Answer
```

**设计理由：**

- 针对不同知识类型的独立格式化确保适当的呈现
- 置信度分数提供答案质量的透明度
- 后备响应在未找到精确匹配时保持用户参与

### 5. 上下文管理组件

**职责：**

- 在会话中维护对话历史
- 使用上下文解析代词和引用
- 检测话题变化
- 管理会话超时

**接口：**

```python
class ContextManager:
    def create_session(self, user_id: str) -> Session
    def add_to_context(self, session_id: str, question: str, answer: Answer) -> None
    def resolve_references(self, question: str, context: Context) -> str
    def detect_topic_change(self, question: str, context: Context) -> bool
    def cleanup_expired_sessions(self) -> None
```

**设计理由：**

- 基于会话的上下文支持自然的追问
- 30 分钟超时在内存使用和用户体验之间取得平衡
- 话题变化检测防止不相关问题污染上下文

### 6. FAQ 管理组件

**职责：**

- FAQ 条目的增删改查操作
- 将 FAQ 关联到特定课程
- 在答案生成中优先匹配 FAQ

**接口：**

```python
class FAQManager:
    def create_faq(self, question: str, answer: str,
                   course_id: Optional[str]) -> FAQ
    def update_faq(self, faq_id: str, question: Optional[str],
                   answer: Optional[str]) -> FAQ
    def delete_faq(self, faq_id: str) -> bool
    def get_course_faqs(self, course_id: str) -> List[FAQ]
```

**设计理由：**

- 教师精选的 FAQ 确保常见问题的答案一致且准确
- 课程关联支持特定课程的 FAQ 管理
- 优先匹配确保精选答案优先于自动生成的答案

### 7. 资料索引组件

**职责：**

- 从上传的资料中提取文本内容
- 将内容分段为段落
- 构建和维护可搜索索引
- 在资料变更时更新索引

**接口：**

```python
class MaterialIndexer:
    def index_material(self, material_id: str, content: bytes,
                      file_type: str) -> IndexResult
    def update_index(self, material_id: str, content: bytes) -> IndexResult
    def remove_from_index(self, material_id: str) -> bool
    def search_index(self, query: str, course_id: Optional[str]) -> List[IndexMatch]
```

**设计理由：**

- 上传时自动索引确保资料立即可搜索
- 段落级分段提供精确的答案上下文
- 位置跟踪使得能够返回周围上下文以便更好理解

### 8. 分析组件

**职责：**

- 记录问答交互
- 跟踪用户反馈（有帮助/无帮助）
- 生成性能统计
- 识别高频和低评价问题

**接口：**

```python
class AnalyticsService:
    def record_interaction(self, question: str, answer: Answer,
                          user_id: str) -> InteractionRecord
    def record_feedback(self, interaction_id: str, helpful: bool,
                       feedback_text: Optional[str]) -> None
    def get_statistics(self) -> Statistics
    def get_frequent_questions(self, limit: int) -> List[QuestionStats]
    def get_low_rated_questions(self) -> List[QuestionStats]
    def export_data(self, start_date: date, end_date: date) -> bytes
```

**设计理由：**

- 全面的日志记录支持系统持续改进
- 反馈收集识别需要创建 FAQ 或系统调优的领域
- 导出功能支持外部分析和报告

## 数据模型

### Question（问题）

```python
@dataclass
class Question:
    id: str
    text: str
    user_id: str
    course_id: Optional[str]
    session_id: str
    timestamp: datetime
    keywords: List[str]
    intent: Intent
```

### Intent（意图）

```python
class Intent(Enum):
    COURSE_INFO = "course_info"        # 课程信息
    ASSIGNMENT_INFO = "assignment_info"  # 作业信息
    EXAM_INFO = "exam_info"            # 考试信息
    MATERIAL_INFO = "material_info"    # 资料信息
    GENERAL = "general"                # 通用查询
```

### KnowledgeItem（知识条目）

```python
@dataclass
class KnowledgeItem:
    id: str
    content: str
    source_type: str  # "course", "assignment", "exam", "material", "faq"
    source_id: str
    metadata: Dict[str, Any]  # 标题、日期、位置等
```

### RankedItem（排序条目）

```python
@dataclass
class RankedItem:
    item: KnowledgeItem
    similarity_score: float
    relevance_level: RelevanceLevel  # HIGH, MEDIUM, LOW
```

### Answer（答案）

```python
@dataclass
class Answer:
    content: str
    sources: List[SourceInfo]
    confidence_score: float
    suggestions: Optional[List[str]]  # 用于后备响应
```

### SourceInfo（来源信息）

```python
@dataclass
class SourceInfo:
    type: str
    title: str
    reference: str  # 资料名称、FAQ ID 等
```

### FAQ（常见问题）

```python
@dataclass
class FAQ:
    id: str
    question: str
    answer: str
    course_id: Optional[str]
    created_by: str
    created_at: datetime
    updated_at: datetime
```

### Session（会话）

```python
@dataclass
class Session:
    id: str
    user_id: str
    created_at: datetime
    last_activity: datetime
    context: Context
```

### Context（上下文）

```python
@dataclass
class Context:
    history: List[Tuple[Question, Answer]]
    current_topic: Optional[str]
    referenced_entities: Dict[str, Any]  # 代词 -> 实体
```

### InteractionRecord（交互记录）

```python
@dataclass
class InteractionRecord:
    id: str
    question: Question
    answer: Answer
    feedback_helpful: Optional[bool]
    feedback_text: Optional[str]
    timestamp: datetime
```

### MaterialIndex（资料索引）

```python
@dataclass
class MaterialIndex:
    material_id: str
    course_id: str
    segments: List[ContentSegment]
    indexed_at: datetime
```

### ContentSegment（内容段落）

```python
@dataclass
class ContentSegment:
    segment_id: str
    content: str
    position: int  # 段落编号
    vector: Vector
```

### ValidationResult（验证结果）

```python
@dataclass
class ValidationResult:
    is_valid: bool
    error_message: Optional[str]
    error_code: Optional[str]  # "EMPTY_QUESTION", "TOO_LONG", etc.
```

### Statistics（统计数据）

```python
@dataclass
class Statistics:
    total_questions: int
    answer_success_rate: float
    average_confidence: float
    total_feedback_count: int
    helpful_feedback_count: int
    period_start: datetime
    period_end: datetime
```

### QuestionStats（问题统计）

```python
@dataclass
class QuestionStats:
    question_text: str
    frequency: int
    average_rating: Optional[float]
    last_asked: datetime
```
