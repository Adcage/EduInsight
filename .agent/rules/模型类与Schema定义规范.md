---
trigger: model_decision
description: 编写后端模型类和Schema类时需要遵守的规范
---

# 模型类与Schema定义规范

## 一、概述

本文档定义了教师智能助手系统中数据库模型类(Model)和数据验证模式(Schema)的编写规范，确保代码的一致性、可维护性和可扩展性。

---

## 二、模型类(Model)定义规范

### 2.1 基础结构

#### 2.1.1 文件组织
```
backend/app/models/
├── __init__.py          # 导出所有模型
├── base.py              # 基础模型类
├── user.py              # 用户模型
├── material.py          # 资料模型
├── course.py            # 课程模型
├── attendance.py        # 考勤模型
├── grade.py             # 成绩模型
└── ...                  # 其他模型
```

#### 2.1.2 导入顺序
```python
# 1. 标准库导入
from datetime import datetime
from enum import Enum

# 2. 第三方库导入
from werkzeug.security import generate_password_hash, check_password_hash

# 3. 本地应用导入
from app.extensions import db
from .base import BaseModel
```

### 2.2 基础模型类 (BaseModel)

所有模型必须继承自 `BaseModel`，提供通用字段和方法。

```python
from datetime import datetime
from app.extensions import db

class BaseModel(db.Model):
    """基础模型类"""
    __abstract__ = True
    
    # 通用字段
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    
    def save(self):
        """保存到数据库"""
        db.session.add(self)
        db.session.commit()
        return self
    
    def delete(self):
        """从数据库删除"""
        db.session.delete(self)
        db.session.commit()
    
    @classmethod
    def get_by_id(cls, id):
        """根据ID获取记录"""
        return cls.query.get(id)
    
    @classmethod
    def get_all(cls):
        """获取所有记录"""
        return cls.query.all()
```

**BaseModel 提供的功能**:
- ✅ 自动主键 `id`
- ✅ 自动时间戳 `created_at`, `updated_at`
- ✅ 通用方法: `to_dict()`, `save()`, `delete()`
- ✅ 类方法: `get_by_id()`, `get_all()`

### 2.3 模型类定义规范

#### 2.3.1 完整示例

```python
from werkzeug.security import generate_password_hash, check_password_hash
from app.extensions import db
from .base import BaseModel
from datetime import datetime
from enum import Enum

class UserRole(Enum):
    """用户角色枚举"""
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'

class User(BaseModel):
    """用户模型
    
    存储系统所有用户的基本信息，支持多角色用户系统。
    """
    __tablename__ = 'users'
    
    # ==================== 字段定义 ====================
    # 基本信息
    username = db.Column(db.String(50), nullable=False)
    user_code = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    real_name = db.Column(db.String(50), nullable=False)
    avatar = db.Column(db.String(255), nullable=True)
    
    # 角色和权限
    role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False, index=True)
    
    # 外键关联
    class_id = db.Column(db.Integer, nullable=True, index=True)  # FK→classes.id
    
    # 状态和时间
    status = db.Column(db.Boolean, default=True, nullable=False)
    last_login_time = db.Column(db.DateTime, nullable=True)
    
    # ==================== 关系定义 ====================
    # 一对多关系示例
    # materials = db.relationship('Material', backref='uploader', lazy='dynamic', cascade='all, delete-orphan')
    
    # 多对多关系示例
    # courses = db.relationship('Course', secondary='course_students', backref='students', lazy='dynamic')
    
    # ==================== 实例方法 ====================
    def set_password(self, password):
        """设置密码"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """验证密码"""
        return check_password_hash(self.password_hash, password)
    
    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_time = datetime.utcnow()
        db.session.commit()
    
    # ==================== 角色判断方法 ====================
    def is_admin(self):
        """检查是否为管理员"""
        return self.role == UserRole.ADMIN
    
    def is_teacher(self):
        """检查是否为教师"""
        return self.role == UserRole.TEACHER
    
    def is_student(self):
        """检查是否为学生"""
        return self.role == UserRole.STUDENT
    
    # ==================== 权限检查方法 ====================
    def has_permission(self, permission):
        """检查用户是否有指定权限
        
        Args:
            permission: 权限字符串，格式为 'resource:action'
            
        Returns:
            bool: 是否拥有该权限
        """
        if self.is_admin():
            return True
        
        role_permissions = {
            UserRole.TEACHER: [
                'material:create', 'material:read', 'material:update', 'material:delete',
                'course:create', 'course:read', 'course:update',
                'attendance:create', 'attendance:read', 'attendance:update',
                'grade:create', 'grade:read', 'grade:update',
            ],
            UserRole.STUDENT: [
                'material:read',
                'course:read',
                'attendance:read', 'attendance:checkin',
                'grade:read',
            ]
        }
        
        return permission in role_permissions.get(self.role, [])
    
    # ==================== 数据转换方法 ====================
    def to_dict(self):
        """转换为字典，排除敏感信息"""
        data = super().to_dict()
        data.pop('password_hash', None)  # 移除密码哈希
        data['role'] = self.role.value if self.role else None  # 枚举转字符串
        return data
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_email(cls, email):
        """根据邮箱获取用户"""
        return cls.query.filter_by(email=email).first()
    
    @classmethod
    def get_by_user_code(cls, user_code):
        """根据工号/学号获取用户"""
        return cls.query.filter_by(user_code=user_code).first()
    
    @classmethod
    def get_by_username(cls, username):
        """根据用户名获取用户"""
        return cls.query.filter_by(username=username).first()
    
    # ==================== 魔术方法 ====================
    def __repr__(self):
        return f'<User {self.username}({self.real_name})>'
```

#### 2.3.2 字段定义规范

**字段分组**:
```python
# 1. 基本信息字段
username = db.Column(db.String(50), nullable=False)
email = db.Column(db.String(100), unique=True, nullable=False, index=True)

# 2. 外键字段
course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id

# 3. 状态和时间字段
status = db.Column(db.Boolean, default=True, nullable=False)
last_login_time = db.Column(db.DateTime, nullable=True)
```

**字段属性规范**:
```python
# 字符串字段
name = db.Column(db.String(100), nullable=False)  # 必填
description = db.Column(db.Text, nullable=True)   # 可选

# 数值字段
score = db.Column(db.Decimal(5, 2), nullable=False)  # 精确小数
count = db.Column(db.Integer, default=0, nullable=False)

# 布尔字段
is_active = db.Column(db.Boolean, default=True, nullable=False)

# 日期时间字段
exam_date = db.Column(db.Date, nullable=True)
check_in_time = db.Column(db.DateTime, nullable=True)

# 枚举字段
role = db.Column(db.Enum(UserRole), default=UserRole.STUDENT, nullable=False)

# JSON字段 (MySQL 5.7+)
options = db.Column(db.JSON, nullable=True)

# 唯一约束
email = db.Column(db.String(100), unique=True, nullable=False)

# 索引
user_code = db.Column(db.String(50), index=True, nullable=False)
```

**外键定义规范** ⚠️ 重要:
```python
# ❌ 错误做法：不要使用 ForeignKey 约束
course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False, index=True)

# ✅ 正确做法：只使用注释标记外键关系
course_id = db.Column(db.Integer, nullable=False, index=True)  # FK→courses.id
student_id = db.Column(db.Integer, nullable=False, index=True)  # FK→users.id
```

**外键规范说明**:
1. **不要使用 `db.ForeignKey()`**: 避免创建表时的依赖问题和循环引用
2. **使用注释标记**: 在字段后添加 `# FK→table.id` 注释说明外键关系
3. **添加索引**: 外键字段应该添加 `index=True` 以提高查询性能
4. **保持一致性**: 所有外键字段都遵循此规范

**关联表外键规范**:
```python
# ❌ 错误做法
material_tag_relation = db.Table(
    'material_tag_relation',
    db.Column('material_id', db.Integer, db.ForeignKey('materials.id')),
    db.Column('tag_id', db.Integer, db.ForeignKey('material_tags.id'))
)

# ✅ 正确做法
material_tag_relation = db.Table(
    'material_tag_relation',
    db.Column('id', db.Integer, primary_key=True, autoincrement=True),
    db.Column('material_id', db.Integer, nullable=False, index=True),  # FK→materials.id
    db.Column('tag_id', db.Integer, nullable=False, index=True),  # FK→material_tags.id
    db.Column('created_at', db.DateTime, default=db.func.current_timestamp()),
    db.UniqueConstraint('material_id', 'tag_id', name='uk_material_tag')
)
```

#### 2.3.3 关系定义规范

**一对多关系**:
```python
class Course(BaseModel):
    __tablename__ = 'courses'
    
    # 一对多: 一个课程有多个资料
    materials = db.relationship(
        'Material',           # 关联的模型
        backref='course',     # 反向引用名称
        lazy='dynamic',       # 延迟加载
        cascade='all, delete-orphan'  # 级联删除
    )
```

**多对多关系**:
```python
# 关联表
course_students = db.Table('course_students',
    db.Column('course_id', db.Integer, db.ForeignKey('courses.id'), primary_key=True),
    db.Column('student_id', db.Integer, db.ForeignKey('users.id'), primary_key=True),
    db.Column('created_at', db.DateTime, default=datetime.utcnow)
)

class Course(BaseModel):
    __tablename__ = 'courses'
    
    # 多对多: 课程和学生
    students = db.relationship(
        'User',
        secondary=course_students,
        backref='enrolled_courses',
        lazy='dynamic'
    )
```

**lazy 参数说明**:
- `select`: 默认值，使用标准SELECT语句加载
- `dynamic`: 返回查询对象，适合大量数据
- `joined`: 使用JOIN加载，适合一对一或小数据量
- `subquery`: 使用子查询加载

**cascade 参数说明**:
- `all`: 所有操作都级联
- `delete`: 删除时级联
- `delete-orphan`: 删除孤儿记录
- `save-update`: 保存更新时级联

#### 2.3.4 方法定义规范

**方法分类和顺序**:
```python
class User(BaseModel):
    # 1. 实例方法 - 业务逻辑
    def set_password(self, password):
        """设置密码"""
        pass
    
    def check_password(self, password):
        """验证密码"""
        pass
    
    # 2. 实例方法 - 状态判断
    def is_admin(self):
        """检查是否为管理员"""
        pass
    
    # 3. 实例方法 - 权限检查
    def has_permission(self, permission):
        """检查权限"""
        pass
    
    # 4. 数据转换方法
    def to_dict(self):
        """转换为字典"""
        pass
    
    # 5. 类方法 - 查询方法
    @classmethod
    def get_by_email(cls, email):
        """根据邮箱获取用户"""
        pass
    
    # 6. 魔术方法
    def __repr__(self):
        return f'<User {self.username}>'
```

**方法文档字符串规范**:
```python
def has_permission(self, permission):
    """检查用户是否有指定权限
    
    Args:
        permission (str): 权限字符串，格式为 'resource:action'
                         例如: 'material:create', 'grade:read'
    
    Returns:
        bool: 如果用户拥有该权限返回True，否则返回False
    
    Examples:
        >>> user.has_permission('material:create')
        True
    """
    pass
```

#### 2.3.5 枚举类定义规范

```python
from enum import Enum

class UserRole(Enum):
    """用户角色枚举
    
    定义系统中所有可用的用户角色。
    """
    ADMIN = 'admin'      # 管理员
    TEACHER = 'teacher'  # 教师
    STUDENT = 'student'  # 学生

class AttendanceStatus(Enum):
    """考勤状态枚举"""
    PRESENT = 'present'  # 出勤
    LATE = 'late'        # 迟到
    ABSENT = 'absent'    # 缺勤
    LEAVE = 'leave'      # 请假

class ExamType(Enum):
    """考试类型枚举"""
    DAILY = 'daily'        # 平时成绩
    MIDTERM = 'midterm'    # 期中考试
    FINAL = 'final'        # 期末考试
    HOMEWORK = 'homework'  # 作业
```

**枚举使用规范**:
- ✅ 枚举类名使用单数形式
- ✅ 枚举值使用小写字符串
- ✅ 添加中文注释说明每个枚举值的含义
- ✅ 枚举类定义在模型类之前

---

## 三、Schema定义规范

### 3.1 基础结构

#### 3.1.1 文件组织
```
backend/app/schemas/
├── __init__.py          # 导出所有Schema
├── base_schemas.py      # 基础Schema类
├── user_schemas.py      # 用户Schema
├── material_schemas.py  # 资料Schema
├── course_schemas.py    # 课程Schema
└── ...                  # 其他Schema
```

#### 3.1.2 导入顺序
```python
# 1. 标准库导入
from typing import Optional, List
from enum import Enum

# 2. 第三方库导入
from pydantic import Field, EmailStr, validator

# 3. 本地应用导入
from app.schemas.base_schemas import CamelCaseModel
```

### 3.2 基础Schema类 (CamelCaseModel)

```python
from pydantic import BaseModel
from humps import camelize

class CamelCaseModel(BaseModel):
    """驼峰命名转换的基础模型
    
    自动将snake_case字段名转换为camelCase，
    用于前后端数据交互的命名风格统一。
    """
    class Config:
        alias_generator = camelize
        populate_by_name = True
        from_attributes = True
```

**CamelCaseModel 功能**:
- ✅ 自动转换字段名: `user_code` → `userCode`
- ✅ 支持双向转换: 接收和返回都支持
- ✅ 支持ORM对象转换

### 3.3 Schema类型分类

#### 3.3.1 请求Schema (Request Models)

**用途**: 验证客户端发送的请求数据

```python
class UserRegisterModel(CamelCaseModel):
    """用户注册请求模型"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    user_code: str = Field(..., description="工号/学号", min_length=1, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=128)
    email: EmailStr = Field(..., description="邮箱地址")
    real_name: str = Field(..., description="真实姓名", min_length=1, max_length=50)
    role: UserRoleEnum = Field(UserRoleEnum.STUDENT, description="用户角色")
    phone: Optional[str] = Field(None, description="手机号码", max_length=20)
    class_id: Optional[int] = Field(None, description="班级ID", ge=1)
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v
```

**命名规范**: `{模型名}{操作}Model`
- `UserRegisterModel` - 用户注册
- `UserLoginModel` - 用户登录
- `UserUpdateModel` - 用户更新
- `MaterialUploadModel` - 资料上传
- `GradeCreateModel` - 成绩创建

#### 3.3.2 响应Schema (Response Models)

**用途**: 定义返回给客户端的数据结构

```python
class UserResponseModel(CamelCaseModel):
    """用户响应模型"""
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    user_code: str = Field(..., description="工号/学号")
    email: str = Field(..., description="邮箱地址")
    real_name: str = Field(..., description="真实姓名")
    role: str = Field(..., description="用户角色")
    phone: Optional[str] = Field(None, description="手机号码")
    avatar: Optional[str] = Field(None, description="头像URL")
    class_id: Optional[int] = Field(None, description="班级ID")
    status: bool = Field(..., description="账户状态")
    last_login_time: Optional[str] = Field(None, description="最后登录时间")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")
```

**命名规范**: `{模型名}ResponseModel`
- `UserResponseModel` - 单个用户响应
- `UserListResponseModel` - 用户列表响应
- `MaterialResponseModel` - 资料响应
- `GradeResponseModel` - 成绩响应

#### 3.3.3 查询参数Schema (Query Models)

**用途**: 验证URL查询参数

```python
class UserQueryModel(CamelCaseModel):
    """用户查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    role: Optional[UserRoleEnum] = Field(None, description="角色筛选")
    status: Optional[bool] = Field(None, description="状态筛选")
    search: Optional[str] = Field(None, description="搜索关键词", max_length=100)
```

**命名规范**: `{模型名}QueryModel`

#### 3.3.4 路径参数Schema (Path Models)

**用途**: 验证URL路径参数

```python
class UserPathModel(CamelCaseModel):
    """用户路径参数模型"""
    user_id: int = Field(..., description="用户ID", ge=1)

class MaterialPathModel(CamelCaseModel):
    """资料路径参数模型"""
    material_id: int = Field(..., description="资料ID", ge=1)
```

**命名规范**: `{模型名}PathModel`

### 3.4 字段定义规范

#### 3.4.1 Field参数说明

```python
# 必填字段
username: str = Field(..., description="用户名")

# 可选字段
phone: Optional[str] = Field(None, description="手机号码")

# 默认值
page: int = Field(1, description="页码")

# 字符串长度限制
username: str = Field(..., min_length=3, max_length=50)

# 数值范围限制
age: int = Field(..., ge=0, le=150)  # ge: >=, le: <=
score: float = Field(..., gt=0, lt=100)  # gt: >, lt: <

# 正则表达式验证
phone: str = Field(..., regex=r'^1[3-9]\d{9}$')

# 示例值
email: EmailStr = Field(..., example="user@example.com")
```

#### 3.4.2 类型注解规范

```python
from typing import Optional, List, Dict, Union

# 基础类型
name: str
age: int
score: float
is_active: bool

# 可选类型
phone: Optional[str] = None
avatar: Optional[str] = Field(None)

# 列表类型
tags: List[str] = Field(default_factory=list)
scores: List[float] = []

# 字典类型
metadata: Dict[str, str] = Field(default_factory=dict)

# 联合类型
identifier: Union[str, int]

# 嵌套模型
user: UserResponseModel
users: List[UserResponseModel]
```

#### 3.4.3 特殊字段类型

```python
from pydantic import EmailStr, HttpUrl, constr, conint

# 邮箱验证
email: EmailStr = Field(...)

# URL验证
website: HttpUrl = Field(...)

# 约束字符串
username: constr(min_length=3, max_length=50) = Field(...)

# 约束整数
age: conint(ge=0, le=150) = Field(...)
```

### 3.5 验证器(Validator)规范

#### 3.5.1 单字段验证器

```python
from pydantic import validator

class UserRegisterModel(CamelCaseModel):
    username: str = Field(...)
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式
        
        Args:
            v: 字段值
            
        Returns:
            验证后的值
            
        Raises:
            ValueError: 验证失败时抛出
        """
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v
```

#### 3.5.2 多字段验证器

```python
class PasswordChangeModel(CamelCaseModel):
    new_password: str = Field(...)
    confirm_password: str = Field(...)
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        """验证两次密码输入是否一致"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v
```

#### 3.5.3 条件验证器

```python
class UserRegisterModel(CamelCaseModel):
    role: UserRoleEnum = Field(...)
    class_id: Optional[int] = Field(None)
    
    @validator('class_id', always=True)
    def validate_class_id(cls, v, values):
        """验证班级ID（学生角色时必须提供）"""
        role = values.get('role')
        if role == UserRoleEnum.STUDENT and v is None:
            raise ValueError('学生角色必须指定班级ID')
        elif role != UserRoleEnum.STUDENT and v is not None:
            return None  # 非学生角色不需要班级ID
        return v
```

#### 3.5.4 预处理验证器

```python
from pydantic import validator

class UserUpdateModel(CamelCaseModel):
    email: Optional[EmailStr] = Field(None)
    
    @validator('email', pre=True)
    def lowercase_email(cls, v):
        """邮箱转小写（预处理）"""
        if v is not None:
            return v.lower()
        return v
```

### 3.6 枚举Schema定义

```python
from enum import Enum

class UserRoleEnum(str, Enum):
    """用户角色枚举
    
    注意: 继承str和Enum，确保JSON序列化正常
    """
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'

class AttendanceStatusEnum(str, Enum):
    """考勤状态枚举"""
    PRESENT = 'present'
    LATE = 'late'
    ABSENT = 'absent'
    LEAVE = 'leave'
```

**枚举规范**:
- ✅ 必须同时继承 `str` 和 `Enum`
- ✅ 枚举类名以 `Enum` 结尾
- ✅ 与模型中的枚举保持一致

### 3.7 列表响应Schema

```python
class UserListResponseModel(CamelCaseModel):
    """用户列表响应模型"""
    users: List[UserResponseModel] = Field(..., description="用户列表")
    total: int = Field(..., description="用户总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")

class MaterialListResponseModel(CamelCaseModel):
    """资料列表响应模型"""
    materials: List[MaterialResponseModel] = Field(..., description="资料列表")
    total: int = Field(..., description="资料总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")
```

**列表响应规范**:
- ✅ 包含数据列表字段
- ✅ 包含分页信息: `total`, `page`, `per_page`, `pages`
- ✅ 命名格式: `{模型名}ListResponseModel`

### 3.8 通用响应Schema

```python
class MessageResponseModel(CamelCaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="响应消息")
    error_code: Optional[str] = Field(None, description="错误代码")

class SuccessResponseModel(CamelCaseModel):
    """成功响应模型"""
    success: bool = Field(True, description="操作是否成功")
    message: str = Field(..., description="响应消息")
    data: Optional[dict] = Field(None, description="附加数据")

class ErrorResponseModel(CamelCaseModel):
    """错误响应模型"""
    success: bool = Field(False, description="操作是否成功")
    message: str = Field(..., description="错误消息")
    error_code: str = Field(..., description="错误代码")
    details: Optional[dict] = Field(None, description="错误详情")
```

---

## 四、命名规范总结

### 4.1 模型类命名

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 模型类 | 单数名词 | `User`, `Material`, `Course` |
| 枚举类 | 单数名词 | `UserRole`, `AttendanceStatus` |
| 关联表 | 复数_复数 | `course_students`, `material_tags` |

### 4.2 Schema类命名

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 请求Schema | {模型}{操作}Model | `UserRegisterModel`, `MaterialUploadModel` |
| 响应Schema | {模型}ResponseModel | `UserResponseModel`, `MaterialResponseModel` |
| 列表响应 | {模型}ListResponseModel | `UserListResponseModel` |
| 查询参数 | {模型}QueryModel | `UserQueryModel` |
| 路径参数 | {模型}PathModel | `UserPathModel` |
| 枚举 | {名称}Enum | `UserRoleEnum`, `AttendanceStatusEnum` |

### 4.3 字段命名

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 普通字段 | snake_case | `user_name`, `created_at` |
| 布尔字段 | is_/has_前缀 | `is_active`, `has_permission` |
| 外键字段 | {表名}_id | `user_id`, `course_id` |
| 时间字段 | {动作}_time/at | `created_at`, `login_time` |

### 4.4 方法命名

| 类型 | 命名格式 | 示例 |
|------|---------|------|
| 获取方法 | get_{字段} | `get_by_email`, `get_by_id` |
| 设置方法 | set_{字段} | `set_password` |
| 检查方法 | is_/has_/can_ | `is_admin`, `has_permission` |
| 验证方法 | validate_{字段} | `validate_username` |
| 转换方法 | to_{格式} | `to_dict`, `to_json` |

---

## 五、最佳实践

### 5.1 模型类最佳实践

#### ✅ 推荐做法

```python
# 1. 使用枚举而不是字符串常量
class UserRole(Enum):
    ADMIN = 'admin'
    TEACHER = 'teacher'

role = db.Column(db.Enum(UserRole), nullable=False)

# 2. ⚠️ 外键字段：不使用ForeignKey，只用注释标记
course_id = db.Column(db.Integer, index=True, nullable=False)  # FK→courses.id

# 3. 为外键添加索引
course_id = db.Column(db.Integer, index=True, nullable=False)

# 4. 使用级联删除
materials = db.relationship('Material', cascade='all, delete-orphan')

# 5. 重写to_dict方法排除敏感信息
def to_dict(self):
    data = super().to_dict()
    data.pop('password_hash', None)
    return data

# 6. 添加有意义的__repr__
def __repr__(self):
    return f'<User {self.username}>'
```

#### ❌ 避免做法

```python
# 1. ⚠️ 不要使用 db.ForeignKey() 约束
course_id = db.Column(db.Integer, db.ForeignKey('courses.id'))  # ❌ 错误！

# 2. 不要使用魔法数字
status = db.Column(db.Integer)  # 0, 1, 2 代表什么？

# 3. 不要忘记添加索引
email = db.Column(db.String(100), unique=True)  # 缺少index=True

# 4. 不要在模型中写复杂业务逻辑
def calculate_final_grade(self):
    # 复杂计算应该放在Service层
    pass

# 5. 不要直接暴露敏感信息
def to_dict(self):
    return {c.name: getattr(self, c.name) for c in self.__table__.columns}
    # 会暴露password_hash!
```

### 5.2 Schema最佳实践

#### ✅ 推荐做法

```python
# 1. 使用描述性的Field描述
username: str = Field(..., description="用户名", min_length=3, max_length=50)

# 2. 使用validator进行复杂验证
@validator('email')
def validate_email(cls, v):
    if v and not v.endswith('@example.com'):
        raise ValueError('必须使用公司邮箱')
    return v

# 3. 使用Optional明确可选字段
phone: Optional[str] = Field(None, description="手机号码")

# 4. 分离请求和响应Schema
class UserCreateModel(CamelCaseModel):  # 请求
    username: str
    password: str

class UserResponseModel(CamelCaseModel):  # 响应
    id: int
    username: str
    # 不包含password
```

#### ❌ 避免做法

```python
# 1. 不要省略Field描述
username: str = Field(...)  # 缺少description

# 2. 不要在Schema中写业务逻辑
@validator('score')
def calculate_grade(cls, v):
    # 业务逻辑应该在Service层
    return v * 1.1

# 3. 不要混用请求和响应Schema
class UserModel(CamelCaseModel):
    password: str  # 响应时不应该包含密码
    id: int        # 请求时不应该包含ID

# 4. 不要忘记类型注解
username = Field(...)  # 缺少类型注解
```

### 5.3 代码组织最佳实践

```python
# models/user.py
"""
用户模型模块

包含用户相关的数据模型定义。
"""

# 1. 导入部分
from werkzeug.security import generate_password_hash
from app.extensions import db
from .base import BaseModel

# 2. 枚举定义
class UserRole(Enum):
    """用户角色枚举"""
    pass

# 3. 模型定义
class User(BaseModel):
    """用户模型"""
    
    # 3.1 表名
    __tablename__ = 'users'
    
    # 3.2 字段定义（分组）
    # 基本信息
    username = db.Column(...)
    
    # 外键
    class_id = db.Column(...)
    
    # 状态和时间
    status = db.Column(...)
    
    # 3.3 关系定义
    materials = db.relationship(...)
    
    # 3.4 实例方法
    def set_password(self): pass
    
    # 3.5 类方法
    @classmethod
    def get_by_email(cls): pass
    
    # 3.6 魔术方法
    def __repr__(self): pass
```

---

## 六、完整示例

### 6.1 Material模型完整示例

```python
# models/material.py
from app.extensions import db
from .base import BaseModel
from datetime import datetime

class Material(BaseModel):
    """资料模型
    
    存储所有教学资料的元数据和文件信息。
    """
    __tablename__ = 'materials'
    
    # ==================== 字段定义 ====================
    # 基本信息
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
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
    # 多对多: 资料和标签
    tags = db.relationship(
        'MaterialTag',
        secondary='material_tag_relation',
        backref='materials',
        lazy='dynamic'
    )
    
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
    
    # ==================== 类方法 ====================
    @classmethod
    def get_by_course(cls, course_id):
        """获取指定课程的所有资料"""
        return cls.query.filter_by(course_id=course_id).all()
    
    @classmethod
    def search(cls, keyword):
        """搜索资料"""
        return cls.query.filter(
            db.or_(
                cls.title.like(f'%{keyword}%'),
                cls.description.like(f'%{keyword}%')
            )
        ).all()
    
    def __repr__(self):
        return f'<Material {self.title}>'
```

### 6.2 Material Schema完整示例

```python
# schemas/material_schemas.py
from pydantic import Field, validator
from typing import Optional, List
from app.schemas.base_schemas import CamelCaseModel

class MaterialUploadModel(CamelCaseModel):
    """资料上传请求模型"""
    title: str = Field(..., description="资料标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="资料描述")
    course_id: Optional[int] = Field(None, description="课程ID", ge=1)
    category_id: Optional[int] = Field(None, description="分类ID", ge=1)
    tags: List[str] = Field(default_factory=list, description="标签列表")
    
    @validator('title')
    def validate_title(cls, v):
        """验证标题不能为空白"""
        if not v.strip():
            raise ValueError('标题不能为空白')
        return v.strip()

class MaterialUpdateModel(CamelCaseModel):
    """资料更新模型"""
    title: Optional[str] = Field(None, description="资料标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="资料描述")
    category_id: Optional[int] = Field(None, description="分类ID", ge=1)
    tags: Optional[List[str]] = Field(None, description="标签列表")

class MaterialResponseModel(CamelCaseModel):
    """资料响应模型"""
    id: int = Field(..., description="资料ID")
    title: str = Field(..., description="资料标题")
    description: Optional[str] = Field(None, description="资料描述")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., description="文件大小(字节)")
    file_type: str = Field(..., description="文件类型")
    course_id: Optional[int] = Field(None, description="课程ID")
    uploader_id: int = Field(..., description="上传者ID")
    category_id: Optional[int] = Field(None, description="分类ID")
    download_count: int = Field(..., description="下载次数")
    view_count: int = Field(..., description="浏览次数")
    keywords: Optional[str] = Field(None, description="关键词")
    auto_classified: bool = Field(..., description="是否自动分类")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")

class MaterialListResponseModel(CamelCaseModel):
    """资料列表响应模型"""
    materials: List[MaterialResponseModel] = Field(..., description="资料列表")
    total: int = Field(..., description="资料总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")

class MaterialQueryModel(CamelCaseModel):
    """资料查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    course_id: Optional[int] = Field(None, description="课程ID筛选", ge=1)
    category_id: Optional[int] = Field(None, description="分类ID筛选", ge=1)
    search: Optional[str] = Field(None, description="搜索关键词", max_length=100)
```

---

## 七、检查清单

### 7.1 模型类检查清单

- [ ] 继承自 `BaseModel`
- [ ] 定义 `__tablename__`
- [ ] 字段按类型分组并添加注释
- [ ] ⚠️ **外键字段不使用 `db.ForeignKey()`，只用注释标记 `# FK→table.id`**
- [ ] 外键字段添加索引 `index=True`
- [ ] 枚举字段使用Enum类
- [ ] 重写 `to_dict()` 方法排除敏感信息
- [ ] 添加必要的类方法和实例方法
- [ ] 实现 `__repr__()` 方法
- [ ] 关系定义正确配置lazy和cascade
- [ ] 添加完整的文档字符串

### 7.2 Schema检查清单

- [ ] 继承自 `CamelCaseModel`
- [ ] 所有字段都有类型注解
- [ ] 所有Field都有description
- [ ] 必填字段使用 `...`，可选字段使用 `None`
- [ ] 添加必要的validator
- [ ] 枚举继承 `str` 和 `Enum`
- [ ] 请求和响应Schema分离
- [ ] 列表响应包含分页信息
- [ ] 添加完整的文档字符串