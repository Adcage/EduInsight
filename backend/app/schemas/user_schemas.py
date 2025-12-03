from pydantic import Field, EmailStr, validator
from typing import Optional, List
from enum import Enum
from app.schemas.base_schemas import CamelCaseModel

class UserRoleEnum(str, Enum):
    """用户角色枚举"""
    ADMIN = 'admin'
    TEACHER = 'teacher'
    STUDENT = 'student'

class UserRegisterModel(CamelCaseModel):
    """用户注册请求模型"""
    username: str = Field(..., description="用户名", min_length=3, max_length=50)
    user_code: str = Field(..., description="工号/学号", min_length=1, max_length=50)
    password: str = Field(..., description="密码", min_length=6, max_length=128)
    email: EmailStr = Field(..., description="邮箱地址")
    real_name: str = Field(..., description="真实姓名", min_length=1, max_length=50)
    role: UserRoleEnum = Field(UserRoleEnum.STUDENT, description="用户角色")
    phone: Optional[str] = Field(None, description="手机号码", max_length=20)
    class_id: Optional[int] = Field(None, description="班级ID（学生角色时使用）", ge=1)
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v
    
    @validator('user_code')
    def validate_user_code(cls, v):
        """验证工号/学号格式"""
        if not v.replace('-', '').isalnum():
            raise ValueError('工号/学号只能包含字母、数字和连字符')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            # 简单的手机号验证
            import re
            if not re.match(r'^1[3-9]\d{9}$', v):
                raise ValueError('请输入有效的手机号码')
        return v
    
    @validator('class_id', always=True)
    def validate_class_id(cls, v, values):
        """验证班级ID（学生角色时必须提供）"""
        role = values.get('role')
        if role == UserRoleEnum.STUDENT and v is None:
            raise ValueError('学生角色必须指定班级ID')
        elif role != UserRoleEnum.STUDENT and v is not None:
            # 非学生角色不需要班级ID
            return None
        return v

class UserLoginModel(CamelCaseModel):
    """用户登录请求模型"""
    login_identifier: str = Field(..., description="登录标识符（邮箱/用户名/工号）", min_length=1)
    password: str = Field(..., description="密码", min_length=1)

class UserUpdateModel(CamelCaseModel):
    """用户信息更新模型"""
    username: Optional[str] = Field(None, description="用户名", min_length=3, max_length=50)
    email: Optional[EmailStr] = Field(None, description="邮箱地址")
    real_name: Optional[str] = Field(None, description="真实姓名", min_length=1, max_length=50)
    phone: Optional[str] = Field(None, description="手机号码", max_length=20)
    avatar: Optional[str] = Field(None, description="头像URL", max_length=255)
    
    @validator('username')
    def validate_username(cls, v):
        """验证用户名格式"""
        if v is not None and not v.replace('_', '').replace('-', '').isalnum():
            raise ValueError('用户名只能包含字母、数字、下划线和连字符')
        return v
    
    @validator('phone')
    def validate_phone(cls, v):
        """验证手机号格式"""
        if v is not None:
            import re
            if not re.match(r'^1[3-9]\d{9}$', v):
                raise ValueError('请输入有效的手机号码')
        return v

class PasswordChangeModel(CamelCaseModel):
    """密码修改模型"""
    old_password: str = Field(..., description="原密码", min_length=1)
    new_password: str = Field(..., description="新密码", min_length=6, max_length=128)
    confirm_password: str = Field(..., description="确认新密码", min_length=6, max_length=128)
    
    @validator('confirm_password')
    def validate_passwords_match(cls, v, values):
        """验证两次密码输入是否一致"""
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('两次输入的密码不一致')
        return v

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

class UserListResponseModel(CamelCaseModel):
    """用户列表响应模型"""
    users: List[UserResponseModel] = Field(..., description="用户列表")
    total: int = Field(..., description="用户总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")

class UserPathModel(CamelCaseModel):
    """用户路径参数模型"""
    user_id: int = Field(..., description="用户ID", ge=1)

class UserQueryModel(CamelCaseModel):
    """用户查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    role: Optional[UserRoleEnum] = Field(None, description="角色筛选")
    status: Optional[bool] = Field(None, description="状态筛选")
    search: Optional[str] = Field(None, description="搜索关键词（用户名、真实姓名、邮箱）", max_length=100)

class LoginResponseModel(CamelCaseModel):
    """登录响应模型"""
    user: UserResponseModel = Field(..., description="用户信息")
    message: str = Field(..., description="登录结果消息")

class MessageResponseModel(CamelCaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="响应消息")
    error_code: Optional[str] = Field(None, description="错误代码")

class UserStatsModel(CamelCaseModel):
    """用户统计模型"""
    total_users: int = Field(..., description="用户总数")
    admin_count: int = Field(..., description="管理员数量")
    teacher_count: int = Field(..., description="教师数量")
    student_count: int = Field(..., description="学生数量")
    active_users: int = Field(..., description="活跃用户数")
    inactive_users: int = Field(..., description="非活跃用户数")

class UserProfileModel(CamelCaseModel):
    """用户个人资料模型"""
    username: str = Field(..., description="用户名")
    user_code: str = Field(..., description="工号/学号")
    email: str = Field(..., description="邮箱地址")
    real_name: str = Field(..., description="真实姓名")
    role: str = Field(..., description="用户角色")
    phone: Optional[str] = Field(None, description="手机号码")
    avatar: Optional[str] = Field(None, description="头像URL")
    class_id: Optional[int] = Field(None, description="班级ID")
    last_login_time: Optional[str] = Field(None, description="最后登录时间")
    created_at: str = Field(..., description="注册时间")
