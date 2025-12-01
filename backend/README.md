# Flask-OpenAPI3 后端项目

基于 Flask-OpenAPI3 的现代化 RESTful API 项目，采用分层架构设计，支持自动API文档生成、数据验证和JWT认证。

## 🚀 功能特性

- **现代化架构**: 采用分层架构设计，代码结构清晰
- **自动文档生成**: 基于 OpenAPI 3.0 规范，自动生成 Swagger UI 和 ReDoc 文档
- **数据验证**: 使用 Pydantic 进行请求/响应数据验证
- **JWT认证**: 完整的用户认证和授权系统
- **CORS支持**: 跨域资源共享配置
- **异常处理**: 统一的异常处理机制
- **代码规范**: 遵循 PEP 8 代码规范

## 📁 项目结构

```
backend/
├── app/
│   ├── __init__.py              # 应用工厂函数
│   ├── config.py                # 配置文件
│   ├── extensions.py            # 扩展初始化
│   ├── api/                     # API接口层
│   │   ├── auth_api.py          # 认证API
│   │   ├── user_api.py          # 用户API
│   │   ├── product_api.py       # 产品API
│   │   └── order_api.py         # 订单API
│   ├── models/                  # 数据库模型层
│   │   ├── base.py              # 基础模型类
│   │   ├── user.py              # 用户模型
│   │   ├── product.py           # 产品模型
│   │   └── order.py             # 订单模型
│   ├── model/                   # Pydantic数据模型
│   │   ├── user_model.py        # 用户数据模型
│   │   ├── product_model.py     # 产品数据模型
│   │   ├── order_model.py       # 订单数据模型
│   │   ├── auth_model.py        # 认证数据模型
│   │   └── common_model.py      # 通用数据模型
│   ├── services/                # 业务逻辑层
│   │   ├── user_service.py      # 用户业务逻辑
│   │   ├── product_service.py   # 产品业务逻辑
│   │   ├── order_service.py     # 订单业务逻辑
│   │   └── auth_service.py      # 认证业务逻辑
│   ├── utils/                   # 工具函数
│   │   ├── validators.py        # 验证器
│   │   ├── helpers.py           # 辅助函数
│   │   └── decorators.py        # 装饰器
│   └── exceptions/              # 异常处理
│       ├── base.py              # 基础异常
│       └── handlers.py          # 异常处理器
├── tests/                       # 测试文件
├── requirements.txt             # 依赖包
├── requirements-dev.txt         # 开发依赖
├── .env.example                 # 环境变量示例
├── .gitignore                   # Git忽略文件
├── run.py                       # 启动文件
└── README.md                    # 项目说明
```

## 🛠️ 安装和运行

### 1. 环境准备

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
# Windows
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate

# 安装依赖
pip install -r requirements.txt
pip install -r requirements-dev.txt
```

### 2. 环境配置

```bash
# 复制环境变量文件
copy .env.example .env

# 编辑 .env 文件，设置必要的配置项
```

### 3. 数据库初始化

```python
# 在Python控制台中执行
from app import create_app
from app.extensions import db

app = create_app()
with app.app_context():
    db.create_all()
```

### 4. 启动项目

```bash
# 开发模式
python run.py

# 或使用Flask命令
flask run
```

## 📚 API文档

项目启动后，可以访问以下地址查看API文档：

- **Swagger UI**: http://localhost:5000/openapi/swagger
- **ReDoc**: http://localhost:5000/openapi/redoc
- **OpenAPI JSON**: http://localhost:5000/openapi/openapi.json

## 🔐 认证说明

项目使用JWT进行用户认证：

1. **注册**: `POST /api/v1/auth/register`
2. **登录**: `POST /api/v1/auth/login`
3. **获取用户信息**: `GET /api/v1/auth/profile` (需要认证)
4. **刷新令牌**: `POST /api/v1/auth/refresh` (需要认证)

需要认证的接口在请求头中添加：
```
Authorization: Bearer <access_token>
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_api/

# 生成覆盖率报告
pytest --cov=app --cov-report=html
```

## 📝 开发规范

- 遵循 PEP 8 代码规范
- 使用类型注解
- 编写单元测试
- 提交前运行代码检查工具

## 🚀 部署

### Docker部署

```bash
# 构建镜像
docker build -t flask-backend .

# 运行容器
docker run -p 5000:5000 flask-backend
```

### 生产环境

```bash
# 使用Gunicorn
gunicorn --bind 0.0.0.0:5000 run:app
```

## 📄 许可证

MIT License
