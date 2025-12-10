"""
弹幕API
提供弹幕相关的RESTful接口
"""
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.interaction_schemas import (
    BarrageCreateModel, BarrageResponseModel,
    BarrageDetailResponseModel, BarragePathModel,
    SensitiveWordModel, SensitiveWordPathModel, ContentCheckModel
)
from app.schemas.common_schemas import MessageResponseModel, QueryModel
from app.services.barrage_service import BarrageService
from app.utils.auth_decorators import login_required
from app.utils.response_handler import ResponseHandler
from app.models.user import UserRole
from flask import session
import logging

logger = logging.getLogger(__name__)

barrage_api_bp = APIBlueprint('barrage_api', __name__, url_prefix='/api/v1/barrages')
barrage_tag = Tag(name="BarrageController", description="弹幕管理API")


class BarrageAPI:
    """
    弹幕API类 - 装饰器方式
    
    提供弹幕相关的完整功能，包括：
    - 发送弹幕（自由弹幕）
    - 获取弹幕列表
    - 删除弹幕（教师/管理员）
    - 获取弹幕统计信息
    """
    
    # 类属性：请求计数
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[{cls.request_count}] {action}{user_desc}")
    
    # ==================== 弹幕管理接口 ====================
    
    @staticmethod
    @barrage_api_bp.post('/',
                        summary="发送弹幕",
                        tags=[barrage_tag],
                        responses={201: BarrageResponseModel, 400: MessageResponseModel})
    @login_required
    def create_barrage(body: BarrageCreateModel):
        """
        发送弹幕（自由弹幕）
        
        用户发送自由弹幕，内容会自动进行敏感词过滤。
        如果包含敏感词，将返回错误。
        """
        try:
            user_id = session.get('user_id')
            
            BarrageAPI.log_request("CREATE_BARRAGE", f"user_id={user_id}, course_id={body.course_id}")
            
            # 创建弹幕（自动敏感词过滤）
            barrage = BarrageService.create_barrage(user_id, body)
            
            # ⭐ WebSocket广播弹幕（待集成）
            # from app.extensions import socketio
            # socketio.emit('new_barrage', {
            #     'barrage': barrage.to_dict(),
            #     'is_answer': False,
            #     'question_id': None
            # }, room=f'course_{barrage.course_id}')
            
            return ResponseHandler.success(
                data=barrage.to_dict(),
                message="弹幕发送成功"
            ), 201
            
        except ValueError as e:
            logger.warning(f"Barrage creation validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error creating barrage: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.get('/',
                       summary="获取弹幕列表",
                       tags=[barrage_tag],
                       responses={200: BarrageDetailResponseModel, 400: MessageResponseModel})
    @login_required
    def list_barrages(query: QueryModel):
        """
        获取弹幕列表
        
        支持按课程查询和按问题查询。
        - 提供 course_id: 获取课程的所有弹幕
        - 提供 question_id: 获取问题的答案弹幕
        - 提供 type=free: 获取自由弹幕（不关联问题）
        """
        try:
            user_id = session.get('user_id')
            BarrageAPI.log_request("LIST_BARRAGES", f"user_id={user_id}")
            
            # 获取查询参数
            course_id = query.course_id if hasattr(query, 'course_id') else None
            question_id = query.question_id if hasattr(query, 'question_id') else None
            barrage_type = query.type if hasattr(query, 'type') else None
            limit = query.limit if hasattr(query, 'limit') else 100
            
            barrages = []
            
            # 按问题查询（答案弹幕）
            if question_id:
                barrages = BarrageService.get_barrages_by_question(question_id)
            # 按课程查询自由弹幕
            elif course_id and barrage_type == 'free':
                barrages = BarrageService.get_free_barrages(course_id, limit=limit)
            # 按课程查询所有弹幕
            elif course_id:
                barrages = BarrageService.get_barrages_by_course(course_id, limit=limit)
            else:
                return ResponseHandler.error(
                    message="缺少查询参数（course_id 或 question_id）",
                    error_code="MISSING_PARAM"
                ), 400
            
            # 转换为字典列表
            barrage_list = [barrage.to_dict() for barrage in barrages]
            
            return ResponseHandler.success(
                data={
                    'barrages': barrage_list,
                    'total': len(barrage_list)
                },
                message="获取弹幕列表成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error listing barrages: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.get('/recent',
                       summary="获取最近的弹幕",
                       tags=[barrage_tag],
                       responses={200: BarrageDetailResponseModel, 400: MessageResponseModel})
    @login_required
    def get_recent_barrages(query: QueryModel):
        """
        获取最近N分钟的弹幕
        
        用于实时弹幕墙展示。
        
        参数说明：
        - courseId: 课程ID（必填）
        - minutes: 最近N分钟（可选，默认10分钟，最大1440分钟即24小时）
        
        示例：
        - 获取最近10分钟的弹幕：?courseId=1&minutes=10
        - 获取最近30分钟的弹幕：?courseId=1&minutes=30
        - 获取最近1小时的弹幕：?courseId=1&minutes=60
        """
        try:
            user_id = session.get('user_id')
            
            # 获取查询参数
            course_id = query.course_id
            minutes = query.minutes if query.minutes else 10
            
            if not course_id:
                return ResponseHandler.error(
                    message="缺少课程ID参数",
                    error_code="MISSING_PARAM"
                ), 400
            
            BarrageAPI.log_request("GET_RECENT_BARRAGES", f"course_id={course_id}, minutes={minutes}, user_id={user_id}")
            
            # 获取最近的弹幕
            barrages = BarrageService.get_recent_barrages(course_id, minutes=minutes)
            
            barrage_list = [barrage.to_dict() for barrage in barrages]
            
            return ResponseHandler.success(
                data={
                    'barrages': barrage_list,
                    'total': len(barrage_list),
                    'minutes': minutes,
                    'course_id': course_id
                },
                message=f"获取最近{minutes}分钟的弹幕成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error getting recent barrages: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.get('/statistics',
                       summary="获取弹幕统计信息",
                       tags=[barrage_tag],
                       responses={200: MessageResponseModel, 400: MessageResponseModel})
    @login_required
    def get_statistics(query: QueryModel):
        """
        获取弹幕统计信息
        
        包含总弹幕数、答案弹幕数、自由弹幕数、最近弹幕数等。
        
        参数说明：
        - courseId: 课程ID（必填）
        - minutes: 最近N分钟（可选，默认10分钟，用于统计最近弹幕数）
        """
        try:
            user_id = session.get('user_id')
            
            # 获取参数
            course_id = query.course_id
            recent_minutes = query.minutes if query.minutes else 10
            
            if not course_id:
                return ResponseHandler.error(
                    message="缺少课程ID参数",
                    error_code="MISSING_PARAM"
                ), 400
            
            BarrageAPI.log_request("GET_STATISTICS", f"course_id={course_id}, recent_minutes={recent_minutes}, user_id={user_id}")
            
            # 获取统计信息
            statistics = BarrageService.get_barrage_statistics(course_id, recent_minutes=recent_minutes)
            
            return ResponseHandler.success(
                data=statistics,
                message="获取弹幕统计信息成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error getting barrage statistics: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.delete('/<int:barrageId>',
                          summary="删除弹幕",
                          tags=[barrage_tag],
                          responses={200: MessageResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def delete_barrage(path: BarragePathModel):
        """
        删除弹幕（软删除）
        
        参数说明：
        - barrageId: 弹幕ID（在URL路径中）
        
        权限：
        - 弹幕发送者本人可以删除
        - 教师可以删除课程内的任何弹幕
        - 管理员可以删除任何弹幕
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            BarrageAPI.log_request("DELETE_BARRAGE", f"barrage_id={path.barrage_id}, user_id={user_id}")
            
            # 获取弹幕
            barrage = BarrageService.get_barrage_by_id(path.barrage_id)
            if not barrage:
                return ResponseHandler.error(
                    message="弹幕不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限
            # 1. 弹幕发送者本人
            # 2. 教师（需要验证是否是该课程的教师）
            # 3. 管理员
            if (barrage.user_id != user_id and 
                user_role not in [UserRole.TEACHER.value, UserRole.ADMIN.value]):
                logger.warning(f"User {user_id} attempted to delete barrage {path.barrage_id} without permission")
                return ResponseHandler.error(
                    message="无权限删除此弹幕",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 删除弹幕（软删除）
            success = BarrageService.delete_barrage(path.barrage_id)
            
            if not success:
                return ResponseHandler.error(
                    message="删除失败",
                    error_code="DELETE_FAILED"
                ), 500
            
            return ResponseHandler.success(
                message="弹幕删除成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error deleting barrage: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    # ==================== 敏感词管理接口 ====================
    
    @staticmethod
    @barrage_api_bp.get('/sensitive-words',
                       summary="获取敏感词列表",
                       tags=[barrage_tag],
                       responses={200: MessageResponseModel})
    @login_required
    def get_sensitive_words():
        """
        获取敏感词列表（教师/管理员）
        
        返回当前系统的敏感词库。
        """
        try:
            user_id = session.get('user_id')
            BarrageAPI.log_request("GET_SENSITIVE_WORDS", f"user_id={user_id}")
            
            # 获取敏感词列表
            sensitive_words = BarrageService.get_sensitive_words()
            
            return ResponseHandler.success(
                data={
                    'sensitive_words': sensitive_words,
                    'total': len(sensitive_words)
                },
                message="获取敏感词列表成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error getting sensitive words: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.post('/sensitive-words',
                        summary="添加敏感词",
                        tags=[barrage_tag],
                        responses={201: MessageResponseModel, 403: MessageResponseModel})
    @login_required
    def add_sensitive_word(body: SensitiveWordModel):
        """
        添加敏感词（教师/管理员）
        
        请求体: {"word": "敏感词"}
        """
        try:
            user_id = session.get('user_id')
            word = body.word
            
            if not word:
                return ResponseHandler.error(
                    message="缺少敏感词参数",
                    error_code="MISSING_PARAM"
                ), 400
            
            BarrageAPI.log_request("ADD_SENSITIVE_WORD", f"user_id={user_id}, word={word}")
            
            # 添加敏感词
            success = BarrageService.add_sensitive_word(word)
            
            if success:
                return ResponseHandler.success(
                    message="敏感词添加成功"
                ), 201
            else:
                return ResponseHandler.error(
                    message="敏感词已存在",
                    error_code="ALREADY_EXISTS"
                ), 400
            
        except Exception as e:
            logger.error(f"Error adding sensitive word: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.delete('/sensitive-words/<string:word>',
                          summary="删除敏感词",
                          tags=[barrage_tag],
                          responses={200: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def remove_sensitive_word(path: SensitiveWordPathModel):
        """
        删除敏感词（教师/管理员）
        
        参数说明：
        - word: 要删除的敏感词（在URL路径中）
        
        示例：
        - DELETE /api/v1/barrages/sensitive-words/测试敏感词
        """
        try:
            user_id = session.get('user_id')
            word = path.word
            
            BarrageAPI.log_request("REMOVE_SENSITIVE_WORD", f"user_id={user_id}, word={word}")
            
            # 删除敏感词
            success = BarrageService.remove_sensitive_word(word)
            
            if success:
                return ResponseHandler.success(
                    message="敏感词删除成功"
                ), 200
            else:
                return ResponseHandler.error(
                    message="敏感词不存在",
                    error_code="NOT_FOUND"
                ), 404
            
        except Exception as e:
            logger.error(f"Error removing sensitive word: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @barrage_api_bp.post('/check-content',
                        summary="检查内容安全性",
                        tags=[barrage_tag],
                        responses={200: MessageResponseModel})
    @login_required
    def check_content(body: ContentCheckModel):
        """
        检查内容安全性
        
        用于前端实时检测用户输入是否包含敏感词。
        请求体: {"content": "待检测的内容"}
        """
        try:
            user_id = session.get('user_id')
            content = body.content
            
            if not content:
                return ResponseHandler.error(
                    message="缺少内容参数",
                    error_code="MISSING_PARAM"
                ), 400
            
            BarrageAPI.log_request("CHECK_CONTENT", f"user_id={user_id}")
            
            # 检查内容安全性
            is_safe, detected_words = BarrageService.check_content_safety(content)
            
            return ResponseHandler.success(
                data={
                    'is_safe': is_safe,
                    'detected_words': detected_words,
                    'message': '内容安全' if is_safe else f'检测到敏感词: {", ".join(detected_words)}'
                },
                message="内容检测完成"
            ), 200
            
        except Exception as e:
            logger.error(f"Error checking content: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
