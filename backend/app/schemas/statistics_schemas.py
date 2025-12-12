"""
统计分析模块Schema定义
"""
from pydantic import Field
from typing import Optional, List, Dict, Any
from app.schemas.base_schemas import CamelCaseModel
from app.schemas.grade_schemas import ExamTypeEnum


class StatisticsQueryModel(CamelCaseModel):
    """统计分析查询参数"""
    course_id: int = Field(..., description="课程ID", ge=1)
    class_id: Optional[int] = Field(None, description="班级ID(可选,用于更细致的统计)", ge=1)
    exam_type: Optional[str] = Field(None, description="考试类型筛选(可选,支持枚举值或'comprehensive')")


class BasicStatisticsModel(CamelCaseModel):
    """基础统计数据模型"""
    total_count: int = Field(..., description="总人数")
    average_score: float = Field(..., description="平均分")
    max_score: float = Field(..., description="最高分")
    min_score: float = Field(..., description="最低分")
    median_score: float = Field(..., description="中位数")
    std_deviation: float = Field(..., description="标准差")
    pass_rate: float = Field(..., description="及格率(%)")
    excellent_rate: float = Field(..., description="优秀率(%)")


class ScoreDistributionModel(CamelCaseModel):
    """分数段分布模型"""
    fail_count: int = Field(..., description="不及格(0-59)人数")
    pass_count: int = Field(..., description="及格(60-69)人数")
    medium_count: int = Field(..., description="中等(70-79)人数")
    good_count: int = Field(..., description="良好(80-89)人数")
    excellent_count: int = Field(..., description="优秀(90-100)人数")
    fail_rate: float = Field(..., description="不及格率(%)")
    pass_rate: float = Field(..., description="及格率(%)")
    medium_rate: float = Field(..., description="中等率(%)")
    good_rate: float = Field(..., description="良好率(%)")
    excellent_rate: float = Field(..., description="优秀率(%)")


class TrendDataPointModel(CamelCaseModel):
    """趋势数据点模型"""
    exam_type: str = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称")
    exam_date: str = Field(..., description="考试日期")
    average_score: float = Field(..., description="平均分")
    max_score: float = Field(..., description="最高分")
    min_score: float = Field(..., description="最低分")


class StudentTrendModel(CamelCaseModel):
    """学生成绩趋势模型"""
    student_id: int = Field(..., description="学生ID")
    student_code: str = Field(..., description="学号")
    student_name: str = Field(..., description="姓名")
    scores: List[Dict[str, Any]] = Field(..., description="成绩列表")


class StatisticsResponseModel(CamelCaseModel):
    """统计分析响应模型"""
    basic_statistics: BasicStatisticsModel = Field(..., description="基础统计")
    score_distribution: ScoreDistributionModel = Field(..., description="分数段分布")
    trend_data: List[TrendDataPointModel] = Field(..., description="趋势数据")
    course_name: str = Field(..., description="课程名称")
    class_name: Optional[str] = Field(None, description="班级名称")
    exam_type_filter: Optional[str] = Field(None, description="考试类型筛选")
