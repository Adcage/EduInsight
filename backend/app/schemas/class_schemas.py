"""
班级相关Schema定义
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class ClassPathModel(BaseModel):
    """班级路径参数模型"""
    class_id: int = Field(..., description="班级ID", ge=1)


class StudentInfoModel(BaseModel):
    """学生信息模型"""
    id: int = Field(..., description="学生ID")
    user_code: str = Field(..., description="学号")
    real_name: str = Field(..., description="真实姓名")
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    phone: Optional[str] = Field(None, description="手机号")
    avatar: Optional[str] = Field(None, description="头像URL")
    status: bool = Field(..., description="状态：True-正常，False-禁用")
    last_login_time: Optional[datetime] = Field(None, description="最后登录时间")
    created_at: datetime = Field(..., description="创建时间")


class ClassStudentsResponseModel(BaseModel):
    """班级学生列表响应模型"""
    class_id: int = Field(..., description="班级ID")
    class_name: str = Field(..., description="班级名称")
    class_code: str = Field(..., description="班级代码")
    grade: Optional[str] = Field(None, description="年级")
    major: Optional[str] = Field(None, description="专业")
    students: List[StudentInfoModel] = Field(..., description="学生列表")
    total: int = Field(..., description="学生总数")


class ClassInfoModel(BaseModel):
    """班级信息模型"""
    id: int = Field(..., description="班级ID")
    name: str = Field(..., description="班级名称")
    code: str = Field(..., description="班级代码")
    description: Optional[str] = Field(None, description="班级描述")
    grade: Optional[str] = Field(None, description="年级")
    major: Optional[str] = Field(None, description="专业")
    teacher_id: Optional[int] = Field(None, description="班主任ID")
    status: bool = Field(..., description="状态")
    student_count: int = Field(0, description="学生人数")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class ClassListResponseModel(BaseModel):
    """班级列表响应模型"""
    classes: List[ClassInfoModel] = Field(..., description="班级列表")
    total: int = Field(..., description="总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(1, description="总页数")
