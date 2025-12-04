"""
课程模块Schema

包含课程相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from datetime import date
from app.schemas.base_schemas import CamelCaseModel


# ==================== 课程 Schema ====================

class CourseCreateModel(CamelCaseModel):
    """课程创建模型"""
    name: str = Field(..., description="课程名称", min_length=1, max_length=100)
    code: str = Field(..., description="课程代码", min_length=1, max_length=50)
    description: Optional[str] = Field(None, description="课程描述")
    semester: str = Field(..., description="学期(如:2024-2025-1)", max_length=20)
    academic_year: str = Field(..., description="学年(如:2024-2025)", max_length=20)
    credit: Optional[float] = Field(None, description="学分", ge=0, le=10)
    total_hours: Optional[int] = Field(None, description="总学时", ge=0)
    teacher_id: int = Field(..., description="教师ID", ge=1)
    
    @validator('code')
    def validate_code(cls, v):
        """验证课程代码"""
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('课程代码只能包含字母、数字、连字符和下划线')
        return v.upper()
    
    @validator('semester')
    def validate_semester(cls, v):
        """验证学期格式"""
        import re
        if not re.match(r'^\d{4}-\d{4}-[12]$', v):
            raise ValueError('学期格式应为: YYYY-YYYY-1或YYYY-YYYY-2')
        return v
    
    @validator('academic_year')
    def validate_academic_year(cls, v):
        """验证学年格式"""
        import re
        if not re.match(r'^\d{4}-\d{4}$', v):
            raise ValueError('学年格式应为: YYYY-YYYY')
        return v


class CourseUpdateModel(CamelCaseModel):
    """课程更新模型"""
    name: Optional[str] = Field(None, description="课程名称", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="课程描述")
    credit: Optional[float] = Field(None, description="学分", ge=0, le=10)
    total_hours: Optional[int] = Field(None, description="总学时", ge=0)
    status: Optional[bool] = Field(None, description="课程状态")


class CourseResponseModel(CamelCaseModel):
    """课程响应模型"""
    id: int = Field(..., description="课程ID")
    name: str = Field(..., description="课程名称")
    code: str = Field(..., description="课程代码")
    description: Optional[str] = Field(None, description="课程描述")
    semester: str = Field(..., description="学期")
    academic_year: str = Field(..., description="学年")
    credit: Optional[float] = Field(None, description="学分")
    total_hours: Optional[int] = Field(None, description="总学时")
    teacher_id: int = Field(..., description="教师ID")
    status: bool = Field(..., description="课程状态")
    class_count: Optional[int] = Field(None, description="班级数")
    student_count: Optional[int] = Field(None, description="学生数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class CourseDetailResponseModel(CourseResponseModel):
    """课程详情响应模型（包含关联信息）"""
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    teacher_email: Optional[str] = Field(None, description="教师邮箱")


class CourseListResponseModel(CamelCaseModel):
    """课程列表响应模型"""
    courses: List[CourseResponseModel] = Field(..., description="课程列表")
    total: int = Field(..., description="课程总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")


class CourseQueryModel(CamelCaseModel):
    """课程查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    teacher_id: Optional[int] = Field(None, description="教师ID筛选", ge=1)
    semester: Optional[str] = Field(None, description="学期筛选", max_length=20)
    status: Optional[bool] = Field(None, description="状态筛选")
    include_stats: bool = Field(True, description="是否包含统计信息")
    search: Optional[str] = Field(None, description="搜索关键词（课程名、代码）", max_length=100)


class CoursePathModel(CamelCaseModel):
    """课程路径参数模型"""
    course_id: int = Field(..., description="课程ID", ge=1)


class CourseClassAddModel(CamelCaseModel):
    """课程添加班级模型"""
    class_ids: List[int] = Field(..., description="班级ID列表", min_items=1)
    start_date: Optional[date] = Field(None, description="开始日期")
    end_date: Optional[date] = Field(None, description="结束日期")
    
    @validator('end_date')
    def validate_dates(cls, v, values):
        """验证日期"""
        if v and 'start_date' in values and values['start_date']:
            if v < values['start_date']:
                raise ValueError('结束日期不能早于开始日期')
        return v


class CourseStatsModel(CamelCaseModel):
    """课程统计模型"""
    total_courses: int = Field(..., description="课程总数")
    active_courses: int = Field(..., description="进行中课程数")
    total_students: int = Field(..., description="总学生数")
    total_materials: int = Field(..., description="总资料数")
    by_semester: dict = Field(..., description="按学期统计")
    by_teacher: dict = Field(..., description="按教师统计")


class CourseClassInfoModel(CamelCaseModel):
    """课程班级信息模型"""
    class_id: int = Field(..., description="班级ID")
    class_name: str = Field(..., description="班级名称")
    class_code: str = Field(..., description="班级代码")
    grade: Optional[str] = Field(None, description="年级")
    major: Optional[str] = Field(None, description="专业")
    student_count: int = Field(0, description="班级学生数")
    start_date: Optional[str] = Field(None, description="课程开始日期")
    end_date: Optional[str] = Field(None, description="课程结束日期")
    status: bool = Field(True, description="关联状态")


class CourseClassListResponseModel(CamelCaseModel):
    """课程班级列表响应模型"""
    classes: List[CourseClassInfoModel] = Field(..., description="班级列表")
    total: int = Field(..., description="班级总数")
    total_students: int = Field(0, description="总学生数")
