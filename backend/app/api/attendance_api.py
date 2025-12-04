"""
考勤管理API
"""
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.attendance_schemas import (
    AttendanceCreateModel, AttendanceUpdateModel, AttendanceResponseModel,
    AttendanceDetailResponseModel, AttendanceListResponseModel,
    AttendanceQueryModel, AttendancePathModel
)
from app.schemas.common_schemas import MessageResponseModel
from app.services.attendance_service import AttendanceService
from app.utils.auth_decorators import (
    login_required, teacher_required, teacher_or_admin_required,
    log_user_action, get_current_user_info
)
from app.models.attendance import AttendanceType
import logging

logger = logging.getLogger(__name__)

# 创建蓝图
attendance_api_bp = APIBlueprint('attendance_api', __name__, url_prefix='/api/v1/attendances')
attendance_tag = Tag(name="AttendanceController", description="考勤管理API")


class AttendanceAPI:
    """
    考勤管理API类 - 装饰器方式
    
    提供考勤管理的完整功能，包括：
    - 创建考勤任务
    - 查询考勤列表
    - 获取考勤详情
    - 更新考勤任务
    - 删除考勤任务
    - 开始/结束考勤
    """
    
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[{cls.request_count}] {action}{user_desc}")
    
    @staticmethod
    @attendance_api_bp.post('/',
                           summary="创建考勤任务",
                           tags=[attendance_tag],
                           responses={
                               201: AttendanceResponseModel,
                               400: MessageResponseModel,
                               401: MessageResponseModel,
                               403: MessageResponseModel
                           })
    @teacher_required
    @log_user_action("创建考勤任务")
    def create_attendance(body: AttendanceCreateModel):
        """
        创建考勤任务
        
        教师为课程创建考勤任务，支持：
        - 选择多个班级
        - 可选择指定学生
        - 四种考勤方式：二维码、手动、人脸识别、位置
        - 设置考勤时间范围
        
        只有课程教师可以创建考勤。
        """
        try:
            AttendanceAPI.log_request("CREATE_ATTENDANCE")
            
            # 获取当前用户信息
            current_user = get_current_user_info()
            teacher_id = current_user['user_id']
            
            # 创建考勤任务
            attendance = AttendanceService.create_attendance(
                title=body.title,
                course_id=body.course_id,
                class_ids=body.class_ids,
                teacher_id=teacher_id,
                attendance_type=body.attendance_type.value,
                start_time=body.start_time,
                end_time=body.end_time,
                student_ids=body.student_ids,
                location=body.location,
                require_location=body.require_location
            )
            
            return {
                'message': '考勤任务创建成功',
                'data': attendance.to_dict()
            }, 201
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error creating attendance: {str(e)}")
            return {
                'message': '创建考勤任务失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @attendance_api_bp.get('/',
                          summary="获取考勤列表",
                          tags=[attendance_tag],
                          responses={
                              200: AttendanceListResponseModel,
                              401: MessageResponseModel
                          })
    @teacher_or_admin_required
    @log_user_action("查询考勤列表")
    def list_attendances(query: AttendanceQueryModel):
        """
        获取考勤列表
        
        支持分页、课程筛选、教师筛选、状态筛选。
        教师只能查看自己创建的考勤，管理员可以查看所有考勤。
        """
        try:
            AttendanceAPI.log_request("LIST_ATTENDANCES")
            
            # 获取当前用户信息
            current_user = get_current_user_info()
            user_role = current_user['role']
            user_id = current_user['user_id']
            
            # 根据角色获取考勤列表
            if user_role == 'admin':
                # 管理员可以查看所有考勤
                if query.teacher_id:
                    result = AttendanceService.get_attendances_by_teacher(
                        teacher_id=query.teacher_id,
                        page=query.page,
                        per_page=query.per_page,
                        course_id=query.course_id,
                        status=query.status.value if query.status else None
                    )
                elif query.course_id:
                    result = AttendanceService.get_attendances_by_course(
                        course_id=query.course_id,
                        page=query.page,
                        per_page=query.per_page,
                        status=query.status.value if query.status else None
                    )
                else:
                    # 获取所有考勤（需要在Service中实现）
                    result = AttendanceService.get_attendances_by_teacher(
                        teacher_id=user_id,
                        page=query.page,
                        per_page=query.per_page,
                        course_id=query.course_id,
                        status=query.status.value if query.status else None
                    )
            else:
                # 教师只能查看自己创建的考勤
                result = AttendanceService.get_attendances_by_teacher(
                    teacher_id=user_id,
                    page=query.page,
                    per_page=query.per_page,
                    course_id=query.course_id,
                    status=query.status.value if query.status else None
                )
            
            # 转换为字典
            attendances = [att.to_dict() for att in result['attendances']]
            
            return {
                'attendances': attendances,
                'total': result['total'],
                'page': result['page'],
                'per_page': result['per_page'],
                'pages': result['pages']
            }, 200
            
        except Exception as e:
            logger.error(f"Error listing attendances: {str(e)}")
            return {
                'message': '获取考勤列表失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @attendance_api_bp.get('/<int:attendance_id>',
                          summary="获取考勤详情",
                          tags=[attendance_tag],
                          responses={
                              200: AttendanceDetailResponseModel,
                              404: MessageResponseModel,
                              401: MessageResponseModel
                          })
    @login_required
    @log_user_action("查询考勤详情")
    def get_attendance(path: AttendancePathModel):
        """
        获取考勤详情
        
        返回考勤任务的详细信息，包括统计数据。
        """
        try:
            AttendanceAPI.log_request(f"GET_ATTENDANCE: {path.attendance_id}")
            
            # 获取考勤详情
            detail = AttendanceService.get_attendance_detail(path.attendance_id)
            
            if not detail:
                return {
                    'message': f'考勤任务ID {path.attendance_id} 不存在'
                }, 404
            
            return detail, 200
            
        except Exception as e:
            logger.error(f"Error getting attendance: {str(e)}")
            return {
                'message': '获取考勤详情失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @attendance_api_bp.put('/<int:attendance_id>',
                          summary="更新考勤任务",
                          tags=[attendance_tag],
                          responses={
                              200: AttendanceResponseModel,
                              400: MessageResponseModel,
                              404: MessageResponseModel,
                              401: MessageResponseModel,
                              403: MessageResponseModel
                          })
    @teacher_required
    @log_user_action("更新考勤任务")
    def update_attendance(path: AttendancePathModel, body: AttendanceUpdateModel):
        """
        更新考勤任务
        
        只有创建教师可以更新考勤任务。
        可更新的字段：标题、地点、结束时间、状态。
        """
        try:
            AttendanceAPI.log_request(f"UPDATE_ATTENDANCE: {path.attendance_id}")
            
            # 获取当前用户信息
            current_user = get_current_user_info()
            teacher_id = current_user['user_id']
            
            # 更新考勤任务
            attendance = AttendanceService.update_attendance(
                attendance_id=path.attendance_id,
                teacher_id=teacher_id,
                **body.model_dump(exclude_unset=True)
            )
            
            if not attendance:
                return {
                    'message': f'考勤任务ID {path.attendance_id} 不存在'
                }, 404
            
            return {
                'message': '考勤任务更新成功',
                'data': attendance.to_dict()
            }, 200
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error updating attendance: {str(e)}")
            return {
                'message': '更新考勤任务失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @attendance_api_bp.delete('/<int:attendance_id>',
                             summary="删除考勤任务",
                             tags=[attendance_tag],
                             responses={
                                 200: MessageResponseModel,
                                 400: MessageResponseModel,
                                 404: MessageResponseModel,
                                 401: MessageResponseModel,
                                 403: MessageResponseModel
                             })
    @teacher_required
    @log_user_action("删除考勤任务")
    def delete_attendance(path: AttendancePathModel):
        """
        删除考勤任务
        
        只有创建教师可以删除考勤任务。
        只能删除未开始的考勤任务。
        """
        try:
            AttendanceAPI.log_request(f"DELETE_ATTENDANCE: {path.attendance_id}")
            
            # 获取当前用户信息
            current_user = get_current_user_info()
            teacher_id = current_user['user_id']
            
            # 删除考勤任务
            success = AttendanceService.delete_attendance(
                attendance_id=path.attendance_id,
                teacher_id=teacher_id
            )
            
            if not success:
                return {
                    'message': f'考勤任务ID {path.attendance_id} 不存在'
                }, 404
            
            return {
                'message': '考勤任务删除成功'
            }, 200
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error deleting attendance: {str(e)}")
            return {
                'message': '删除考勤任务失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @attendance_api_bp.post('/<int:attendance_id>/start',
                           summary="开始考勤",
                           tags=[attendance_tag],
                           responses={
                               200: AttendanceResponseModel,
                               400: MessageResponseModel,
                               404: MessageResponseModel,
                               401: MessageResponseModel,
                               403: MessageResponseModel
                           })
    @teacher_required
    @log_user_action("开始考勤")
    def start_attendance(path: AttendancePathModel):
        """
        开始考勤
        
        只有创建教师可以开始考勤。
        只能开始状态为"待开始"的考勤任务。
        """
        try:
            AttendanceAPI.log_request(f"START_ATTENDANCE: {path.attendance_id}")
            
            # 获取当前用户信息
            current_user = get_current_user_info()
            teacher_id = current_user['user_id']
            
            # 开始考勤
            attendance = AttendanceService.start_attendance(
                attendance_id=path.attendance_id,
                teacher_id=teacher_id
            )
            
            return {
                'message': '考勤已开始',
                'data': attendance.to_dict()
            }, 200
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error starting attendance: {str(e)}")
            return {
                'message': '开始考勤失败',
                'error': str(e)
            }, 500
    
    @staticmethod
    @attendance_api_bp.post('/<int:attendance_id>/end',
                           summary="结束考勤",
                           tags=[attendance_tag],
                           responses={
                               200: AttendanceResponseModel,
                               400: MessageResponseModel,
                               404: MessageResponseModel,
                               401: MessageResponseModel,
                               403: MessageResponseModel
                           })
    @teacher_required
    @log_user_action("结束考勤")
    def end_attendance(path: AttendancePathModel):
        """
        结束考勤
        
        只有创建教师可以结束考勤。
        结束后学生将无法继续签到。
        """
        try:
            AttendanceAPI.log_request(f"END_ATTENDANCE: {path.attendance_id}")
            
            # 获取当前用户信息
            current_user = get_current_user_info()
            teacher_id = current_user['user_id']
            
            # 结束考勤
            attendance = AttendanceService.end_attendance(
                attendance_id=path.attendance_id,
                teacher_id=teacher_id
            )
            
            return {
                'message': '考勤已结束',
                'data': attendance.to_dict()
            }, 200
            
        except ValueError as e:
            logger.warning(f"Validation error: {str(e)}")
            return {
                'message': str(e)
            }, 400
        except Exception as e:
            logger.error(f"Error ending attendance: {str(e)}")
            return {
                'message': '结束考勤失败',
                'error': str(e)
            }, 500
