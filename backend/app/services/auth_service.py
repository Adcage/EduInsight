from typing import Optional, Dict, Any
from app.models.user import User, UserRole
from app.extensions import db
from flask import session
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """认证业务逻辑服务"""
    
    @staticmethod
    def register_user(username: str, user_code: str, password: str, email: str, 
                     real_name: str, role: UserRole = UserRole.STUDENT, 
                     phone: str = None, class_id: int = None) -> User:
        """
        用户注册
        
        Args:
            username: 用户名
            user_code: 工号/学号
            password: 密码
            email: 邮箱
            real_name: 真实姓名
            role: 用户角色
            phone: 手机号
            class_id: 班级ID（学生角色时使用）
            
        Returns:
            创建的用户对象
        """
        # 检查邮箱是否已存在
        if User.get_by_email(email):
            raise ValueError("邮箱已被注册")
        
        # 检查工号/学号是否已存在
        if User.get_by_user_code(user_code):
            raise ValueError("工号/学号已存在")
        
        # 检查用户名是否已存在
        if User.get_by_username(username):
            raise ValueError("用户名已存在")
        
        # 创建新用户
        user = User(
            username=username,
            user_code=user_code,
            email=email,
            real_name=real_name,
            role=role,
            phone=phone,
            class_id=class_id if role == UserRole.STUDENT else None
        )
        user.set_password(password)
        
        try:
            db.session.add(user)
            db.session.commit()
            logger.info(f"User registered successfully: {username} ({user_code})")
            return user
        except Exception as e:
            db.session.rollback()
            logger.error(f"Error registering user: {str(e)}")
            raise
    
    @staticmethod
    def authenticate_user(login_identifier: str, password: str) -> Optional[User]:
        """
        用户认证
        
        Args:
            login_identifier: 登录标识符（邮箱/用户名/工号）
            password: 密码
            
        Returns:
            认证成功的用户对象，失败返回none
        """
        user = None
        
        # 尝试不同的登录方式
        if '@' in login_identifier:
            # 邮箱登录
            user = User.get_by_email(login_identifier)
        else:
            # 用户名或工号登录
            user = User.get_by_username(login_identifier)
            if not user:
                user = User.get_by_user_code(login_identifier)
        
        if user and user.status and user.check_password(password):
            # 更新最后登录时间
            user.update_last_login()
            logger.info(f"User authenticated successfully: {user.username}")
            return user
        
        logger.warning(f"Authentication failed for: {login_identifier}")
        return None
    
    @staticmethod
    def get_user_by_id(user_id: int) -> Optional[User]:
        """根据ID获取用户"""
        return User.query.filter_by(id=user_id, status=True).first()
    
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
    def login_user(login_identifier: str, password: str) -> Dict[str, Any]:
        """
        用户登录
        
        Args:
            login_identifier: 登录标识符
            password: 密码
            
        Returns:
            包含用户信息的字典
        """
        user = AuthService.authenticate_user(login_identifier, password)
        if not user:
            raise ValueError("用户名或密码错误")
        
        # 将用户信息存储到session中
        session['user_id'] = user.id
        session['username'] = user.username
        session['role'] = user.role.value
        session['real_name'] = user.real_name
        session.permanent = True  # 设置为永久session
        
        logger.info(f"User logged in successfully: {user.username}")
        
        return {
            'user': user.to_dict(),
            'message': '登录成功'
        }
    
    @staticmethod
    def logout_user() -> Dict[str, str]:
        """
        用户登出
        
        Returns:
            登出结果消息
        """
        if 'user_id' in session:
            username = session.get('username', 'Unknown')
            session.clear()
            logger.info(f"User logged out: {username}")
            return {'message': '登出成功'}
        else:
            return {'message': '用户未登录'}
    
    @staticmethod
    def get_current_user() -> Optional[User]:
        """
        从session获取当前用户
        
        Returns:
            当前用户对象，未登录返回None
        """
        user_id = session.get('user_id')
        if not user_id:
            return None
        
        return AuthService.get_user_by_id(user_id)
    
    @staticmethod
    def is_logged_in() -> bool:
        """
        检查用户是否已登录
        
        Returns:
            是否已登录
        """
        return 'user_id' in session and session.get('user_id') is not None
    
    @staticmethod
    def get_current_user_role() -> Optional[str]:
        """
        获取当前用户角色
        
        Returns:
            用户角色字符串
        """
        return session.get('role')
    
    @staticmethod
    def require_login() -> bool:
        """
        要求用户登录
        
        Returns:
            是否已登录
        """
        if not AuthService.is_logged_in():
            raise ValueError("请先登录")
        return True
    
    @staticmethod
    def deactivate_user(user_id: int) -> bool:
        """停用用户账户"""
        user = AuthService.get_user_by_id(user_id)
        if not user:
            return False
        
        user.status = False
        db.session.commit()
        logger.info(f"User deactivated: {user.username}")
        return True
    
    @staticmethod
    def activate_user(user_id: int) -> bool:
        """激活用户账户"""
        user = User.query.get(user_id)
        if not user:
            return False
        
        user.status = True
        db.session.commit()
        logger.info(f"User activated: {user.username}")
        return True
