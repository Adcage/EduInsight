import jwt
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from flask import current_app
import logging

logger = logging.getLogger(__name__)

class JWTManager:
    """JWT令牌管理器"""
    
    @staticmethod
    def generate_token(user_id: int, role: str, expires_in: int = 3600) -> str:
        """
        生成JWT令牌
        
        Args:
            user_id: 用户ID
            role: 用户角色
            expires_in: 过期时间（秒），默认1小时
            
        Returns:
            JWT令牌字符串
        """
        try:
            payload = {
                'user_id': user_id,
                'role': role,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow(),
                'type': 'access'
            }
            
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            token = jwt.encode(payload, secret_key, algorithm=algorithm)
            logger.info(f"Generated JWT token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating JWT token: {str(e)}")
            raise
    
    @staticmethod
    def generate_refresh_token(user_id: int, expires_in: int = 86400 * 7) -> str:
        """
        生成刷新令牌
        
        Args:
            user_id: 用户ID
            expires_in: 过期时间（秒），默认7天
            
        Returns:
            刷新令牌字符串
        """
        try:
            payload = {
                'user_id': user_id,
                'exp': datetime.utcnow() + timedelta(seconds=expires_in),
                'iat': datetime.utcnow(),
                'type': 'refresh'
            }
            
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            token = jwt.encode(payload, secret_key, algorithm=algorithm)
            logger.info(f"Generated refresh token for user {user_id}")
            return token
            
        except Exception as e:
            logger.error(f"Error generating refresh token: {str(e)}")
            raise
    
    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        解码JWT令牌
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            解码后的payload字典，失败返回None
        """
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            payload = jwt.decode(token, secret_key, algorithms=[algorithm])
            return payload
            
        except jwt.ExpiredSignatureError:
            logger.warning("JWT token has expired")
            return None
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error decoding JWT token: {str(e)}")
            return None
    
    @staticmethod
    def verify_token(token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        验证JWT令牌
        
        Args:
            token: JWT令牌字符串
            
        Returns:
            (是否有效, payload字典)
        """
        payload = JWTManager.decode_token(token)
        if payload is None:
            return False, None
        
        # 检查令牌类型
        if payload.get('type') != 'access':
            logger.warning("Invalid token type")
            return False, None
        
        return True, payload
    
    @staticmethod
    def verify_refresh_token(token: str) -> tuple[bool, Optional[Dict[str, Any]]]:
        """
        验证刷新令牌
        
        Args:
            token: 刷新令牌字符串
            
        Returns:
            (是否有效, payload字典)
        """
        payload = JWTManager.decode_token(token)
        if payload is None:
            return False, None
        
        # 检查令牌类型
        if payload.get('type') != 'refresh':
            logger.warning("Invalid refresh token type")
            return False, None
        
        return True, payload
    
    @staticmethod
    def refresh_access_token(refresh_token: str, role: str) -> Optional[str]:
        """
        使用刷新令牌生成新的访问令牌
        
        Args:
            refresh_token: 刷新令牌
            role: 用户角色
            
        Returns:
            新的访问令牌，失败返回None
        """
        is_valid, payload = JWTManager.verify_refresh_token(refresh_token)
        if not is_valid or not payload:
            return None
        
        user_id = payload.get('user_id')
        if not user_id:
            return None
        
        return JWTManager.generate_token(user_id, role)
    
    @staticmethod
    def extract_token_from_header(auth_header: str) -> Optional[str]:
        """
        从Authorization头中提取令牌
        
        Args:
            auth_header: Authorization头的值
            
        Returns:
            提取的令牌，失败返回None
        """
        if not auth_header:
            return None
        
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None
        
        return parts[1]
    
    @staticmethod
    def get_token_info(token: str) -> Optional[Dict[str, Any]]:
        """
        获取令牌信息（不验证过期时间）
        
        Args:
            token: JWT令牌
            
        Returns:
            令牌信息字典
        """
        try:
            secret_key = current_app.config.get('JWT_SECRET_KEY', 'your-secret-key')
            algorithm = current_app.config.get('JWT_ALGORITHM', 'HS256')
            
            # 不验证过期时间
            payload = jwt.decode(
                token, 
                secret_key, 
                algorithms=[algorithm],
                options={"verify_exp": False}
            )
            return payload
            
        except jwt.InvalidTokenError as e:
            logger.warning(f"Invalid JWT token: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Error getting token info: {str(e)}")
            return None
