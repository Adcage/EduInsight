from typing import List, Optional
from app.models.user import User
from app.schemas.user_schemas import UserRegisterModel, UserUpdateModel
from app.extensions import db

class UserService:
    """用户业务逻辑服务"""
    
    @staticmethod
    def get_all_users() -> List[User]:
        """获取所有用户"""
        return User.query.filter_by(is_active=True).all()
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.filter_by(id=user_id, is_active=True).first()
    
    @staticmethod
    def get_user_by_email(email: str) -> Optional[User]:
        """根据邮箱获取用户"""
        return User.query.filter_by(email=email, is_active=True).first()
    
    @staticmethod
    def create_user(user_data: UserRegisterModel) -> User:
        """创建新用户"""
        # 检查邮箱是否已存在
        existing_user = User.get_by_email(user_data.email)
        if existing_user:
            raise ValueError("邮箱已被注册")
        
        # 创建新用户
        user = User(
            username=user_data.username,
            user_code=user_data.user_code,
            email=user_data.email,
            real_name=user_data.real_name,
            phone=user_data.phone,
            role=user_data.role,
            class_id=user_data.class_id
        )
        user.set_password(user_data.password)
        
        db.session.add(user)
        db.session.commit()
        return user
    
    @staticmethod
    def update_user(user_id: int, user_data: UserUpdateModel) -> Optional[User]:
        """更新用户信息"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            return None
        
        # 检查邮箱是否被其他用户使用
        if user_data.email and user_data.email != user.email:
            existing_user = User.get_by_email(user_data.email)
            if existing_user and existing_user.id != user_id:
                raise ValueError("邮箱已被其他用户使用")
        
        # 更新用户信息
        update_data = user_data.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(user, field, value)
        
        db.session.commit()
        return user
    
    @staticmethod
    def delete_user(user_id: int) -> bool:
        """软删除用户"""
        user = UserService.get_user_by_id(user_id)
        if not user:
            return False
        
        user.is_active = False
        db.session.commit()
        return True
    
    @staticmethod
    def search_users(keyword: str) -> List[User]:
        """搜索用户"""
        return User.query.filter(
            User.is_active == True,
            (User.name.contains(keyword) | User.email.contains(keyword))
        ).all()
