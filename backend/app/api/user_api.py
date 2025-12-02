from flask_openapi3 import APIBlueprint, Tag
from app.model.user_model import (
    UserCreateModel, UserUpdateModel, UserResponseModel, 
    UserListResponseModel, UserPathModel
)
from app.services.user_service import UserService

user_api_bp = APIBlueprint('user_api', __name__, url_prefix='/api/v1/users')
user_tag = Tag(name="UserController", description="用户管理API")

class UserAPI:
    """用户API类"""
    
    @staticmethod
    @user_api_bp.get('/', summary="获取用户列表", tags=[user_tag])
    def list_users():
        """获取用户列表 - 公开接口"""
        try:
            users = UserService.get_all_users()
            return UserListResponseModel(users=users, total=len(users)).dict()
        except Exception as e:
            return {'message': str(e)}, 500
    
    @staticmethod
    @user_api_bp.post(
        '/', 
        summary="创建新用户", 
        tags=[user_tag]
    )
    def create_user(body: UserCreateModel):
        """创建新用户"""
        try:
            user = UserService.create_user(body)
            return {
                'message': 'User created successfully',
                'user': UserResponseModel.from_orm(user).dict()
            }, 201
        except ValueError as e:
            return {'message': str(e)}, 400
        except Exception as e:
            return {'message': 'Internal server error'}, 500
    
    @staticmethod
    @user_api_bp.get('/<int:user_id>', summary="获取指定用户", tags=[user_tag])
    def get_user(path: UserPathModel):
        """获取指定用户 - 公开接口"""
        user = UserService.get_user_by_id(path.user_id)
        if not user:
            return {'message': 'User not found'}, 404
        return UserResponseModel.from_orm(user).dict()
    
    @staticmethod
    @user_api_bp.put(
        '/<int:user_id>', 
        summary="更新用户信息", 
        tags=[user_tag]
    )
    def update_user(path: UserPathModel, body: UserUpdateModel):
        """更新用户信息"""
        user = UserService.update_user(path.user_id, body)
        if not user:
            return {'message': 'User not found'}, 404
        return {
            'message': 'User updated successfully',
            'user': UserResponseModel.from_orm(user).dict()
        }
    
    @staticmethod
    @user_api_bp.delete(
        '/<int:user_id>', 
        summary="删除用户", 
        tags=[user_tag]
    )
    def delete_user(path: UserPathModel):
        """删除用户"""
        if not UserService.delete_user(path.user_id):
            return {'message': 'User not found'}, 404
        return {'message': 'User deleted successfully'}, 204

    @staticmethod
    @user_api_bp.get(
        '/health', 
        summary="删除用户", 
        tags=[user_tag]
    )
    def health():
        return {'message': 'health'}, 204
