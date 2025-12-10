"""
投票API
提供投票相关的RESTful接口
"""
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.interaction_schemas import (
    PollCreateModel, PollUpdateModel, PollResponseModel,
    PollDetailResponseModel, PollPathModel,
    PollVoteModel
)
from app.schemas.common_schemas import MessageResponseModel, QueryModel
from app.services.poll_service import PollService
from app.utils.auth_decorators import login_required
from app.utils.response_handler import ResponseHandler
from app.models.user import UserRole
from flask import session
import logging

logger = logging.getLogger(__name__)

poll_api_bp = APIBlueprint('poll_api', __name__, url_prefix='/api/v1/polls')
poll_tag = Tag(name="PollController", description="投票管理API")


class PollAPI:
    """
    投票API类 - 装饰器方式
    
    提供投票相关的完整功能，包括：
    - 创建投票（教师）
    - 获取投票列表
    - 获取投票详情
    - 更新投票（教师）
    - 删除投票（教师）
    - 学生投票
    - 获取投票结果
    - 关闭投票（教师）
    """
    
    # 类属性：请求计数
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[{cls.request_count}] {action}{user_desc}")
    
    @staticmethod
    @poll_api_bp.post('/',
                     summary="创建投票",
                     tags=[poll_tag],
                     responses={201: PollResponseModel, 400: MessageResponseModel, 403: MessageResponseModel})
    @login_required
    def create_poll(body: PollCreateModel):
        """
        创建投票（教师）
        
        教师在课程中创建投票问题，支持单选和多选。
        """
        try:
            # 获取当前用户
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            PollAPI.log_request("CREATE_POLL", f"user_id={user_id}")
            
            # 验证权限（只有教师可以创建投票）
            if user_role != UserRole.TEACHER.value:
                logger.warning(f"User {user_id} with role {user_role} attempted to create poll")
                return ResponseHandler.error(
                    message="只有教师可以创建投票",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 创建投票
            poll = PollService.create_poll(user_id, body)
            
            return ResponseHandler.success(
                data=poll.to_dict(),
                message="投票创建成功"
            ), 201
            
        except ValueError as e:
            logger.warning(f"Poll creation validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error creating poll: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.get('/',
                    summary="获取投票列表",
                    tags=[poll_tag],
                    responses={200: PollResponseModel, 400: MessageResponseModel})
    @login_required
    def list_polls(query: QueryModel):
        """
        获取投票列表
        
        支持分页和状态过滤。
        需要提供course_id参数。
        """
        try:
            user_id = session.get('user_id')
            PollAPI.log_request("LIST_POLLS", f"user_id={user_id}")
            
            # 获取course_id（从查询参数）
            course_id = query.course_id if hasattr(query, 'course_id') else None
            
            if not course_id:
                return ResponseHandler.error(
                    message="缺少课程ID参数",
                    error_code="MISSING_PARAM"
                ), 400
            
            # 获取状态过滤（如果有）
            status = query.status if hasattr(query, 'status') else None
            
            # 获取投票列表
            polls, total = PollService.get_polls_by_course(
                course_id=course_id,
                page=query.page if hasattr(query, 'page') else 1,
                per_page=query.per_page if hasattr(query, 'per_page') else 20,
                status=status
            )
            
            # 转换为字典列表
            poll_list = [poll.to_dict() for poll in polls]
            
            # 检查用户是否已投票
            for poll_dict in poll_list:
                poll_dict['has_voted'] = PollService.check_user_voted(
                    poll_dict['id'],
                    user_id
                )
            
            return ResponseHandler.paginated(
                items=poll_list,
                total=total,
                page=query.page if hasattr(query, 'page') else 1,
                per_page=query.per_page if hasattr(query, 'per_page') else 20,
                message="获取投票列表成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error listing polls: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.get('/<int:pollId>',
                    summary="获取投票详情",
                    tags=[poll_tag],
                    responses={200: PollDetailResponseModel, 404: MessageResponseModel})
    @login_required
    def get_poll(path: PollPathModel):
        """
        获取投票详情
        
        包含投票信息和统计结果。
        """
        try:
            user_id = session.get('user_id')
            PollAPI.log_request("GET_POLL", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 获取投票
            poll = PollService.get_poll_by_id(path.poll_id)
            
            if not poll:
                return ResponseHandler.error(
                    message="投票不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 获取投票详细统计
            poll_data = PollService.get_poll_statistics(path.poll_id)
            
            # 检查用户是否已投票
            poll_data['has_voted'] = PollService.check_user_voted(path.poll_id, user_id)
            
            # 如果已投票，获取用户的投票记录
            if poll_data['has_voted']:
                user_vote = PollService.get_user_vote(path.poll_id, user_id)
                poll_data['user_vote'] = user_vote.to_dict() if user_vote else None
            
            return ResponseHandler.success(
                data=poll_data,
                message="获取投票详情成功"
            ), 200
            
        except ValueError as e:
            logger.warning(f"Get poll validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error getting poll: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.put('/<int:pollId>',
                    summary="更新投票",
                    tags=[poll_tag],
                    responses={200: PollResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def update_poll(path: PollPathModel, body: PollUpdateModel):
        """
        更新投票（教师）
        
        只有创建投票的教师或管理员可以更新。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            PollAPI.log_request("UPDATE_POLL", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 获取投票
            poll = PollService.get_poll_by_id(path.poll_id)
            if not poll:
                return ResponseHandler.error(
                    message="投票不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限
            if poll.teacher_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to update poll {path.poll_id} without permission")
                return ResponseHandler.error(
                    message="无权限修改此投票",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 更新投票
            updated_poll = PollService.update_poll(path.poll_id, body)
            
            return ResponseHandler.success(
                data=updated_poll.to_dict(),
                message="投票更新成功"
            ), 200
            
        except ValueError as e:
            logger.warning(f"Poll update validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error updating poll: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.delete('/<int:pollId>',
                       summary="删除投票",
                       tags=[poll_tag],
                       responses={200: MessageResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def delete_poll(path: PollPathModel):
        """
        删除投票（教师）
        
        只有创建投票的教师或管理员可以删除。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            PollAPI.log_request("DELETE_POLL", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 获取投票
            poll = PollService.get_poll_by_id(path.poll_id)
            if not poll:
                return ResponseHandler.error(
                    message="投票不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限
            if poll.teacher_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to delete poll {poll_id} without permission")
                return ResponseHandler.error(
                    message="无权限删除此投票",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 删除投票
            PollService.delete_poll(path.poll_id)
            
            return ResponseHandler.success(
                message="投票删除成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error deleting poll: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.post('/<int:pollId>/vote',
                     summary="学生投票",
                     tags=[poll_tag],
                     responses={201: MessageResponseModel, 400: MessageResponseModel, 403: MessageResponseModel})
    @login_required
    def vote(path: PollPathModel, body: PollVoteModel):
        """
        学生投票
        
        学生选择选项参与投票。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            PollAPI.log_request("VOTE", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 验证权限（只有学生可以投票）
            if user_role != UserRole.STUDENT.value:
                logger.warning(f"User {user_id} with role {user_role} attempted to vote")
                return ResponseHandler.error(
                    message="只有学生可以投票",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 投票
            response = PollService.vote(
                path.poll_id,
                user_id,
                body.selected_options
            )
            
            return ResponseHandler.success(
                data=response.to_dict(),
                message="投票成功"
            ), 201
            
        except ValueError as e:
            logger.warning(f"Vote validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error voting: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.get('/<int:pollId>/results',
                    summary="获取投票结果",
                    tags=[poll_tag],
                    responses={200: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def get_results(path: PollPathModel):
        """
        获取投票结果统计
        
        返回每个选项的票数和百分比。
        """
        try:
            user_id = session.get('user_id')
            PollAPI.log_request("GET_RESULTS", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 获取投票
            poll = PollService.get_poll_by_id(path.poll_id)
            if not poll:
                return ResponseHandler.error(
                    message="投票不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 获取结果统计
            results = PollService.get_poll_results(path.poll_id)
            
            return ResponseHandler.success(
                data=results,
                message="获取投票结果成功"
            ), 200
            
        except ValueError as e:
            logger.warning(f"Get results validation failed: {str(e)}")
            return ResponseHandler.error(
                message=str(e),
                error_code="VALIDATION_ERROR"
            ), 400
        except Exception as e:
            logger.error(f"Error getting poll results: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.put('/<int:pollId>/close',
                    summary="关闭投票",
                    tags=[poll_tag],
                    responses={200: MessageResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def close_poll(path: PollPathModel):
        """
        关闭投票（教师）
        
        结束投票，学生将无法继续投票。
        只有创建投票的教师或管理员可以关闭。
        """
        try:
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            PollAPI.log_request("CLOSE_POLL", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 获取投票
            poll = PollService.get_poll_by_id(path.poll_id)
            if not poll:
                return ResponseHandler.error(
                    message="投票不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限
            if poll.teacher_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to close poll {path.poll_id} without permission")
                return ResponseHandler.error(
                    message="无权限关闭此投票",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 关闭投票
            closed_poll = PollService.close_poll(path.poll_id)
            
            return ResponseHandler.success(
                data=closed_poll.to_dict(),
                message="投票已关闭"
            ), 200
            
        except Exception as e:
            logger.error(f"Error closing poll: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
    
    @staticmethod
    @poll_api_bp.get('/<int:pollId>/responses',
                    summary="获取投票响应列表",
                    tags=[poll_tag],
                    responses={200: MessageResponseModel, 403: MessageResponseModel, 404: MessageResponseModel})
    @login_required
    def get_poll_responses(path: PollPathModel):
        """
        获取投票的所有响应记录（教师）
        
        返回该投票的所有学生投票记录，包括学生信息和选择的选项。
        只有创建投票的教师或管理员可以查看。
        """
        try:
            from app.models.interaction import PollResponse
            from app.models.user import User
            
            user_id = session.get('user_id')
            user_role = session.get('role')
            
            PollAPI.log_request("GET_POLL_RESPONSES", f"poll_id={path.poll_id}, user_id={user_id}")
            
            # 获取投票
            poll = PollService.get_poll_by_id(path.poll_id)
            if not poll:
                return ResponseHandler.error(
                    message="投票不存在",
                    error_code="NOT_FOUND"
                ), 404
            
            # 验证权限（只有教师或管理员可以查看）
            if poll.teacher_id != user_id and user_role != UserRole.ADMIN.value:
                logger.warning(f"User {user_id} attempted to view poll responses {path.poll_id} without permission")
                return ResponseHandler.error(
                    message="无权限查看投票响应",
                    error_code="PERMISSION_DENIED"
                ), 403
            
            # 获取所有响应
            responses = PollResponse.get_by_poll(path.poll_id)
            
            # 构建响应数据
            response_list = []
            for resp in responses:
                # 获取学生信息
                student = User.query.get(resp.student_id)
                
                response_list.append({
                    'id': resp.id,
                    'student_id': resp.student_id,
                    'student_name': student.real_name if student else f'学生{resp.student_id}',
                    'student_username': student.username if student else '',
                    'selected_options': resp.selected_options,
                    'created_at': resp.created_at.isoformat() if resp.created_at else None
                })
            
            return ResponseHandler.success(
                data={
                    'responses': response_list,
                    'total': len(response_list)
                },
                message="获取投票响应成功"
            ), 200
            
        except Exception as e:
            logger.error(f"Error getting poll responses: {str(e)}")
            return ResponseHandler.error(
                message="服务器内部错误",
                error_code="INTERNAL_ERROR"
            ), 500
