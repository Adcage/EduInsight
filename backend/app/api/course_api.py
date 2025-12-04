"""
课程管理API
"""
import logging
from flask import request, g
from flask_openapi3 import APIBlueprint, Tag
from app.schemas.course_schemas import (
    CoursePathModel,
    CourseClassListResponseModel,
    CourseClassAddModel,
    CourseResponseModel,
    CourseDetailResponseModel,
    CourseListResponseModel,
    CourseQueryModel
)
from app.schemas.common_schemas import MessageResponseModel
from app.services.course_service import CourseService
from app.utils.decorators import log_api_call
from app.utils.auth_decorators import login_required, teacher_or_admin_required, get_current_user_info

logger = logging.getLogger(__name__)

# 创建API蓝图
course_api_bp = APIBlueprint('course_api', __name__, url_prefix='/api/v1/courses')

# 创建Tag
course_tag = Tag(name="CourseController", description="课程管理API")


class CourseAPI:
    """课程管理API类"""
    
    @staticmethod
    @course_api_bp.get(
        '/<int:course_id>/classes',
        summary="获取课程关联的班级信息",
        description="查询指定课程关联的所有班级及其学生数量",
        responses={
            200: CourseClassListResponseModel,
            404: MessageResponseModel,
            500: MessageResponseModel
        },
        tags=[course_tag]
    )
    # @login_required  # 暂时注释，方便开发测试
    @log_api_call
    def get_course_classes(path: CoursePathModel):
        """
        获取课程关联的班级信息
        
        返回课程下所有关联班级的详细信息，包括：
        - 班级基本信息（名称、代码、年级、专业）
        - 班级学生数量
        - 课程开始/结束日期
        - 关联状态
        """
        try:
            course_id = path.course_id
            
            # 调用服务层获取班级信息
            result = CourseService.get_course_classes(course_id)
            
            return {
                'classes': result['classes'],
                'total': result['total'],
                'total_students': result['total_students']
            }, 200
            
        except ValueError as e:
            logger.warning(f"获取课程班级信息失败: {str(e)}")
            return {'message': str(e)}, 404
        except Exception as e:
            logger.error(f"获取课程班级信息异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @course_api_bp.post(
        '/<int:course_id>/classes',
        summary="为课程添加班级",
        description="为指定课程添加一个或多个班级",
        responses={
            200: MessageResponseModel,
            400: MessageResponseModel,
            403: MessageResponseModel,
            404: MessageResponseModel,
            500: MessageResponseModel
        },
        tags=[course_tag]
    )
    @teacher_or_admin_required
    @log_api_call
    def add_classes_to_course(path: CoursePathModel, body: CourseClassAddModel):
        """
        为课程添加班级
        
        只有教师和管理员可以操作
        """
        try:
            course_id = path.course_id
            user_info = get_current_user_info()
            user_id = user_info['user_id']
            user_role = user_info['role']
            
            # 如果是教师，验证是否为该课程的教师
            if user_role == 'teacher':
                course = CourseService.get_course_by_id(course_id)
                if not course or course.teacher_id != user_id:
                    return {'message': '无权操作此课程'}, 403
            
            # 添加班级
            added_count = CourseService.add_classes_to_course(
                course_id=course_id,
                class_ids=body.class_ids,
                start_date=body.start_date,
                end_date=body.end_date
            )
            
            return {'message': f'成功添加 {added_count} 个班级'}, 200
            
        except ValueError as e:
            logger.warning(f"添加课程班级失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"添加课程班级异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @course_api_bp.delete(
        '/<int:course_id>/classes/<int:class_id>',
        summary="从课程中移除班级",
        description="从指定课程中移除指定班级",
        responses={
            200: MessageResponseModel,
            403: MessageResponseModel,
            404: MessageResponseModel,
            500: MessageResponseModel
        },
        tags=[course_tag]
    )
    @teacher_or_admin_required
    @log_api_call
    def remove_class_from_course(course_id: int, class_id: int):
        """
        从课程中移除班级
        
        只有教师和管理员可以操作
        """
        try:
            user_info = get_current_user_info()
            user_id = user_info['user_id']
            user_role = user_info['role']
            
            # 如果是教师，验证是否为该课程的教师
            if user_role == 'teacher':
                course = CourseService.get_course_by_id(course_id)
                if not course or course.teacher_id != user_id:
                    return {'message': '无权操作此课程'}, 403
            
            # 移除班级
            success = CourseService.remove_class_from_course(course_id, class_id)
            
            if success:
                return {'message': '成功移除班级'}, 200
            else:
                return {'message': '班级关联不存在'}, 404
                
        except Exception as e:
            logger.error(f"移除课程班级异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @course_api_bp.get(
        '/teacher/<int:teacher_id>',
        summary="获取教师的课程列表",
        description="查询指定教师的所有课程，支持筛选和统计",
        responses={
            200: CourseListResponseModel,
            500: MessageResponseModel
        },
        tags=[course_tag]
    )
    # @login_required  # 暂时注释，方便开发测试
    @log_api_call
    def get_teacher_courses(teacher_id: int, query: CourseQueryModel):
        """
        获取教师的课程列表
        
        支持的查询参数：
        - page: 页码
        - per_page: 每页数量
        - semester: 学期筛选
        - status: 状态筛选
        - include_stats: 是否包含班级数和学生数统计
        """
        try:
            result = CourseService.get_courses_by_teacher(
                teacher_id=teacher_id,
                page=query.page,
                per_page=query.per_page,
                include_stats=query.include_stats,
                semester=query.semester,
                status=query.status
            )
            
            return result, 200
            
        except Exception as e:
            logger.error(f"获取教师课程列表异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @course_api_bp.get(
        '/<int:course_id>',
        summary="获取课程详情",
        description="查询指定课程的详细信息，包含教师信息和统计数据",
        responses={
            200: CourseDetailResponseModel,
            404: MessageResponseModel,
            500: MessageResponseModel
        },
        tags=[course_tag]
    )
    # @login_required  # 暂时注释，方便开发测试
    @log_api_call
    def get_course_detail(path: CoursePathModel):
        """
        获取课程详情
        
        返回课程的完整信息，包括：
        - 课程基本信息
        - 教师姓名和邮箱
        - 班级数量
        - 学生数量
        """
        try:
            course_id = path.course_id
            result = CourseService.get_course_detail(course_id)
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"获取课程详情失败: {str(e)}")
            return {'message': str(e)}, 404
        except Exception as e:
            logger.error(f"获取课程详情异常: {str(e)}", exc_info=True)
            return {'message': '服务器内部错误'}, 500
