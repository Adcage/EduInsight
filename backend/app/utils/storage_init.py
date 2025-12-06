"""
文件存储初始化脚本

创建必要的文件存储目录结构。
"""
import os
from pathlib import Path


def init_storage_directories(base_dir: str = 'uploads'):
    """
    初始化文件存储目录结构
    
    Args:
        base_dir: 基础目录
    """
    # 定义目录结构
    directories = [
        # 资料文件目录
        os.path.join(base_dir, 'materials'),
        
        # 临时文件目录
        os.path.join(base_dir, 'temp'),
        
        # 分片上传元数据目录
        os.path.join(base_dir, 'temp', 'metadata'),
        
        # 用户头像目录
        os.path.join(base_dir, 'avatars'),
        
        # 课程封面目录
        os.path.join(base_dir, 'course_covers'),
        
        # 导出文件目录
        os.path.join(base_dir, 'exports'),
    ]
    
    # 创建所有目录
    created_dirs = []
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        created_dirs.append(directory)
        print(f"✓ 创建目录: {directory}")
    
    # 创建.gitkeep文件（确保空目录被Git跟踪）
    for directory in directories:
        gitkeep_path = os.path.join(directory, '.gitkeep')
        if not os.path.exists(gitkeep_path):
            Path(gitkeep_path).touch()
    
    print(f"\n✓ 成功创建 {len(created_dirs)} 个存储目录")
    
    return created_dirs


def create_gitignore_for_uploads(base_dir: str = 'uploads'):
    """
    为上传目录创建.gitignore文件
    
    Args:
        base_dir: 基础目录
    """
    gitignore_content = """# 忽略所有上传的文件
*

# 但保留目录结构
!.gitignore
!.gitkeep
!*/
"""
    
    gitignore_path = os.path.join(base_dir, '.gitignore')
    
    with open(gitignore_path, 'w', encoding='utf-8') as f:
        f.write(gitignore_content)
    
    print(f"✓ 创建 .gitignore: {gitignore_path}")


def get_storage_info(base_dir: str = 'uploads') -> dict:
    """
    获取存储信息
    
    Args:
        base_dir: 基础目录
        
    Returns:
        dict: 存储信息
    """
    if not os.path.exists(base_dir):
        return {
            'exists': False,
            'total_size': 0,
            'file_count': 0
        }
    
    total_size = 0
    file_count = 0
    
    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file != '.gitkeep' and file != '.gitignore':
                file_path = os.path.join(root, file)
                total_size += os.path.getsize(file_path)
                file_count += 1
    
    return {
        'exists': True,
        'base_dir': os.path.abspath(base_dir),
        'total_size': total_size,
        'total_size_mb': round(total_size / (1024 * 1024), 2),
        'file_count': file_count
    }


def cleanup_temp_files(base_dir: str = 'uploads', max_age_hours: int = 24):
    """
    清理临时文件
    
    Args:
        base_dir: 基础目录
        max_age_hours: 最大保留时间（小时）
    """
    import time
    from datetime import datetime, timedelta
    
    temp_dir = os.path.join(base_dir, 'temp')
    
    if not os.path.exists(temp_dir):
        return
    
    cutoff_time = time.time() - (max_age_hours * 3600)
    cleaned_count = 0
    
    for root, dirs, files in os.walk(temp_dir):
        for file in files:
            if file in ['.gitkeep', '.gitignore']:
                continue
            
            file_path = os.path.join(root, file)
            
            # 检查文件修改时间
            if os.path.getmtime(file_path) < cutoff_time:
                try:
                    os.remove(file_path)
                    cleaned_count += 1
                except Exception as e:
                    print(f"删除文件失败 {file_path}: {e}")
    
    print(f"✓ 清理了 {cleaned_count} 个临时文件")


def main():
    """主函数"""
    print("=" * 60)
    print("文件存储初始化")
    print("=" * 60)
    print()
    
    # 初始化目录
    init_storage_directories()
    print()
    
    # 创建.gitignore
    create_gitignore_for_uploads()
    print()
    
    # 显示存储信息
    info = get_storage_info()
    print("存储信息:")
    print(f"  - 基础目录: {info.get('base_dir', 'N/A')}")
    print(f"  - 文件数量: {info.get('file_count', 0)}")
    print(f"  - 总大小: {info.get('total_size_mb', 0)} MB")
    print()
    
    print("=" * 60)
    print("✓ 初始化完成")
    print("=" * 60)


if __name__ == '__main__':
    main()
