"""
分片上传API

提供大文件分片上传、断点续传功能。
"""
from flask_openapi3 import APIBlueprint, Tag
from flask import request, session
from app.schemas.common_schemas import MessageResponseModel
from app.utils.auth_decorators import login_required
from app.utils.response_handler import success_response, error_response
from app.utils.chunked_upload import chunked_upload_manager
from app.utils.file_utils import generate_unique_filename, get_upload_path
import logging
import os

logger = logging.getLogger(__name__)

chunked_upload_api_bp = APIBlueprint('chunked_upload_api', __name__, url_prefix='/api/v1/chunked-upload')
chunked_upload_tag = Tag(name="ChunkedUploadController", description="分片上传API")


class ChunkedUploadAPI:
    """
    分片上传API类
    
    提供大文件的分片上传、断点续传功能。
    """
    
    @staticmethod
    @chunked_upload_api_bp.post('/init',
                                summary="初始化分片上传",
                                tags=[chunked_upload_tag],
                                responses={200: MessageResponseModel})
    @login_required
    def init_chunked_upload():
        """
        初始化分片上传
        
        请求参数：
        - filename: 文件名
        - file_size: 文件大小（字节）
        - total_chunks: 总分片数
        """
        try:
            data = request.get_json()
            
            filename = data.get('filename')
            file_size = data.get('file_size')
            total_chunks = data.get('total_chunks')
            
            if not all([filename, file_size, total_chunks]):
                return error_response("缺少必要参数", 400)
            
            # 初始化上传
            metadata = chunked_upload_manager.init_upload(
                filename=filename,
                file_size=file_size,
                total_chunks=total_chunks
            )
            
            return success_response(
                data=metadata,
                message="分片上传初始化成功"
            )
            
        except Exception as e:
            logger.error(f"初始化分片上传失败: {str(e)}")
            return error_response(f"初始化失败: {str(e)}", 500)
    
    @staticmethod
    @chunked_upload_api_bp.post('/chunk',
                                summary="上传分片",
                                tags=[chunked_upload_tag],
                                responses={200: MessageResponseModel})
    @login_required
    def upload_chunk():
        """
        上传单个分片
        
        请求参数：
        - upload_id: 上传ID
        - chunk_index: 分片索引
        - chunk: 分片文件数据
        """
        try:
            upload_id = request.form.get('upload_id')
            chunk_index = request.form.get('chunk_index', type=int)
            
            if not upload_id or chunk_index is None:
                return error_response("缺少必要参数", 400)
            
            if 'chunk' not in request.files:
                return error_response("未找到分片数据", 400)
            
            chunk_file = request.files['chunk']
            
            # 保存分片
            success = chunked_upload_manager.save_chunk(
                upload_id=upload_id,
                chunk_index=chunk_index,
                chunk_data=chunk_file
            )
            
            if not success:
                return error_response("保存分片失败", 500)
            
            # 检查是否完成
            is_complete = chunked_upload_manager.is_upload_complete(upload_id)
            
            return success_response(
                data={
                    'chunk_index': chunk_index,
                    'is_complete': is_complete
                },
                message="分片上传成功"
            )
            
        except Exception as e:
            logger.error(f"上传分片失败: {str(e)}")
            return error_response(f"上传失败: {str(e)}", 500)
    
    @staticmethod
    @chunked_upload_api_bp.post('/merge',
                                summary="合并分片",
                                tags=[chunked_upload_tag],
                                responses={200: MessageResponseModel})
    @login_required
    def merge_chunks():
        """
        合并所有分片
        
        请求参数：
        - upload_id: 上传ID
        """
        try:
            data = request.get_json()
            upload_id = data.get('upload_id')
            
            if not upload_id:
                return error_response("缺少上传ID", 400)
            
            # 检查是否完成
            if not chunked_upload_manager.is_upload_complete(upload_id):
                missing_chunks = chunked_upload_manager.get_missing_chunks(upload_id)
                return error_response(
                    f"上传未完成，缺少分片: {missing_chunks}",
                    400
                )
            
            # 获取元数据
            metadata = chunked_upload_manager.get_upload_metadata(upload_id)
            if not metadata:
                return error_response("上传信息不存在", 404)
            
            # 生成唯一文件名
            unique_filename = generate_unique_filename(metadata['filename'])
            
            # 获取上传路径
            upload_path = get_upload_path()
            output_path = os.path.join(upload_path, unique_filename)
            
            # 合并分片
            success = chunked_upload_manager.merge_chunks(upload_id, output_path)
            
            if not success:
                return error_response("合并分片失败", 500)
            
            return success_response(
                data={
                    'file_path': output_path,
                    'filename': unique_filename,
                    'original_filename': metadata['filename']
                },
                message="文件合并成功"
            )
            
        except Exception as e:
            logger.error(f"合并分片失败: {str(e)}")
            return error_response(f"合并失败: {str(e)}", 500)
    
    @staticmethod
    @chunked_upload_api_bp.get('/status/<upload_id>',
                               summary="查询上传状态",
                               tags=[chunked_upload_tag],
                               responses={200: MessageResponseModel})
    @login_required
    def get_upload_status(upload_id: str):
        """
        查询上传状态
        
        返回已上传的分片列表和缺失的分片列表。
        """
        try:
            metadata = chunked_upload_manager.get_upload_metadata(upload_id)
            
            if not metadata:
                return error_response("上传信息不存在", 404)
            
            missing_chunks = chunked_upload_manager.get_missing_chunks(upload_id)
            is_complete = chunked_upload_manager.is_upload_complete(upload_id)
            
            return success_response(
                data={
                    'upload_id': upload_id,
                    'filename': metadata['filename'],
                    'file_size': metadata['file_size'],
                    'total_chunks': metadata['total_chunks'],
                    'uploaded_chunks': metadata['uploaded_chunks'],
                    'missing_chunks': missing_chunks,
                    'is_complete': is_complete,
                    'progress': len(metadata['uploaded_chunks']) / metadata['total_chunks'] * 100
                },
                message="查询成功"
            )
            
        except Exception as e:
            logger.error(f"查询上传状态失败: {str(e)}")
            return error_response(f"查询失败: {str(e)}", 500)
    
    @staticmethod
    @chunked_upload_api_bp.delete('/<upload_id>',
                                  summary="取消上传",
                                  tags=[chunked_upload_tag],
                                  responses={200: MessageResponseModel})
    @login_required
    def cancel_upload(upload_id: str):
        """
        取消上传并清理临时文件
        """
        try:
            success = chunked_upload_manager.cleanup_upload(upload_id)
            
            if not success:
                return error_response("清理失败", 500)
            
            return success_response(message="上传已取消")
            
        except Exception as e:
            logger.error(f"取消上传失败: {str(e)}")
            return error_response(f"取消失败: {str(e)}", 500)
