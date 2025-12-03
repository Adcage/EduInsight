"""
Schemas 模块 - 所有 Pydantic 数据模型
"""

# 基础模型
from .base_schemas import CamelCaseModel

# 用户相关模型
from .user_schemas import (
    UserRoleEnum,
    UserRegisterModel,
    UserLoginModel,
    UserUpdateModel,
    PasswordChangeModel,
    UserResponseModel,
    UserListResponseModel,
    UserPathModel,
    UserQueryModel,
    LoginResponseModel,
    MessageResponseModel,
    UserStatsModel,
    UserProfileModel,
)

# 通用模型
from .common_schemas import (
    BaseResponseModel,
    PaginationModel,
)

__all__ = [
    # 基础
    'CamelCaseModel',
    
    # 用户
    'UserRoleEnum',
    'UserRegisterModel',
    'UserLoginModel',
    'UserUpdateModel',
    'PasswordChangeModel',
    'UserResponseModel',
    'UserListResponseModel',
    'UserPathModel',
    'UserQueryModel',
    'LoginResponseModel',
    'MessageResponseModel',
    'UserStatsModel',
    'UserProfileModel',
    
    # 通用
    'BaseResponseModel',
    'PaginationModel',
]
