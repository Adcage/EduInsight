from flask_openapi3 import APIBlueprint, Tag
from app.schemas.user_schemas import (
    UserUpdateModel, UserResponseModel, UserListResponseModel, 
    UserPathModel, UserQueryModel, MessageResponseModel, UserStatsModel
)
from app.services.auth_service import AuthService
from app.models.user import User, UserRole
from app.utils.auth_decorators import (
    login_required, admin_required, teacher_or_admin_required, 
    log_user_action, get_current_user_info
)
from app.extensions import db
from sqlalchemy import or_, func
import logging

logger = logging.getLogger(__name__)

user_api_bp = APIBlueprint('user_api', __name__, url_prefix='/api/v1/users')
user_tag = Tag(name="UserController", description="用户管理API")

class UserAPI:
    """
    用户管理API类 - 装饰器方式
    
    提供用户管理的完整功能，包括：
    - 用户列表查询（支持分页和搜索）
    - 用户信息更新
    - 用户状态管理
    - 用户统计信息
    """
    
    # 类属性：配置和状态
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[{cls.request_count}] {action}{user_desc}")
    
    @staticmethod
    @user_api_bp.get('/', 
                    summary="获取用户列表", 
                    tags=[user_tag],
                    responses={200: UserListResponseModel, 401: MessageResponseModel})
    @teacher_or_admin_required
    @log_user_action("查询用户列表")
    def list_users(query: UserQueryModel):
        """
        获取用户列表
        
        支持分页、角色筛选、状态筛选和关键词搜索。
        只有教师和管理员可以访问。
        """
        try:
            UserAPI.log_request("LIST_USERS")
            
            # 构建查询
            query_obj = User.query.filter_by(status=True)  # 只显示活跃用户
            
            # 角色筛选
            if query.role:
                query_obj = query_obj.filter(User.role == UserRole(query.role.value))
            
            # 状态筛选
            if query.status is not None:
                query_obj = query_obj.filter(User.status == query.status)
            
            # 关键词搜索
            if query.search:
                search_term = f"%{query.search}%"
                query_obj = query_obj.filter(
                    or_(
                        User.username.like(search_term),
                        User.real_name.like(search_term),
                        User.email.like(search_term),
                        User.user_code.like(search_term)
                    )
                )
            
            # 分页查询
            pagination = query_obj.paginate(
                page=query.page,
                per_page=query.per_page,
                error_out=False
            )
            
            users = [user.to_dict() for user in pagination.items]
            
            return {
                'users': users,
                'total': pagination.total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': pagination.pages
            }, 200
            
        except Exception as e:
            logger.error(f"List users error: {str(e)}")
            return {
                'message': '获取用户列表失败',
                'error_code': 'LIST_USERS_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.get('/stats', 
                    summary="获取用户统计", 
                    tags=[user_tag],
                    responses={200: UserStatsModel, 401: MessageResponseModel})
    @admin_required
    @log_user_action("查询用户统计")
    def get_user_stats():
        """
        获取用户统计信息
        
        只有管理员可以访问。
        """
        try:
            UserAPI.log_request("GET_USER_STATS")
            
            # 统计用户数量
            total_users = User.query.count()
            admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
            teacher_count = User.query.filter_by(role=UserRole.TEACHER).count()
            student_count = User.query.filter_by(role=UserRole.STUDENT).count()
            active_users = User.query.filter_by(status=True).count()
            inactive_users = User.query.filter_by(status=False).count()
            
            return {
                'total_users': total_users,
                'admin_count': admin_count,
                'teacher_count': teacher_count,
                'student_count': student_count,
                'active_users': active_users,
                'inactive_users': inactive_users
            }, 200
            
        except Exception as e:
            logger.error(f"Get user stats error: {str(e)}")
            return {
                'message': '获取用户统计失败',
                'error_code': 'GET_STATS_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.get('/<int:user_id>', 
                    summary="获取指定用户", 
                    tags=[user_tag],
                    responses={200: UserResponseModel, 404: MessageResponseModel})
    @teacher_or_admin_required
    def get_user(path: UserPathModel):
        """
        获取指定用户信息
        
        只有教师和管理员可以访问。
        """
        try:
            UserAPI.log_request("GET_USER", str(path.user_id))
            
            user = User.query.get(path.user_id)
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            return user.to_dict(), 200
            
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return {
                'message': '获取用户信息失败',
                'error_code': 'GET_USER_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.put('/<int:user_id>', 
                    summary="更新用户信息", 
                    tags=[user_tag],
                    responses={200: UserResponseModel, 404: MessageResponseModel})
    @admin_required
    @log_user_action("更新用户信息")
    def update_user(path: UserPathModel, body: UserUpdateModel):
        """
        更新用户信息
        
        只有管理员可以更新其他用户的信息。
        """
        try:
            UserAPI.log_request("UPDATE_USER", str(path.user_id))
            
            user = User.query.get(path.user_id)
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            # 更新用户信息
            update_data = body.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            
            db.session.commit()
            
            return {
                'message': '用户信息更新成功',
                'user': user.to_dict()
            }, 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update user error: {str(e)}")
            return {
                'message': '更新用户信息失败',
                'error_code': 'UPDATE_USER_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.post('/<int:user_id>/deactivate', 
                     summary="停用用户账户", 
                     tags=[user_tag],
                     responses={200: MessageResponseModel, 404: MessageResponseModel})
    @admin_required
    @log_user_action("停用用户账户")
    def deactivate_user(path: UserPathModel):
        """
        停用用户账户
        
        只有管理员可以停用用户账户。
        """
        try:
            UserAPI.log_request("DEACTIVATE_USER", str(path.user_id))
            
            success = AuthService.deactivate_user(path.user_id)
            if not success:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            return {
                'message': '用户账户已停用'
            }, 200
            
        except Exception as e:
            logger.error(f"Deactivate user error: {str(e)}")
            return {
                'message': '停用用户账户失败',
                'error_code': 'DEACTIVATE_USER_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.post('/<int:user_id>/activate', 
                     summary="激活用户账户", 
                     tags=[user_tag],
                     responses={200: MessageResponseModel, 404: MessageResponseModel})
    @admin_required
    @log_user_action("激活用户账户")
    def activate_user(path: UserPathModel):
        """
        激活用户账户
        
        只有管理员可以激活用户账户。
        """
        try:
            UserAPI.log_request("ACTIVATE_USER", str(path.user_id))
            
            success = AuthService.activate_user(path.user_id)
            if not success:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            return {
                'message': '用户账户已激活'
            }, 200
            
        except Exception as e:
            logger.error(f"Activate user error: {str(e)}")
            return {
                'message': '激活用户账户失败',
                'error_code': 'ACTIVATE_USER_ERROR'
            }, 500

    @staticmethod
    @user_api_bp.get('/health', 
                    summary="用户API健康检查", 
                    tags=[user_tag])
    def health_check():
        """用户API健康检查"""
        import time
        return {
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'request_count': UserAPI.request_count,
            'version': '1.0.0'
        }, 200
