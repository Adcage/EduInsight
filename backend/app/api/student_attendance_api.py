"""
学生端考勤API
"""
from flask_openapi3 import APIBlueprint, Tag
from pydantic import BaseModel, Field
from typing import Optional
from app.schemas.attendance_schemas import (
    AttendanceDetailResponseModel, AttendanceListResponseModel,
    AttendanceQueryModel, AttendancePathModel
)
from app.schemas.common_schemas import MessageResponseModel
from app.services.student_attendance_service import StudentAttendanceService
from app.utils.auth_decorators import (
    student_required, log_user_action, get_current_user_info
)
import logging


# 手势签到请求模型
class GestureCheckInRequest(BaseModel):
    attendance_id: int = Field(..., description="考勤ID")
    gesture_code: str = Field(..., description="手势码", max_length=50)
    gesture_pattern: Optional[dict] = Field(None, description="完整手势数据")


# 位置签到请求模型
class LocationCheckInRequest(BaseModel):
    attendance_id: int = Field(..., description="考勤ID")
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")

logger = logging.getLogger(__name__)

# 创建蓝图
student_attendance_api_bp = APIBlueprint(
    'student_attendance_api', 
    __name__, 
    url_prefix='/api/v1/students/attendances'
)
student_attendance_tag = Tag(name="StudentAttendanceController", description="学生端考勤API")


class StudentAttendanceAPI:
    """学生端考勤API类"""
    
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[Student][{cls.request_count}] {action}{user_desc}")
    
    @staticmethod
    @student_attendance_api_bp.get('',
                                   summary="获取学生考勤通知列表",
                                   tags=[student_attendance_tag],
                                   responses={
                                       200: AttendanceListResponseModel,
                                       401: MessageResponseModel
                                   })
    @student_required
    @log_user_action("获取考勤通知列表")
    def get_student_attendances(query: AttendanceQueryModel):
        """
        获取学生的考勤通知列表
        
        返回当前登录学生的所有考勤通知，包括：
        - 考勤基本信息
        - 课程名称
        - 教师名称
        - 学生的签到记录
        - 是否已签到标识
        
        支持按状态筛选和分页。
        """
        try:
            StudentAttendanceAPI.log_request(f"GET_ATTENDANCES: page={query.page}")
            
            # 获取当前学生信息
            current_user = get_current_user_info()
            student_id = current_user['user_id']
            
            # 获取考勤列表
            result = StudentAttendanceService.get_student_attendances(
                student_id=student_id,
                page=query.page,
                per_page=query.per_page,
                status=query.status
            )
            
            return result, 200
            
        except Exception as e:
            logger.error(f"Error getting student attendances: {str(e)}")
            return {
                'message': '获取考勤通知失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @student_attendance_api_bp.get('/<int:attendance_id>',
                                   summary="获取学生考勤详情",
                                   tags=[student_attendance_tag],
                                   responses={
                                       200: AttendanceDetailResponseModel,
                                       404: MessageResponseModel,
                                       401: MessageResponseModel
                                   })
    @student_required
    @log_user_action("获取考勤详情")
    def get_student_attendance_detail(path: AttendancePathModel):
        """
        获取学生的考勤详情
        
        返回指定考勤的详细信息，包括：
        - 完整的考勤信息
        - 课程和教师信息
        - 学生的签到记录
        """
        try:
            StudentAttendanceAPI.log_request(f"GET_DETAIL: {path.attendance_id}")
            
            # 获取当前学生信息
            current_user = get_current_user_info()
            student_id = current_user['user_id']
            
            # 获取考勤详情
            attendance = StudentAttendanceService.get_student_attendance_detail(
                student_id=student_id,
                attendance_id=path.attendance_id
            )
            
            if not attendance:
                return {
                    'message': '考勤不存在或无权访问'
                }, 404
            
            return attendance, 200
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'message': str(e)
            }, 404
        except Exception as e:
            logger.error(f"Error getting attendance detail: {str(e)}")
            return {
                'message': '获取考勤详情失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @student_attendance_api_bp.post('/gesture/verify',
                                    summary="手势签到",
                                    tags=[student_attendance_tag],
                                    responses={
                                        200: MessageResponseModel,
                                        400: MessageResponseModel,
                                        401: MessageResponseModel
                                    })
    @student_required
    @log_user_action("手势签到")
    def verify_gesture_checkin(body: GestureCheckInRequest):
        """
        手势签到
        
        学生通过输入手势码完成签到
        
        请求体:
        - attendance_id: 考勤ID
        - gesture_code: 手势码
        """
        try:
            StudentAttendanceAPI.log_request(f"GESTURE_CHECKIN: {body.attendance_id}")
            
            # 获取当前学生信息
            current_user = get_current_user_info()
            student_id = current_user['user_id']
            
            # 获取参数
            attendance_id = body.attendance_id
            gesture_code = body.gesture_code
            gesture_pattern = body.gesture_pattern
            
            # 验证并签到
            from app.services.attendance_service import AttendanceService
            record = AttendanceService.verify_gesture_and_checkin(
                student_id=student_id,
                attendance_id=attendance_id,
                gesture_code=gesture_code,
                gesture_pattern=gesture_pattern
            )
            
            return {
                'message': '签到成功',
                'record': record.to_dict()
            }, 200
            
        except ValueError as e:
            logger.warning(f"Gesture check-in validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error in gesture check-in: {str(e)}")
            return {
                'message': '签到失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @student_attendance_api_bp.post('/location/verify',
                                    summary="位置签到",
                                    tags=[student_attendance_tag],
                                    responses={
                                        200: MessageResponseModel,
                                        400: MessageResponseModel,
                                        401: MessageResponseModel
                                    })
    @student_required
    @log_user_action("位置签到")
    def verify_location_checkin(body: LocationCheckInRequest):
        """
        位置签到
        
        学生通过提供当前位置完成签到
        
        请求体:
        - attendance_id: 考勤ID
        - latitude: 纬度
        - longitude: 经度
        """
        try:
            StudentAttendanceAPI.log_request(f"LOCATION_CHECKIN: {body.attendance_id}")
            
            # 获取当前学生信息
            current_user = get_current_user_info()
            student_id = current_user['user_id']
            
            # 获取参数
            attendance_id = body.attendance_id
            latitude = body.latitude
            longitude = body.longitude
            
            # 验证并签到
            from app.services.attendance_service import AttendanceService
            record = AttendanceService.verify_location_and_checkin(
                student_id=student_id,
                attendance_id=attendance_id,
                latitude=latitude,
                longitude=longitude
            )
            
            return {
                'message': '签到成功',
                'record': record.to_dict()
            }, 200
            
        except ValueError as e:
            logger.warning(f"Location check-in validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error in location check-in: {str(e)}")
            return {
                'message': '签到失败',
                'error': str(e)
            }, 500
