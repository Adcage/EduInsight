"""
大文件分片上传工具

支持大文件的分片上传、断点续传功能。
"""
import os
import hashlib
import json
from typing import Dict, Optional, List
from datetime import datetime, timedelta
from werkzeug.datastructures import FileStorage


class ChunkedUploadManager:
    """分片上传管理器"""
    
    def __init__(self, temp_dir: str = None):
        """
        初始化分片上传管理器
        
        Args:
            temp_dir: 临时文件目录，默认为 uploads/temp
        """
        if temp_dir is None:
            temp_dir = os.path.join('uploads', 'temp')
        self.temp_dir = temp_dir
        self.metadata_dir = os.path.join(temp_dir, 'metadata')
        
        # 确保目录存在
        os.makedirs(self.temp_dir, exist_ok=True)
        os.makedirs(self.metadata_dir, exist_ok=True)
    
    def generate_upload_id(self, filename: str, file_size: int) -> str:
        """
        生成上传ID
        
        Args:
            filename: 文件名
            file_size: 文件大小
            
        Returns:
            str: 上传ID
        """
        data = f"{filename}_{file_size}_{datetime.now().isoformat()}"
        return hashlib.md5(data.encode()).hexdigest()
    
    def init_upload(self, filename: str, file_size: int, total_chunks: int) -> Dict:
        """
        初始化分片上传
        
        Args:
            filename: 文件名
            file_size: 文件大小
            total_chunks: 总分片数
            
        Returns:
            Dict: 上传信息
        """
        upload_id = self.generate_upload_id(filename, file_size)
        
        # 创建上传目录
        upload_dir = os.path.join(self.temp_dir, upload_id)
        os.makedirs(upload_dir, exist_ok=True)
        
        # 保存元数据
        metadata = {
            'upload_id': upload_id,
            'filename': filename,
            'file_size': file_size,
            'total_chunks': total_chunks,
            'uploaded_chunks': [],
            'created_at': datetime.now().isoformat(),
            'expires_at': (datetime.now() + timedelta(days=1)).isoformat()
        }
        
        metadata_path = os.path.join(self.metadata_dir, f"{upload_id}.json")
        with open(metadata_path, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        return metadata
    
    def save_chunk(self, upload_id: str, chunk_index: int, chunk_data: FileStorage) -> bool:
        """
        保存分片数据
        
        Args:
            upload_id: 上传ID
            chunk_index: 分片索引
            chunk_data: 分片数据
            
        Returns:
            bool: 是否成功
        """
        try:
            # 获取元数据
            metadata = self.get_upload_metadata(upload_id)
            if not metadata:
                return False
            
            # 保存分片
            upload_dir = os.path.join(self.temp_dir, upload_id)
            chunk_path = os.path.join(upload_dir, f"chunk_{chunk_index}")
            
            chunk_data.save(chunk_path)
            
            # 更新元数据
            if chunk_index not in metadata['uploaded_chunks']:
                metadata['uploaded_chunks'].append(chunk_index)
                metadata['uploaded_chunks'].sort()
                self.save_upload_metadata(upload_id, metadata)
            
            return True
            
        except Exception as e:
            print(f"保存分片失败: {e}")
            return False
    
    def get_upload_metadata(self, upload_id: str) -> Optional[Dict]:
        """
        获取上传元数据
        
        Args:
            upload_id: 上传ID
            
        Returns:
            Optional[Dict]: 元数据
        """
        metadata_path = os.path.join(self.metadata_dir, f"{upload_id}.json")
        
        if not os.path.exists(metadata_path):
            return None
        
        try:
            with open(metadata_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"读取元数据失败: {e}")
            return None
    
    def save_upload_metadata(self, upload_id: str, metadata: Dict) -> bool:
        """
        保存上传元数据
        
        Args:
            upload_id: 上传ID
            metadata: 元数据
            
        Returns:
            bool: 是否成功
        """
        metadata_path = os.path.join(self.metadata_dir, f"{upload_id}.json")
        
        try:
            with open(metadata_path, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"保存元数据失败: {e}")
            return False
    
    def is_upload_complete(self, upload_id: str) -> bool:
        """
        检查上传是否完成
        
        Args:
            upload_id: 上传ID
            
        Returns:
            bool: 是否完成
        """
        metadata = self.get_upload_metadata(upload_id)
        if not metadata:
            return False
        
        return len(metadata['uploaded_chunks']) == metadata['total_chunks']
    
    def merge_chunks(self, upload_id: str, output_path: str) -> bool:
        """
        合并分片文件
        
        Args:
            upload_id: 上传ID
            output_path: 输出文件路径
            
        Returns:
            bool: 是否成功
        """
        try:
            metadata = self.get_upload_metadata(upload_id)
            if not metadata:
                return False
            
            if not self.is_upload_complete(upload_id):
                return False
            
            upload_dir = os.path.join(self.temp_dir, upload_id)
            
            # 确保输出目录存在
            os.makedirs(os.path.dirname(output_path), exist_ok=True)
            
            # 合并分片
            with open(output_path, 'wb') as output_file:
                for chunk_index in range(metadata['total_chunks']):
                    chunk_path = os.path.join(upload_dir, f"chunk_{chunk_index}")
                    
                    if not os.path.exists(chunk_path):
                        return False
                    
                    with open(chunk_path, 'rb') as chunk_file:
                        output_file.write(chunk_file.read())
            
            # 验证文件大小
            actual_size = os.path.getsize(output_path)
            expected_size = metadata['file_size']
            
            if actual_size != expected_size:
                os.remove(output_path)
                return False
            
            # 清理临时文件
            self.cleanup_upload(upload_id)
            
            return True
            
        except Exception as e:
            print(f"合并分片失败: {e}")
            return False
    
    def cleanup_upload(self, upload_id: str) -> bool:
        """
        清理上传临时文件
        
        Args:
            upload_id: 上传ID
            
        Returns:
            bool: 是否成功
        """
        try:
            # 删除分片目录
            upload_dir = os.path.join(self.temp_dir, upload_id)
            if os.path.exists(upload_dir):
                import shutil
                shutil.rmtree(upload_dir)
            
            # 删除元数据
            metadata_path = os.path.join(self.metadata_dir, f"{upload_id}.json")
            if os.path.exists(metadata_path):
                os.remove(metadata_path)
            
            return True
            
        except Exception as e:
            print(f"清理临时文件失败: {e}")
            return False
    
    def get_missing_chunks(self, upload_id: str) -> List[int]:
        """
        获取缺失的分片列表
        
        Args:
            upload_id: 上传ID
            
        Returns:
            List[int]: 缺失的分片索引列表
        """
        metadata = self.get_upload_metadata(upload_id)
        if not metadata:
            return []
        
        all_chunks = set(range(metadata['total_chunks']))
        uploaded_chunks = set(metadata['uploaded_chunks'])
        
        return sorted(list(all_chunks - uploaded_chunks))
    
    def cleanup_expired_uploads(self) -> int:
        """
        清理过期的上传
        
        Returns:
            int: 清理的数量
        """
        cleaned_count = 0
        
        try:
            # 遍历所有元数据文件
            for filename in os.listdir(self.metadata_dir):
                if not filename.endswith('.json'):
                    continue
                
                upload_id = filename[:-5]  # 移除.json后缀
                metadata = self.get_upload_metadata(upload_id)
                
                if not metadata:
                    continue
                
                # 检查是否过期
                expires_at = datetime.fromisoformat(metadata['expires_at'])
                if datetime.now() > expires_at:
                    self.cleanup_upload(upload_id)
                    cleaned_count += 1
            
            return cleaned_count
            
        except Exception as e:
            print(f"清理过期上传失败: {e}")
            return cleaned_count


# 全局实例
chunked_upload_manager = ChunkedUploadManager()
