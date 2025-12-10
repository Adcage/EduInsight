from flask_openapi3 import APIBlueprint, Tag, FileStorage
from app.schemas.user_schemas import (
    UserUpdateModel, UserResponseModel, UserListResponseModel, 
    UserPathModel, UserQueryModel, MessageResponseModel, UserStatsModel,
    UserCreateModel, BatchDeleteModel, BatchImportResponseModel,
    FaceImageUploadModel
)
from app.services.auth_service import AuthService
from app.services.user_service import UserService
from app.models.user import User, UserRole
from app.utils.auth_decorators import (
    login_required, admin_required, teacher_or_admin_required, 
    log_user_action, get_current_user_info
)
from app.extensions import db
from werkzeug.utils import secure_filename
import os
import base64
from datetime import datetime
from sqlalchemy import or_, func
import logging

logger = logging.getLogger(__name__)

user_api_bp = APIBlueprint('user_api', __name__, url_prefix='/api/v1/users')
user_tag = Tag(name="UserController", description="用户管理API")

class UserAPI:
    """
    用户管理API类 - 装饰器方式
    
    提供用户管理的完整功能，包括：
    - 用户列表查询（支持分页和搜索）
    - 用户信息更新
    - 用户状态管理
    - 用户统计信息
    """
    
    # 类属性：配置和状态
    request_count = 0
    
    @classmethod
    def log_request(cls, action: str, user_info: str = None):
        """记录API请求日志"""
        cls.request_count += 1
        user_desc = f" ({user_info})" if user_info else ""
        logger.info(f"[{cls.request_count}] {action}{user_desc}")
    
    @staticmethod
    @user_api_bp.get('/list',
                    summary="获取用户列表", 
                    tags=[user_tag],
                    responses={200: UserListResponseModel, 401: MessageResponseModel})
    @teacher_or_admin_required
    @log_user_action("查询用户列表")
    def list_users(query: UserQueryModel):
        """
        获取用户列表
        
        支持分页、角色筛选、状态筛选和关键词搜索。
        只有教师和管理员可以访问。
        """
        try:
            UserAPI.log_request("LIST_USERS")
            
            # 构建查询
            query_obj = User.query.filter_by(status=True)  # 只显示活跃用户
            
            # 角色筛选
            if query.role:
                query_obj = query_obj.filter(User.role == UserRole(query.role.value))
            
            # 状态筛选
            if query.status is not None:
                query_obj = query_obj.filter(User.status == query.status)
            
            # 关键词搜索
            if query.search:
                search_term = f"%{query.search}%"
                query_obj = query_obj.filter(
                    or_(
                        User.username.like(search_term),
                        User.real_name.like(search_term),
                        User.email.like(search_term),
                        User.user_code.like(search_term)
                    )
                )
            
            # 分页查询
            pagination = query_obj.paginate(
                page=query.page,
                per_page=query.per_page,
                error_out=False
            )
            
            users = [user.to_dict() for user in pagination.items]
            logger.info(f"用户列表:{users}")

            # 使用 Schema 序列化，自动转换为驼峰格式
            response = UserListResponseModel(
                users=users,
                total=pagination.total,
                page=query.page,
                per_page=query.per_page,
                pages=pagination.pages
            )

            return response.model_dump(by_alias=True), 200
            
        except Exception as e:
            logger.error(f"List users error: {str(e)}")
            return {
                'message': '获取用户列表失败',
                'error_code': 'LIST_USERS_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.get('/stats', 
                    summary="获取用户统计", 
                    tags=[user_tag],
                    responses={200: UserStatsModel, 401: MessageResponseModel})
    @admin_required
    @log_user_action("查询用户统计")
    def get_user_stats():
        """
        获取用户统计信息
        
        只有管理员可以访问。
        """
        try:
            UserAPI.log_request("GET_USER_STATS")
            
            # 统计用户数量
            total_users = User.query.count()
            admin_count = User.query.filter_by(role=UserRole.ADMIN).count()
            teacher_count = User.query.filter_by(role=UserRole.TEACHER).count()
            student_count = User.query.filter_by(role=UserRole.STUDENT).count()
            active_users = User.query.filter_by(status=True).count()
            inactive_users = User.query.filter_by(status=False).count()
            
            # 使用 Schema 序列化，自动转换为驼峰格式
            response = UserStatsModel(
                total_users=total_users,
                admin_count=admin_count,
                teacher_count=teacher_count,
                student_count=student_count,
                active_users=active_users,
                inactive_users=inactive_users
            )

            return response.model_dump(by_alias=True), 200
            
        except Exception as e:
            logger.error(f"Get user stats error: {str(e)}")
            return {
                'message': '获取用户统计失败',
                'error_code': 'GET_STATS_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.get('/<int:userId>', 
                    summary="获取指定用户", 
                    tags=[user_tag],
                    responses={200: UserResponseModel, 404: MessageResponseModel})
    @teacher_or_admin_required
    def get_user(path: UserPathModel):
        """
        获取指定用户信息
        
        只有教师和管理员可以访问。
        """
        try:
            UserAPI.log_request("GET_USER", str(path.user_id))
            
            user = User.query.get(path.user_id)
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            # 使用 Schema 序列化，自动转换为驼峰格式
            response = UserResponseModel.model_validate(user)
            return response.model_dump(by_alias=True), 200
            
        except Exception as e:
            logger.error(f"Get user error: {str(e)}")
            return {
                'message': '获取用户信息失败',
                'error_code': 'GET_USER_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.put('/<int:userId>', 
                    summary="更新用户信息", 
                    tags=[user_tag],
                    responses={200: UserResponseModel, 404: MessageResponseModel})
    @admin_required
    @log_user_action("更新用户信息")
    def update_user(path: UserPathModel, body: UserUpdateModel):
        """
        更新用户信息
        
        只有管理员可以更新其他用户的信息。
        """
        try:
            UserAPI.log_request("UPDATE_USER", str(path.user_id))
            
            user = User.query.get(path.user_id)
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            # 更新用户信息
            update_data = body.dict(exclude_unset=True)
            for field, value in update_data.items():
                if hasattr(user, field) and value is not None:
                    setattr(user, field, value)
            
            db.session.commit()
            
            # 使用 Schema 序列化，自动转换为驼峰格式
            user_response = UserResponseModel.model_validate(user)
            return {
                'message': '用户信息更新成功',
                'user': user_response.model_dump(by_alias=True)
            }, 200
            
        except Exception as e:
            db.session.rollback()
            logger.error(f"Update user error: {str(e)}")
            return {
                'message': '更新用户信息失败',
                'error_code': 'UPDATE_USER_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.post('/<int:userId>/deactivate', 
                     summary="停用用户账户", 
                     tags=[user_tag],
                     responses={200: MessageResponseModel, 404: MessageResponseModel})
    @admin_required
    @log_user_action("停用用户账户")
    def deactivate_user(path: UserPathModel):
        """
        停用用户账户
        
        只有管理员可以停用用户账户。
        """
        try:
            UserAPI.log_request("DEACTIVATE_USER", str(path.user_id))
            
            success = AuthService.deactivate_user(path.user_id)
            if not success:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            return {
                'message': '用户账户已停用'
            }, 200
            
        except Exception as e:
            logger.error(f"Deactivate user error: {str(e)}")
            return {
                'message': '停用用户账户失败',
                'error_code': 'DEACTIVATE_USER_ERROR'
            }, 500
    
    @staticmethod
    @user_api_bp.post('/<int:userId>/activate', 
                     summary="激活用户账户", 
                     tags=[user_tag],
                     responses={200: MessageResponseModel, 404: MessageResponseModel})
    @admin_required
    @log_user_action("激活用户账户")
    def activate_user(path: UserPathModel):
        """
        激活用户账户
        
        只有管理员可以激活用户账户。
        """
        try:
            UserAPI.log_request("ACTIVATE_USER", str(path.user_id))
            
            success = AuthService.activate_user(path.user_id)
            if not success:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404
            
            return {
                'message': '用户账户已激活'
            }, 200
            
        except Exception as e:
            logger.error(f"Activate user error: {str(e)}")
            return {
                'message': '激活用户账户失败',
                'error_code': 'ACTIVATE_USER_ERROR'
            }, 500


    @staticmethod
    @user_api_bp.post('/face-image',
                     summary="上传人脸照片",
                     tags=[user_tag],
                     responses={200: MessageResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("上传人脸照片")
    def upload_face_image(body: FaceImageUploadModel):
        """
        上传人脸照片

        学生上传人脸照片用于人脸识别签到。
        照片以Base64格式上传，后端保存为文件并更新用户表。
        """
        try:
            UserAPI.log_request("UPLOAD_FACE_IMAGE")

            # 获取当前用户信息
            current_user = get_current_user_info()
            if not current_user:
                return {
                    'message': '用户未登录',
                    'error_code': 'USER_NOT_LOGGED_IN'
                }, 401

            user_id = current_user.get('user_id')
            user = User.query.get(user_id)
            if not user:
                return {
                    'message': '用户不存在',
                    'error_code': 'USER_NOT_FOUND'
                }, 404

            # 解析Base64图片数据
            try:
                # 移除data:image/xxx;base64,前缀（如果有）
                face_image_data = body.face_image_base64
                logger.info(f"接收到的 Base64 数据长度: {len(face_image_data)}")
                logger.info(f"Base64 数据前50字符: {face_image_data[:50]}")
                
                if ',' in face_image_data:
                    face_image_data = face_image_data.split(',')[1]
                    logger.info(f"移除前缀后的数据长度: {len(face_image_data)}")
                
                # 清理 Base64 数据：移除空格、换行符等
                face_image_data = face_image_data.strip().replace(' ', '').replace('\n', '').replace('\r', '')
                logger.info(f"清理后的数据长度: {len(face_image_data)}")

                # 解码Base64
                image_bytes = base64.b64decode(face_image_data)
                logger.info(f"解码后的图片大小: {len(image_bytes)} bytes")

                # 验证文件大小（限制5MB）
                max_size = 5 * 1024 * 1024
                if len(image_bytes) > max_size:
                    return {
                        'message': '图片大小超过限制（最大5MB）',
                        'error_code': 'FILE_TOO_LARGE'
                    }, 400

            except Exception as e:
                logger.error(f"Base64 decode error: {str(e)}")
                return {
                    'message': '图片数据格式错误',
                    'error_code': 'INVALID_IMAGE_DATA'
                }, 400

            # 创建上传目录
            upload_dir = os.path.join('uploads', 'face_images')
            os.makedirs(upload_dir, exist_ok=True)

            # 生成文件名：user_id_timestamp.jpg
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"user_{user_id}_{timestamp}.jpg"
            file_path = os.path.join(upload_dir, filename)

            # 删除旧的人脸照片（如果存在）
            if user.face_image and os.path.exists(user.face_image):
                try:
                    os.remove(user.face_image)
                except Exception as e:
                    logger.warning(f"Failed to delete old face image: {str(e)}")

            # 保存文件
            with open(file_path, 'wb') as f:
                f.write(image_bytes)

            # 更新用户表
            user.face_image = file_path
            db.session.commit()

            return {
                'message': '人脸照片上传成功',
                'face_image_path': file_path
            }, 200

        except Exception as e:
            db.session.rollback()
            logger.error(f"Upload face image error: {str(e)}")
            return {
                'message': '上传人脸照片失败',
                'error_code': 'UPLOAD_FACE_IMAGE_ERROR'
            }, 500

    @staticmethod
    @user_api_bp.post('/create',
                     summary="创建用户",
                     tags=[user_tag],
                     responses={200: UserResponseModel, 400: MessageResponseModel})
    @admin_required
    @log_user_action("创建用户")
    def create_user(body: UserCreateModel):
        """
        创建新用户

        只有管理员可以创建用户。
        """
        try:
            UserAPI.log_request("CREATE_USER", body.email)

            user = UserService.create_user(body)

            # 使用 Schema 序列化，自动转换为驼峰格式
            user_response = UserResponseModel.model_validate(user)
            return {
                'message': '用户创建成功',
                'user': user_response.model_dump(by_alias=True)
            }, 200

        except ValueError as e:
            logger.error(str(e))
            return {
                'message': str(e),
                'error_code': 'CREATE_USER_FAILED'
            }, 400
        except Exception as e:
            logger.error(f"Create user error: {str(e)}")
            return {
                'message': '创建用户失败',
                'error_code': 'CREATE_USER_ERROR'
            }, 500

    @staticmethod
    @user_api_bp.post('/batch-import',
                     summary="批量导入用户",
                     tags=[user_tag],
                     responses={200: BatchImportResponseModel, 400: MessageResponseModel})
    @admin_required
    @log_user_action("批量导入用户")
    def batch_import_users():
        """
        从Excel文件批量导入用户

        只有管理员可以批量导入用户。
        Excel文件应包含列: username, user_code, email, real_name, role, phone(可选), class_id(学生必填)
        """
        try:
            from flask import request

            UserAPI.log_request("BATCH_IMPORT_USERS")

            # 检查文件是否存在
            if 'file' not in request.files:
                return {
                    'message': '未找到上传的文件',
                    'error_code': 'NO_FILE'
                }, 400

            file = request.files['file']
            if file.filename == '':
                return {
                    'message': '未选择文件',
                    'error_code': 'NO_FILE_SELECTED'
                }, 400

            # 验证文件类型
            if not file.filename.endswith(('.xlsx', '.xls')):
                return {
                    'message': '只支持Excel文件(.xlsx, .xls)',
                    'error_code': 'INVALID_FILE_TYPE'
                }, 400

            # 保存文件
            filename = secure_filename(file.filename)
            upload_folder = 'uploads/temp'
            os.makedirs(upload_folder, exist_ok=True)
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)

            try:
                # 批量导入
                result = UserService.batch_import_users(file_path)

                # 删除临时文件
                os.remove(file_path)

                # 使用 Schema 序列化，自动转换为驼峰格式
                response = BatchImportResponseModel(
                    success_count=result['success_count'],
                    failed_count=result['failed_count'],
                    total_count=result['total_count'],
                    errors=result['errors'],
                    message=f"导入完成: 成功{result['success_count']}条, 失败{result['failed_count']}条"
                )

                return response.model_dump(by_alias=True), 200

            except Exception as e:
                # 删除临时文件
                if os.path.exists(file_path):
                    os.remove(file_path)
                raise e

        except ValueError as e:
            return {
                'message': str(e),
                'error_code': 'IMPORT_FAILED'
            }, 400
        except Exception as e:
            logger.error(f"Batch import users error: {str(e)}")
            return {
                'message': '批量导入失败',
                'error_code': 'BATCH_IMPORT_ERROR'
            }, 500

    @staticmethod
    @user_api_bp.delete('/batch-delete',
                       summary="批量删除用户",
                       tags=[user_tag],
                       responses={200: BatchImportResponseModel, 400: MessageResponseModel})
    @admin_required
    @log_user_action("批量删除用户")
    def batch_delete_users(body: BatchDeleteModel):
        """
        批量删除用户(软删除)

        只有管理员可以批量删除用户。
        """
        try:
            UserAPI.log_request("BATCH_DELETE_USERS", f"{len(body.user_ids)} users")

            result = UserService.batch_delete_users(body.user_ids)

            # 使用 Schema 序列化，自动转换为驼峰格式
            response = BatchImportResponseModel(
                success_count=result['success_count'],
                failed_count=result['failed_count'],
                total_count=result['total_count'],
                errors=result['errors'],
                message=f"删除完成: 成功{result['success_count']}条, 失败{result['failed_count']}条"
            )

            return response.model_dump(by_alias=True), 200

        except ValueError as e:
            return {
                'message': str(e),
                'error_code': 'DELETE_FAILED'
            }, 400
        except Exception as e:
            logger.error(f"Batch delete users error: {str(e)}")
            return {
                'message': '批量删除失败',
                'error_code': 'BATCH_DELETE_ERROR'
            }, 500
