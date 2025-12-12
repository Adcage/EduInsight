---
trigger: model_decision
description: 编写后端接口的时候必须遵守的规则
---

# Flask-OpenAPI 装饰器类方式开发规范

## 📋 概述

本文档定义了使用 Flask-OpenAPI3 装饰器类方式开发 RESTful API 的标准规范和最佳实践。

## 🏗️ 基础结构规范

### 1. 文件组织结构

```
app/
├── api/
│   ├── __init__.py
│   ├── user_api.py          # 用户相关API
│   ├── product_api.py       # 产品相关API
│   └── admin_api.py         # 管理员API
├── models/
│   ├── __init__.py
│   ├── user.py              # 用户数据库模型 (SQLAlchemy)
│   ├── product.py           # 产品数据库模型
│   └── base.py              # 基础模型类
├── schemas/
│   ├── __init__.py
│   ├── user_schemas.py      # 用户Pydantic模型
│   └── product_schemas.py   # 产品Pydantic模型
├── services/
│   ├── __init__.py
│   ├── user_service.py      # 用户业务逻辑
│   └── product_service.py   # 产品业务逻辑
├── migrations/              # 数据库迁移文件
│   ├── versions/
│   ├── alembic.ini
│   ├── env.py
│   └── script.py.mako
└── __init__.py
```

### 2. 基本文件模板

```python
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from typing import List, Optional
import time
import logging

# 1. 创建蓝图和标签
{resource}_api_bp = APIBlueprint('{resource}_api', __name__, url_prefix='/api/v1/{resource}')
{resource}_tag = Tag(name="{ResourceName}Controller", description="{资源描述}")

# 2. Pydantic 模型定义
class {Resource}Model(BaseModel):
    """完整的{资源}模型"""
    pass

class {Resource}CreateModel(BaseModel):
    """创建{资源}的请求模型"""
    pass

class {Resource}UpdateModel(BaseModel):
    """更新{资源}的请求模型"""
    pass

class {Resource}PathModel(BaseModel):
    """路径参数模型"""
    {resource}_id: int = Field(..., description="{资源}ID", ge=1)

# 3. 装饰器类定义
class {Resource}API:
    """
    {资源}API类 - 装饰器方式
    
    提供{资源}的完整CRUD操作
    """
    
    # 类属性：配置和共享状态
    cache_timeout = 300
    request_count = 0
    
    # 工具方法
    @classmethod
    def log_request(cls, action: str):
        cls.request_count += 1
        logging.info(f"[{cls.request_count}] {action}")
    
    # API端点定义
    @staticmethod
    @{resource}_api_bp.get('/', summary="获取{资源}列表", tags=[{resource}_tag])
    def list_{resource}s():
        pass
```

## 🗄️ 数据库迁移和ORM工具

### 1. 数据库迁移的作用

**数据库迁移 (Database Migration)** 是管理数据库结构变更的版本控制系统：

#### 主要作用：
- ✅ **版本控制**：跟踪数据库结构的每次变更
- ✅ **团队协作**：确保所有开发者的数据库结构一致
- ✅ **部署安全**：可控地在生产环境应用数据库变更
- ✅ **回滚能力**：出现问题时可以回退到之前的版本
- ✅ **自动化**：自动执行复杂的数据库结构变更

#### 实际场景：
```python
# 场景1：添加新字段
# 迁移前：users表只有 id, name, email
# 迁移后：users表有 id, name, email, phone, created_at

# 场景2：修改字段类型
# 迁移前：age字段是VARCHAR(10)
# 迁移后：age字段是INTEGER

# 场景3：添加索引
# 为email字段添加唯一索引，提高查询性能
```

### 2. ORM工具的作用

**ORM (Object-Relational Mapping)** 是对象关系映射工具：

#### 主要优势：
- ✅ **面向对象**：用Python类和对象操作数据库
- ✅ **数据库无关**：同一套代码支持多种数据库
- ✅ **SQL注入防护**：自动处理参数化查询
- ✅ **关系管理**：自动处理表之间的关联关系
- ✅ **懒加载**：按需加载关联数据，提高性能

### 3. Flask-SQLAlchemy 配置

#### 安装依赖
```bash
pip install Flask-SQLAlchemy Flask-Migrate
```

#### 基础配置
```python
# app/config.py
import os

class Config:
    # 数据库配置
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or \
        'sqlite:///app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # 迁移配置
    SQLALCHEMY_MIGRATE_REPO = os.path.join(basedir, 'migrations')

# app/__init__.py
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()

def create_app(config_name='development'):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    
    # 初始化扩展
    db.init_app(app)
    migrate.init_app(app, db)
    
    return app
```

### 4. 数据库模型定义

#### 基础模型类

**⚠️ 重要：to_dict() 方法必须自动转换 datetime**

```python
# app/models/base.py
from datetime import datetime
from app import db

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True
    
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """
        转换为字典
        
        ⚠️ 重要：自动将 datetime 对象转换为字符串格式
        这样可以避免在每个 API 中手动转换 datetime
        """
        result = {}
        for c in self.__table__.columns:
            value = getattr(self, c.name)
            # 自动转换 datetime 为字符串
            if isinstance(value, datetime):
                result[c.name] = value.strftime('%a, %d %b %Y %H:%M:%S GMT')
            else:
                result[c.name] = value
        return result
    
    def save(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()
```

**为什么要在 to_dict() 中转换 datetime？**

1. **Pydantic 验证要求**：Pydantic Schema 中定义的 `created_at: str`，但数据库返回的是 `datetime` 对象
2. **避免重复代码**：不需要在每个 API 中手动转换
3. **统一格式**：所有 datetime 都使用相同的格式
4. **一次修改，全局生效**：所有继承 `BaseModel` 的模型都自动获得此功能

**错误示例（不要这样做）：**
```python
# ❌ 错误：每个 API 都要手动转换
material_data = material.to_dict()
if material_data.get('created_at'):
    material_data['created_at'] = material_data['created_at'].strftime(...)
if material_data.get('updated_at'):
    material_data['updated_at'] = material_data['updated_at'].strftime(...)
```

**正确示例：**
```python
# ✅ 正确：to_dict() 自动转换
material_data = material.to_dict()  # datetime 已经是字符串了
response_model = MaterialResponseModel(**material_data)  # 直接使用
```

#### 用户模型
```python
# app/models/user.py
from app.models.base import BaseModel
from app import db

class User(BaseModel):
    """用户模型"""
    __tablename__ = 'users'
    
    name = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    age = db.Column(db.Integer, nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    
    # 关联关系
    orders = db.relationship('Order', backref='user', lazy='dynamic', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.email}>'
    
    @classmethod
    def find_by_email(cls, email):
        """根据邮箱查找用户"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_active_users(cls):
        """获取活跃用户"""
        return cls.query.filter_by(is_active=True).all()
```

#### 订单模型
```python
# app/models/order.py
from app.models.base import BaseModel
from app import db

class Order(BaseModel):
    """订单模型"""
    __tablename__ = 'orders'
    
    order_number = db.Column(db.String(50), unique=True, nullable=False, index=True)
    total_amount = db.Column(db.Decimal(10, 2), nullable=False)
    status = db.Column(db.String(20), default='pending', nullable=False)
    
    # 外键
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    
    def __repr__(self):
        return f'<Order {self.order_number}>'
```

### 5. 数据库迁移操作

#### 初始化迁移
```bash
# 初始化迁移环境
flask db init

# 创建第一个迁移
flask db migrate -m "Initial migration"

# 应用迁移
flask db upgrade
```

#### 常用迁移命令
```bash
# 创建新迁移
flask db migrate -m "Add phone field to users"

# 查看迁移历史
flask db history

# 应用迁移到最新版本
flask db upgrade

# 回退到指定版本
flask db downgrade <revision_id>

# 查看当前版本
flask db current

# 查看SQL语句（不执行）
flask db upgrade --sql
```

#### 迁移文件示例
```python
# migrations/versions/001_add_phone_field.py
"""Add phone field to users

Revision ID: abc123
Revises: def456
Create Date: 2024-01-01 10:00:00.000000
"""

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision = 'abc123'
down_revision = 'def456'
branch_labels = None
depends_on = None

def upgrade():
    # 添加phone字段
    op.add_column('users', sa.Column('phone', sa.String(20), nullable=True))
    
    # 添加索引
    op.create_index('ix_users_phone', 'users', ['phone'])

def downgrade():
    # 删除索引
    op.drop_index('ix_users_phone', 'users')
    
    # 删除字段
    op.drop_column('users', 'phone')
```

### 6. 服务层集成

#### 用户服务
```python
# app/services/user_service.py
from typing import List, Optional
from app.models.user import User
from app.schemas.user_schemas import UserCreateModel, UserUpdateModel
from app import db

class UserService:
    """用户服务层"""
    
    @staticmethod
    def create_user(user_data: UserCreateModel) -> User:
        """创建用户"""
        # 检查邮箱是否已存在
        if User.find_by_email(user_data.email):
            raise ValueError("Email already exists")
        
        user = User(
            name=user_data.name,
            email=user_data.email,
            phone=user_data.phone,
            age=user_data.age
        )
        return user.save()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.get(user_id)
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdateModel) -> Optional[User]:
        """更新用户"""
        user = User.query.get(user_id)
        if not user:
            return None
        
        # 更新字段
        for field, value in user_data.dict(exclude_unset=True).items():
            setattr(user, field, value)
        
        return user.save()
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """删除用户"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        user.delete()
        return True
    
    @staticmethod
    def get_users_paginated(page: int = 1, per_page: int = 20) -> dict:
        """分页获取用户"""
        pagination = User.query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return {
            'users': [user.to_dict() for user in pagination.items],
            'total': pagination.total,
            'page': page,
            'per_page': per_page,
            'pages': pagination.pages
        }
```

### 7. API层集成ORM

#### 更新的用户API
```python
# app/api/user_api.py
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.user_schemas import UserCreateModel, UserUpdateModel, UserPathModel
from app.services.user_service import UserService

user_api_bp = APIBlueprint('user_api', __name__, url_prefix='/api/v1/users')
user_tag = Tag(name="UserController", description="用户管理API")

class UserAPI:
    """用户API类 - 集成ORM"""
    
    @staticmethod
    @user_api_bp.post('/', summary="创建新用户", tags=[user_tag])
    def create_user(body: UserCreateModel):
        """创建新用户"""
        try:
            user = UserService.create_user(body)
            return {
                'message': 'User created successfully',
                'user': user.to_dict()
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @user_api_bp.get('/<int:user_id>', summary="获取指定用户", tags=[user_tag])
    def get_user(path: UserPathModel):
        """获取指定用户"""
        user = UserService.get_user_by_id(path.user_id)
        if not user:
            return {'message': 'User not found'}, 404
        
        return user.to_dict()
    
    @staticmethod
    @user_api_bp.put('/<int:user_id>', summary="更新用户信息", tags=[user_tag])
    def update_user(path: UserPathModel, body: UserUpdateModel):
        """更新用户信息"""
        user = UserService.update_user(path.user_id, body)
        if not user:
            return {'message': 'User not found'}, 404
        
        return {
            'message': 'User updated successfully',
            'user': user.to_dict()
        }
    
    @staticmethod
    @user_api_bp.delete('/<int:user_id>', summary="删除用户", tags=[user_tag])
    def delete_user(path: UserPathModel):
        """删除用户"""
        if not UserService.delete_user(path.user_id):
            return {'message': 'User not found'}, 404
        
        return {'message': 'User deleted successfully'}, 204
```

### 8. 数据库最佳实践

#### 连接池配置
```python
# app/config.py
class Config:
    # 连接池配置
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_size': 10,
        'pool_recycle': 120,
        'pool_pre_ping': True,
        'max_overflow': 20
    }
```

#### 查询优化
```python
# 使用索引
class User(BaseModel):
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    
# 预加载关联数据
users_with_orders = User.query.options(db.joinedload(User.orders)).all()

# 分页查询
pagination = User.query.paginate(page=1, per_page=20)

# 原生SQL查询（复杂查询）
result = db.session.execute(
    "SELECT u.name, COUNT(o.id) as order_count "
    "FROM users u LEFT JOIN orders o ON u.id = o.user_id "
    "GROUP BY u.id"
)
```

#### 事务管理
```python
from app import db

def transfer_money(from_user_id: int, to_user_id: int, amount: float):
    """转账操作 - 事务示例"""
    try:
        # 开始事务
        from_user = User.query.get(from_user_id)
        to_user = User.query.get(to_user_id)
        
        if from_user.balance < amount:
            raise ValueError("Insufficient balance")
        
        from_user.balance -= amount
        to_user.balance += amount
        
        # 提交事务
        db.session.commit()
        
    except Exception as e:
        # 回滚事务
        db.session.rollback()
        raise e
```

## 🎯 命名规范

### 1. 文件命名
- **格式**: `{resource}_api.py`
- **示例**: `user_api.py`, `product_api.py`, `order_api.py`

### 2. 类命名
- **格式**: `{Resource}API`
- **示例**: `UserAPI`, `ProductAPI`, `OrderAPI`

### 3. 蓝图命名
- **格式**: `{resource}_api_bp`
- **示例**: `user_api_bp`, `product_api_bp`

### 4. 标签命名
- **格式**: `{Resource}Controller` (英文，用于代码生成)
- **示例**: `UserController`, `ProductController`

### 5. 方法命名
- **列表**: `list_{resource}s()` → `list_users()`
- **创建**: `create_{resource}()` → `create_user()`
- **获取**: `get_{resource}()` → `get_user()`
- **更新**: `update_{resource}()` → `update_user()`
- **部分更新**: `patch_{resource}()` → `patch_user()`
- **删除**: `delete_{resource}()` → `delete_user()`

## 📝 Pydantic 模型规范

### 1. 模型命名规范

```python
# 基础模型
class UserModel(BaseModel):
    """完整的用户模型 - 用于响应"""
    id: int = Field(..., description="用户ID")
    name: str = Field(..., description="用户姓名", min_length=1, max_length=50)
    email: str = Field(..., description="用户邮箱")
    created_at: Optional[str] = Field(None, description="创建时间")

# 请求模型
class UserCreateModel(BaseModel):
    """创建用户的请求模型"""
    name: str = Field(..., description="用户姓名", min_length=1, max_length=50)
    email: str = Field(..., description="用户邮箱")

class UserUpdateModel(BaseModel):
    """部分更新用户的请求模型"""
    name: Optional[str] = Field(None, description="用户姓名", min_length=1, max_length=50)
    email: Optional[str] = Field(None, description="用户邮箱")

# 路径参数模型
class UserPathModel(BaseModel):
    """用户路径参数模型"""
    user_id: int = Field(..., description="用户ID", ge=1)

# 响应模型
class UserListResponse(BaseModel):
    """用户列表响应模型"""
    users: List[UserModel]
    total: int = Field(..., description="用户总数")
    page: int = Field(1, description="当前页码")

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="附加数据")
```

### 2. 字段验证规范

```python
# 字符串验证
name: str = Field(..., description="姓名", min_length=1, max_length=50)
email: str = Field(..., description="邮箱", regex=r'^[^@]+@[^@]+\.[^@]+$')

# 数字验证
age: int = Field(..., description="年龄", ge=0, le=120)
price: float = Field(..., description="价格", gt=0)

# 可选字段
phone: Optional[str] = Field(None, description="电话号码")

# 枚举字段
from enum import Enum
class StatusEnum(str, Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"

status: StatusEnum = Field(StatusEnum.ACTIVE, description="状态")
```

## 🔧 装饰器类实现规范

### 1. 类结构规范

```python
class UserAPI:
    """
    用户API类 - 装饰器方式
    
    提供用户管理的完整CRUD操作，包括：
    - 用户列表查询
    - 用户创建
    - 用户详情获取
    - 用户信息更新
    - 用户删除
    """
    
    # 1. 类属性：配置和状态
    cache_timeout = 300
    rate_limit = 100
    request_count = 0
    
    # 2. 工具方法
    @classmethod
    def log_request(cls, action: str, user_id: Optional[int] = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_info = f" (User: {user_id})" if user_id else ""
        logging.info(f"[{cls.request_count}] {action}{user_info}")
    
    @classmethod
    def validate_permissions(cls, user_id: int) -> bool:
        """验证用户权限"""
        # 权限验证逻辑
        return True
    
    # 3. 装饰器方法
    @classmethod
    def with_logging(cls, action: str):
        """日志装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                cls.log_request(action)
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    # 4. API端点定义
    @staticmethod
    @user_api_bp.get('/', summary="获取用户列表", tags=[user_tag])
    @UserAPI.with_logging("LIST_USERS")
    def list_users():
        """获取用户列表"""
        return {
            'users': [],
            'total': 0,
            'request_count': UserAPI.request_count
        }
```

### 2. 装饰器使用规范

```python
# 标准装饰器顺序
@staticmethod                    # 1. Python内置装饰器
@user_api_bp.get(               # 2. Flask-OpenAPI路由装饰器
    '/',                        # 路径
    summary="获取用户列表",       # 简短描述
    description="获取所有用户的分页列表", # 详细描述
    tags=[user_tag],            # 标签
    responses={                 # 响应定义
        200: UserListResponse,
        400: MessageResponse
    }
)
@UserAPI.with_logging("LIST")   # 3. 自定义装饰器
def list_users():
    """获取用户列表"""
    pass
```

## 🛣️ RESTful 路由规范

### 1. 标准路由模式

```python
class UserAPI:
    # GET /api/v1/users - 获取用户列表
    @staticmethod
    @user_api_bp.get('/', summary="获取用户列表", tags=[user_tag])
    def list_users():
        pass
    
    # POST /api/v1/users - 创建新用户
    @staticmethod
    @user_api_bp.post('/', summary="创建新用户", tags=[user_tag])
    def create_user(body: UserCreateModel):
        pass
    
    # GET /api/v1/users/{userId} - 获取指定用户
    @staticmethod
    @user_api_bp.get('/<int:userId>', summary="获取指定用户", tags=[user_tag])
    def get_user(path: UserPathModel):
        pass
    
    # PUT /api/v1/users/{userId} - 完整更新用户
    @staticmethod
    @user_api_bp.put('/<int:userId>', summary="更新用户信息", tags=[user_tag])
    def update_user(path: UserPathModel, body: UserCreateModel):
        pass
    
    # PATCH /api/v1/users/{userId} - 部分更新用户
    @staticmethod
    @user_api_bp.patch('/<int:userId>', summary="部分更新用户", tags=[user_tag])
    def patch_user(path: UserPathModel, body: UserUpdateModel):
        pass
    
    # DELETE /api/v1/users/{userId} - 删除用户
    @staticmethod
    @user_api_bp.delete('/<int:userId>', summary="删除用户", tags=[user_tag])
    def delete_user(path: UserPathModel):
        pass
```

### ⚠️ 重要：路径参数命名规范

**必须使用驼峰命名（camelCase）而非蛇形命名（snake_case）！**

#### ❌ 错误示例
```python
# 错误：使用蛇形命名
@user_api_bp.get('/<int:user_id>', ...)  # ❌
@material_api_bp.get('/<int:material_id>', ...)  # ❌
@category_api_bp.get('/<int:category_id>', ...)  # ❌
```

#### ✅ 正确示例
```python
# 正确：使用驼峰命名
@user_api_bp.get('/<int:userId>', ...)  # ✅
@material_api_bp.get('/<int:materialId>', ...)  # ✅
@category_api_bp.get('/<int:categoryId>', ...)  # ✅
```

#### 原因说明

1. **OpenAPI 文档生成**：
   - Pydantic 模型使用 `CamelCaseModel`，字段名会自动转换为驼峰命名
   - 路径参数如果使用蛇形命名，会导致 OpenAPI 文档中出现两个参数名（`userId` 和 `user_id`）
   - 前端自动生成工具会同时支持两者，但实际使用时会出现 `undefined` 错误

2. **前端代码生成**：
   - 前端使用 `openapi2ts` 自动生成 API 调用代码
   - 如果路径参数和 Schema 参数名不一致，生成的代码会有歧义
   - 统一使用驼峰命名可以避免参数名冲突

3. **示例对比**：

```python
# ❌ 错误：路径参数与 Schema 不一致
class UserPathModel(CamelCaseModel):
    user_id: int  # Schema 中是 user_id，但会转换为 userId

@user_api_bp.get('/<int:user_id>', ...)  # 路径中是 user_id
# OpenAPI 文档中会出现：materialId（来自 Schema）和 material_id（来自路径）

# ✅ 正确：路径参数与 Schema 一致
class UserPathModel(CamelCaseModel):
    user_id: int  # Schema 中是 user_id，转换为 userId

@user_api_bp.get('/<int:userId>', ...)  # 路径中也是 userId
# OpenAPI 文档中只有：userId
```

#### 检查清单

在编写 API 时，请确保：
- [ ] 所有路径参数使用驼峰命名
- [ ] 路径参数名与 Pydantic 模型字段名（转换后）一致
- [ ] 生成 OpenAPI 文档后检查参数名是否唯一
- [ ] 前端重新生成 API 代码后测试是否正常

### 2. 扩展路由模式

```python
# 批量操作
@user_api_bp.post('/batch', summary="批量创建用户", tags=[user_tag])
def batch_create_users(body: List[UserCreateModel]):
    pass

# 搜索和过滤
@user_api_bp.get('/search', summary="搜索用户", tags=[user_tag])
def search_users(query: str = Query(..., description="搜索关键词")):
    pass

# 统计信息
@user_api_bp.get('/stats', summary="获取用户统计", tags=[user_tag])
def get_user_stats():
    pass

# 关联资源
@user_api_bp.get('/<int:user_id>/orders', summary="获取用户订单", tags=[user_tag])
def get_user_orders(path: UserPathModel):
    pass
```

## 📊 响应格式规范

### 1. 统一响应结构

所有API响应必须遵循统一的响应格式，使用 `BaseResponseModel`：

```python
# app/schemas/common_schemas.py
class BaseResponseModel(CamelCaseModel):
    """基础响应模型"""
    message: str = Field(..., description="响应消息")
    success: bool = Field(..., description="是否成功")
    data: Optional[Any] = Field(None, description="响应数据")
    error_code: Optional[str] = Field(None, description="错误代码")
    details: Optional[Any] = Field(None, description="错误详情")
    timestamp: datetime = Field(default_factory=datetime.utcnow, description="时间戳")

class PaginationModel(CamelCaseModel):
    """分页模型"""
    page: int = Field(1, description="当前页码", ge=1)
    per_page: int = Field(10, description="每页数量", ge=1, le=100)
    total: int = Field(..., description="总记录数", ge=0)
    pages: int = Field(..., description="总页数", ge=0)
    has_prev: bool = Field(..., description="是否有上一页")
    has_next: bool = Field(..., description="是否有下一页")
```

### 2. 响应处理工具

#### success_response 便捷函数（推荐使用）

**⚠️ 重要：success_response 会自动处理 Pydantic 模型转换**

```python
# app/utils/response_handler.py
from typing import Any, Optional, Dict
from datetime import datetime
from pydantic import BaseModel

def _convert_datetime_to_string(obj: Any) -> Any:
    """
    递归转换对象中的 datetime 为字符串
    
    自动处理：
    - datetime 对象 → 字符串
    - Pydantic 模型 → 驼峰命名字典
    - 嵌套结构的递归转换
    """
    if isinstance(obj, datetime):
        return obj.strftime('%a, %d %b %Y %H:%M:%S GMT')
    elif isinstance(obj, dict):
        return {key: _convert_datetime_to_string(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [_convert_datetime_to_string(item) for item in obj]
    elif isinstance(obj, BaseModel):
        # 如果是 Pydantic 模型，自动调用 model_dump(by_alias=True)
        return _convert_datetime_to_string(obj.model_dump(by_alias=True))
    else:
        return obj


def success_response(data: Any = None, message: str = "操作成功", status_code: int = 200):
    """
    返回成功响应（便捷函数）
    
    ✅ 自动处理：
    - datetime 对象转换为字符串
    - Pydantic 模型转换为驼峰命名的字典
    - 嵌套结构的递归转换
    
    Args:
        data: 响应数据（支持字典、列表、Pydantic模型等）
        message: 响应消息
        status_code: HTTP状态码
        
    Returns:
        (响应字典, 状态码) 元组
    """
    # 自动转换 datetime 和 Pydantic 模型
    processed_data = _convert_datetime_to_string(data)
    
    return {
        'code': status_code,
        'message': message,
        'data': processed_data
    }, status_code


def error_response(message: str, status_code: int = 400, error_code: Optional[str] = None):
    """
    返回错误响应（便捷函数）
    
    Args:
        message: 错误消息
        status_code: HTTP状态码
        error_code: 错误代码
        
    Returns:
        (响应字典, 状态码) 元组
    """
    return {
        'code': status_code,
        'message': message,
        'error_code': error_code
    }, status_code
```

**为什么 success_response 要自动处理 Pydantic 模型？**

1. **简化代码**：不需要手动调用 `model_dump(by_alias=True)`
2. **统一转换**：所有 API 自动获得驼峰命名转换
3. **递归处理**：自动处理嵌套的 Pydantic 模型和列表
4. **datetime 兼容**：同时处理可能遗漏的 datetime 对象

**使用示例：**

```python
# ✅ 推荐：直接传递 Pydantic 模型
response_model = MaterialDetailResponseModel(**material_data)
return success_response(data=response_model)

# ✅ 也支持：传递 Pydantic 模型列表
materials_models = [MaterialResponseModel(**m.to_dict()) for m in materials]
response_model = MaterialListResponseModel(materials=materials_models, ...)
return success_response(data=response_model)

# ✅ 也支持：传递普通字典
return success_response(data={'key': 'value'})
```

### 3. 标准响应格式

#### 成功响应示例

```json
{
  "message": "获取用户成功",
  "success": true,
  "data": {
    "id": 1,
    "username": "张三",
    "email": "zhangsan@example.com"
  },
  "errorCode": null,
  "details": null,
  "timestamp": "2025-12-03T12:37:00Z"
}
```

#### 分页响应示例

```json
{
  "message": "获取用户列表成功",
  "success": true,
  "data": {
    "items": [
      {
        "id": 1,
        "username": "张三",
        "email": "zhangsan@example.com"
      }
    ],
    "pagination": {
      "page": 1,
      "perPage": 20,
      "total": 100,
      "pages": 5,
      "hasPrev": false,
      "hasNext": true
    }
  },
  "errorCode": null,
  "details": null,
  "timestamp": "2025-12-03T12:37:00Z"
}
```

#### 错误响应示例

```json
{
  "message": "用户不存在",
  "success": false,
  "data": null,
  "errorCode": "USER_NOT_FOUND",
  "details": "用户ID: 999 不存在",
  "timestamp": "2025-12-03T12:37:00Z"
}
```

### 4. API 实现规范

#### 完整的 API 实现示例

**⚠️ 重要：遵循三层自动化处理**

```python
from app.utils.response_handler import success_response, error_response
from app.schemas.material_schemas import MaterialDetailResponseModel

class MaterialAPI:
    @staticmethod
    @material_api_bp.get('/<int:materialId>', 
                        summary="获取资料详情",
                        tags=[material_tag])
    @login_required
    def get_material_detail(path: MaterialPathModel):
        """
        获取资料详情
        
        三层自动化处理：
        1. BaseModel.to_dict() - 自动转换 datetime 为字符串
        2. Pydantic 模型 - 验证数据类型
        3. success_response() - 自动转换为驼峰命名
        """
        try:
            # 1. 获取数据库对象
            material = MaterialService.get_material_by_id(path.material_id)
            
            if not material:
                return error_response("资料不存在", 404)
            
            # 2. 转换为字典（to_dict 已自动转换 datetime）
            material_data = material.to_dict()
            
            # 3. 添加额外信息
            material_data['tags'] = [tag.to_dict() for tag in material.tags.all()]
            if material.category:
                material_data['category_name'] = material.category.name
            
            # 4. 创建 Pydantic 模型（验证数据）
            response_model = MaterialDetailResponseModel(**material_data)
            
            # 5. 返回响应（success_response 自动转换为驼峰命名）
            return success_response(data=response_model)
            
        except Exception as e:
            logger.error(f"获取资料详情失败: {str(e)}")
            return error_response("获取资料详情失败", 500)
```

**三层自动化处理流程：**

```
数据库对象 (datetime)
    ↓
to_dict() → 字典 (datetime → 字符串) ✅ 第一层
    ↓
Pydantic 模型 → 验证数据类型 ✅ 第二层
    ↓
success_response() → 驼峰命名字典 ✅ 第三层
    ↓
前端接收 (驼峰命名 + 字符串时间)
```

**错误示例（不要这样做）：**

```python
# ❌ 错误1：手动转换 datetime（重复劳动）
material_data = material.to_dict()
if material_data.get('created_at'):
    material_data['created_at'] = material_data['created_at'].strftime(...)

# ❌ 错误2：手动调用 model_dump（重复劳动）
response_model = MaterialDetailResponseModel(**material_data)
return success_response(data=response_model.model_dump(by_alias=True))

# ❌ 错误3：不使用 Pydantic 模型（缺少验证）
return success_response(data=material.to_dict())
```

**正确示例：**

```python
# ✅ 正确：让三层自动化处理
material_data = material.to_dict()  # 自动转换 datetime
response_model = MaterialDetailResponseModel(**material_data)  # 验证
return success_response(data=response_model)  # 自动转驼峰
```

### 6. 响应格式最佳实践

#### 必须遵循的规范

1. **统一性**: 所有API必须使用 `BaseResponseModel` 格式
2. **驼峰命名**: 所有字段名使用驼峰命名（通过 `CamelCaseModel` 自动转换）
3. **时间戳**: 所有响应必须包含 `timestamp` 字段
4. **成功标识**: 使用 `success` 字段明确标识操作是否成功
5. **错误代码**: 错误响应必须包含 `errorCode` 便于前端处理

#### 推荐的实现方式

1. **优先使用 `@auto_response` 装饰器** - 减少重复代码，自动处理异常
2. **业务异常使用 `ValueError`** - 自动转换为 400 错误
3. **分页使用元组返回** - `(items, total, page, per_page)` 自动处理
4. **复杂逻辑手动处理** - 使用 `ResponseHandler` 精确控制响应

## 🔒 安全和验证规范

### 1. 输入验证

```python
class UserAPI:
    @classmethod
    def validate_user_data(cls, user_data: dict) -> Optional[dict]:
        """验证用户数据"""
        errors = {}
        
        if not user_data.get('name'):
            errors['name'] = 'Name is required'
        
        if not user_data.get('email'):
            errors['email'] = 'Email is required'
        elif '@' not in user_data['email']:
            errors['email'] = 'Invalid email format'
        
        return errors if errors else None
    
    @staticmethod
    @user_api_bp.post('/', summary="创建新用户", tags=[user_tag])
    def create_user(body: UserCreateModel):
        # 额外验证
        errors = UserAPI.validate_user_data(body.dict())
        if errors:
            return {'message': 'Validation error', 'errors': errors}, 400
        
        # 创建用户逻辑
        pass
```

### 2. 权限控制

```python
class UserAPI:
    @classmethod
    def require_permission(cls, permission: str):
        """权限验证装饰器"""
        def decorator(func):
            @wraps(func)
            def wrapper(*args, **kwargs):
                # 权限检查逻辑
                if not cls.check_permission(permission):
                    return {'message': 'Permission denied'}, 403
                return func(*args, **kwargs)
            return wrapper
        return decorator
    
    @staticmethod
    @user_api_bp.delete('/<int:user_id>', summary="删除用户", tags=[user_tag])
    @UserAPI.require_permission('user:delete')
    def delete_user(path: UserPathModel):
        pass
```

## 🧪 测试规范

### 1. 单元测试

```python
import pytest
from app.api.user_api import UserAPI

class TestUserAPI:
    def test_validate_user_data_valid(self):
        """测试有效用户数据验证"""
        data = {'name': '张三', 'email': 'zhangsan@example.com'}
        errors = UserAPI.validate_user_data(data)
        assert errors is None
    
    def test_validate_user_data_invalid(self):
        """测试无效用户数据验证"""
        data = {'name': '', 'email': 'invalid-email'}
        errors = UserAPI.validate_user_data(data)
        assert 'name' in errors
        assert 'email' in errors
    
    def test_log_request(self):
        """测试请求日志记录"""
        initial_count = UserAPI.request_count
        UserAPI.log_request('TEST')
        assert UserAPI.request_count == initial_count + 1
```

### 2. 集成测试

```python
def test_create_user_endpoint(client):
    """测试创建用户端点"""
    response = client.post('/api/v1/users', json={
        'name': '张三',
        'email': 'zhangsan@example.com'
    })
    assert response.status_code == 201
    assert response.json['message'] == 'User created successfully'
```

## 📚 文档规范

### 1. 类文档

```python
class UserAPI:
    """
    用户API类 - 装饰器方式
    
    提供用户管理的完整CRUD操作。
    
    Features:
        - 用户列表查询（支持分页和搜索）
        - 用户创建（包含数据验证）
        - 用户详情获取
        - 用户信息更新（完整更新和部分更新）
        - 用户删除（软删除）
        - 请求日志记录
        - 权限验证
    
    Attributes:
        cache_timeout (int): 缓存超时时间（秒）
        rate_limit (int): 速率限制（请求/分钟）
        request_count (int): 请求计数器
    
    Example:
        >>> user_api = UserAPI()
        >>> user_api.log_request('CREATE_USER')
    """
```

### 2. 方法文档

```python
@staticmethod
@user_api_bp.post('/', summary="创建新用户", tags=[user_tag])
def create_user(body: UserCreateModel):
    """
    创建新用户
    
    创建一个新的用户账户，包含基本信息验证和重复邮箱检查。
    
    Args:
        body (UserCreateModel): 用户创建数据
            - name (str): 用户姓名，1-50个字符
            - email (str): 用户邮箱，必须是有效格式
    
    Returns:
        dict: 创建结果
            - message (str): 操作结果消息
            - user (dict): 创建的用户信息
    
    Raises:
        400: 数据验证失败
        409: 邮箱已存在
        500: 服务器内部错误
    
    Example:
        POST /api/v1/users
        {
            "name": "张三",
            "email": "zhangsan@example.com"
        }
    """
```

## ⚡ 性能优化规范

### 1. 缓存策略

```python
class UserAPI:
    cache = {}
    cache_timeout = 300
    
    @classmethod
    def get_from_cache(cls, key: str):
        """从缓存获取数据"""
        cache_data = cls.cache.get(key)
        if cache_data and time.time() - cache_data['timestamp'] < cls.cache_timeout:
            return cache_data['data']
        return None
    
    @classmethod
    def set_cache(cls, key: str, data: any):
        """设置缓存数据"""
        cls.cache[key] = {
            'data': data,
            'timestamp': time.time()
        }
    
    @staticmethod
    @user_api_bp.get('/', summary="获取用户列表", tags=[user_tag])
    def list_users():
        # 尝试从缓存获取
        cached_data = UserAPI.get_from_cache('users_list')
        if cached_data:
            return cached_data
        
        # 查询数据库
        users = get_users_from_db()
        
        # 设置缓存
        result = {'users': users, 'total': len(users)}
        UserAPI.set_cache('users_list', result)
        
        return result
```

### 2. 分页处理

```python
class PaginationModel(BaseModel):
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)

@staticmethod
@user_api_bp.get('/', summary="获取用户列表", tags=[user_tag])
def list_users(query: PaginationModel = Query()):
    """分页获取用户列表"""
    offset = (query.page - 1) * query.per_page
    users = get_users_paginated(offset, query.per_page)
    total = get_users_count()
    
    return {
        'users': users,
        'total': total,
        'page': query.page,
        'per_page': query.per_page,
        'pages': (total + query.per_page - 1) // query.per_page
    }
```

## 🚀 部署和监控规范

### 1. 健康检查

```python
@user_api_bp.get('/health', summary="健康检查", tags=[user_tag])
def health_check():
    """API健康检查"""
    return {
        'status': 'healthy',
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
        'request_count': UserAPI.request_count,
        'version': '1.0.0'
    }
```

### 2. 监控指标

```python
class UserAPI:
    metrics = {
        'total_requests': 0,
        'error_count': 0,
        'avg_response_time': 0
    }
    
    @classmethod
    def record_metric(cls, metric_name: str, value: any):
        """记录监控指标"""
        cls.metrics[metric_name] = value
    
    @staticmethod
    @user_api_bp.get('/metrics', summary="获取API指标", tags=[user_tag])
    def get_metrics():
        """获取API监控指标"""
        return UserAPI.metrics
```

## 📋 检查清单

### 开发前检查
- [ ] 确定资源名称和API结构
- [ ] 定义Pydantic模型
- [ ] 设计路由结构
- [ ] 确定权限和验证规则

### 开发中检查
- [ ] 遵循命名规范
- [ ] 添加适当的文档字符串
- [ ] 实现错误处理
- [ ] 添加日志记录
- [ ] 编写单元测试

### 部署前检查
- [ ] 所有测试通过
- [ ] API文档生成正确
- [ ] 性能测试通过
- [ ] 安全检查通过
- [ ] 监控指标配置完成

---

## 🎯 总结

遵循本规范可以确保：
- **一致性**: 所有API具有统一的结构和风格
- **可维护性**: 代码易于理解和修改
- **可扩展性**: 便于添加新功能和优化
- **可测试性**: 便于编写和执行测试
- **文档化**: 自动生成完整的API文档

建议团队成员熟悉并严格遵循本规范，以提高开发效率和代码质量。