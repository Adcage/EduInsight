from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional, List
from datetime import datetime

class UserCreateModel(BaseModel):
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

class UserUpdateModel(BaseModel):
    """用户更新模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="用户姓名")
    email: Optional[EmailStr] = Field(None, description="用户邮箱")
    phone: Optional[str] = Field(None, max_length=20, description="手机号码")
    age: Optional[int] = Field(None, ge=0, le=150, description="年龄")
    
    @validator('phone')
    def validate_phone(cls, v):
        if v and not v.isdigit():
            raise ValueError('手机号码只能包含数字')
        return v

class UserResponseModel(BaseModel):
    """用户响应模型"""
    id: int
    name: str
    email: str
    phone: Optional[str] = None
    age: Optional[int] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class UserListResponseModel(BaseModel):
    """用户列表响应模型"""
    users: List[UserResponseModel]
    total: int

class UserPathModel(BaseModel):
    """用户路径参数模型"""
    user_id: int = Field(..., description="用户ID")
