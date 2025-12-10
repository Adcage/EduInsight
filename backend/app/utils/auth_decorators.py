from functools import wraps
from flask import session, jsonify
from typing import List, Optional, Callable, Dict, Any
from app.models.user import UserRole
import logging
import jwt
from datetime import datetime

logger = logging.getLogger(__name__)

def verify_token(token: str) -> Optional[Dict[str, Any]]:
    """
    验证JWT token并返回用户信息
    
    Args:
        token: JWT token字符串
        
    Returns:
        用户信息字典或None
    """
    try:
        # 从环境变量或配置获取密钥
        from flask import current_app
        secret_key = current_app.config.get('SECRET_KEY', 'your-secret-key')
        
        # 解码token
        payload = jwt.decode(token, secret_key, algorithms=['HS256'])
        
        # 检查是否过期
        if 'exp' in payload:
            exp_timestamp = payload['exp']
            if datetime.utcnow().timestamp() > exp_timestamp:
                logger.warning("Token expired")
                return None
        
        # 返回用户信息
        return {
            'user_id': payload.get('user_id'),
            'username': payload.get('username'),
            'role': payload.get('role'),
            'real_name': payload.get('real_name')
        }
        
    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        return None
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {str(e)}")
        return None
    except Exception as e:
        logger.error(f"Error verifying token: {str(e)}")
        return None

def login_required(f: Callable) -> Callable:
    """
    登录验证装饰器
    
    要求用户必须已登录才能访问接口
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session or session.get('user_id') is None:
            logger.warning("Unauthorized access attempt - user not logged in")
            return jsonify({
                'message': '请先登录',
                'error_code': 'UNAUTHORIZED'
            }), 401
        
        return f(*args, **kwargs)
    
    return decorated_function

def role_required(*allowed_roles: UserRole):
    """
    角色验证装饰器
    
    Args:
        allowed_roles: 允许访问的用户角色列表
    
    Usage:
        @role_required(UserRole.ADMIN, UserRole.TEACHER)
        def admin_or_teacher_only():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 首先检查是否已登录
            if 'user_id' not in session or session.get('user_id') is None:
                logger.warning("Unauthorized access attempt - user not logged in")
                return jsonify({
                    'message': '请先登录',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            # 检查用户角色
            user_role = session.get('role')
            if not user_role:
                logger.warning(f"User {session.get('username')} has no role assigned")
                return jsonify({
                    'message': '用户角色未设置',
                    'error_code': 'NO_ROLE'
                }), 403
            
            # 将字符串角色转换为枚举进行比较
            try:
                # 兼容大小写，统一转换为大写
                user_role_upper = user_role.upper() if isinstance(user_role, str) else user_role
                current_role = UserRole(user_role_upper)
                if current_role not in allowed_roles:
                    logger.warning(f"Access denied for user {session.get('username')} with role {user_role}")
                    return jsonify({
                        'message': '权限不足',
                        'error_code': 'INSUFFICIENT_PERMISSIONS'
                    }), 403
            except ValueError:
                logger.error(f"Invalid role value: {user_role}")
                return jsonify({
                    'message': '无效的用户角色',
                    'error_code': 'INVALID_ROLE'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def admin_required(f: Callable) -> Callable:
    """
    管理员权限装饰器
    
    只允许管理员访问
    """
    return role_required(UserRole.ADMIN)(f)

def teacher_required(f: Callable) -> Callable:
    """
    教师权限装饰器
    
    只允许教师访问
    """
    return role_required(UserRole.TEACHER)(f)

def student_required(f: Callable) -> Callable:
    """
    学生权限装饰器
    
    只允许学生访问
    """
    return role_required(UserRole.STUDENT)(f)

def teacher_or_admin_required(f: Callable) -> Callable:
    """
    教师或管理员权限装饰器
    
    允许教师或管理员访问
    """
    return role_required(UserRole.TEACHER, UserRole.ADMIN)(f)

def permission_required(permission: str):
    """
    权限验证装饰器
    
    Args:
        permission: 需要的权限字符串
    
    Usage:
        @permission_required('material:create')
        def create_material():
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 首先检查是否已登录
            if 'user_id' not in session or session.get('user_id') is None:
                logger.warning("Unauthorized access attempt - user not logged in")
                return jsonify({
                    'message': '请先登录',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            # 获取当前用户
            from app.services.auth_service import AuthService
            current_user = AuthService.get_current_user()
            if not current_user:
                logger.warning("Current user not found in database")
                return jsonify({
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }), 404
            
            # 检查权限
            if not current_user.has_permission(permission):
                logger.warning(f"Permission denied for user {current_user.username} - required: {permission}")
                return jsonify({
                    'message': f'权限不足，需要权限: {permission}',
                    'error_code': 'INSUFFICIENT_PERMISSIONS'
                }), 403
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator

def owner_or_admin_required(get_resource_owner_id: Callable):
    """
    资源所有者或管理员权限装饰器
    
    Args:
        get_resource_owner_id: 获取资源所有者ID的函数
    
    Usage:
        def get_material_owner_id(**kwargs):
            material_id = kwargs.get('material_id')
            material = Material.query.get(material_id)
            return material.uploader_id if material else None
        
        @owner_or_admin_required(get_material_owner_id)
        def update_material(material_id):
            pass
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 首先检查是否已登录
            if 'user_id' not in session or session.get('user_id') is None:
                logger.warning("Unauthorized access attempt - user not logged in")
                return jsonify({
                    'message': '请先登录',
                    'error_code': 'UNAUTHORIZED'
                }), 401
            
            current_user_id = session.get('user_id')
            current_role = session.get('role')
            
            # 管理员拥有所有权限
            if current_role == UserRole.ADMIN.value:
                return f(*args, **kwargs)
            
            # 检查是否为资源所有者
            try:
                resource_owner_id = get_resource_owner_id(*args, **kwargs)
                if resource_owner_id == current_user_id:
                    return f(*args, **kwargs)
                else:
                    logger.warning(f"Access denied - user {current_user_id} is not owner of resource (owner: {resource_owner_id})")
                    return jsonify({
                        'message': '只能操作自己的资源',
                        'error_code': 'NOT_RESOURCE_OWNER'
                    }), 403
            except Exception as e:
                logger.error(f"Error checking resource ownership: {str(e)}")
                return jsonify({
                    'message': '权限检查失败',
                    'error_code': 'PERMISSION_CHECK_ERROR'
                }), 500
        
        return decorated_function
    return decorator

def get_current_user_info() -> Optional[dict]:
    """
    获取当前登录用户的基本信息
    
    Returns:
        用户信息字典或None
    """
    if 'user_id' not in session:
        return None
    
    return {
        'user_id': session.get('user_id'),
        'username': session.get('username'),
        'role': session.get('role'),
        'real_name': session.get('real_name')
    }

def log_user_action(action: str):
    """
    用户操作日志装饰器
    
    Args:
        action: 操作类型描述
    """
    def decorator(f: Callable) -> Callable:
        @wraps(f)
        def decorated_function(*args, **kwargs):
            user_info = get_current_user_info()
            if user_info:
                logger.info(f"User action - {action} by {user_info['username']} (ID: {user_info['user_id']})")
            else:
                logger.info(f"Anonymous action - {action}")
            
            return f(*args, **kwargs)
        
        return decorated_function
    return decorator
