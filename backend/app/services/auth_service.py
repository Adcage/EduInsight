from typing import Optional
from app.models.user import User
from app.model.auth_model import RegisterModel, LoginModel
from app.extensions import db

class AuthService:
    """认证业务逻辑服务"""
    
    @staticmethod
    def register_user(register_data: RegisterModel) -> User:
        """用户注册"""
        # 检查邮箱是否已存在
        existing_user = User.get_by_email(register_data.email)
        if existing_user:
            raise ValueError("邮箱已被注册")
        
        # 创建新用户
        user = User(
            name=register_data.name,
            email=register_data.email,
            phone=register_data.phone
        )
        user.set_password(register_data.password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def authenticate_user(email: str, password: str) -> Optional[User]:
        """用户认证"""
        user = User.get_by_email(email)
        if user and user.is_active and user.check_password(password):
            return user
        return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.filter_by(id=user_id, is_active=True).first()
    
    @staticmethod
    def change_password(user_id: int, old_password: str, new_password: str) -> bool:
        """修改密码"""
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return False
        
        if not user.check_password(old_password):
            raise ValueError("原密码错误")
        
        user.set_password(new_password)
        db.session.commit()
        return True
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """停用用户账户"""
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        db.session.commit()
        return True
