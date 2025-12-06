"""
文件安全验证工具

提供文件内容验证、安全检查等功能，防止恶意文件上传。
"""
import os
from typing import Tuple, Optional, List
from werkzeug.datastructures import FileStorage


# 危险文件扩展名黑名单
DANGEROUS_EXTENSIONS = {
    'exe', 'bat', 'cmd', 'com', 'pif', 'scr', 'vbs', 'js', 'jar',
    'msi', 'dll', 'so', 'dylib', 'sh', 'bash', 'ps1', 'app'
}

# 允许的MIME类型白名单
ALLOWED_MIME_TYPES = {
    # 文档
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'application/vnd.ms-powerpoint',
    'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'application/vnd.ms-excel',
    'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'text/plain',
    'text/markdown',
    # 图片
    'image/jpeg',
    'image/png',
    'image/gif',
    'image/bmp',
    'image/svg+xml',
    'image/webp',
    # 压缩包
    'application/zip',
    'application/x-rar-compressed',
    'application/x-7z-compressed',
    'application/x-tar',
    'application/gzip',
    # 视频
    'video/mp4',
    'video/x-msvideo',
    'video/quicktime',
    'video/x-ms-wmv',
    'video/x-flv',
    'video/x-matroska'
}

# 文件头魔数（用于验证真实文件类型）
FILE_SIGNATURES = {
    'pdf': [b'%PDF'],
    'jpg': [b'\xFF\xD8\xFF'],
    'png': [b'\x89PNG\r\n\x1a\n'],
    'gif': [b'GIF87a', b'GIF89a'],
    'zip': [b'PK\x03\x04', b'PK\x05\x06', b'PK\x07\x08'],
    'doc': [b'\xD0\xCF\x11\xE0\xA1\xB1\x1A\xE1'],
    'docx': [b'PK\x03\x04'],  # DOCX是ZIP格式
    'xlsx': [b'PK\x03\x04'],  # XLSX是ZIP格式
    'pptx': [b'PK\x03\x04'],  # PPTX是ZIP格式
}


def check_dangerous_extension(filename: str) -> Tuple[bool, Optional[str]]:
    """
    检查文件扩展名是否在危险列表中
    
    Args:
        filename: 文件名
        
    Returns:
        Tuple[bool, Optional[str]]: (是否安全, 错误信息)
    """
    if '.' not in filename:
        return True, None
    
    ext = filename.rsplit('.', 1)[1].lower()
    
    if ext in DANGEROUS_EXTENSIONS:
        return False, f"禁止上传 .{ext} 类型的文件"
    
    return True, None


def verify_file_signature(file: FileStorage, expected_ext: str) -> Tuple[bool, Optional[str]]:
    """
    验证文件头魔数，确保文件类型真实性
    
    Args:
        file: 上传的文件对象
        expected_ext: 期望的文件扩展名
        
    Returns:
        Tuple[bool, Optional[str]]: (是否匹配, 错误信息)
    """
    if expected_ext not in FILE_SIGNATURES:
        # 如果没有定义魔数，跳过验证
        return True, None
    
    # 读取文件头
    file.seek(0)
    header = file.read(16)
    file.seek(0)  # 重置文件指针
    
    # 检查是否匹配任一签名
    signatures = FILE_SIGNATURES[expected_ext]
    for signature in signatures:
        if header.startswith(signature):
            return True, None
    
    return False, f"文件内容与扩展名 .{expected_ext} 不匹配，可能是伪装文件"


def check_file_content(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    检查文件内容是否安全
    
    Args:
        file: 上传的文件对象
        
    Returns:
        Tuple[bool, Optional[str]]: (是否安全, 错误信息)
    """
    # 检查文件扩展名
    is_safe, error = check_dangerous_extension(file.filename)
    if not is_safe:
        return False, error
    
    # 获取文件扩展名
    if '.' in file.filename:
        ext = file.filename.rsplit('.', 1)[1].lower()
        
        # 验证文件签名
        is_valid, error = verify_file_signature(file, ext)
        if not is_valid:
            return False, error
    
    return True, None


def validate_mime_type(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    验证文件MIME类型
    
    Args:
        file: 上传的文件对象
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    mime_type = file.content_type
    
    if mime_type not in ALLOWED_MIME_TYPES:
        return False, f"不支持的文件类型: {mime_type}"
    
    return True, None


def scan_file_for_malware(file_path: str) -> Tuple[bool, Optional[str]]:
    """
    扫描文件是否包含恶意软件（需要安装ClamAV等杀毒软件）
    
    注意：这是一个可选功能，需要额外配置
    
    Args:
        file_path: 文件路径
        
    Returns:
        Tuple[bool, Optional[str]]: (是否安全, 错误信息)
    """
    # TODO: 集成ClamAV或其他杀毒引擎
    # 这里暂时返回True，表示跳过病毒扫描
    return True, None


def validate_file_size_by_type(file_size: int, file_type: str) -> Tuple[bool, Optional[str]]:
    """
    根据文件类型验证文件大小
    
    Args:
        file_size: 文件大小（字节）
        file_type: 文件类型
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    # 不同文件类型的大小限制
    size_limits = {
        'image': 10 * 1024 * 1024,      # 图片: 10MB
        'pdf': 50 * 1024 * 1024,        # PDF: 50MB
        'doc': 50 * 1024 * 1024,        # 文档: 50MB
        'ppt': 100 * 1024 * 1024,       # PPT: 100MB
        'xls': 50 * 1024 * 1024,        # Excel: 50MB
        'video': 500 * 1024 * 1024,     # 视频: 500MB
        'archive': 200 * 1024 * 1024,   # 压缩包: 200MB
        'text': 5 * 1024 * 1024,        # 文本: 5MB
    }
    
    max_size = size_limits.get(file_type, 100 * 1024 * 1024)  # 默认100MB
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"{file_type}类型文件大小不能超过 {max_size_mb:.0f}MB"
    
    return True, None


def check_filename_length(filename: str, max_length: int = 255) -> Tuple[bool, Optional[str]]:
    """
    检查文件名长度
    
    Args:
        filename: 文件名
        max_length: 最大长度
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    if len(filename) > max_length:
        return False, f"文件名过长（最大{max_length}字符）"
    
    return True, None


def validate_file_security(file: FileStorage) -> Tuple[bool, Optional[str]]:
    """
    综合验证文件安全性
    
    Args:
        file: 上传的文件对象
        
    Returns:
        Tuple[bool, Optional[str]]: (是否安全, 错误信息)
    """
    # 检查文件名长度
    is_valid, error = check_filename_length(file.filename)
    if not is_valid:
        return False, error
    
    # 检查危险扩展名
    is_safe, error = check_dangerous_extension(file.filename)
    if not is_safe:
        return False, error
    
    # 验证MIME类型
    is_valid, error = validate_mime_type(file)
    if not is_valid:
        return False, error
    
    # 检查文件内容
    is_safe, error = check_file_content(file)
    if not is_safe:
        return False, error
    
    return True, None
