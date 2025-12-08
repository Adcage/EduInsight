"""
成绩管理模块Schema

包含成绩、成绩统计、成绩预测相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from datetime import date
from enum import Enum
from app.schemas.base_schemas import CamelCaseModel


# ==================== 枚举 ====================

class ExamTypeEnum(str, Enum):
    """考试类型枚举"""
    DAILY = 'daily'
    MIDTERM = 'midterm'
    FINAL = 'final'
    HOMEWORK = 'homework'


class RiskLevelEnum(str, Enum):
    """风险等级枚举"""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'


# ==================== 成绩 Schema ====================

class GradeCreateModel(CamelCaseModel):
    """成绩创建模型"""
    course_id: int = Field(..., description="课程ID", ge=1)
    student_id: int = Field(..., description="学生ID", ge=1)
    exam_type: ExamTypeEnum = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称", max_length=100)
    exam_date: Optional[date] = Field(None, description="考试日期")
    score: float = Field(..., description="分数", ge=0)
    full_score: float = Field(100.0, description="满分", ge=0)
    weight: float = Field(1.0, description="权重", ge=0, le=10)
    remark: Optional[str] = Field(None, description="备注", max_length=255)
    
    @validator('score')
    def validate_score(cls, v, values):
        """验证分数不能超过满分"""
        if 'full_score' in values and v > values['full_score']:
            raise ValueError('分数不能超过满分')
        return v


class GradeUpdateModel(CamelCaseModel):
    """成绩更新模型"""
    score: Optional[float] = Field(None, description="分数", ge=0)
    full_score: Optional[float] = Field(None, description="满分", ge=0)
    weight: Optional[float] = Field(None, description="权重", ge=0, le=10)
    remark: Optional[str] = Field(None, description="备注", max_length=255)


class GradeBatchImportModel(CamelCaseModel):
    """成绩批量导入模型"""
    course_id: int = Field(..., description="课程ID", ge=1)
    exam_type: ExamTypeEnum = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称", max_length=100)
    exam_date: Optional[date] = Field(None, description="考试日期")
    full_score: float = Field(100.0, description="满分", ge=0)
    weight: float = Field(1.0, description="权重", ge=0, le=10)
    grades: List[dict] = Field(..., description="成绩列表", min_items=1)


class GradeResponseModel(CamelCaseModel):
    """成绩响应模型"""
    id: int = Field(..., description="成绩ID")
    course_id: int = Field(..., description="课程ID")
    student_id: int = Field(..., description="学生ID")
    exam_type: str = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称")
    exam_date: Optional[str] = Field(None, description="考试日期")
    score: float = Field(..., description="分数")
    full_score: float = Field(..., description="满分")
    weight: float = Field(..., description="权重")
    remark: Optional[str] = Field(None, description="备注")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class GradeDetailResponseModel(GradeResponseModel):
    """成绩详情响应模型"""
    student_name: Optional[str] = Field(None, description="学生姓名")
    student_code: Optional[str] = Field(None, description="学号")
    course_name: Optional[str] = Field(None, description="课程名称")
    percentage: float = Field(..., description="百分比")
    is_pass: bool = Field(..., description="是否及格")


class GradeListResponseModel(CamelCaseModel):
    """成绩列表响应模型"""
    grades: List[GradeDetailResponseModel] = Field(..., description="成绩列表")
    total: int = Field(..., description="成绩总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")


class GradeQueryModel(CamelCaseModel):
    """成绩查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    course_id: Optional[int] = Field(None, description="课程ID筛选", ge=1)
    student_id: Optional[int] = Field(None, description="学生ID筛选", ge=1)
    exam_type: Optional[ExamTypeEnum] = Field(None, description="考试类型筛选")


class GradePathModel(CamelCaseModel):
    """成绩路径参数模型"""
    grade_id: int = Field(..., description="成绩ID", ge=1)


# ==================== 成绩统计 Schema ====================

class GradeStatisticsResponseModel(CamelCaseModel):
    """成绩统计响应模型"""
    id: int = Field(..., description="统计ID")
    course_id: int = Field(..., description="课程ID")
    exam_type: str = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称")
    total_students: int = Field(..., description="总人数")
    average_score: float = Field(..., description="平均分")
    highest_score: float = Field(..., description="最高分")
    lowest_score: float = Field(..., description="最低分")
    std_deviation: float = Field(..., description="标准差")
    median_score: float = Field(..., description="中位数")
    pass_rate: float = Field(..., description="及格率(%)")
    excellent_rate: float = Field(..., description="优秀率(%)")
    score_distribution: Optional[dict] = Field(None, description="分数段分布")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class GradeStatisticsDetailResponseModel(GradeStatisticsResponseModel):
    """成绩统计详情响应模型"""
    course_name: Optional[str] = Field(None, description="课程名称")


# ==================== 成绩预测 Schema ====================

class GradePredictionCreateModel(CamelCaseModel):
    """成绩预测创建模型"""
    student_id: int = Field(..., description="学生ID", ge=1)
    course_id: int = Field(..., description="课程ID", ge=1)


class GradePredictionResponseModel(CamelCaseModel):
    """成绩预测响应模型"""
    id: int = Field(..., description="预测ID")
    student_id: int = Field(..., description="学生ID")
    course_id: int = Field(..., description="课程ID")
    predicted_score: float = Field(..., description="预测分数")
    confidence: Optional[float] = Field(None, description="置信度")
    risk_level: str = Field(..., description="风险等级")
    is_warning: bool = Field(..., description="是否预警")
    prediction_date: str = Field(..., description="预测日期")
    model_version: Optional[str] = Field(None, description="模型版本")
    features_used: Optional[dict] = Field(None, description="使用的特征")
    recommendation: Optional[str] = Field(None, description="改进建议")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class GradePredictionDetailResponseModel(GradePredictionResponseModel):
    """成绩预测详情响应模型"""
    student_name: Optional[str] = Field(None, description="学生姓名")
    student_code: Optional[str] = Field(None, description="学号")
    course_name: Optional[str] = Field(None, description="课程名称")


class GradePredictionListResponseModel(CamelCaseModel):
    """成绩预测列表响应模型"""
    predictions: List[GradePredictionDetailResponseModel] = Field(..., description="预测列表")
    total: int = Field(..., description="预测总数")


# ==================== Excel导入相关 Schema ====================

class GradeImportResultModel(CamelCaseModel):
    """成绩导入结果模型"""
    total_rows: int = Field(..., description="总行数")
    success_count: int = Field(..., description="成功导入数量")
    skip_count: int = Field(..., description="跳过重复数量")
    fail_count: int = Field(..., description="失败数量")
    errors: List[dict] = Field(default_factory=list, description="错误列表")
    warnings: List[dict] = Field(default_factory=list, description="警告列表")


class MessageResponseModel(CamelCaseModel):
    """通用消息响应模型"""
    message: str = Field(..., description="消息内容")


class GradeTemplateQueryModel(CamelCaseModel):
    """成绩模板下载查询参数"""
    course_name: Optional[str] = Field(None, description="课程名称")


class GradeParseFormModel(CamelCaseModel):
    """Excel解析表单模型"""
    course_id: int = Field(..., description="课程ID", ge=1)


class GradeImportFormModel(CamelCaseModel):
    """成绩导入表单模型"""
    course_id: int = Field(..., description="课程ID", ge=1)
    exam_type: ExamTypeEnum = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称", max_length=100)
    exam_date: str = Field(..., description="考试日期(YYYY-MM-DD)")
    full_score: float = Field(100.0, description="满分", ge=0)
    weight: float = Field(1.0, description="权重", ge=0, le=10)


class GradeExportQueryModel(CamelCaseModel):
    """成绩导出查询参数"""
    course_id: int = Field(..., description="课程ID", ge=1)
    exam_type: Optional[ExamTypeEnum] = Field(None, description="考试类型筛选")


class TeacherCourseModel(CamelCaseModel):
    """教师课程模型"""
    id: int = Field(..., description="课程ID")
    name: str = Field(..., description="课程名称")
    code: str = Field(..., description="课程代码")
    semester: str = Field(..., description="学期")
    student_count: int = Field(0, description="学生人数")


class CourseStudentModel(CamelCaseModel):
    """课程学生模型"""
    id: int = Field(..., description="学生ID")
    user_code: str = Field(..., description="学号")
    real_name: str = Field(..., description="姓名")
    class_name: Optional[str] = Field(None, description="班级名称")
    grade_count: int = Field(0, description="该课程成绩数量")


class CourseIdQueryModel(CamelCaseModel):
    """课程ID查询参数"""
    course_id: int = Field(..., description="课程ID", ge=1)


class TeacherCourseListModel(CamelCaseModel):
    """教师课程列表响应模型"""
    courses: List[TeacherCourseModel] = Field(..., description="课程列表")


class CourseStudentListModel(CamelCaseModel):
    """课程学生列表响应模型"""
    students: List[CourseStudentModel] = Field(..., description="学生列表")


# ==================== 学生端成绩查看 Schema ====================

class StudentGradeQueryModel(CamelCaseModel):
    """学生成绩查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    course_id: Optional[int] = Field(None, description="课程ID筛选", ge=1)
    exam_type: Optional[ExamTypeEnum] = Field(None, description="考试类型筛选")


class StudentCourseGradeModel(CamelCaseModel):
    """学生课程成绩模型"""
    course_id: int = Field(..., description="课程ID")
    course_name: str = Field(..., description="课程名称")
    course_code: str = Field(..., description="课程代码")
    semester: str = Field(..., description="学期")
    grade_count: int = Field(..., description="成绩数量")
    average_score: Optional[float] = Field(None, description="平均分")
    highest_score: Optional[float] = Field(None, description="最高分")
    lowest_score: Optional[float] = Field(None, description="最低分")
    pass_rate: Optional[float] = Field(None, description="及格率(%)")


class StudentGradeStatisticsModel(CamelCaseModel):
    """学生成绩统计模型"""
    total_courses: int = Field(..., description="总课程数")
    total_grades: int = Field(..., description="总成绩数")
    average_score: Optional[float] = Field(None, description="总平均分")
    pass_count: int = Field(..., description="及格科目数")
    fail_count: int = Field(..., description="不及格科目数")
    pass_rate: Optional[float] = Field(None, description="及格率(%)")
