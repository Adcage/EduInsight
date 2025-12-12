"""
班级管理API
"""
import logging
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.class_schemas import (
    ClassPathModel,
    ClassStudentsResponseModel,
    ClassListResponseModel
)
from app.schemas.common_schemas import MessageResponseModel
from app.services.class_service import ClassService
from app.utils.decorators import log_api_call
from app.utils.auth_decorators import login_required

logger = logging.getLogger(__name__)

# 创建API蓝图
class_api_bp = APIBlueprint('class_api', __name__, url_prefix='/api/v1/classes')

# 创建Tag
class_tag = Tag(name="ClassController", description="班级管理API")


class ClassAPI:
    """班级管理API类"""
    
    @staticmethod
    @class_api_bp.get(
        '/<int:class_id>/students',
        summary="获取班级学生列表",
        description="查询指定班级的所有学生信息",
        responses={
            200: ClassStudentsResponseModel,
            404: MessageResponseModel,
            500: MessageResponseModel
        },
        tags=[class_tag]
    )
    # @login_required  # 暂时注释，方便开发测试
    @log_api_call
    def get_class_students(path: ClassPathModel):
        """
        获取班级学生列表
        
        返回班级下所有学生的详细信息，包括：
        - 学生基本信息（学号、姓名、邮箱、手机）
        - 学生状态
        - 最后登录时间
        - 创建时间
        """
        try:
            class_id = path.class_id
            
            # 调用服务层获取学生信息
            result = ClassService.get_class_students(class_id)
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"获取班级学生信息失败: {str(e)}")
            return {'message': str(e)}, 404
        except Exception as e:
            logger.error(f"获取班级学生信息异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @class_api_bp.get(
        '/',
        summary="获取班级列表",
        description="查询所有班级信息，支持分页和筛选",
        responses={
            200: ClassListResponseModel,
            500: MessageResponseModel
        },
        tags=[class_tag]
    )
    # @login_required  # 暂时注释，方便开发测试
    @log_api_call
    def get_classes():
        """
        获取班级列表
        
        支持分页查询和条件筛选
        """
        try:
            # 这里可以从query参数获取筛选条件
            # 暂时使用默认值
            result = ClassService.get_all_classes()
            
            return result, 200
            
        except Exception as e:
            logger.error(f"获取班级列表异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
