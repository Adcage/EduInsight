from flask_openapi3 import APIBlueprint, Tag
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity
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
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return TokenResponseModel(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user.to_dict()
            ).dict(), 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @auth_api_bp.post('/login', summary="用户登录", tags=[auth_tag])
    def login(body: LoginModel):
        """用户登录获取JWT令牌"""
        try:
            user = AuthService.authenticate_user(body.email, body.password)
            if not user:
                return {'message': 'Invalid credentials'}, 401
            
            access_token = create_access_token(identity=user.id)
            refresh_token = create_refresh_token(identity=user.id)
            
            return TokenResponseModel(
                access_token=access_token,
                refresh_token=refresh_token,
                user=user.to_dict()
            ).dict()
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @auth_api_bp.get(
        '/profile', 
        summary="获取当前用户信息", 
        tags=[auth_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required()
    def get_profile():
        """获取当前用户信息 - 需要JWT认证"""
        current_user_id = get_jwt_identity()
        user = AuthService.get_user_by_id(current_user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return user.to_dict()
    
    @staticmethod
    @auth_api_bp.post(
        '/refresh', 
        summary="刷新访问令牌", 
        tags=[auth_tag],
        security=[{"bearerAuth": []}]  # 🔒 需要JWT认证
    )
    @jwt_required(refresh=True)
    def refresh_token():
        """刷新访问令牌"""
        current_user_id = get_jwt_identity()
        new_token = create_access_token(identity=current_user_id)
        return {'access_token': new_token}
