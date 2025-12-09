# Implementation Plan

## 自动化资料归类功能实现任务

- [x] 1. 项目依赖和基础设施

  - [x] 1.1 添加新依赖到 requirements.txt

    - 添加 PyPDF2、python-docx、hypothesis 依赖
    - _需求: 1.1, 1.2, 测试策略_

  - [x] 1.2 创建智能模块目录结构

    - 创建 `backend/app/intelligence/` 目录
    - 创建 `__init__.py`、停用词文件等基础文件
    - _需求: 2.1, 2.5_

- [x] 2. 文档解析器实现

  - [x] 2.1 实现 DocumentParser 基础类和 ParseResult 数据类

    - 创建 `backend/app/intelligence/document_parser.py`
    - 实现 ParseResult 数据类，包含序列化/反序列化方法
    - _需求: 1.4, 1.5, 8.1, 8.2, 8.3_

  - [x] 2.2 编写属性测试：解析结果序列化往返一致性

    - **属性 2: 解析结果序列化往返一致性**
    - **验证需求: 8.1, 8.2, 8.3**

  - [x] 2.3 实现 PDF 解析功能

    - 使用 PyPDF2 提取 PDF 文本内容
    - _需求: 1.1_

  - [x] 2.4 实现 Word 文档解析功能

    - 使用 python-docx 提取 Word 文档内容
    - _需求: 1.2_

  - [x] 2.5 实现文本文件解析功能

    - 支持多种编码格式
    - _需求: 1.3_

  - [x] 2.6 编写属性测试：文档解析往返一致性

    - **属性 1: 文档解析往返一致性**
    - **验证需求: 1.1, 1.2, 1.3**

- [x] 3. 检查点 - 确保所有测试通过

  - 确保所有测试通过，如有问题请询问用户。

- [x] 4. 关键词提取器实现

  - [x] 4.1 实现 KeywordExtractor 类

    - 创建 `backend/app/intelligence/keyword_extractor.py`
    - 实现 Jieba 分词和 TF-IDF 关键词提取
    - 实现停用词过滤
    - _需求: 2.1, 2.2, 2.3, 2.4, 2.5_

  - [x] 4.2 编写属性测试：关键词权重有效性

    - **属性 3: 关键词提取产生有效权重**
    - **验证需求: 2.2**

  - [x] 4.3 编写属性测试：关键词数量限制

    - **属性 4: 关键词数量遵守限制**
    - **验证需求: 2.3**

  - [x] 4.4 编写属性测试：关键词排除停用词

    - **属性 5: 关键词排除停用词和单字**
    - **验证需求: 2.5**

- [x] 5. 检查点 - 确保所有测试通过

  - 确保所有测试通过，如有问题请询问用户。

- [x] 6. 分类器实现

  - [x] 6.1 实现 CategoryClassifier 类

    - 创建 `backend/app/intelligence/category_classifier.py`
    - 实现基于 Naive Bayes 的分类预测
    - 实现模型训练、保存和加载功能
    - _需求: 3.1, 3.2, 5.1, 5.2, 5.3, 5.4_

  - [x] 6.2 编写属性测试：分类置信度范围

    - **属性 6: 分类置信度在有效范围内**
    - **验证需求: 3.2**

  - [x] 6.3 实现置信度阈值逻辑

    - 高置信度 (>0.7) 自动应用
    - 中等置信度 (0.5-0.7) 需要确认
    - 低置信度 (<0.5) 不建议
    - _需求: 3.3, 3.4, 3.5_

  - [x] 6.4 编写属性测试：置信度阈值行为

    - **属性 7: 高置信度触发自动应用**
    - **属性 8: 中等置信度需要确认**
    - **属性 9: 低置信度不产生建议**
    - **验证需求: 3.3, 3.4, 3.5**

- [x] 7. 检查点 - 确保所有测试通过

  - 确保所有测试通过，如有问题请询问用户。

- [x] 8. 标签推荐器实现

  - [x] 8.1 实现 TagRecommender 类

    - 创建 `backend/app/intelligence/tag_recommender.py`

    - 实现基于关键词的标签匹配和推荐

    - _需求: 4.1, 4.2, 4.3, 4.4_

  - [x] 8.2 编写属性测试：标签数量限制

    - **属性 10: 标签建议遵守最大数量限制**
    - **验证需求: 4.4**

- [x] 9. 服务层实现

  - [x] 9.1 实现 ClassificationService 类

    - 创建 `backend/app/services/classification_service.py`
    - 整合文档解析、关键词提取、分类和标签推荐
    - 实现 classify_material、extract_keywords、suggest_tags 方法

    - _需求: 2.6, 3.6, 4.5, 5.5_

  - [x] 9.2 实现分类日志管理

    - 实现 accept_classification 和 reject_classification 方法
    - 更新 ClassificationLog 记录
    - _需求: 3.6, 5.5_

- [x] 10. 检查点 - 确保所有测试通过

  - 确保所有测试通过，如有问题请询问用户。

- [x] 11. API 层实现

  - [x] 11.1 创建分类相关 Schema

    - 创建 `backend/app/schemas/classification_schemas.py`
    - 定义请求和响应模型
    - _需求: 6.1, 6.2, 6.3, 6.4, 6.5_

  - [x] 11.2 扩展 material_api.py 添加分类相关端点

    - POST /{materialId}/classify - 分析并分类资料
    - GET /{materialId}/keywords - 获取关键词
    - POST /{materialId}/suggest-tags - 获取标签建议
    - _需求: 6.1, 6.2, 6.3_

  - [x] 11.3 添加分类日志管理端点

    - POST /classification-logs/{logId}/accept - 接受分类建议
    - POST /classification-logs/{logId}/reject - 拒绝分类建议
    - _需求: 6.4, 6.5_

  - [x] 11.4 编写属性测试：API 错误响应格式

    - **属性 11: API 错误响应遵循标准格式**
    - **验证需求: 6.6**

- [x] 12. 检查点 - 确保所有测试通过

  - 确保所有测试通过，如有问题请询问用户。

- [x] 13. 前端集成

  - [x] 13.1 分类相关 API 封装
    - 在 `frontend/src/api/` 中有对应的 API
    - _需求: 7.1_
  - [x] 13.2 创建智能分类组件
    - 创建 ClassificationPanel.vue 组件
    - 显示分类建议、置信度和关键词
    - _需求: 7.2, 7.6_
  - [x] 13.3 创建标签推荐组件
    - 创建 TagSuggestions.vue 组件
    - 显示推荐标签为可点击的标签
    - _需求: 7.3_
  - [x] 13.4 集成到资料上传流程
    - 在上传完成后自动触发分类分析
    - 显示加载状态和分类结果
    - _需求: 7.1, 7.4, 7.5_
  - [x] 13.5 集成到资料详情页
    - 在详情页显示关键词和分类信息
    - _需求: 7.6_

- [x] 14. 最终检查点 - 确保所有测试通过

  - 确保所有测试通过，如有问题请询问用户。
