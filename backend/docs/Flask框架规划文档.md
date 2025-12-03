# Flask 后端框架规划文档

> **项目名称**: EduInsight Backend API  
> **框架版本**: Flask 3.0.0 + Flask-OpenAPI3 3.1.0  
> **文档版本**: v1.0  
> **更新日期**: 2024-12

---

## 📋 目录

- [1. 项目概述](#1-项目概述)
- [2. 技术栈](#2-技术栈)
- [3. 项目结构](#3-项目结构)
- [4. 核心配置](#4-核心配置)
- [5. 开发规范](#5-开发规范)
- [6. API 开发指南](#6-api-开发指南)
- [7. 数据模型规范](#7-数据模型规范)
- [8. 认证授权](#8-认证授权)
- [9. 错误处理](#9-错误处理)
- [10. 部署指南](#10-部署指南)

---

## 1. 项目概述

### 1.1 架构设计

本项目采用 **Flask-OpenAPI3** 框架,实现了:

- ✅ RESTful API 设计规范
- ✅ 自动生成 OpenAPI 3.0 文档 (Swagger/ReDoc)
- ✅ Pydantic 数据验证
- ✅ JWT 身份认证
- ✅ 类装饰器模式开发
- ✅ 驼峰命名自动转换

### 1.2 设计原则

- **关注点分离**: API层、Service层、Model层职责清晰
- **可扩展性**: 模块化设计,易于添加新功能
- **类型安全**: 使用 Pydantic 进行严格的类型检查
- **文档优先**: 代码即文档,自动生成 API 文档
- **前后端分离**: 统一的 JSON API 接口

---

## 2. 技术栈

### 2.1 核心依赖

```txt
flask-openapi3==3.1.0          # OpenAPI 3.0 支持
Flask==3.0.0                   # Web 框架
Flask-SQLAlchemy==3.1.1        # ORM
pydantic==2.4.2                # 数据验证
Flask-JWT-Extended==4.6.0      # JWT 认证
Flask-CORS==4.0.0              # 跨域支持
email-validator==2.3.0         # 邮箱验证
python-dotenv==1.0.0           # 环境变量管理
gunicorn==21.2.0               # 生产服务器
```

### 2.2 开发依赖

```txt
pytest==7.4.3                  # 测试框架
pytest-cov==4.1.0              # 测试覆盖率
black==23.11.0                 # 代码格式化
flake8==6.1.0                  # 代码检查
```

---

## 3. 项目结构

```
backend/
├── app/
│   ├── __init__.py              # 应用工厂
│   ├── config.py                # 配置管理
│   ├── extensions.py            # 扩展初始化
│   │
│   ├── api/                     # API 层 (控制器)
│   │   ├── __init__.py
│   │   ├── auth_api.py          # 认证接口
│   │   ├── user_api.py          # 用户接口
│   │   ├── product_api.py       # 产品接口
│   │   └── order_api.py         # 订单接口
│   │
│   ├── services/                # 业务逻辑层
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── product_service.py
│   │   └── order_service.py
│   │
│   ├── models/                  # 数据库模型 (SQLAlchemy)
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── product.py
│   │   └── order.py
│   │
│   ├── model/                   # API 模型 (Pydantic)
│   │   ├── __init__.py
│   │   ├── base_model.py        # 驼峰命名基类 ⭐
│   │   ├── common_model.py      # 通用响应模型
│   │   ├── auth_model.py
│   │   ├── user_model.py
│   │   ├── product_model.py
│   │   └── order_model.py
│   │
│   ├── utils/                   # 工具函数
│   │   ├── __init__.py
│   │   ├── validators.py        # 自定义验证器
│   │   └── helpers.py           # 辅助函数
│   │
│   └── exceptions/              # 异常处理
│       ├── __init__.py
│       ├── custom_exceptions.py
│       └── handlers.py
│
├── tests/                       # 测试目录
│   ├── __init__.py
│   ├── conftest.py
│   └── test_*.py
│
├── docs/                        # 文档目录
│   └── Flask框架规划文档.md
│
├── .env.example                 # 环境变量示例
├── .gitignore
├── requirements.txt             # 生产依赖
├── requirements-dev.txt         # 开发依赖
├── run.py                       # 开发服务器入口
└── README.md
```

---

## 4. 核心配置

### 4.1 应用工厂模式

**文件**: `app/__init__.py`

```python
from flask_openapi3 import OpenAPI, Info, SecurityScheme
from app.config import config
from app.extensions import init_extensions

def create_app(config_name='development'):
    """应用工厂函数"""
    # 定义JWT安全方案
    jwt_scheme = SecurityScheme(
        type="http",
        scheme="bearer",
        bearerFormat="JWT",
        description="JWT认证令牌"
    )
    
    # OpenAPI 信息配置
    info = Info(
        title="Flask Backend API", 
        version="1.0.0", 
        description="基于Flask-OpenAPI3的现代化RESTful API"
    )
    
    # 创建 OpenAPI 应用
    app = OpenAPI(
        __name__, 
        info=info,
        security_schemes={"bearerAuth": jwt_scheme}
    )
    
    # 加载配置
    app.config.from_object(config[config_name])
    
    # ⭐ 配置JSON输出,禁用ASCII转义以正确显示中文
    app.config['JSON_AS_ASCII'] = False
    app.json.ensure_ascii = False
    
    # 初始化扩展
    init_extensions(app)
    
    # 注册API蓝图
    register_apis(app)
    
    # 注册错误处理器
    register_error_handlers(app)
    
    return app
```

### 4.2 配置管理

**文件**: `app/config.py`

```python
import os
from datetime import timedelta

class Config:
    """基础配置"""
    # 应用配置
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'dev-secret-key'
    
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
    
    # JWT配置
    JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY') or 'jwt-secret'
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
    
    # CORS配置
    CORS_ORIGINS = ['http://localhost:3000', 'http://localhost:5173']
    
    # JSON配置 - 支持中文显示
    JSON_AS_ASCII = False
    JSONIFY_PRETTYPRINT_REGULAR = True

class DevelopmentConfig(Config):
    """开发环境配置"""
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///app-dev.db'

class ProductionConfig(Config):
    """生产环境配置"""
    DEBUG = False

config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'default': DevelopmentConfig
}
```

### 4.3 扩展初始化

**文件**: `app/extensions.py`

```python
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from flask_jwt_extended import JWTManager

# 初始化扩展
db = SQLAlchemy()
cors = CORS()
jwt = JWTManager()

def init_extensions(app):
    """初始化所有扩展"""
    db.init_app(app)
    cors.init_app(app, 
                  supports_credentials=True, 
                  origins=app.config['CORS_ORIGINS'])
    jwt.init_app(app)
```

### 4.4 环境变量配置

**文件**: `.env.example`

```bash
# 应用配置
FLASK_ENV=development
SECRET_KEY=your-secret-key-here
JWT_SECRET_KEY=your-jwt-secret-here

# 数据库配置
DATABASE_URL=sqlite:///app.db
DEV_DATABASE_URL=sqlite:///app-dev.db

# 服务器配置
PORT=5000
DEBUG=True

# CORS配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

---

## 5. 开发规范

### 5.1 Python 代码规范

遵循 **PEP 8** 标准:

#### 命名规范

```python
# ✅ 类名: 大驼峰 (CapWords)
class UserService:
    pass

# ✅ 函数/变量: 小写+下划线 (snake_case)
def get_user_by_id(user_id: int):
    user_name = "张三"
    return user_name

# ✅ 常量: 全大写+下划线
MAX_PAGE_SIZE = 100
DEFAULT_TIMEOUT = 30

# ✅ 私有成员: 前缀单下划线
class User:
    def __init__(self):
        self._password = None  # 私有属性
```

#### 代码格式

```python
# ✅ 缩进: 4个空格
def example():
    if condition:
        do_something()

# ✅ 导入顺序: 标准库 -> 第三方库 -> 本地模块
import os
import sys

from flask import Flask
from pydantic import BaseModel

from app.models import User
from app.services import UserService

# ✅ 每行最多 88 字符 (Black 标准)
```

### 5.2 Git 提交规范

```bash
# 格式: <type>(<scope>): <subject>

feat(user): 添加用户列表分页功能
fix(auth): 修复JWT令牌过期问题
docs(api): 更新API文档
refactor(service): 重构用户服务层
test(user): 添加用户创建测试用例
chore(deps): 更新依赖包版本
```

### 5.3 文档注释规范

```python
def create_user(user_data: dict) -> User:
    """
    创建新用户
    
    Args:
        user_data: 用户数据字典,包含 name, email, password
        
    Returns:
        User: 创建的用户对象
        
    Raises:
        ValueError: 当邮箱已存在时
        DatabaseError: 数据库操作失败时
        
    Example:
        >>> user = create_user({"name": "张三", "email": "test@example.com"})
        >>> print(user.id)
        1
    """
    pass
```

---

## 6. API 开发指南

### 6.1 使用类装饰器模式 (推荐)

**文件**: `app/api/user_api.py`

```python
from flask_openapi3 import APIBlueprint, Tag
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.model.user_model import UserCreateModel, UserResponseModel
from app.services.user_service import UserService

# 创建 API 蓝图
user_api_bp = APIBlueprint('user_api', __name__, url_prefix='/api/v1/users')
user_tag = Tag(name="UserController", description="用户管理API")

class UserAPI:
    """用户API类 - 采用类装饰器模式"""
    
    @staticmethod
    @user_api_bp.get('/', summary="获取用户列表", tags=[user_tag])
    def list_users():
        """获取用户列表 - 公开接口"""
        users = UserService.get_all_users()
        return {'users': users, 'total': len(users)}
    
    @staticmethod
    @user_api_bp.post(
        '/', 
        summary="创建新用户", 
        tags=[user_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def create_user(body: UserCreateModel):
        """创建新用户 - 需要JWT认证"""
        current_user_id = get_jwt_identity()
        user = UserService.create_user(body)
        return {
            'message': 'User created successfully',
            'user': UserResponseModel.model_validate(user).model_dump(),
            'created_by': current_user_id
        }, 201
    
    @staticmethod
    @user_api_bp.get('/<int:user_id>', summary="获取指定用户", tags=[user_tag])
    def get_user(path: UserPathModel):
        """获取指定用户信息"""
        user = UserService.get_user_by_id(path.user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return UserResponseModel.model_validate(user).model_dump()
```

### 6.2 注册 API 蓝图

**文件**: `app/api/__init__.py`

```python
from app.api.auth_api import auth_api_bp
from app.api.user_api import user_api_bp
from app.api.product_api import product_api_bp
from app.api.order_api import order_api_bp

# 导出所有API蓝图
api_blueprints = [
    auth_api_bp,
    user_api_bp,
    product_api_bp,
    order_api_bp
]
```

### 6.3 RESTful API 设计规范

| HTTP方法 | 路径 | 说明 | 示例 |
|---------|------|------|------|
| GET | `/api/v1/users` | 获取列表 | 获取所有用户 |
| GET | `/api/v1/users/{id}` | 获取单个 | 获取ID为1的用户 |
| POST | `/api/v1/users` | 创建资源 | 创建新用户 |
| PUT | `/api/v1/users/{id}` | 完整更新 | 更新用户全部信息 |
| PATCH | `/api/v1/users/{id}` | 部分更新 | 更新用户部分信息 |
| DELETE | `/api/v1/users/{id}` | 删除资源 | 删除用户 |

---

## 7. 数据模型规范

### 7.1 驼峰命名基类 ⭐

**文件**: `app/model/base_model.py`

```python
"""
Pydantic基础模型
提供驼峰命名转换功能
"""
from pydantic import BaseModel, ConfigDict
from pydantic.alias_generators import to_camel

class CamelCaseModel(BaseModel):
    """
    驼峰命名基类
    
    所有继承此类的模型会自动将Python下划线命名转换为驼峰式命名
    用于OpenAPI文档和JSON序列化
    
    示例:
        user_name -> userName
        created_at -> createdAt
        is_active -> isActive
    """
    model_config = ConfigDict(
        # 自动将字段名转换为驼峰命名
        alias_generator=to_camel,
        # 允许使用原字段名或别名进行赋值
        populate_by_name=True,
        # 支持从ORM对象创建(如SQLAlchemy模型)
        from_attributes=True
    )
```

### 7.2 API 模型定义

**文件**: `app/model/user_model.py`

```python
from pydantic import EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime
from app.model.base_model import CamelCaseModel

class UserCreateModel(CamelCaseModel):
    """用户创建模型"""
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名")
    email: EmailStr = Field(..., description="用户邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    password: str = Field(..., min_length=6, description="密码")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号码只能包含数字')
        return v

class UserResponseModel(CamelCaseModel):
    """用户响应模型"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # ⭐ 继承 CamelCaseModel 后,JSON输出自动转为驼峰:
    # isActive, createdAt, updatedAt

class UserPathModel(CamelCaseModel):
    """用户路径参数模型"""
    user_id: int = Field(..., description="用户ID")
```

### 7.3 通用响应模型

**文件**: `app/model/common_model.py`

```python
from pydantic import BaseModel
from typing import Optional, Any
from datetime import datetime
from app.model.base_model import CamelCaseModel

class BaseResponseModel(CamelCaseModel):
    """基础响应模型"""
    message: str
    success: bool = True
    timestamp: datetime = datetime.utcnow()

class ErrorResponseModel(CamelCaseModel):
    """错误响应模型"""
    message: str
    error_code: Optional[str] = None
    details: Optional[Any] = None
    success: bool = False
    timestamp: datetime = datetime.utcnow()

class SuccessResponseModel(CamelCaseModel):
    """成功响应模型"""
    message: str = "操作成功"
    data: Optional[Any] = None
    success: bool = True
    timestamp: datetime = datetime.utcnow()

class PaginationModel(CamelCaseModel):
    """分页模型"""
    page: int = 1
    per_page: int = 10
    total: int
    pages: int
    has_prev: bool
    has_next: bool
```

### 7.4 数据库模型 (SQLAlchemy)

**文件**: `app/models/user.py`

```python
from app.extensions import db
from datetime import datetime

class User(db.Model):
    """用户数据库模型"""
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20))
    age = db.Column(db.Integer)
    password_hash = db.Column(db.String(255), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<User {self.email}>'
```

---

## 8. 认证授权

### 8.1 JWT 认证配置

```python
# config.py
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')
JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=1)
JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=30)
```

### 8.2 登录接口

```python
from flask_jwt_extended import create_access_token, create_refresh_token

@auth_api_bp.post('/login', summary="用户登录", tags=[auth_tag])
def login(body: LoginModel):
    """用户登录"""
    user = UserService.authenticate(body.email, body.password)
    if not user:
        return {'message': '邮箱或密码错误'}, 401
    
    # 生成JWT令牌
    access_token = create_access_token(identity=user.id)
    refresh_token = create_refresh_token(identity=user.id)
    
    return TokenResponseModel(
        access_token=access_token,
        refresh_token=refresh_token,
        user=UserResponseModel.model_validate(user).model_dump()
    ).model_dump()
```

### 8.3 保护接口

```python
from flask_jwt_extended import jwt_required, get_jwt_identity

@user_api_bp.get(
    '/me', 
    summary="获取当前用户信息",
    security=[{"bearerAuth": []}]  # 🔒 OpenAPI文档中显示需要认证
)
@jwt_required()  # 🔒 实际的JWT验证装饰器
def get_current_user():
    """获取当前登录用户信息"""
    current_user_id = get_jwt_identity()
    user = UserService.get_user_by_id(current_user_id)
    return UserResponseModel.model_validate(user).model_dump()
```

---

## 9. 错误处理

### 9.1 自定义异常

**文件**: `app/exceptions/custom_exceptions.py`

```python
class APIException(Exception):
    """API基础异常"""
    status_code = 500
    message = "Internal server error"
    
    def __init__(self, message=None, status_code=None):
        if message:
            self.message = message
        if status_code:
            self.status_code = status_code

class ValidationError(APIException):
    """数据验证错误"""
    status_code = 400
    message = "Validation error"

class NotFoundError(APIException):
    """资源不存在"""
    status_code = 404
    message = "Resource not found"

class UnauthorizedError(APIException):
    """未授权"""
    status_code = 401
    message = "Unauthorized"
```

### 9.2 全局错误处理器

**文件**: `app/exceptions/handlers.py`

```python
from flask import jsonify
from app.exceptions.custom_exceptions import APIException

def register_handlers(app):
    """注册错误处理器"""
    
    @app.errorhandler(APIException)
    def handle_api_exception(error):
        """处理自定义API异常"""
        response = {
            'success': False,
            'message': error.message,
            'error_code': error.__class__.__name__
        }
        return jsonify(response), error.status_code
    
    @app.errorhandler(404)
    def handle_not_found(error):
        """处理404错误"""
        return jsonify({
            'success': False,
            'message': 'Resource not found'
        }), 404
    
    @app.errorhandler(500)
    def handle_internal_error(error):
        """处理500错误"""
        return jsonify({
            'success': False,
            'message': 'Internal server error'
        }), 500
```

---

## 10. 部署指南

### 10.1 开发环境运行

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 3. 初始化数据库
flask db init
flask db migrate -m "Initial migration"
flask db upgrade

# 4. 运行开发服务器
python run.py
```

### 10.2 生产环境部署 (Gunicorn)

```bash
# 1. 安装生产依赖
pip install -r requirements.txt

# 2. 使用 Gunicorn 运行
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app('production')"

# 参数说明:
# -w 4: 4个工作进程
# -b 0.0.0.0:5000: 绑定地址和端口
# --timeout 120: 请求超时时间
# --access-logfile -: 访问日志输出到标准输出
```

### 10.3 Docker 部署

**Dockerfile**:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:create_app('production')"]
```

**docker-compose.yml**:

```yaml
version: '3.8'

services:
  backend:
    build: .
    ports:
      - "5000:5000"
    environment:
      - FLASK_ENV=production
      - DATABASE_URL=postgresql://user:pass@db:5432/dbname
    depends_on:
      - db
  
  db:
    image: postgres:15
    environment:
      - POSTGRES_USER=user
      - POSTGRES_PASSWORD=pass
      - POSTGRES_DB=dbname
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

---

## 📌 附录

### A. 常用命令

```bash
# 代码格式化
black app/

# 代码检查
flake8 app/

# 运行测试
pytest

# 测试覆盖率
pytest --cov=app tests/

# 生成依赖文件
pip freeze > requirements.txt

# 数据库迁移
flask db migrate -m "描述"
flask db upgrade
```

### B. API 文档访问

- **Swagger UI**: `http://localhost:5000/openapi/swagger`
- **ReDoc**: `http://localhost:5000/openapi/redoc`
- **OpenAPI JSON**: `http://localhost:5000/openapi/openapi.json`

### C. 项目检查清单

开发新功能时的检查清单:

- [ ] 创建 Pydantic 模型 (继承 `CamelCaseModel`)
- [ ] 创建 SQLAlchemy 模型 (如需要)
- [ ] 实现 Service 层业务逻辑
- [ ] 创建 API 接口 (类装饰器模式)
- [ ] 添加 API 文档注释
- [ ] 编写单元测试
- [ ] 更新 API 文档
- [ ] 代码格式化和检查

### D. 常见问题

**Q: OpenAPI 文档中中文显示为 Unicode 转义?**  
A: 在 `create_app()` 中添加 `app.json.ensure_ascii = False`

**Q: 如何实现驼峰命名转换?**  
A: 所有 Pydantic 模型继承 `CamelCaseModel` 基类

**Q: JWT 令牌如何传递?**  
A: 在请求头中添加 `Authorization: Bearer <token>`

**Q: 如何处理跨域问题?**  
A: 已配置 Flask-CORS,在 `config.py` 中设置 `CORS_ORIGINS`

---

## 📝 更新日志

- **v1.0** (2024-12): 初始版本,包含完整的框架规划和开发规范

---

**文档维护**: 开发团队  
**联系方式**: dev@example.com
