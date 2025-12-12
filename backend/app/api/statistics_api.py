"""
统计分析API接口
"""
from flask_openapi3 import APIBlueprint, Tag
from flask import session
from app.schemas.statistics_schemas import (
    StatisticsQueryModel, StatisticsResponseModel
)
from app.services.statistics_service import StatisticsService
from app.services.grade_service import GradeService
from app.utils.auth_decorators import login_required
from app.models.user import User, UserRole
import logging

logger = logging.getLogger(__name__)

statistics_api_bp = APIBlueprint('statistics_api', __name__, url_prefix='/api/v1/statistics')
statistics_tag = Tag(name="StatisticsController", description="统计分析API")


class StatisticsAPI:
    """统计分析API类"""
    
    @staticmethod
    @statistics_api_bp.get('/course',
                          summary="获取课程统计分析",
                          tags=[statistics_tag],
                          responses={200: StatisticsResponseModel})
    @login_required
    def get_course_statistics(query: StatisticsQueryModel):
        """
        获取课程统计分析数据
        
        权限: 教师(只能查看自己教授的课程)
        
        参数:
        - course_id: 课程ID(必填)
        - class_id: 班级ID(可选,用于更细致的统计)
        - exam_type: 考试类型(可选,筛选特定类型的考试)
        
        返回:
        - basic_statistics: 基础统计(平均分、最高分、最低分、标准差、中位数、及格率、优秀率)
        - score_distribution: 分数段分布(不及格、及格、中等、良好、优秀的人数和比例)
        - trend_data: 成绩趋势数据(按考试类型和日期的平均分变化)
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有教师可以查看统计
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以查看统计分析'}, 403
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, query.course_id):
                return {'message': '您没有权限查看该课程的统计分析'}, 403
            
            logger.info(f"教师{user_id}查看课程{query.course_id}的统计分析")
            
            # 验证exam_type参数
            exam_type_value = None
            if query.exam_type:
                # 允许的值: daily, midterm, final, homework, comprehensive
                allowed_types = ['daily', 'midterm', 'final', 'homework', 'comprehensive']
                if query.exam_type not in allowed_types:
                    return {'message': f'无效的考试类型: {query.exam_type}'}, 400
                exam_type_value = query.exam_type
            
            # 获取统计数据
            statistics_data = StatisticsService.get_course_statistics(
                course_id=query.course_id,
                class_id=query.class_id,
                exam_type=exam_type_value
            )
            
            return statistics_data, 200
            
        except ValueError as e:
            logger.warning(f"获取统计分析失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"获取统计分析错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500


# TODO: PDF导出功能 - 待后续实现
# @statistics_api_bp.get('/export-pdf')
# def export_statistics_pdf(query: StatisticsQueryModel):
#     """
#     导出统计分析PDF报告
#     
#     功能说明:
#     - 生成包含所有统计数据和图表的PDF报告
#     - 使用后端PDF生成库(如ReportLab或WeasyPrint)
#     - 包含基础统计、分数分布图表、趋势分析图表
#     """
#     pass
