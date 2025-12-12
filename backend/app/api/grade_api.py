"""
成绩管理API接口
"""
from flask_openapi3 import APIBlueprint, Tag, FileStorage
from flask import session, send_file, request
from app.schemas.grade_schemas import (
    GradeCreateModel, GradeUpdateModel, GradeResponseModel,
    GradeDetailResponseModel, GradeListResponseModel, GradeQueryModel,
    GradePathModel, MessageResponseModel, GradeImportResultModel,
    ExamTypeEnum, GradeTemplateQueryModel, GradeParseFormModel, GradeImportFormModel,
    GradeExportQueryModel, TeacherCourseModel, CourseStudentModel,
    CourseIdQueryModel, TeacherCourseListModel, CourseStudentListModel,
    StudentGradeQueryModel, StudentCourseGradeModel, StudentGradeStatisticsModel
)
from app.services.grade_service import GradeService
from app.utils.excel_utils import ExcelUtils
from app.utils.auth_decorators import login_required, log_user_action
from app.models.user import User, UserRole
from app.models.grade import Grade
from datetime import datetime, date
from typing import Optional
import logging

logger = logging.getLogger(__name__)

grade_api_bp = APIBlueprint('grade_api', __name__, url_prefix='/api/v1/grades')
grade_tag = Tag(name="GradeController", description="成绩管理API")


class GradeAPI:
    """
    成绩管理API类
    
    提供成绩管理相关的完整功能:
    - 单条成绩录入
    - Excel批量导入
    - 成绩列表查询
    - 成绩修改
    - 成绩删除
    - 成绩导出
    """
    
    @staticmethod
    @grade_api_bp.post('',
                      summary="创建成绩记录",
                      tags=[grade_tag],
                      responses={201: GradeDetailResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("创建成绩")
    def create_grade(body: GradeCreateModel):
        """
        创建单条成绩记录
        
        权限: 教师
        """
        try:
            # 获取当前用户
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 验证权限
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以录入成绩'}, 403
            
            # 验证教师是否有权限操作该课程
            if not GradeService.check_teacher_permission(user_id, body.course_id):
                return {'message': '您没有权限操作该课程的成绩'}, 403
            
            # 创建成绩
            grade = GradeService.create_grade(
                course_id=body.course_id,
                student_id=body.student_id,
                exam_type=body.exam_type.value,
                score=body.score,
                exam_date=body.exam_date or date.today(),
                exam_name=body.exam_name,
                full_score=body.full_score,
                weight=body.weight,
                remark=body.remark
            )
            
            # 构建响应
            response = grade.to_dict()
            response['student_name'] = grade.student.real_name if grade.student else None
            response['student_code'] = grade.student.user_code if grade.student else None
            response['course_name'] = grade.course.name if grade.course else None
            response['percentage'] = round((grade.score / grade.full_score) * 100, 2)
            response['is_pass'] = grade.score >= 60
            
            return response, 201
            
        except ValueError as e:
            logger.warning(f"创建成绩失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"创建成绩错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.get('',
                     summary="获取成绩列表",
                     tags=[grade_tag],
                     responses={200: GradeListResponseModel})
    @login_required
    def get_grades(query: GradeQueryModel):
        """
        获取成绩列表
        
        权限: 教师(查看所有), 学生(查看自己)
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 学生只能查看自己的成绩
            student_id = query.student_id
            if user.role == UserRole.STUDENT:
                student_id = user_id
            
            # 教师需要验证课程权限
            if user.role == UserRole.TEACHER and query.course_id:
                if not GradeService.check_teacher_permission(user_id, query.course_id):
                    return {'message': '您没有权限查看该课程的成绩'}, 403
            
            # 查询成绩
            grades, total = GradeService.get_grades(
                course_id=query.course_id,
                student_id=student_id,
                exam_type=query.exam_type.value if query.exam_type else None,
                page=query.page,
                per_page=query.per_page
            )
            
            # 构建响应
            grades_list = []
            for grade in grades:
                grade_dict = grade.to_dict()
                grade_dict['student_name'] = grade.student.real_name if grade.student else None
                grade_dict['student_code'] = grade.student.user_code if grade.student else None
                grade_dict['course_name'] = grade.course.name if grade.course else None
                grade_dict['percentage'] = round((grade.score / grade.full_score) * 100, 2)
                grade_dict['is_pass'] = grade.score >= 60
                grades_list.append(grade_dict)
            
            pages = (total + query.per_page - 1) // query.per_page
            
            return {
                'grades': grades_list,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': pages
            }, 200
            
        except Exception as e:
            logger.error(f"获取成绩列表错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.put('/<int:grade_id>',
                     summary="更新成绩",
                     tags=[grade_tag],
                     responses={200: GradeDetailResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("更新成绩")
    def update_grade(path: GradePathModel, body: GradeUpdateModel):
        """
        更新成绩记录
        
        权限: 教师
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 验证权限
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以修改成绩'}, 403
            
            # 获取成绩记录
            grade = Grade.query.get(path.grade_id)
            if not grade:
                return {'message': '成绩记录不存在'}, 404
            
            # 验证教师是否有权限操作该课程
            if not GradeService.check_teacher_permission(user_id, grade.course_id):
                return {'message': '您没有权限操作该课程的成绩'}, 403
            
            # 更新成绩
            updated_grade = GradeService.update_grade(
                grade_id=path.grade_id,
                score=body.score,
                full_score=body.full_score,
                weight=body.weight,
                remark=body.remark
            )
            
            # 构建响应
            response = updated_grade.to_dict()
            response['student_name'] = updated_grade.student.real_name if updated_grade.student else None
            response['student_code'] = updated_grade.student.user_code if updated_grade.student else None
            response['course_name'] = updated_grade.course.name if updated_grade.course else None
            response['percentage'] = round((updated_grade.score / updated_grade.full_score) * 100, 2)
            response['is_pass'] = updated_grade.score >= 60
            
            return response, 200
            
        except ValueError as e:
            logger.warning(f"更新成绩失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"更新成绩错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.delete('/<int:grade_id>',
                        summary="删除成绩",
                        tags=[grade_tag],
                        responses={200: MessageResponseModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("删除成绩")
    def delete_grade(path: GradePathModel):
        """
        删除成绩记录
        
        权限: 教师
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 验证权限
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以删除成绩'}, 403
            
            # 获取成绩记录
            grade = Grade.query.get(path.grade_id)
            if not grade:
                return {'message': '成绩记录不存在'}, 404
            
            # 验证教师是否有权限操作该课程
            if not GradeService.check_teacher_permission(user_id, grade.course_id):
                return {'message': '您没有权限操作该课程的成绩'}, 403
            
            # 删除成绩
            GradeService.delete_grade(path.grade_id)
            
            return {'message': '删除成功'}, 200
            
        except ValueError as e:
            logger.warning(f"删除成绩失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"删除成绩错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.get('/template',
                     summary="下载Excel导入模板",
                     tags=[grade_tag])
    @login_required
    def download_template(query: GradeTemplateQueryModel):
        """
        下载成绩导入Excel模板
        
        权限: 教师
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以下载模板'}, 403
            
            course_name = query.course_name or '示例课程'
            
            # 生成模板
            excel_file = ExcelUtils.generate_grade_template(course_name)
            
            return send_file(
                excel_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name='成绩导入模板.xlsx'
            )
            
        except Exception as e:
            logger.error(f"下载模板错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.post('/parse-excel',
                      summary="解析Excel文件并验证",
                      tags=[grade_tag])
    @login_required
    def parse_excel_file():
        """
        解析Excel文件并验证学生是否在课程中
        
        权限: 教师
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以导入成绩'}, 403
            
            # 从request中获取表单数据和文件
            course_id = request.form.get('courseId')
            if not course_id:
                return {'message': '缺少课程ID'}, 400
            
            course_id = int(course_id)
            
            # 获取上传的文件
            if 'file' not in request.files:
                return {'message': '未上传文件'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'message': '文件名为空'}, 400
            
            # 验证课程权限
            if not GradeService.check_teacher_permission(user_id, course_id):
                return {'message': '您没有权限操作该课程的成绩'}, 403
            
            logger.info(f"开始解析Excel文件,课程ID: {course_id}")
            
            # 解析Excel
            grades_data = ExcelUtils.parse_grade_excel(file.stream)
            logger.info(f"Excel解析成功,共{len(grades_data)}条数据")
            
            # 获取课程学生列表
            course_students_list = GradeService.get_course_students(course_id)
            logger.info(f"课程学生列表获取成功,共{len(course_students_list)}名学生")
            
            student_code_set = {s['user_code'] for s in course_students_list}
            student_name_map = {s['user_code']: s['real_name'] for s in course_students_list}
            
            logger.info(f"学生代码集合: {student_code_set}")
            
            # 验证每条数据
            validated_data = []
            for idx, item in enumerate(grades_data):
                student_code = item.get('student_code')
                student_name = item.get('student_name')
                
                logger.info(f"验证第{idx+1}条: 学号={student_code}, 姓名={student_name}")
                
                # 检查学生是否在课程中
                if student_code not in student_code_set:
                    item['valid'] = False
                    item['error'] = '学号不存在或不在此课程班级中'
                    logger.info(f"  -> 学号不存在")
                # 检查姓名是否匹配
                elif student_name and student_name_map.get(student_code) != student_name:
                    item['valid'] = False
                    item['error'] = f'姓名不匹配,应为: {student_name_map.get(student_code)}'
                    logger.info(f"  -> 姓名不匹配")
                else:
                    item['valid'] = True
                    item['error'] = None
                    logger.info(f"  -> 验证通过")
                
                validated_data.append(item)
            
            logger.info(f"验证完成,返回{len(validated_data)}条数据")
            
            return {
                'data': validated_data,
                'total': len(validated_data)
            }, 200
            
        except ValueError as e:
            logger.warning(f"解析Excel失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"解析Excel错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @grade_api_bp.post('/import',
                      summary="Excel批量导入成绩",
                      tags=[grade_tag],
                      responses={200: GradeImportResultModel, 400: MessageResponseModel})
    @login_required
    @log_user_action("批量导入成绩")
    def import_grades():
        """
        Excel批量导入成绩
        
        权限: 教师
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以导入成绩'}, 403
            
            # 从request中获取表单数据
            course_id = request.form.get('courseId')
            exam_type = request.form.get('examType')
            exam_name = request.form.get('examName')
            exam_date_str = request.form.get('examDate')
            full_score = request.form.get('fullScore', '100')
            weight = request.form.get('weight', '1.0')
            
            # 验证必填字段
            if not course_id or not exam_type or not exam_date_str:
                return {'message': '缺少必填字段'}, 400
            
            course_id = int(course_id)
            full_score = float(full_score)
            weight = float(weight)
            
            # 获取上传的文件
            if 'file' not in request.files:
                return {'message': '未上传文件'}, 400
            
            file = request.files['file']
            if file.filename == '':
                return {'message': '文件名为空'}, 400
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, course_id):
                return {'message': '您没有权限操作该课程的成绩'}, 403
            
            # 解析日期
            exam_date = datetime.strptime(exam_date_str, '%Y-%m-%d').date()
            
            logger.info(f"开始导入成绩: 课程ID={course_id}, 考试类型={exam_type}, 日期={exam_date}")
            
            # 解析Excel
            grades_data = ExcelUtils.parse_grade_excel(file.stream)
            
            # 导入成绩
            result = GradeService.import_grades_from_excel(
                course_id=course_id,
                exam_type=exam_type,
                exam_date=exam_date,
                grades_data=grades_data,
                exam_name=exam_name,
                full_score=full_score,
                weight=weight
            )
            
            logger.info(f"导入完成: 成功={result['success_count']}, 失败={result['fail_count']}, 跳过={result['skip_count']}")
            
            return result, 200
            
        except ValueError as e:
            logger.warning(f"导入成绩失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"导入成绩错误: {str(e)}", exc_info=True)
            return {'message': f'服务器内部错误: {str(e)}'}, 500
    
    @staticmethod
    @grade_api_bp.get('/export',
                     summary="导出成绩Excel",
                     tags=[grade_tag])
    @login_required
    def export_grades(query: GradeExportQueryModel):
        """
        导出成绩到Excel
        
        权限: 教师
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以导出成绩'}, 403
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, query.course_id):
                return {'message': '您没有权限导出该课程的成绩'}, 403
            
            # 查询成绩
            grades, _ = GradeService.get_grades(
                course_id=query.course_id,
                exam_type=query.exam_type.value if query.exam_type else None,
                page=1,
                per_page=10000  # 导出全部
            )
            
            # 构建导出数据
            export_data = []
            for grade in grades:
                export_data.append({
                    'student_code': grade.student.user_code if grade.student else '',
                    'student_name': grade.student.real_name if grade.student else '',
                    'exam_type': grade.exam_type.value,
                    'exam_name': grade.exam_name or '',
                    'score': grade.score,
                    'full_score': grade.full_score,
                    'exam_date': grade.exam_date.strftime('%Y-%m-%d') if grade.exam_date else '',
                    'remark': grade.remark or ''
                })
            
            course_name = grades[0].course.name if grades and grades[0].course else '课程'
            
            # 生成Excel
            excel_file = ExcelUtils.export_grades_to_excel(export_data, course_name)
            
            filename = f'成绩单_{course_name}_{datetime.now().strftime("%Y%m%d")}.xlsx'
            
            return send_file(
                excel_file,
                mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
                as_attachment=True,
                download_name=filename
            )
            
        except Exception as e:
            logger.error(f"导出成绩错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.get('/teacher-courses',
                     summary="获取教师课程列表",
                     tags=[grade_tag])
    @login_required
    def get_teacher_courses():
        """
        获取当前教师的授课课程列表
        
        权限: 教师
        返回: 课程列表数组
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以访问此接口'}, 403
            
            courses = GradeService.get_teacher_courses(user_id)
            
            # 直接返回列表,不包装
            return courses, 200
            
        except Exception as e:
            logger.error(f"获取教师课程列表错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.get('/course-students',
                     summary="获取课程学生列表",
                     tags=[grade_tag])
    @login_required
    def get_course_students(query: CourseIdQueryModel):
        """
        获取指定课程的学生列表
        
        权限: 教师
        返回: 学生列表数组
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            if user.role != UserRole.TEACHER:
                return {'message': '只有教师可以访问此接口'}, 403
            
            # 验证教师权限
            if not GradeService.check_teacher_permission(user_id, query.course_id):
                return {'message': '您没有权限访问该课程的学生列表'}, 403
            
            students = GradeService.get_course_students(query.course_id)
            
            # 直接返回列表,不包装
            return students, 200
            
        except ValueError as e:
            logger.warning(f"获取课程学生列表失败: {str(e)}")
            return {'message': str(e)}, 400
        except Exception as e:
            logger.error(f"获取课程学生列表错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500

    
    # ==================== 学生端API ====================
    
    @staticmethod
    @grade_api_bp.get('/student/my-grades',
                     summary="获取学生个人成绩列表",
                     tags=[grade_tag])
    @login_required
    def get_student_my_grades(query: StudentGradeQueryModel):
        """
        获取当前学生的个人成绩列表
        
        权限: 学生
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有学生可以访问
            if user.role != UserRole.STUDENT:
                return {'message': '只有学生可以访问此接口'}, 403
            
            # 查询成绩
            grades, total = GradeService.get_grades(
                student_id=user_id,
                course_id=query.course_id,
                exam_type=query.exam_type.value if query.exam_type else None,
                page=query.page,
                per_page=query.per_page
            )
            
            # 构建响应
            grades_list = []
            for grade in grades:
                grade_dict = grade.to_dict()
                grade_dict['course_name'] = grade.course.name if grade.course else None
                grade_dict['course_code'] = grade.course.code if grade.course else None
                grade_dict['percentage'] = round((grade.score / grade.full_score) * 100, 2)
                grade_dict['is_pass'] = grade.score >= 60
                grades_list.append(grade_dict)
            
            pages = (total + query.per_page - 1) // query.per_page
            
            return {
                'grades': grades_list,
                'total': total,
                'page': query.page,
                'per_page': query.per_page,
                'pages': pages
            }, 200
            
        except Exception as e:
            logger.error(f"获取学生成绩列表错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.get('/student/courses',
                     summary="获取学生课程成绩统计",
                     tags=[grade_tag])
    @login_required
    def get_student_courses():
        """
        获取学生按课程分组的成绩统计
        
        权限: 学生
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有学生可以访问
            if user.role != UserRole.STUDENT:
                return {'message': '只有学生可以访问此接口'}, 403
            
            # 获取课程成绩统计
            courses = GradeService.get_student_grades_by_course(user_id)
            
            return courses, 200
            
        except Exception as e:
            logger.error(f"获取学生课程统计错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
    
    @staticmethod
    @grade_api_bp.get('/student/statistics',
                     summary="获取学生总体成绩统计",
                     tags=[grade_tag])
    @login_required
    def get_student_statistics():
        """
        获取学生的总体成绩统计
        
        权限: 学生
        """
        try:
            user_id = session.get('user_id')
            user = User.query.get(user_id)
            
            # 只有学生可以访问
            if user.role != UserRole.STUDENT:
                return {'message': '只有学生可以访问此接口'}, 403
            
            # 获取统计数据
            statistics = GradeService.get_student_grade_statistics(user_id)
            
            return statistics, 200
            
        except Exception as e:
            logger.error(f"获取学生统计数据错误: {str(e)}")
            return {'message': '服务器内部错误'}, 500
