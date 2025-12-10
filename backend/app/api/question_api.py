"""
提问API
提供提问和回答相关的RESTful接口
"""
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.interaction_schemas import (
    QuestionCreateModel, QuestionUpdateModel, QuestionResponseModel,
    QuestionDetailResponseModel, QuestionPathModel,
    QuestionAnswerCreateModel, QuestionAnswerUpdateModel,
    QuestionAnswerResponseModel, QuestionAnswerPathModel,
    QuestionAnswerCombinedPathModel
)
from app.schemas.common_schemas import MessageResponseModel, QueryModel
from app.services.question_service import QuestionService
from app.utils.auth_decorators import login_required
from app.utils.response_handler import ResponseHandler
from app.models.user import UserRole
from flask import session
import logging

logger = logging.getLogger(__name__)

question_api_bp = APIBlueprint('question_api', __name__, url_prefix='/api/v1/questions')
question_tag = Tag(name="QuestionController", description="提问管理API")


class QuestionAPI:
    """
    提问API类 - 装饰器方式
    
    提供提问和回答相关的完整功能，包括：
    - 创建问题（教师）
    - 获取问题列表
    - 获取问题详情
    - 更新问题（教师）
    - 删除问题（教师）
    - 回答问题（学生）⭐ 核心功能：答案自动转弹幕
    - 采纳答案（教师）
    - 点赞功能
    """
    
    # 类属性：请求计数
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[{cls.request_count}] {action}{user_desc}")
    
    # ==================== 问题管理接口 ====================
    
    @staticmethod
    @question_api_bp.post('/',
                         summary="创建问题",
                         tags=[question_tag],
                         responses={201: QuestionResponseModel, 400: MessageResponseModel, 403: MessageResponseModel})
    @login_required
    def create_question(body: QuestionCreateModel):
        """
        创建问题（教师）
        
        教师在课程中发布开放性问题，学生可以回答。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            QuestionAPI.log_request("CREATE_QUESTION", f"user_id={user_id}")
            
            # 验证权限（只有教师可以创建问题）
            if user_role != UserRole.TEACHER.value:
                logger.warning(f"User {user_id} with role {user_role} attempted to create question")
                return ResponseHandler.error(
                    message="只有教师可以创建问题",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 创建问题
            question = QuestionService.create_question(user_id, body)
            
            return ResponseHandler.success(
                data=question.to_dict(),
                message="问题创建成功"
            ), 201
            
        except ValueError as e:
            logger.warning(f"Question creation validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error creating question: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.get('/',
                        summary="获取问题列表",
                        tags=[question_tag],
                        responses={200: QuestionDetailResponseModel, 400: MessageResponseModel})
    @login_required
    def list_questions(query: QueryModel):
        """
        获取问题列表
        
        支持分页和状态过滤。
        需要提供course_id参数。
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("LIST_QUESTIONS", f"user_id={user_id}")
            
            # 获取course_id（从查询参数）
            course_id = query.course_id if hasattr(query, 'course_id') else None
            
            if not course_id:
                return ResponseHandler.error(
                    message="缺少课程ID参数",
                    error_code="MISSING_PARAM"
                ), 400
            
            # 获取状态过滤（如果有）
            status = query.status if hasattr(query, 'status') else None
            
            # 获取问题列表
            questions, total = QuestionService.get_questions_by_course(
                course_id=course_id,
                page=query.page if hasattr(query, 'page') else 1,
                per_page=query.per_page if hasattr(query, 'per_page') else 20,
                status=status
            )
            
            # 转换为字典列表，包含回答数量
            question_list = []
            for question in questions:
                question_dict = question.to_dict()
                question_dict['answer_count'] = question.get_answer_count()
                question_list.append(question_dict)
            
            return ResponseHandler.paginated(
                items=question_list,
                total=total,
                page=query.page if hasattr(query, 'page') else 1,
                per_page=query.per_page if hasattr(query, 'per_page') else 20,
                message="获取问题列表成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error listing questions: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.get('/<int:questionId>',
                        summary="获取问题详情",
                        tags=[question_tag],
                        responses={200: QuestionDetailResponseModel, 404: MessageResponseModel})
    @login_required
    def get_question(path: QuestionPathModel):
        """
        获取问题详情
        
        包含问题信息和所有回答。
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("GET_QUESTION", f"question_id={path.question_id}, user_id={user_id}")
            
            # 获取问题详情（包含所有回答）
            question_data = QuestionService.get_question_with_answers(path.question_id)
            
            if not question_data:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            return ResponseHandler.success(
                data=question_data,
                message="获取问题详情成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error getting question: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.put('/<int:questionId>',
                        summary="更新问题",
                        tags=[question_tag],
                        responses={200: QuestionResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def update_question(path: QuestionPathModel, body: QuestionUpdateModel):
        """
        更新问题（教师）
        
        只有创建问题的教师或管理员可以更新。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            QuestionAPI.log_request("UPDATE_QUESTION", f"question_id={path.question_id}, user_id={user_id}")
            
            # 获取问题
            question = QuestionService.get_question_by_id(path.question_id)
            if not question:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限
            if question.user_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to update question {path.question_id} without permission")
                return ResponseHandler.error(
                    message="无权限修改此问题",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 更新问题
            updated_question = QuestionService.update_question(path.question_id, body)
            
            return ResponseHandler.success(
                data=updated_question.to_dict(),
                message="问题更新成功"
            ), 200
            
        except ValueError as e:
            logger.warning(f"Question update validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error updating question: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.delete('/<int:questionId>',
                           summary="删除问题",
                           tags=[question_tag],
                           responses={200: MessageResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def delete_question(path: QuestionPathModel):
        """
        删除问题（教师）
        
        只有创建问题的教师或管理员可以删除。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            QuestionAPI.log_request("DELETE_QUESTION", f"question_id={path.question_id}, user_id={user_id}")
            
            # 获取问题
            question = QuestionService.get_question_by_id(path.question_id)
            if not question:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限
            if question.user_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to delete question {path.question_id} without permission")
                return ResponseHandler.error(
                    message="无权限删除此问题",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 删除问题
            QuestionService.delete_question(path.question_id)
            
            return ResponseHandler.success(
                message="问题删除成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error deleting question: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    # ==================== 回答管理接口 ====================
    
    @staticmethod
    @question_api_bp.post('/<int:questionId>/answers',
                         summary="回答问题",
                         tags=[question_tag],
                         responses={201: QuestionAnswerResponseModel, 400: MessageResponseModel, 403: MessageResponseModel})
    @login_required
    def create_answer(path: QuestionPathModel, body: QuestionAnswerCreateModel):
        """
        回答问题（学生）⭐ 核心功能
        
        学生回答问题，答案会自动转换为弹幕实时展示。
        
        核心流程：
        1. 保存答案到 question_answers 表
        2. 创建弹幕到 barrages 表（带 question_id）
        3. 通过WebSocket广播弹幕
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            QuestionAPI.log_request("CREATE_ANSWER", f"question_id={path.question_id}, user_id={user_id}")
            
            # 验证权限（只有学生可以回答问题）
            if user_role != UserRole.STUDENT.value:
                logger.warning(f"User {user_id} with role {user_role} attempted to answer question")
                return ResponseHandler.error(
                    message="只有学生可以回答问题",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # ⭐ 核心功能：创建答案和弹幕
            answer, barrage = QuestionService.create_answer(
                question_id=path.question_id,
                user_id=user_id,
                answer_data=body
            )
            
            # ⭐ WebSocket广播弹幕（实时推送给所有在线用户）
            # 注意：这里需要在后续集成WebSocket时实现
            # from app.extensions import socketio
            # socketio.emit('new_barrage', {
            #     'barrage': barrage.to_dict(),
            #     'is_answer': True,
            #     'question_id': path.question_id
            # }, room=f'course_{barrage.course_id}')
            
            return ResponseHandler.success(
                data={
                    'answer': answer.to_dict(),
                    'barrage': barrage.to_dict()
                },
                message="回答成功，答案已转为弹幕展示"
            ), 201
            
        except ValueError as e:
            logger.warning(f"Answer creation validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error creating answer: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.get('/<int:questionId>/answers',
                        summary="获取问题的所有回答",
                        tags=[question_tag],
                        responses={200: QuestionAnswerResponseModel, 404: MessageResponseModel})
    @login_required
    def get_answers(path: QuestionPathModel):
        """
        获取问题的所有回答
        
        回答按智能排序：采纳 > 点赞 > 时间
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("GET_ANSWERS", f"question_id={path.question_id}, user_id={user_id}")
            
            # 获取问题
            question = QuestionService.get_question_by_id(path.question_id)
            if not question:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 获取所有回答
            answers = QuestionService.get_answers_by_question(path.question_id)
            
            answer_list = [answer.to_dict() for answer in answers]
            
            return ResponseHandler.success(
                data={
                    'answers': answer_list,
                    'total': len(answer_list)
                },
                message="获取回答列表成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error getting answers: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.put('/<int:questionId>/answers/<int:answerId>/accept',
                        summary="采纳答案",
                        tags=[question_tag],
                        responses={200: QuestionAnswerResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def accept_answer(path: QuestionAnswerCombinedPathModel):
        """
        采纳答案（教师）
        
        教师采纳优秀答案，被采纳的答案会显示在最前面。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            QuestionAPI.log_request("ACCEPT_ANSWER", f"question_id={path.question_id}, answer_id={path.answer_id}")
            
            # 获取问题
            question = QuestionService.get_question_by_id(path.question_id)
            if not question:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限（只有创建问题的教师或管理员可以采纳答案）
            if question.user_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to accept answer without permission")
                return ResponseHandler.error(
                    message="无权限采纳答案",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 采纳答案
            accepted_answer = QuestionService.accept_answer(path.answer_id)
            
            if not accepted_answer:
                return ResponseHandler.error(
                    message="答案不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            return ResponseHandler.success(
                data=accepted_answer.to_dict(),
                message="答案已采纳"
            ), 200
            
        except Exception as e:
            logger.error(f"Error accepting answer: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.delete('/<int:questionId>/answers/<int:answerId>',
                           summary="删除回答",
                           tags=[question_tag],
                           responses={200: MessageResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def delete_answer(path: QuestionAnswerCombinedPathModel):
        """
        删除回答
        
        回答者本人、问题创建者或管理员可以删除。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            QuestionAPI.log_request("DELETE_ANSWER", f"question_id={path.question_id}, answer_id={path.answer_id}")
            
            # 获取答案
            answer = QuestionService.get_answer_by_id(path.answer_id)
            if not answer:
                return ResponseHandler.error(
                    message="答案不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 获取问题
            question = QuestionService.get_question_by_id(path.question_id)
            
            # 验证权限（回答者本人、问题创建者或管理员）
            if (answer.user_id != user_id and 
                question.user_id != user_id and 
                user_role != UserRole.ADMIN.value):
                logger.warning(f"User {user_id} attempted to delete answer without permission")
                return ResponseHandler.error(
                    message="无权限删除此回答",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 删除回答
            QuestionService.delete_answer(path.answer_id)
            
            return ResponseHandler.success(
                message="回答删除成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error deleting answer: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    # ==================== 互动接口 ====================
    
    @staticmethod
    @question_api_bp.post('/<int:questionId>/like',
                         summary="点赞问题",
                         tags=[question_tag],
                         responses={200: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def like_question(path: QuestionPathModel):
        """
        点赞问题
        
        增加问题的点赞数。
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("LIKE_QUESTION", f"question_id={path.question_id}, user_id={user_id}")
            
            # 点赞问题
            question = QuestionService.like_question(path.question_id)
            
            if not question:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            return ResponseHandler.success(
                data={'like_count': question.like_count},
                message="点赞成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error liking question: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.delete('/<int:questionId>/like',
                           summary="取消点赞问题",
                           tags=[question_tag],
                           responses={200: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def unlike_question(path: QuestionPathModel):
        """
        取消点赞问题
        
        减少问题的点赞数。
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("UNLIKE_QUESTION", f"question_id={path.question_id}, user_id={user_id}")
            
            # 取消点赞
            question = QuestionService.unlike_question(path.question_id)
            
            if not question:
                return ResponseHandler.error(
                    message="问题不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            return ResponseHandler.success(
                data={'like_count': question.like_count},
                message="取消点赞成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error unliking question: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.post('/<int:questionId>/answers/<int:answerId>/like',
                         summary="点赞回答",
                         tags=[question_tag],
                         responses={200: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def like_answer(path: QuestionAnswerCombinedPathModel):
        """
        点赞回答
        
        增加回答的点赞数。
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("LIKE_ANSWER", f"answer_id={path.answer_id}, user_id={user_id}")
            
            # 点赞回答
            answer = QuestionService.like_answer(path.answer_id)
            
            if not answer:
                return ResponseHandler.error(
                    message="回答不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            return ResponseHandler.success(
                data={'like_count': answer.like_count},
                message="点赞成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error liking answer: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @question_api_bp.delete('/<int:questionId>/answers/<int:answerId>/like',
                           summary="取消点赞回答",
                           tags=[question_tag],
                           responses={200: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def unlike_answer(path: QuestionAnswerCombinedPathModel):
        """
        取消点赞回答
        
        减少回答的点赞数。
        """
        try:
            user_id = session.get('user_id')
            QuestionAPI.log_request("UNLIKE_ANSWER", f"answer_id={path.answer_id}, user_id={user_id}")
            
            # 取消点赞
            answer = QuestionService.unlike_answer(path.answer_id)
            
            if not answer:
                return ResponseHandler.error(
                    message="回答不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            return ResponseHandler.success(
                data={'like_count': answer.like_count},
                message="取消点赞成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error unliking answer: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
