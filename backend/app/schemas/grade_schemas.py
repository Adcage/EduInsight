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
