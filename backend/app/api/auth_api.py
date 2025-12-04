from flask_openapi3 import APIBlueprint, Tag
from app.schemas.user_schemas import (
    UserRegisterModel, UserLoginModel, UserResponseModel, 
    LoginResponseModel, MessageResponseModel, UserProfileModel,
    PasswordChangeModel, UserPathModel
)
from app.services.auth_service import AuthService
from app.models.user import UserRole
from app.utils.auth_decorators import login_required, log_user_action
import logging

logger = logging.getLogger(__name__)

auth_api_bp = APIBlueprint('auth_api', __name__, url_prefix='/api/v1/auth')
auth_tag = Tag(name="AuthController", description="认证管理API")

class AuthAPI:
    """
    认证API类 - 装饰器方式
    
    提供用户认证相关的完整功能，包括：
    - 用户注册
    - 用户登录/登出
    - 用户信息获取
    - 密码修改
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
    @auth_api_bp.post('/register', 
                     summary="用户注册", 
                     tags=[auth_tag],
                     responses={201: UserResponseModel, 400: MessageResponseModel})
    @log_user_action("用户注册")
    def register(body: UserRegisterModel):
        """
        用户注册
        
        创建新的用户账户，支持多角色注册。
        """
        try:
            AuthAPI.log_request("USER_REGISTER", body.username)
            
            user = AuthService.register_user(
                username=body.username,
                user_code=body.user_code,
                password=body.password,
                email=body.email,
                real_name=body.real_name,
                role=UserRole(body.role.value),
                phone=body.phone,
                class_id=body.class_id
            )
            
            return {
                'message': '注册成功',
                'user': user.to_dict()
            }, 201
            
        except ValueError as e:
            logger.warning(f"Registration failed: {str(e)}")
            return {
                'message': str(e),
                'error_code': 'REGISTRATION_FAILED'
            }, 400
        except Exception as e:
            logger.error(f"Registration error: {str(e)}")
            return {
                'message': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, 500
    
    @staticmethod
    @auth_api_bp.post('/login', 
                     summary="用户登录", 
                     tags=[auth_tag],
                     responses={200: LoginResponseModel, 401: MessageResponseModel})
    @log_user_action("用户登录")
    def login(body: UserLoginModel):
        """
        用户登录
        
        支持多种登录方式：邮箱、用户名、工号/学号。
        登录成功后会将用户信息存储到session中。
        """
        try:
            AuthAPI.log_request("USER_LOGIN", body.login_identifier)
            
            result = AuthService.login_user(body.login_identifier, body.password)
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"Login failed for {body.login_identifier}: {str(e)}")
            return {
                'message': str(e),
                'error_code': 'LOGIN_FAILED'
            }, 401
        except Exception as e:
            logger.error(f"Login error: {str(e)}")
            return {
                'message': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, 500
    
    @staticmethod
    @auth_api_bp.post('/logout', 
                     summary="用户登出", 
                     tags=[auth_tag],
                     responses={200: MessageResponseModel})
    @login_required
    @log_user_action("用户登出")
    def logout():
        """
        用户登出
        
        清除session中的用户信息。
        """
        try:
            result = AuthService.logout_user()
            AuthAPI.log_request("USER_LOGOUT")
            return result, 200
        except Exception as e:
            logger.error(f"Logout error: {str(e)}")
            return {
                'message': '登出失败',
                'error_code': 'LOGOUT_ERROR'
            }, 500
    
    @staticmethod
    @auth_api_bp.get('/get_loginuser', 
                    summary="获取当前登录用户信息", 
                    tags=[auth_tag],
                    responses={200: UserProfileModel, 401: MessageResponseModel})
    @login_required
    def get_loginuser():
        """
        获取当前登录用户的个人信息
        """
        try:
            user = AuthService.get_current_user()
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            return user.to_dict(), 200
            
        except Exception as e:
            logger.error(f"Get loginuser error: {str(e)}")
            return {
                'message': '获取用户信息失败',
                'error_code': 'GET_LOGINUSER_ERROR'
            }, 500
    
    @staticmethod
    @auth_api_bp.post('/change-password', 
                     summary="修改密码", 
                     tags=[auth_tag],
                     responses={200: MessageResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("修改密码")
    def change_password(body: PasswordChangeModel):
        """
        修改当前用户密码
        
        需要提供原密码进行验证。
        """
        try:
            user = AuthService.get_current_user()
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            success = AuthService.change_password(
                user.id, 
                body.old_password, 
                body.new_password
            )
            
            if success:
                AuthAPI.log_request("PASSWORD_CHANGED", user.username)
                return {
                    'message': '密码修改成功'
                }, 200
            else:
                return {
                    'message': '密码修改失败',
                    'error_code': 'PASSWORD_CHANGE_FAILED'
                }, 400
                
        except ValueError as e:
            logger.warning(f"Password change failed: {str(e)}")
            return {
                'message': str(e),
                'error_code': 'INVALID_PASSWORD'
            }, 400
        except Exception as e:
            logger.error(f"Password change error: {str(e)}")
            return {
                'message': '服务器内部错误',
                'error_code': 'INTERNAL_ERROR'
            }, 500
    
    @staticmethod
    @auth_api_bp.get('/status', 
                    summary="检查登录状态", 
                    tags=[auth_tag],
                    responses={200: MessageResponseModel})
    def check_login_status():
        """
        检查用户登录状态
        
        返回用户是否已登录的信息。
        """
        try:
            is_logged_in = AuthService.is_logged_in()
            
            if is_logged_in:
                user = AuthService.get_current_user()
                return {
                    'message': '用户已登录',
                    'logged_in': True,
                    'user': user.to_dict() if user else None
                }, 200
            else:
                return {
                    'message': '用户未登录',
                    'logged_in': False
                }, 200
                
        except Exception as e:
            logger.error(f"Check login status error: {str(e)}")
            return {
                'message': '检查登录状态失败',
                'error_code': 'CHECK_STATUS_ERROR'
            }, 500
    
    @staticmethod
    @auth_api_bp.get('/health', 
                    summary="认证API健康检查", 
                    tags=[auth_tag])
    def health_check():
        """认证API健康检查"""
        import time
        return {
            'status': 'healthy',
            'timestamp': time.strftime('%Y-%m-%d %H:%M:%S'),
            'request_count': AuthAPI.request_count,
            'version': '1.0.0'
        }, 200
    
