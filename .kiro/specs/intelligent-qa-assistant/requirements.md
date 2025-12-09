# Requirements Document

## Introduction

智能问答助手是一个基于课程资料库的智能问答系统，能够自动回答学生关于课程安排、作业要求、考试信息等常见问题。系统通过自然语言处理技术理解学生提问，并从课程资料库中检索相关信息提供准确答案，减轻教师重复回答常见问题的负担，提升学生获取信息的效率。

## Glossary

- **QA System**: 智能问答系统，指本系统中的问答助手模块
- **Knowledge Base**: 知识库，由课程资料、常见问题库、课程信息等构成的信息集合
- **Query**: 查询，指学生提出的问题
- **Answer**: 答案，系统返回的回复内容
- **Intent Recognition**: 意图识别，识别用户问题的意图类型
- **Similarity Matching**: 相似度匹配，计算问题与知识库条目的相似程度
- **Context**: 上下文，指当前对话的历史记录和课程环境
- **FAQ**: 常见问题库，预设的问题答案对
- **Material Index**: 资料索引，对课程资料内容的结构化索引

## Requirements

### Requirement 1

**User Story:** 作为学生，我想要向智能助手提问关于课程的问题，以便快速获取准确答案而无需等待教师回复。

#### Acceptance Criteria

1. WHEN 学生输入问题文本并提交 THEN THE QA System SHALL 接收并处理该问题
2. WHEN 问题文本为空或仅包含空白字符 THEN THE QA System SHALL 拒绝处理并提示用户输入有效问题
3. WHEN 问题文本超过 500 字符 THEN THE QA System SHALL 拒绝处理并提示用户精简问题
4. WHEN 学生选择特定课程后提问 THEN THE QA System SHALL 在该课程范围内搜索答案
5. WHEN 学生未选择课程提问 THEN THE QA System SHALL 在所有可访问课程范围内搜索答案

### Requirement 2

**User Story:** 作为系统，我需要理解学生问题的意图，以便提供针对性的答案。

#### Acceptance Criteria

1. WHEN 系统接收到问题 THEN THE QA System SHALL 对问题进行分词和关键词提取
2. WHEN 问题包含课程安排相关词汇 THEN THE QA System SHALL 识别为课程信息查询意图
3. WHEN 问题包含作业相关词汇 THEN THE QA System SHALL 识别为作业信息查询意图
4. WHEN 问题包含考试相关词汇 THEN THE QA System SHALL 识别为考试信息查询意图
5. WHEN 问题包含资料相关词汇 THEN THE QA System SHALL 识别为资料查询意图
6. WHEN 问题意图无法明确识别 THEN THE QA System SHALL 标记为通用查询意图

### Requirement 3

**User Story:** 作为系统，我需要从知识库中检索相关信息，以便为学生问题提供准确答案。

#### Acceptance Criteria

1. WHEN 系统识别问题意图后 THEN THE QA System SHALL 根据意图类型选择对应的知识源进行检索
2. WHEN 检索课程信息 THEN THE QA System SHALL 从课程表和课程资料中提取相关信息
3. WHEN 检索作业信息 THEN THE QA System SHALL 从作业类型资料和课程描述中提取相关信息
4. WHEN 检索考试信息 THEN THE QA System SHALL 从考试类型资料和成绩表中提取相关信息
5. WHEN 检索资料信息 THEN THE QA System SHALL 从资料表和资料内容索引中提取相关信息
6. WHEN 检索结果为空 THEN THE QA System SHALL 返回未找到相关信息的提示

### Requirement 4

**User Story:** 作为系统，我需要计算问题与知识库条目的相似度，以便找到最匹配的答案。

#### Acceptance Criteria

1. WHEN 系统提取问题关键词后 THEN THE QA System SHALL 计算问题与知识库条目的文本相似度
2. WHEN 使用 TF-IDF 向量化 THEN THE QA System SHALL 将问题和知识库条目转换为向量表示
3. WHEN 计算相似度 THEN THE QA System SHALL 使用余弦相似度度量方法
4. WHEN 相似度分数大于等于 0.6 THEN THE QA System SHALL 将该条目标记为高相关
5. WHEN 相似度分数在 0.3 到 0.6 之间 THEN THE QA System SHALL 将该条目标记为中等相关
6. WHEN 相似度分数小于 0.3 THEN THE QA System SHALL 将该条目标记为低相关

### Requirement 5

**User Story:** 作为学生，我想要获得清晰准确的答案，以便理解课程相关信息。

#### Acceptance Criteria

1. WHEN 系统找到高相关答案 THEN THE QA System SHALL 返回最相关的答案内容
2. WHEN 系统找到多个高相关答案 THEN THE QA System SHALL 返回相似度最高的前 3 个答案
3. WHEN 答案来自资料文件 THEN THE QA System SHALL 包含资料标题和相关段落内容
4. WHEN 答案来自结构化数据 THEN THE QA System SHALL 格式化为易读的文本形式
5. WHEN 系统返回答案 THEN THE QA System SHALL 包含答案来源信息和置信度分数
6. WHEN 没有找到高相关答案 THEN THE QA System SHALL 返回建议性提示或推荐相关资料

### Requirement 6

**User Story:** 作为教师，我想要管理常见问题库，以便为学生提供标准化答案。

#### Acceptance Criteria

1. WHEN 教师创建 FAQ 条目 THEN THE QA System SHALL 保存问题和答案到常见问题库
2. WHEN 教师编辑 FAQ 条目 THEN THE QA System SHALL 更新对应的问题或答案内容
3. WHEN 教师删除 FAQ 条目 THEN THE QA System SHALL 从常见问题库中移除该条目
4. WHEN 教师关联 FAQ 到特定课程 THEN THE QA System SHALL 记录 FAQ 与课程的关联关系
5. WHEN 学生问题与 FAQ 高度匹配 THEN THE QA System SHALL 优先返回 FAQ 中的标准答案

### Requirement 7

**User Story:** 作为系统，我需要记录问答历史，以便持续优化问答效果。

#### Acceptance Criteria

1. WHEN 学生提交问题 THEN THE QA System SHALL 记录问题内容、提问时间和提问者信息
2. WHEN 系统返回答案 THEN THE QA System SHALL 记录答案内容、来源和置信度分数
3. WHEN 学生对答案进行评价 THEN THE QA System SHALL 记录评价结果（有帮助/无帮助）
4. WHEN 学生标记答案无帮助 THEN THE QA System SHALL 允许学生提供反馈说明
5. WHEN 教师查看问答历史 THEN THE QA System SHALL 显示问题、答案、评价和反馈信息

### Requirement 8

**User Story:** 作为系统管理员，我想要监控问答系统的性能，以便评估和改进系统效果。

#### Acceptance Criteria

1. WHEN 管理员查看统计数据 THEN THE QA System SHALL 显示总提问次数、回答成功率和平均置信度
2. WHEN 管理员查看高频问题 THEN THE QA System SHALL 显示提问次数最多的前 20 个问题
3. WHEN 管理员查看低评价问题 THEN THE QA System SHALL 显示被标记为无帮助的问题列表
4. WHEN 管理员导出问答数据 THEN THE QA System SHALL 生成包含问题、答案和评价的 Excel 文件
5. WHEN 系统检测到高频低评价问题 THEN THE QA System SHALL 向管理员发送优化建议通知

### Requirement 9

**User Story:** 作为系统，我需要构建和维护资料内容索引，以便快速检索资料内容。

#### Acceptance Criteria

1. WHEN 新资料上传到系统 THEN THE QA System SHALL 自动提取资料文本内容并建立索引
2. WHEN 资料内容更新 THEN THE QA System SHALL 更新对应的内容索引
3. WHEN 资料被删除 THEN THE QA System SHALL 从索引中移除对应的内容
4. WHEN 索引资料内容 THEN THE QA System SHALL 分段存储内容并记录段落位置信息
5. WHEN 检索资料内容 THEN THE QA System SHALL 返回匹配段落及其上下文

### Requirement 10

**User Story:** 作为学生，我想要在对话中追问相关问题，以便深入了解某个主题。

#### Acceptance Criteria

1. WHEN 学生在同一会话中继续提问 THEN THE QA System SHALL 保持对话上下文
2. WHEN 学生使用代词或省略主语 THEN THE QA System SHALL 根据上下文理解问题指代
3. WHEN 学生追问细节 THEN THE QA System SHALL 在前一个答案的基础上提供更详细信息
4. WHEN 会话超过 30 分钟无活动 THEN THE QA System SHALL 清除对话上下文
5. WHEN 学生开始新话题 THEN THE QA System SHALL 识别话题转换并更新上下文
