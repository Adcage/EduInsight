"""
预警预测API接口
"""
from flask_openapi3 import APIBlueprint, Tag
from flask import session
from app.schemas.prediction_schemas import (
    GeneratePredictionModel, GeneratePredictionResponseModel,
    PredictionQueryModel, PredictionItemModel, PredictionDetailModel,
    AddInterventionModel, UpdateInterventionModel, InterventionModel,
    SendNotificationModel, SendNotificationResponseModel,
    PredictionIdPath, InterventionIdPath
)
from app.services.prediction_service import PredictionService
from app.services.grade_service import GradeService
from app.utils.auth_decorators import login_required
from app.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

prediction_api_bp = APIBlueprint('prediction_api', __name__, url_prefix='/api/v1/predictions')
prediction_tag = Tag(name="PredictionController", description="预警预测API")


class PredictionAPI:
    """预警预测API类"""
    
    @staticmethod
    @prediction_api_bp.post('/generate',
                           summary="生成预警预测",
                           tags=[prediction_tag],
                           responses={200: GeneratePredictionResponseModel})
    @login_required
    def generate_predictions(body: GeneratePredictionModel):
        """
        为课程生成预警预测(手动触发)
        
        权限: 教师(只能为自己教授的课程生成预测)
        
        参数:
        - course_id: 课程ID(必填)
        - class_id: 班级ID(可选,如果指定则只预测该班级学生)
        
        返回:
        - 预测结果统计(总学生数、成功预测数、各风险等级人数等)
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以生成预测
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以生成预警预测'}, 403
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, body.course_id):
                return {'message': '您没有权限为该课程生成预测'}, 403
            
            logger.info(f"教师{user_id}为课程{body.course_id}生成预警预测")
            
            # 生成预测
            result = PredictionService.generate_predictions(
                course_id=body.course_id,
                class_id=body.class_id
            )
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"生成预警失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"生成预警错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @prediction_api_bp.get('/list',
                          summary="获取预警列表",
                          tags=[prediction_tag])
    @login_required
    def get_predictions(query: PredictionQueryModel):
        """
        获取预警列表
        
        权限: 教师(只能查看自己教授的课程的预警)
        
        参数:
        - course_id: 课程ID(必填)
        - class_id: 班级ID(可选)
        - risk_level: 风险等级筛选(可选: high/medium/low/none)
        
        返回:
        - 预警列表
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以查看预警
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以查看预警列表'}, 403
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, query.course_id):
                return {'message': '您没有权限查看该课程的预警'}, 403
            
            # 获取预警列表
            predictions = PredictionService.get_predictions(
                course_id=query.course_id,
                class_id=query.class_id,
                risk_level=query.risk_level
            )
            
            return predictions, 200
            
        except ValueError as e:
            logger.warning(f"获取预警列表失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"获取预警列表错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @prediction_api_bp.get('/<int:prediction_id>',
                          summary="获取预警详情",
                          tags=[prediction_tag],
                          responses={200: PredictionDetailModel})
    @login_required
    def get_prediction_detail(path: PredictionIdPath):
        """
        获取预警详情
        
        权限: 教师
        
        返回:
        - 预警详情(包含学生历史成绩和干预记录)
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以查看详情
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以查看预警详情'}, 403
            
            # 获取详情
            detail = PredictionService.get_prediction_detail(path.prediction_id)
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, detail['course_id']):
                return {'message': '您没有权限查看该预警'}, 403
            
            return detail, 200
            
        except ValueError as e:
            logger.warning(f"获取预警详情失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"获取预警详情错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @prediction_api_bp.post('/interventions',
                           summary="添加干预记录",
                           tags=[prediction_tag],
                           responses={200: InterventionModel})
    @login_required
    def add_intervention(body: AddInterventionModel):
        """
        添加干预记录
        
        权限: 教师
        
        参数:
        - prediction_id: 预警ID
        - intervention_date: 干预日期(可选,默认今天)
        - intervention_type: 干预方式(talk/tutoring/homework/other)
        - description: 干预内容描述
        - expected_effect: 预期效果(可选)
        
        返回:
        - 干预记录
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以添加干预
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以添加干预记录'}, 403
            
            # 添加干预
            intervention = PredictionService.add_intervention(
                prediction_id=body.prediction_id,
                teacher_id=user_id,
                intervention_data=body.model_dump()
            )
            
            result = intervention.to_dict()
            result['teacher_name'] = user.real_name
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"添加干预记录失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"添加干预记录错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @prediction_api_bp.put('/interventions/<int:intervention_id>',
                          summary="更新干预记录",
                          tags=[prediction_tag],
                          responses={200: InterventionModel})
    @login_required
    def update_intervention(path: InterventionIdPath, body: UpdateInterventionModel):
        """
        更新干预记录(主要用于填写实际效果和学生反馈)
        
        权限: 教师
        
        参数:
        - actual_effect: 实际效果(可选)
        - student_feedback: 学生反馈(可选)
        - description: 干预内容(可选)
        - expected_effect: 预期效果(可选)
        
        返回:
        - 更新后的干预记录
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以更新干预
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以更新干预记录'}, 403
            
            # 更新干预
            intervention = PredictionService.update_intervention(
                intervention_id=path.intervention_id,
                update_data=body.model_dump(exclude_none=True)
            )
            
            result = intervention.to_dict()
            result['teacher_name'] = intervention.teacher.real_name if intervention.teacher else None
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"更新干预记录失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"更新干预记录错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @prediction_api_bp.post('/send-notifications',
                           summary="批量发送预警通知",
                           tags=[prediction_tag],
                           responses={200: SendNotificationResponseModel})
    @login_required
    def send_notifications(body: SendNotificationModel):
        """
        批量发送预警通知给学生
        
        权限: 教师
        
        参数:
        - prediction_ids: 预警ID列表
        
        返回:
        - 发送结果统计
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以发送通知
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以发送预警通知'}, 403
            
            # 发送通知
            result = PredictionService.send_notifications(body.prediction_ids)
            
            return result, 200
            
        except Exception as e:
            logger.error(f"发送预警通知错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500

    # ==================== 学生端API ====================
    
    @staticmethod
    @prediction_api_bp.get('/student/my-warnings',
                          summary="获取学生个人预警列表",
                          tags=[prediction_tag])
    @login_required
    def get_student_warnings():
        """
        获取当前学生的个人预警列表
        
        权限: 学生
        
        返回:
        - 预警列表（按课程分组）
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有学生可以访问
            if user.role != UserRole.STUDENT:
                return {'message': '只有学生可以访问此接口'}, 403
            
            # 获取学生的预警列表
            warnings = PredictionService.get_student_warnings(user_id)
            
            return warnings, 200
            
        except Exception as e:
            logger.error(f"获取学生预警列表错误: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @prediction_api_bp.get('/student/my-warnings/<int:prediction_id>',
                          summary="获取学生预警详情",
                          tags=[prediction_tag])
    @login_required
    def get_student_warning_detail(path: PredictionIdPath):
        """
        获取学生预警详情（包含干预记录）
        
        权限: 学生（只能查看自己的预警）
        
        返回:
        - 预警详情
        - 干预记录列表
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有学生可以访问
            if user.role != UserRole.STUDENT:
                return {'message': '只有学生可以访问此接口'}, 403
            
            # 获取预警详情（会验证是否属于该学生）
            detail = PredictionService.get_student_warning_detail(
                prediction_id=path.prediction_id,
                student_id=user_id
            )
            
            if not detail:
                return {'message': '预警记录不存在或无权访问'}, 404
            
            return detail, 200
            
        except ValueError as e:
            logger.warning(f"获取预警详情失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"获取预警详情错误: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
