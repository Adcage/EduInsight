from pydantic import BaseModel, EmailStr, Field
from typing import Optional, Dict, Any
from .user_model import UserResponseModel

class LoginModel(BaseModel):
    """登录模型"""
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, description="密码")

class RegisterModel(BaseModel):
    """注册模型"""
    name: str = Field(..., min_length=1, max_length=100, description="用户姓名")
    email: EmailStr = Field(..., description="用户邮箱")
    password: str = Field(..., min_length=6, description="密码")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")

class TokenResponseModel(BaseModel):
    """令牌响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = Field(default="bearer", description="令牌类型")
    expires_in: int = Field(default=3600, description="过期时间（秒）")
    user: Dict[str, Any] = Field(..., description="用户信息")

class RefreshTokenModel(BaseModel):
    """刷新令牌模型"""
    refresh_token: str = Field(..., description="刷新令牌")

class ChangePasswordModel(BaseModel):
    """修改密码模型"""
    old_password: str = Field(..., min_length=6, description="旧密码")
    new_password: str = Field(..., min_length=6, description="新密码")
