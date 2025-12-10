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
    QRCODE = 'qrcode'      # 二维码签到
    GESTURE = 'gesture'    # 手势签到
    LOCATION = 'location'  # 位置签到
    FACE = 'face'          # 人脸识别签到
    MANUAL = 'manual'      # 手动签到


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

class GesturePatternModel(CamelCaseModel):
    """手势路径数据模型"""
    points: List[dict] = Field(..., description="手势路径点数组")
    width: int = Field(..., description="画布宽度")
    height: int = Field(..., description="画布高度")
    duration: Optional[int] = Field(None, description="绘制时长（毫秒）")


class LocationConfigModel(CamelCaseModel):
    """位置配置模型"""
    name: str = Field(..., description="位置名称")
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    radius: int = Field(100, description="签到半径（米）", ge=10, le=1000)


class AttendanceCreateModel(CamelCaseModel):
    """考勤任务创建模型"""
    title: str = Field(..., description="考勤标题", min_length=1, max_length=100)
    description: Optional[str] = Field(None, description="考勤描述", max_length=255)
    course_id: int = Field(..., description="课程ID", ge=1)
    class_ids: List[int] = Field(..., description="班级ID列表（支持多选）", min_length=1)
    student_ids: Optional[List[int]] = Field(None, description="指定学生ID列表（可选，为空则选择所有班级学生）")
    attendance_type: AttendanceTypeEnum = Field(..., description="考勤方式")
    
    # 手势签到配置
    gesture_pattern: Optional[GesturePatternModel] = Field(None, description="手势路径数据")
    
    # 位置签到配置
    location_config: Optional[LocationConfigModel] = Field(None, description="位置签到配置")
    
    # 人脸识别配置
    face_recognition_threshold: Optional[float] = Field(0.80, description="人脸识别阈值", ge=0.0, le=1.0)
    
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
    description: Optional[str] = Field(None, description="考勤描述")
    course_id: int = Field(..., description="课程ID")
    class_id: Optional[int] = Field(None, description="班级ID")
    teacher_id: int = Field(..., description="教师ID")
    attendance_type: str = Field(..., description="考勤方式")
    
    # 二维码配置
    qr_code: Optional[str] = Field(None, description="二维码token")
    
    # 手势配置
    gesture_pattern: Optional[dict] = Field(None, description="手势路径数据")
    
    # 位置配置
    location_name: Optional[str] = Field(None, description="位置名称")
    location_latitude: Optional[float] = Field(None, description="纬度")
    location_longitude: Optional[float] = Field(None, description="经度")
    location_radius: Optional[int] = Field(None, description="签到半径（米）")
    
    # 人脸识别配置
    face_recognition_threshold: Optional[float] = Field(None, description="人脸识别阈值")
    
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


class QRCodeGenerateRequestModel(CamelCaseModel):
    """二维码生成请求模型"""
    token: str = Field(..., description="前端生成的token", min_length=1)


class QRCodeGenerateResponseModel(CamelCaseModel):
    """二维码生成响应模型"""
    qr_code_token: str = Field(..., description="二维码令牌")
    qr_code_data: str = Field(..., description="二维码数据（JSON字符串）")
    expires_at: str = Field(..., description="过期时间")
    valid_duration: int = Field(..., description="有效时长（秒）")


class QRCodeVerifyModel(CamelCaseModel):
    """二维码验证模型"""
    qr_code_token: str = Field(..., description="二维码令牌", min_length=1)
    attendance_id: int = Field(..., description="考勤ID", ge=1)
    student_number: Optional[str] = Field(None, description="学号（不登录时必填）", min_length=1)


class FaceVerificationModel(CamelCaseModel):
    """人脸验证模型"""
    student_number: str = Field(..., description="学号", min_length=1)
    face_image_base64: str = Field(..., description="人脸照片Base64编码", min_length=1)
    attendance_id: int = Field(..., description="考勤ID", ge=1)


class FaceVerificationResponseModel(CamelCaseModel):
    """人脸验证响应模型"""
    verified: bool = Field(..., description="是否验证通过")
    similarity: float = Field(..., description="相似度（0-1）")
    message: str = Field(..., description="验证消息")
    has_face_image: bool = Field(..., description="用户是否已上传人脸照片")


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


class AttendanceRecordPathModel(CamelCaseModel):
    """考勤记录路径参数模型"""
    attendance_id: int = Field(..., description="考勤ID", ge=1)
    record_id: int = Field(..., description="记录ID", ge=1)


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
