"""
文件处理工具函数

提供文件上传、存储、验证等功能。
"""
import os
import uuid
from datetime import datetime
from typing import Tuple, Optional, Dict, Any
from werkzeug.utils import secure_filename
from werkzeug.datastructures import FileStorage
import mimetypes

# 允许的文件扩展名
ALLOWED_EXTENSIONS = {
    # 文档
    'pdf', 'doc', 'docx', 'ppt', 'pptx', 'xls', 'xlsx', 'txt', 'md',
    # 图片
    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'svg', 'webp',
    # 压缩包
    'zip', 'rar', '7z', 'tar', 'gz',
    # 视频（可选）
    'mp4', 'avi', 'mov', 'wmv', 'flv', 'mkv'
}

# 文件类型映射
FILE_TYPE_MAPPING = {
    'pdf': 'pdf',
    'doc': 'doc',
    'docx': 'doc',
    'ppt': 'ppt',
    'pptx': 'ppt',
    'xls': 'xls',
    'xlsx': 'xls',
    'txt': 'text',
    'md': 'text',
    'jpg': 'image',
    'jpeg': 'image',
    'png': 'image',
    'gif': 'image',
    'bmp': 'image',
    'svg': 'image',
    'webp': 'image',
    'zip': 'archive',
    'rar': 'archive',
    '7z': 'archive',
    'tar': 'archive',
    'gz': 'archive',
    'mp4': 'video',
    'avi': 'video',
    'mov': 'video',
    'wmv': 'video',
    'flv': 'video',
    'mkv': 'video'
}

# 文件大小限制（字节）
MAX_FILE_SIZE = 100 * 1024 * 1024  # 100MB

# 文件类型图标映射（用于前端显示）
FILE_TYPE_ICONS = {
    'pdf': 'file-pdf',
    'doc': 'file-word',
    'ppt': 'file-ppt',
    'xls': 'file-excel',
    'text': 'file-text',
    'image': 'file-image',
    'archive': 'file-zip',
    'video': 'file-video',
    'other': 'file'
}

# MIME类型映射
MIME_TYPE_MAPPING = {
    'pdf': 'application/pdf',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'ppt': 'application/vnd.ms-powerpoint',
    'pptx': 'application/vnd.openxmlformats-officedocument.presentationml.presentation',
    'xls': 'application/vnd.ms-excel',
    'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    'txt': 'text/plain',
    'md': 'text/markdown',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'bmp': 'image/bmp',
    'svg': 'image/svg+xml',
    'webp': 'image/webp',
    'zip': 'application/zip',
    'rar': 'application/x-rar-compressed',
    '7z': 'application/x-7z-compressed',
    'mp4': 'video/mp4',
    'avi': 'video/x-msvideo',
    'mov': 'video/quicktime'
}


def allowed_file(filename: str) -> bool:
    """
    检查文件扩展名是否允许
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否允许
    """
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename: str) -> str:
    """
    获取文件扩展名
    
    Args:
        filename: 文件名
        
    Returns:
        str: 扩展名（小写，不含点）
    """
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def get_file_type(filename: str) -> str:
    """
    根据文件名获取文件类型
    
    Args:
        filename: 文件名
        
    Returns:
        str: 文件类型
    """
    ext = get_file_extension(filename)
    return FILE_TYPE_MAPPING.get(ext, 'other')


def generate_unique_filename(original_filename: str) -> str:
    """
    生成唯一的文件名
    
    保留原始文件名，在后面添加UUID确保唯一性
    格式：原始文件名_UUID.扩展名
    
    Args:
        original_filename: 原始文件名
        
    Returns:
        str: 唯一文件名
    """
    # 获取文件名（不含扩展名）和扩展名
    ext = get_file_extension(original_filename)
    name_without_ext = original_filename
    if ext:
        name_without_ext = original_filename[:-(len(ext) + 1)]
    
    # 生成唯一文件名：原始名_UUID.扩展名
    unique_id = uuid.uuid4().hex[:8]  # 使用8位UUID，更简洁
    unique_name = f"{name_without_ext}_{unique_id}"
    if ext:
        unique_name = f"{unique_name}.{ext}"
    
    return unique_name


def get_upload_path(base_dir: str = None) -> str:
    """
    获取上传路径（按年月组织）
    
    Args:
        base_dir: 基础目录，默认为 uploads/materials
        
    Returns:
        str: 完整的上传路径
    """
    if base_dir is None:
        base_dir = os.path.join('uploads', 'materials')
    
    now = datetime.now()
    year = now.strftime('%Y')
    month = now.strftime('%m')
    
    upload_path = os.path.join(base_dir, year, month)
    
    # 确保目录存在
    os.makedirs(upload_path, exist_ok=True)
    
    return upload_path


def validate_file(file: FileStorage, max_size: int = MAX_FILE_SIZE) -> Tuple[bool, Optional[str]]:
    """
    验证上传的文件
    
    Args:
        file: 上传的文件对象
        max_size: 最大文件大小（字节）
        
    Returns:
        Tuple[bool, Optional[str]]: (是否有效, 错误信息)
    """
    # 检查文件是否存在
    if not file or not file.filename:
        return False, "未选择文件"
    
    # 检查文件名是否为空
    if file.filename == '':
        return False, "文件名为空"
    
    # 检查文件扩展名
    if not allowed_file(file.filename):
        return False, f"不支持的文件类型。允许的类型: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    
    # 检查文件大小
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)  # 重置文件指针
    
    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        return False, f"文件大小超过限制（最大 {max_size_mb:.0f}MB）"
    
    if file_size == 0:
        return False, "文件大小为0"
    
    return True, None


def save_uploaded_file(file: FileStorage, base_dir: str = None) -> Tuple[str, str, int]:
    """
    保存上传的文件
    
    Args:
        file: 上传的文件对象
        base_dir: 基础目录，默认为 uploads/materials
        
    Returns:
        Tuple[str, str, int]: (文件路径, 唯一文件名, 文件大小)
        
    Raises:
        ValueError: 文件验证失败
    """
    if base_dir is None:
        base_dir = os.path.join('uploads', 'materials')
    
    # 验证文件
    is_valid, error_msg = validate_file(file)
    if not is_valid:
        raise ValueError(error_msg)
    
    # 生成唯一文件名
    unique_filename = generate_unique_filename(file.filename)
    
    # 获取上传路径
    upload_path = get_upload_path(base_dir)
    
    # 完整文件路径
    file_path = os.path.join(upload_path, unique_filename)
    
    # 保存文件
    file.save(file_path)
    
    # 获取文件大小
    file_size = os.path.getsize(file_path)
    
    return file_path, unique_filename, file_size


def delete_file(file_path: str) -> bool:
    """
    删除文件
    
    Args:
        file_path: 文件路径
        
    Returns:
        bool: 是否成功删除
    """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            return True
        return False
    except Exception as e:
        print(f"删除文件失败: {e}")
        return False


def get_file_size_mb(file_size_bytes: int) -> float:
    """
    将字节转换为MB
    
    Args:
        file_size_bytes: 文件大小（字节）
        
    Returns:
        float: 文件大小（MB）
    """
    return round(file_size_bytes / (1024 * 1024), 2)


def get_file_size_human_readable(file_size_bytes: int) -> str:
    """
    将文件大小转换为人类可读格式
    
    Args:
        file_size_bytes: 文件大小（字节）
        
    Returns:
        str: 人类可读的文件大小
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if file_size_bytes < 1024.0:
            return f"{file_size_bytes:.2f} {unit}"
        file_size_bytes /= 1024.0
    return f"{file_size_bytes:.2f} PB"


def get_mime_type(filename: str) -> str:
    """
    根据文件名获取MIME类型
    
    Args:
        filename: 文件名
        
    Returns:
        str: MIME类型
    """
    ext = get_file_extension(filename)
    if ext in MIME_TYPE_MAPPING:
        return MIME_TYPE_MAPPING[ext]
    
    mime_type, _ = mimetypes.guess_type(filename)
    return mime_type or 'application/octet-stream'


def get_file_icon(filename: str) -> str:
    """
    根据文件名获取图标名称
    
    Args:
        filename: 文件名
        
    Returns:
        str: 图标名称
    """
    file_type = get_file_type(filename)
    return FILE_TYPE_ICONS.get(file_type, 'file')


def is_image_file(filename: str) -> bool:
    """
    判断是否为图片文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为图片
    """
    return get_file_type(filename) == 'image'


def is_document_file(filename: str) -> bool:
    """
    判断是否为文档文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为文档
    """
    file_type = get_file_type(filename)
    return file_type in ['pdf', 'doc', 'ppt', 'xls', 'text']


def is_archive_file(filename: str) -> bool:
    """
    判断是否为压缩包文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为压缩包
    """
    return get_file_type(filename) == 'archive'


def is_video_file(filename: str) -> bool:
    """
    判断是否为视频文件
    
    Args:
        filename: 文件名
        
    Returns:
        bool: 是否为视频
    """
    return get_file_type(filename) == 'video'


def ensure_upload_directory(base_dir: str = None) -> str:
    """
    确保上传目录存在
    
    Args:
        base_dir: 基础目录，默认为 uploads/materials
        
    Returns:
        str: 完整路径
    """
    if base_dir is None:
        base_dir = os.path.join('uploads', 'materials')
    
    os.makedirs(base_dir, exist_ok=True)
    return os.path.abspath(base_dir)


def get_file_info(file_path: str) -> Dict[str, Any]:
    """
    获取文件详细信息
    
    Args:
        file_path: 文件路径
        
    Returns:
        Dict: 文件信息字典
    """
    if not os.path.exists(file_path):
        return None
    
    stat = os.stat(file_path)
    filename = os.path.basename(file_path)
    
    return {
        'filename': filename,
        'size': stat.st_size,
        'size_human': get_file_size_human_readable(stat.st_size),
        'extension': get_file_extension(filename),
        'file_type': get_file_type(filename),
        'mime_type': get_mime_type(filename),
        'icon': get_file_icon(filename),
        'created_at': datetime.fromtimestamp(stat.st_ctime),
        'modified_at': datetime.fromtimestamp(stat.st_mtime)
    }


def sanitize_filename(filename: str) -> str:
    """
    清理文件名，移除危险字符
    
    Args:
        filename: 原始文件名
        
    Returns:
        str: 清理后的文件名
    """
    # 使用werkzeug的secure_filename
    return secure_filename(filename)


def validate_file_path(file_path: str, base_dir: str = 'uploads') -> bool:
    """
    验证文件路径是否安全（防止路径遍历攻击）
    
    Args:
        file_path: 文件路径
        base_dir: 基础目录
        
    Returns:
        bool: 路径是否安全
    """
    # 获取绝对路径
    abs_file_path = os.path.abspath(file_path)
    abs_base_dir = os.path.abspath(base_dir)
    
    # 检查文件路径是否在基础目录内
    return abs_file_path.startswith(abs_base_dir)
