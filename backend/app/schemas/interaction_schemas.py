"""
课堂互动模块Schema

包含投票、提问、回答、弹幕相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.base_schemas import CamelCaseModel


# ==================== 枚举 ====================

class PollTypeEnum(str, Enum):
    """投票类型枚举"""
    SINGLE = 'single'
    MULTIPLE = 'multiple'


class PollStatusEnum(str, Enum):
    """投票状态枚举"""
    ACTIVE = 'active'
    ENDED = 'ended'


class QuestionStatusEnum(str, Enum):
    """问题状态枚举"""
    PENDING = 'pending'
    ANSWERED = 'answered'


# ==================== 投票 Schema ====================

class PollCreateModel(CamelCaseModel):
    """投票创建模型"""
    title: str = Field(..., description="投票标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="投票描述")
    course_id: int = Field(..., description="课程ID", ge=1)
    poll_type: PollTypeEnum = Field(..., description="投票类型")
    options: List[dict] = Field(..., description="选项列表", min_items=2)
    is_anonymous: bool = Field(False, description="是否匿名")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    
    @validator('end_time')
    def validate_time(cls, v, values):
        """验证时间"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v
    
    @validator('options')
    def validate_options(cls, v):
        """验证选项"""
        if len(v) > 20:
            raise ValueError('选项数量不能超过20个')
        for option in v:
            if 'id' not in option or 'text' not in option:
                raise ValueError('选项必须包含id和text字段')
        return v


class PollUpdateModel(CamelCaseModel):
    """投票更新模型"""
    title: Optional[str] = Field(None, description="投票标题", min_length=1, max_length=200)
    description: Optional[str] = Field(None, description="投票描述")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    status: Optional[PollStatusEnum] = Field(None, description="投票状态")


class PollResponseModel(CamelCaseModel):
    """投票响应模型"""
    id: int = Field(..., description="投票ID")
    title: str = Field(..., description="投票标题")
    description: Optional[str] = Field(None, description="投票描述")
    course_id: int = Field(..., description="课程ID")
    teacher_id: int = Field(..., description="教师ID")
    poll_type: str = Field(..., description="投票类型")
    options: List[dict] = Field(..., description="选项列表")
    is_anonymous: bool = Field(..., description="是否匿名")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    status: str = Field(..., description="投票状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class PollDetailResponseModel(PollResponseModel):
    """投票详情响应模型"""
    course_name: Optional[str] = Field(None, description="课程名称")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    response_count: int = Field(0, description="投票人数")
    results: Optional[dict] = Field(None, description="投票结果")


class PollListResponseModel(CamelCaseModel):
    """投票列表响应模型"""
    polls: List[PollResponseModel] = Field(..., description="投票列表")
    total: int = Field(..., description="投票总数")


class PollPathModel(CamelCaseModel):
    """投票路径参数模型"""
    poll_id: int = Field(..., description="投票ID", ge=1)


# ==================== 投票响应 Schema ====================

class PollVoteModel(CamelCaseModel):
    """投票模型"""
    selected_options: List[int] = Field(..., description="选中的选项ID列表", min_items=1)
    
    @validator('selected_options')
    def validate_selected_options(cls, v):
        """验证选项"""
        if len(v) != len(set(v)):
            raise ValueError('不能重复选择相同选项')
        return v


class PollResponseResponseModel(CamelCaseModel):
    """投票响应响应模型"""
    id: int = Field(..., description="响应ID")
    poll_id: int = Field(..., description="投票ID")
    student_id: int = Field(..., description="学生ID")
    selected_options: List[int] = Field(..., description="选中的选项")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


# ==================== 提问 Schema ====================

class QuestionCreateModel(CamelCaseModel):
    """提问创建模型"""
    content: str = Field(..., description="问题内容", min_length=1)
    course_id: int = Field(..., description="课程ID", ge=1)
    is_anonymous: bool = Field(False, description="是否匿名")
    
    @validator('content')
    def validate_content(cls, v):
        """验证内容"""
        if len(v) > 1000:
            raise ValueError('问题内容不能超过1000字')
        return v.strip()


class QuestionUpdateModel(CamelCaseModel):
    """提问更新模型"""
    content: Optional[str] = Field(None, description="问题内容", min_length=1)
    status: Optional[QuestionStatusEnum] = Field(None, description="问题状态")


class QuestionResponseModel(CamelCaseModel):
    """提问响应模型"""
    id: int = Field(..., description="问题ID")
    content: str = Field(..., description="问题内容")
    course_id: int = Field(..., description="课程ID")
    user_id: int = Field(..., description="提问者ID")
    is_anonymous: bool = Field(..., description="是否匿名")
    status: str = Field(..., description="问题状态")
    like_count: int = Field(..., description="点赞数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class QuestionDetailResponseModel(QuestionResponseModel):
    """提问详情响应模型"""
    user_name: Optional[str] = Field(None, description="提问者姓名")
    course_name: Optional[str] = Field(None, description="课程名称")
    answer_count: int = Field(0, description="回答数量")
    answers: List['QuestionAnswerResponseModel'] = Field(default_factory=list, description="回答列表")


class QuestionListResponseModel(CamelCaseModel):
    """提问列表响应模型"""
    questions: List[QuestionDetailResponseModel] = Field(..., description="提问列表")
    total: int = Field(..., description="提问总数")


class QuestionPathModel(CamelCaseModel):
    """提问路径参数模型"""
    question_id: int = Field(..., description="问题ID", ge=1)


# ==================== 回答 Schema ====================

class QuestionAnswerCreateModel(CamelCaseModel):
    """回答创建模型"""
    content: str = Field(..., description="回答内容", min_length=1)
    
    @validator('content')
    def validate_content(cls, v):
        """验证内容"""
        if len(v) > 2000:
            raise ValueError('回答内容不能超过2000字')
        return v.strip()


class QuestionAnswerUpdateModel(CamelCaseModel):
    """回答更新模型"""
    content: Optional[str] = Field(None, description="回答内容", min_length=1)
    is_accepted: Optional[bool] = Field(None, description="是否采纳")


class QuestionAnswerResponseModel(CamelCaseModel):
    """回答响应模型"""
    id: int = Field(..., description="回答ID")
    question_id: int = Field(..., description="问题ID")
    user_id: int = Field(..., description="回答者ID")
    content: str = Field(..., description="回答内容")
    is_accepted: bool = Field(..., description="是否被采纳")
    like_count: int = Field(..., description="点赞数")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class QuestionAnswerDetailResponseModel(QuestionAnswerResponseModel):
    """回答详情响应模型"""
    user_name: Optional[str] = Field(None, description="回答者姓名")


class QuestionAnswerPathModel(CamelCaseModel):
    """回答路径参数模型"""
    answer_id: int = Field(..., description="回答ID", ge=1)


# ==================== 弹幕 Schema ====================

class BarrageCreateModel(CamelCaseModel):
    """弹幕创建模型"""
    content: str = Field(..., description="弹幕内容", min_length=1, max_length=200)
    course_id: int = Field(..., description="课程ID", ge=1)
    is_anonymous: bool = Field(False, description="是否匿名")
    
    @validator('content')
    def validate_content(cls, v):
        """验证内容"""
        return v.strip()


class BarrageResponseModel(CamelCaseModel):
    """弹幕响应模型"""
    id: int = Field(..., description="弹幕ID")
    content: str = Field(..., description="弹幕内容")
    course_id: int = Field(..., description="课程ID")
    user_id: int = Field(..., description="用户ID")
    is_anonymous: bool = Field(..., description="是否匿名")
    status: bool = Field(..., description="状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class BarrageDetailResponseModel(BarrageResponseModel):
    """弹幕详情响应模型"""
    user_name: Optional[str] = Field(None, description="用户姓名")


class BarrageListResponseModel(CamelCaseModel):
    """弹幕列表响应模型"""
    barrages: List[BarrageDetailResponseModel] = Field(..., description="弹幕列表")
    total: int = Field(..., description="弹幕总数")


class BarragePathModel(CamelCaseModel):
    """弹幕路径参数模型"""
    barrage_id: int = Field(..., description="弹幕ID", ge=1)
