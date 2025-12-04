"""
考勤管理模块Schema

包含考勤任务、考勤记录、考勤统计相关的请求和响应模型。
"""
from pydantic import Field, validator
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.base_schemas import CamelCaseModel


# ==================== 枚举 ====================

class AttendanceTypeEnum(str, Enum):
    """考勤方式枚举"""
    QRCODE = 'qrcode'
    MANUAL = 'manual'
    FACE = 'face'


class AttendanceStatusEnum(str, Enum):
    """考勤状态枚举"""
    PENDING = 'pending'
    ACTIVE = 'active'
    ENDED = 'ended'


class CheckInStatusEnum(str, Enum):
    """签到状态枚举"""
    PRESENT = 'present'
    LATE = 'late'
    ABSENT = 'absent'
    LEAVE = 'leave'


# ==================== 考勤任务 Schema ====================

class AttendanceCreateModel(CamelCaseModel):
    """考勤任务创建模型"""
    title: str = Field(..., description="考勤标题", min_length=1, max_length=100)
    course_id: int = Field(..., description="课程ID", ge=1)
    class_id: Optional[int] = Field(None, description="班级ID", ge=1)
    attendance_type: AttendanceTypeEnum = Field(..., description="考勤方式")
    location: Optional[str] = Field(None, description="考勤地点", max_length=100)
    require_location: bool = Field(False, description="是否需要位置验证")
    start_time: datetime = Field(..., description="开始时间")
    end_time: datetime = Field(..., description="结束时间")
    
    @validator('end_time')
    def validate_time(cls, v, values):
        """验证时间"""
        if 'start_time' in values and v <= values['start_time']:
            raise ValueError('结束时间必须晚于开始时间')
        return v


class AttendanceUpdateModel(CamelCaseModel):
    """考勤任务更新模型"""
    title: Optional[str] = Field(None, description="考勤标题", min_length=1, max_length=100)
    location: Optional[str] = Field(None, description="考勤地点", max_length=100)
    end_time: Optional[datetime] = Field(None, description="结束时间")
    status: Optional[AttendanceStatusEnum] = Field(None, description="考勤状态")


class AttendanceResponseModel(CamelCaseModel):
    """考勤任务响应模型"""
    id: int = Field(..., description="考勤ID")
    title: str = Field(..., description="考勤标题")
    course_id: int = Field(..., description="课程ID")
    class_id: Optional[int] = Field(None, description="班级ID")
    teacher_id: int = Field(..., description="教师ID")
    attendance_type: str = Field(..., description="考勤方式")
    qr_code: Optional[str] = Field(None, description="二维码token")
    location: Optional[str] = Field(None, description="考勤地点")
    require_location: bool = Field(..., description="是否需要位置验证")
    start_time: str = Field(..., description="开始时间")
    end_time: str = Field(..., description="结束时间")
    status: str = Field(..., description="考勤状态")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class AttendanceDetailResponseModel(AttendanceResponseModel):
    """考勤任务详情响应模型"""
    course_name: Optional[str] = Field(None, description="课程名称")
    teacher_name: Optional[str] = Field(None, description="教师姓名")
    present_count: int = Field(0, description="出勤人数")
    late_count: int = Field(0, description="迟到人数")
    absent_count: int = Field(0, description="缺勤人数")
    leave_count: int = Field(0, description="请假人数")
    attendance_rate: float = Field(0.0, description="出勤率")


class AttendanceListResponseModel(CamelCaseModel):
    """考勤任务列表响应模型"""
    attendances: List[AttendanceResponseModel] = Field(..., description="考勤列表")
    total: int = Field(..., description="考勤总数")
    page: int = Field(1, description="当前页码")
    per_page: int = Field(20, description="每页数量")
    pages: int = Field(..., description="总页数")


class AttendanceQueryModel(CamelCaseModel):
    """考勤查询参数模型"""
    page: int = Field(1, description="页码", ge=1)
    per_page: int = Field(20, description="每页数量", ge=1, le=100)
    course_id: Optional[int] = Field(None, description="课程ID筛选", ge=1)
    teacher_id: Optional[int] = Field(None, description="教师ID筛选", ge=1)
    status: Optional[AttendanceStatusEnum] = Field(None, description="状态筛选")


class AttendancePathModel(CamelCaseModel):
    """考勤路径参数模型"""
    attendance_id: int = Field(..., description="考勤ID", ge=1)


# ==================== 考勤记录 Schema ====================

class AttendanceCheckInModel(CamelCaseModel):
    """学生签到模型"""
    qr_code: Optional[str] = Field(None, description="二维码token")
    latitude: Optional[float] = Field(None, description="签到纬度", ge=-90, le=90)
    longitude: Optional[float] = Field(None, description="签到经度", ge=-180, le=180)
    face_image: Optional[str] = Field(None, description="人脸照片Base64")


class AttendanceRecordCreateModel(CamelCaseModel):
    """考勤记录创建模型（教师手动签到）"""
    student_id: int = Field(..., description="学生ID", ge=1)
    status: CheckInStatusEnum = Field(..., description="签到状态")
    remark: Optional[str] = Field(None, description="备注", max_length=255)


class AttendanceRecordUpdateModel(CamelCaseModel):
    """考勤记录更新模型"""
    status: CheckInStatusEnum = Field(..., description="签到状态")
    remark: Optional[str] = Field(None, description="备注", max_length=255)


class AttendanceRecordResponseModel(CamelCaseModel):
    """考勤记录响应模型"""
    id: int = Field(..., description="记录ID")
    attendance_id: int = Field(..., description="考勤ID")
    student_id: int = Field(..., description="学生ID")
    status: str = Field(..., description="签到状态")
    check_in_time: Optional[str] = Field(None, description="签到时间")
    check_in_method: Optional[str] = Field(None, description="签到方式")
    latitude: Optional[float] = Field(None, description="签到纬度")
    longitude: Optional[float] = Field(None, description="签到经度")
    face_image_path: Optional[str] = Field(None, description="人脸照片路径")
    remark: Optional[str] = Field(None, description="备注")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class AttendanceRecordDetailResponseModel(AttendanceRecordResponseModel):
    """考勤记录详情响应模型"""
    student_name: Optional[str] = Field(None, description="学生姓名")
    student_code: Optional[str] = Field(None, description="学号")


class AttendanceRecordListResponseModel(CamelCaseModel):
    """考勤记录列表响应模型"""
    records: List[AttendanceRecordDetailResponseModel] = Field(..., description="考勤记录列表")
    total: int = Field(..., description="记录总数")


# ==================== 考勤统计 Schema ====================

class AttendanceStatisticsResponseModel(CamelCaseModel):
    """考勤统计响应模型"""
    id: int = Field(..., description="统计ID")
    course_id: int = Field(..., description="课程ID")
    student_id: int = Field(..., description="学生ID")
    total_count: int = Field(..., description="总考勤次数")
    present_count: int = Field(..., description="出勤次数")
    late_count: int = Field(..., description="迟到次数")
    absent_count: int = Field(..., description="缺勤次数")
    leave_count: int = Field(..., description="请假次数")
    attendance_rate: float = Field(..., description="出勤率(%)")
    created_at: str = Field(..., description="创建时间")
    updated_at: str = Field(..., description="更新时间")


class AttendanceStatisticsDetailResponseModel(AttendanceStatisticsResponseModel):
    """考勤统计详情响应模型"""
    student_name: Optional[str] = Field(None, description="学生姓名")
    student_code: Optional[str] = Field(None, description="学号")
    course_name: Optional[str] = Field(None, description="课程名称")


class AttendanceStatisticsListResponseModel(CamelCaseModel):
    """考勤统计列表响应模型"""
    statistics: List[AttendanceStatisticsDetailResponseModel] = Field(..., description="统计列表")
    total: int = Field(..., description="统计总数")
