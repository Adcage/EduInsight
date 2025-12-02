# EduInsight 后端项目

基于 Flask-OpenAPI3 的现代化 RESTful API 项目，采用分层架构设计，支持自动API文档生成和数据验证。

## 🚀 功能特性

- **现代化架构**: 采用分层架构设计，代码结构清晰
- **自动文档生成**: 基于 OpenAPI 3.0 规范，自动生成 Swagger UI 和 ReDoc 文档
- **数据验证**: 使用 Pydantic 进行请求/响应数据验证
- **CORS支持**: 跨域资源共享配置
- **异常处理**: 统一的异常处理机制
- **数据库ORM**: 使用 Flask-SQLAlchemy 进行数据库操作
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

# 编辑 .env 文件，配置以下项：
# - SECRET_KEY: Flask应用密钥
# - DATABASE_URL: 数据库连接URL
# - CORS_ORIGINS: 允许的跨域来源
```

### 3. 数据库初始化

**推荐方式: 使用初始化脚本**

项目已包含 `init_db.py` 脚本,直接运行即可:

```bash
# 确保虚拟环境已激活,然后运行:
python init_db.py
```

运行后会显示:
- ✅ 数据库表创建成功的提示
- 📁 数据库文件位置
- 📊 已创建的数据表列表

---


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

## 🔌 API接口说明

### 认证接口
- **注册**: `POST /api/v1/auth/register`
- **登录**: `POST /api/v1/auth/login`
- **获取用户信息**: `GET /api/v1/auth/profile/<user_id>`

### 用户管理
- **获取用户列表**: `GET /api/v1/users/`
- **创建用户**: `POST /api/v1/users/`
- **获取指定用户**: `GET /api/v1/users/<user_id>`
- **更新用户**: `PUT /api/v1/users/<user_id>`
- **删除用户**: `DELETE /api/v1/users/<user_id>`

### 产品管理
- **获取产品列表**: `GET /api/v1/products/`
- **创建产品**: `POST /api/v1/products/`
- **获取指定产品**: `GET /api/v1/products/<product_id>`
- **更新产品**: `PUT /api/v1/products/<product_id>`
- **删除产品**: `DELETE /api/v1/products/<product_id>`
- **按分类获取**: `GET /api/v1/products/categories/<category>`

### 订单管理
- **获取订单列表**: `GET /api/v1/orders/`
- **创建订单**: `POST /api/v1/orders/`
- **获取指定订单**: `GET /api/v1/orders/<order_id>`
- **更新订单**: `PUT /api/v1/orders/<order_id>`
- **取消订单**: `DELETE /api/v1/orders/<order_id>/cancel`
- **订单统计**: `GET /api/v1/orders/statistics/<user_id>`

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
gunicorn --bind 0.0.0.0:5000 --workers 4 run:app
```

## ⚙️ 环境变量说明

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| FLASK_ENV | Flask运行环境 | development |
| SECRET_KEY | Flask应用密钥 | your-secret-key-here |
| DATABASE_URL | 生产数据库URL | sqlite:///app.db |
| DEV_DATABASE_URL | 开发数据库URL | sqlite:///app-dev.db |
| PORT | 服务器端口 | 5000 |
| DEBUG | 调试模式 | True |
| CORS_ORIGINS | 允许的跨域来源 | http://localhost:3000,http://localhost:5173 |

## 🗄️ 数据库模型

### User (用户)
- id: 主键
- username: 用户名
- email: 邮箱
- password_hash: 密码哈希
- created_at: 创建时间
- updated_at: 更新时间

### Product (产品)
- id: 主键
- name: 产品名称
- description: 产品描述
- price: 价格
- category: 分类
- stock: 库存
- created_at: 创建时间
- updated_at: 更新时间

### Order (订单)
- id: 主键
- user_id: 用户ID (外键)
- product_id: 产品ID (外键)
- quantity: 数量
- total_price: 总价
- status: 订单状态
- created_at: 创建时间
- updated_at: 更新时间

## 📄 许可证

MIT License
