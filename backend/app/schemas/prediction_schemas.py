"""
预警预测模块Schema定义
"""
from pydantic import Field, BaseModel
from typing import Optional, List
from datetime import date
from app.schemas.base_schemas import CamelCaseModel


class PredictionIdPath(BaseModel):
    """预警ID路径参数"""
    prediction_id: int = Field(..., description="预警ID", ge=1)


class InterventionIdPath(BaseModel):
    """干预ID路径参数"""
    intervention_id: int = Field(..., description="干预ID", ge=1)


class GeneratePredictionModel(CamelCaseModel):
    """生成预警请求模型"""
    course_id: int = Field(..., description="课程ID", ge=1)
    class_id: Optional[int] = Field(None, description="班级ID(可选)", ge=1)


class PredictionQueryModel(CamelCaseModel):
    """预警查询参数模型"""
    course_id: int = Field(..., description="课程ID", ge=1)
    class_id: Optional[int] = Field(None, description="班级ID(可选)", ge=1)
    risk_level: Optional[str] = Field(None, description="风险等级筛选(high/medium/low/none)")


class PredictionItemModel(CamelCaseModel):
    """预警列表项模型"""
    id: int = Field(..., description="预警ID")
    student_id: int = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    student_code: str = Field(..., description="学号")
    class_name: Optional[str] = Field(None, description="班级名称")
    course_id: int = Field(..., description="课程ID")
    course_name: str = Field(..., description="课程名称")
    predicted_score: float = Field(..., description="预测分数")
    confidence: float = Field(..., description="置信度(%)")
    risk_level: str = Field(..., description="风险等级")
    prediction_date: str = Field(..., description="预测日期")
    is_sent: bool = Field(..., description="是否已发送通知")
    intervention_count: int = Field(..., description="干预次数")
    created_at: str = Field(..., description="创建时间")


class HistoricalGradeModel(CamelCaseModel):
    """历史成绩模型"""
    exam_type: str = Field(..., description="考试类型")
    exam_name: Optional[str] = Field(None, description="考试名称")
    score: float = Field(..., description="分数")
    exam_date: str = Field(..., description="考试日期")


class InterventionModel(CamelCaseModel):
    """干预记录模型"""
    id: int = Field(..., description="干预ID")
    prediction_id: int = Field(..., description="预警ID")
    teacher_id: int = Field(..., description="教师ID")
    teacher_name: str = Field(..., description="教师姓名")
    intervention_date: str = Field(..., description="干预日期")
    intervention_type: str = Field(..., description="干预方式")
    description: str = Field(..., description="干预内容")
    expected_effect: Optional[str] = Field(None, description="预期效果")
    actual_effect: Optional[str] = Field(None, description="实际效果")
    student_feedback: Optional[str] = Field(None, description="学生反馈")
    created_at: str = Field(..., description="创建时间")


class PredictionDetailModel(CamelCaseModel):
    """预警详情模型"""
    id: int = Field(..., description="预警ID")
    student_id: int = Field(..., description="学生ID")
    student_name: str = Field(..., description="学生姓名")
    student_code: str = Field(..., description="学号")
    student_email: Optional[str] = Field(None, description="学生邮箱")
    course_id: int = Field(..., description="课程ID")
    course_name: str = Field(..., description="课程名称")
    predicted_score: float = Field(..., description="预测分数")
    confidence: float = Field(..., description="置信度(%)")
    risk_level: str = Field(..., description="风险等级")
    prediction_date: str = Field(..., description="预测日期")
    is_sent: bool = Field(..., description="是否已发送通知")
    historical_grades: List[HistoricalGradeModel] = Field(..., description="历史成绩列表")
    interventions: List[InterventionModel] = Field(..., description="干预记录列表")
    created_at: str = Field(..., description="创建时间")


class AddInterventionModel(CamelCaseModel):
    """添加干预记录请求模型"""
    prediction_id: int = Field(..., description="预警ID", ge=1)
    intervention_date: Optional[date] = Field(None, description="干预日期(默认今天)")
    intervention_type: str = Field(..., description="干预方式(talk/tutoring/homework/other)")
    description: str = Field(..., description="干预内容描述", min_length=1)
    expected_effect: Optional[str] = Field(None, description="预期效果")


class UpdateInterventionModel(CamelCaseModel):
    """更新干预记录请求模型"""
    actual_effect: Optional[str] = Field(None, description="实际效果")
    student_feedback: Optional[str] = Field(None, description="学生反馈")
    description: Optional[str] = Field(None, description="干预内容描述")
    expected_effect: Optional[str] = Field(None, description="预期效果")


class SendNotificationModel(CamelCaseModel):
    """发送通知请求模型"""
    prediction_ids: List[int] = Field(..., description="预警ID列表", min_items=1)


class GeneratePredictionResponseModel(CamelCaseModel):
    """生成预警响应模型"""
    total_students: int = Field(..., description="总学生数")
    predicted_count: int = Field(..., description="成功预测数")
    high_risk_count: int = Field(..., description="高风险人数")
    medium_risk_count: int = Field(..., description="中风险人数")
    low_risk_count: int = Field(..., description="低风险人数")
    no_risk_count: int = Field(..., description="无风险人数")
    skipped_count: int = Field(..., description="跳过人数(成绩不足)")
    predictions: List[dict] = Field(..., description="预测详情列表")


class SendNotificationResponseModel(CamelCaseModel):
    """发送通知响应模型"""
    total: int = Field(..., description="总数")
    success_count: int = Field(..., description="成功数")
    failed_count: int = Field(..., description="失败数")
