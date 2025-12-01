import hashlib
import secrets
import string
from datetime import datetime, timezone
from typing import Any, Dict, Optional

def generate_random_string(length: int = 32) -> str:
    """生成随机字符串"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def generate_hash(data: str) -> str:
    """生成数据的SHA256哈希值"""
    return hashlib.sha256(data.encode()).hexdigest()

def format_datetime(dt: datetime) -> str:
    """格式化日期时间"""
    return dt.strftime('%Y-%m-%d %H:%M:%S')

def get_current_timestamp() -> int:
    """获取当前时间戳"""
    return int(datetime.now(timezone.utc).timestamp())

def paginate_query(query, page: int = 1, per_page: int = 10):
    """分页查询辅助函数"""
    total = query.count()
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    return {
        'items': items,
        'total': total,
        'page': page,
        'per_page': per_page,
        'pages': (total + per_page - 1) // per_page,
        'has_prev': page > 1,
        'has_next': page * per_page < total
    }

def sanitize_filename(filename: str) -> str:
    """清理文件名，移除危险字符"""
    # 移除路径分隔符和其他危险字符
    dangerous_chars = ['/', '\\', '..', '<', '>', ':', '"', '|', '?', '*']
    for char in dangerous_chars:
        filename = filename.replace(char, '_')
    return filename

def format_file_size(size_bytes: int) -> str:
    """格式化文件大小"""
    if size_bytes == 0:
        return "0B"
    
    size_names = ["B", "KB", "MB", "GB", "TB"]
    i = 0
    while size_bytes >= 1024 and i < len(size_names) - 1:
        size_bytes /= 1024.0
        i += 1
    
    return f"{size_bytes:.1f}{size_names[i]}"

def deep_merge_dict(dict1: Dict[str, Any], dict2: Dict[str, Any]) -> Dict[str, Any]:
    """深度合并字典"""
    result = dict1.copy()
    
    for key, value in dict2.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge_dict(result[key], value)
        else:
            result[key] = value
    
    return result

def mask_sensitive_data(data: str, mask_char: str = '*', visible_chars: int = 4) -> str:
    """遮蔽敏感数据"""
    if len(data) <= visible_chars:
        return mask_char * len(data)
    
    return data[:visible_chars] + mask_char * (len(data) - visible_chars)
