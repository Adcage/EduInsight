import re
from typing import Optional

def validate_email(email: str) -> bool:
    """验证邮箱格式"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """验证手机号格式"""
    pattern = r'^1[3-9]\d{9}$'
    return bool(re.match(pattern, phone))

def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """验证密码强度"""
    if len(password) < 6:
        return False, "密码长度至少6位"
    
    if len(password) > 128:
        return False, "密码长度不能超过128位"
    
    # 检查是否包含至少一个字母和一个数字
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_letter and has_digit):
        return False, "密码必须包含至少一个字母和一个数字"
    
    return True, None

def validate_username(username: str) -> tuple[bool, Optional[str]]:
    """验证用户名格式"""
    if len(username) < 2:
        return False, "用户名长度至少2位"
    
    if len(username) > 50:
        return False, "用户名长度不能超过50位"
    
    # 只允许中文、英文、数字和下划线
    pattern = r'^[\u4e00-\u9fa5a-zA-Z0-9_]+$'
    if not re.match(pattern, username):
        return False, "用户名只能包含中文、英文、数字和下划线"
    
    return True, None
