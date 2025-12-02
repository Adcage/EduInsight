from flask_openapi3 import APIBlueprint, Tag
from app.model.auth_model import LoginModel, RegisterModel, TokenResponseModel
from app.services.auth_service import AuthService

auth_api_bp = APIBlueprint('auth_api', __name__, url_prefix='/api/v1/auth')
auth_tag = Tag(name="AuthController", description="认证管理API")

class AuthAPI:
    """认证API类"""
    
    @staticmethod
    @auth_api_bp.post('/register', summary="用户注册", tags=[auth_tag])
    def register(body: RegisterModel):
        """用户注册"""
        try:
            user = AuthService.register_user(body)
            return {
                'message': 'User registered successfully',
                'user': user.to_dict()
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @auth_api_bp.post('/login', summary="用户登录", tags=[auth_tag])
    def login(body: LoginModel):
        """用户登录"""
        try:
            user = AuthService.authenticate_user(body.email, body.password)
            if not user:
                return {'message': 'Invalid credentials'}, 401
            
            return {
                'message': 'Login successful',
                'user': user.to_dict()
            }
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @auth_api_bp.get(
        '/profile/<int:user_id>', 
        summary="获取用户信息", 
        tags=[auth_tag]
    )
    def get_profile(user_id: int):
        """获取用户信息"""
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.to_dict()
    
