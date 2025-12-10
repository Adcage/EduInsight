"""
成绩管理业务逻辑服务
"""
from typing import Optional, List, Dict, Any, Tuple
from datetime import date, datetime
from app.models.grade import Grade, ExamType
from app.models.user import User
from app.models.course import Course
from app.extensions import db
from sqlalchemy import and_
import logging

logger = logging.getLogger(__name__)


class GradeService:
    """成绩管理服务类"""
    
    @staticmethod
    def check_duplicate(student_id: int, course_id: int, exam_type: str, exam_date: date) -> bool:
        """
        检查成绩是否重复
        
        重复判断规则: 学号 + 科目 + 考试类型 + 考试日期
        
        Args:
            student_id: 学生ID
            course_id: 课程ID
            exam_type: 考试类型
            exam_date: 考试日期
            
        Returns:
            True表示重复, False表示不重复
        """
        existing = Grade.query.filter(
            and_(
                Grade.student_id == student_id,
                Grade.course_id == course_id,
                Grade.exam_type == ExamType(exam_type),
                Grade.exam_date == exam_date
            )
        ).first()
        
        return existing is not None
    
    @staticmethod
    def check_teacher_permission(teacher_id: int, course_id: int) -> bool:
        """
        检查教师是否有权限操作该课程的成绩
        
        Args:
            teacher_id: 教师ID
            course_id: 课程ID
            
        Returns:
            True表示有权限, False表示无权限
        """
        course = Course.query.get(course_id)
        if not course:
            return False
        
        return course.teacher_id == teacher_id
    
    @staticmethod
    def get_course_students(course_id: int) -> List[User]:
        """
        获取课程对应的学生列表
        
        Args:
            course_id: 课程ID
            
        Returns:
            学生列表
        """
        course = Course.query.get(course_id)
        if not course:
            return []
        
        # 通过课程关联的班级获取学生
        students = []
        for class_obj in course.classes:
            students.extend(class_obj.students.all())
        
        return students
    
    @staticmethod
    def create_grade(course_id: int, student_id: int, exam_type: str, 
                    score: float, exam_date: date, exam_name: Optional[str] = None,
                    full_score: float = 100.0, weight: float = 1.0, 
                    remark: Optional[str] = None) -> Grade:
        """
        创建单条成绩记录
        
        Args:
            course_id: 课程ID
            student_id: 学生ID
            exam_type: 考试类型
            score: 分数
            exam_date: 考试日期
            exam_name: 考试名称
            full_score: 满分
            weight: 权重
            remark: 备注
            
        Returns:
            创建的成绩对象
            
        Raises:
            ValueError: 参数验证失败或重复
        """
        # 验证课程是否存在
        course = Course.query.get(course_id)
        if not course:
            raise ValueError("课程不存在")
        
        # 验证学生是否存在
        student = User.query.get(student_id)
        if not student:
            raise ValueError("学生不存在")
        
        # 验证学生是否在该课程的班级中
        course_students = GradeService.get_course_students(course_id)
        student_ids = [s['id'] for s in course_students]
        if student_id not in student_ids:
            raise ValueError("该学生不在此课程的班级中")
        
        # 检查是否重复
        if GradeService.check_duplicate(student_id, course_id, exam_type, exam_date):
            raise ValueError("该学生在此日期已有相同类型的成绩记录")
        
        # 验证分数范围
        if score < 0 or score > full_score:
            raise ValueError(f"分数必须在0到{full_score}之间")
        
        # 创建成绩记录
        grade = Grade(
            course_id=course_id,
            student_id=student_id,
            exam_type=ExamType(exam_type),
            exam_name=exam_name,
            exam_date=exam_date,
            score=score,
            full_score=full_score,
            weight=weight,
            remark=remark
        )
        
        db.session.add(grade)
        db.session.commit()
        
        logger.info(f"成绩创建成功: 学生ID={student_id}, 课程ID={course_id}, 分数={score}")
        
        return grade
    
    @staticmethod
    def get_grades(course_id: Optional[int] = None, student_id: Optional[int] = None,
                  exam_type: Optional[str] = None, page: int = 1, 
                  per_page: int = 20) -> Tuple[List[Grade], int]:
        """
        查询成绩列表
        
        Args:
            course_id: 课程ID筛选
            student_id: 学生ID筛选
            exam_type: 考试类型筛选
            page: 页码
            per_page: 每页数量
            
        Returns:
            (成绩列表, 总数)
        """
        query = Grade.query
        
        if course_id:
            query = query.filter(Grade.course_id == course_id)
        
        if student_id:
            query = query.filter(Grade.student_id == student_id)
        
        if exam_type:
            query = query.filter(Grade.exam_type == ExamType(exam_type))
        
        # 按创建时间倒序
        query = query.order_by(Grade.created_at.desc())
        
        # 分页
        total = query.count()
        grades = query.offset((page - 1) * per_page).limit(per_page).all()
        
        return grades, total
    
    @staticmethod
    def update_grade(grade_id: int, score: Optional[float] = None,
                    full_score: Optional[float] = None, weight: Optional[float] = None,
                    remark: Optional[str] = None) -> Grade:
        """
        更新成绩
        
        Args:
            grade_id: 成绩ID
            score: 新分数
            full_score: 新满分
            weight: 新权重
            remark: 新备注
            
        Returns:
            更新后的成绩对象
            
        Raises:
            ValueError: 成绩不存在或参数无效
        """
        grade = Grade.query.get(grade_id)
        if not grade:
            raise ValueError("成绩记录不存在")
        
        if score is not None:
            if score < 0:
                raise ValueError("分数不能为负数")
            if full_score is not None and score > full_score:
                raise ValueError("分数不能超过满分")
            elif score > grade.full_score:
                raise ValueError("分数不能超过满分")
            grade.score = score
        
        if full_score is not None:
            if full_score <= 0:
                raise ValueError("满分必须大于0")
            grade.full_score = full_score
        
        if weight is not None:
            if weight < 0:
                raise ValueError("权重不能为负数")
            grade.weight = weight
        
        if remark is not None:
            grade.remark = remark
        
        db.session.commit()
        
        logger.info(f"成绩更新成功: ID={grade_id}")
        
        return grade
    
    @staticmethod
    def delete_grade(grade_id: int) -> None:
        """
        删除成绩
        
        Args:
            grade_id: 成绩ID
            
        Raises:
            ValueError: 成绩不存在
        """
        grade = Grade.query.get(grade_id)
        if not grade:
            raise ValueError("成绩记录不存在")
        
        db.session.delete(grade)
        db.session.commit()
        
        logger.info(f"成绩删除成功: ID={grade_id}")
    
    @staticmethod
    def import_grades_from_excel(course_id: int, exam_type: str, exam_date: date,
                                grades_data: List[Dict[str, Any]], 
                                exam_name: Optional[str] = None,
                                full_score: float = 100.0, 
                                weight: float = 1.0) -> Dict[str, Any]:
        """
        从Excel数据批量导入成绩
        
        Args:
            course_id: 课程ID
            exam_type: 考试类型
            exam_date: 考试日期
            grades_data: 成绩数据列表 [{"student_code": "2024001", "score": 85.5, ...}, ...]
            exam_name: 考试名称
            full_score: 满分
            weight: 权重
            
        Returns:
            导入结果统计
        """
        result = {
            "total_rows": len(grades_data),
            "success_count": 0,
            "skip_count": 0,
            "fail_count": 0,
            "errors": [],
            "warnings": []
        }
        
        # 验证课程是否存在
        course = Course.query.get(course_id)
        if not course:
            result["errors"].append({
                "row": 0,
                "error": "课程不存在"
            })
            result["fail_count"] = len(grades_data)
            return result
        
        # 获取课程学生列表(字典格式)
        course_students_list = GradeService.get_course_students(course_id)
        # 需要通过user_code查找实际的User对象
        student_code_map = {}
        for student_dict in course_students_list:
            student = User.query.get(student_dict['id'])
            if student:
                student_code_map[student.user_code] = student
        
        for idx, grade_data in enumerate(grades_data, start=1):
            try:
                student_code = grade_data.get("student_code")
                score = grade_data.get("score")
                
                # 验证必填字段
                if not student_code:
                    result["errors"].append({
                        "row": idx,
                        "error": "学号不能为空"
                    })
                    result["fail_count"] += 1
                    continue
                
                if score is None:
                    result["errors"].append({
                        "row": idx,
                        "student_code": student_code,
                        "error": "分数不能为空"
                    })
                    result["fail_count"] += 1
                    continue
                
                # 查找学生
                student = student_code_map.get(student_code)
                if not student:
                    result["errors"].append({
                        "row": idx,
                        "student_code": student_code,
                        "error": "学号不存在或不在此课程班级中"
                    })
                    result["fail_count"] += 1
                    continue
                
                # 验证分数范围
                try:
                    score = float(score)
                    if score < 0 or score > full_score:
                        result["errors"].append({
                            "row": idx,
                            "student_code": student_code,
                            "error": f"分数必须在0到{full_score}之间"
                        })
                        result["fail_count"] += 1
                        continue
                except (ValueError, TypeError):
                    result["errors"].append({
                        "row": idx,
                        "student_code": student_code,
                        "error": "分数格式无效"
                    })
                    result["fail_count"] += 1
                    continue
                
                # 检查是否重复
                if GradeService.check_duplicate(student.id, course_id, exam_type, exam_date):
                    result["warnings"].append({
                        "row": idx,
                        "student_code": student_code,
                        "warning": "该学生在此日期已有相同类型的成绩记录,已跳过"
                    })
                    result["skip_count"] += 1
                    continue
                
                # 创建成绩记录
                grade = Grade(
                    course_id=course_id,
                    student_id=student.id,
                    exam_type=ExamType(exam_type),
                    exam_name=exam_name,
                    exam_date=exam_date,
                    score=score,
                    full_score=full_score,
                    weight=weight,
                    remark=grade_data.get("remark")
                )
                
                db.session.add(grade)
                result["success_count"] += 1
                
            except Exception as e:
                logger.error(f"导入第{idx}行时出错: {str(e)}")
                result["errors"].append({
                    "row": idx,
                    "student_code": grade_data.get("student_code", ""),
                    "error": str(e)
                })
                result["fail_count"] += 1
        
        # 提交所有成功的记录
        if result["success_count"] > 0:
            try:
                db.session.commit()
                logger.info(f"批量导入成功: 成功{result['success_count']}条, 跳过{result['skip_count']}条, 失败{result['fail_count']}条")
            except Exception as e:
                db.session.rollback()
                logger.error(f"批量导入提交失败: {str(e)}")
                result["errors"].append({
                    "row": 0,
                    "error": f"数据库提交失败: {str(e)}"
                })
                result["fail_count"] = result["total_rows"]
                result["success_count"] = 0
                result["skip_count"] = 0
        
        return result
    
    @staticmethod
    def get_teacher_courses(teacher_id: int) -> List[Dict[str, Any]]:
        """
        获取教师的授课课程列表
        
        Args:
            teacher_id: 教师ID
            
        Returns:
            课程列表
        """
        courses = Course.query.filter_by(teacher_id=teacher_id).all()
        
        result = []
        for course in courses:
            # 统计该课程的学生数量
            student_count = 0
            # classes是dynamic关系,需要调用.all()
            course_classes = course.classes.all() if course.classes else []
            for cls in course_classes:
                # students也可能是dynamic关系
                if hasattr(cls.students, 'count'):
                    student_count += cls.students.count()
                else:
                    student_count += len(cls.students)
            
            result.append({
                "id": course.id,
                "name": course.name,
                "code": course.code,
                "semester": course.semester,
                "student_count": student_count
            })
        
        return result
    
    @staticmethod
    def get_course_students(course_id: int) -> List[Dict[str, Any]]:
        """
        获取课程的学生列表
        
        Args:
            course_id: 课程ID
            
        Returns:
            学生列表
        """
        course = Course.query.get(course_id)
        if not course:
            raise ValueError("课程不存在")
        
        result = []
        # 通过课程关联的班级获取学生
        # classes是dynamic关系,需要调用.all()
        course_classes = course.classes.all() if course.classes else []
        for cls in course_classes:
            # students也可能是dynamic关系
            students = cls.students.all() if hasattr(cls.students, 'all') else cls.students
            for student in students:
                # 统计该学生在该课程的成绩数量
                grade_count = Grade.query.filter_by(
                    student_id=student.id,
                    course_id=course_id
                ).count()
                
                result.append({
                    "id": student.id,
                    "user_code": student.user_code,
                    "real_name": student.real_name,
                    "class_id": cls.id if cls else None,
                    "class_name": cls.name if cls else None,
                    "grade_count": grade_count
                })
        
        return result

    @staticmethod
    def get_student_grades_by_course(student_id: int) -> List[Dict[str, Any]]:
        """
        获取学生按课程分组的成绩统计
        
        Args:
            student_id: 学生ID
            
        Returns:
            课程成绩统计列表
        """
        # 查询学生的所有成绩
        grades = Grade.query.filter_by(student_id=student_id).all()
        
        # 按课程分组
        course_grades: Dict[int, List[Grade]] = {}
        for grade in grades:
            if grade.course_id not in course_grades:
                course_grades[grade.course_id] = []
            course_grades[grade.course_id].append(grade)
        
        # 统计每个课程的成绩
        result = []
        for course_id, grades_list in course_grades.items():
            course = Course.query.get(course_id)
            if not course:
                continue
            
            scores = [float(g.score) for g in grades_list]
            pass_count = sum(1 for s in scores if s >= 60)
            
            result.append({
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "semester": course.semester,
                "grade_count": len(grades_list),
                "average_score": round(sum(scores) / len(scores), 2) if scores else None,
                "highest_score": max(scores) if scores else None,
                "lowest_score": min(scores) if scores else None,
                "pass_rate": round((pass_count / len(scores)) * 100, 2) if scores else None
            })
        
        return result
    
    @staticmethod
    def get_student_grade_statistics(student_id: int) -> Dict[str, Any]:
        """
        获取学生的总体成绩统计
        
        Args:
            student_id: 学生ID
            
        Returns:
            统计数据
        """
        # 查询学生的所有成绩
        grades = Grade.query.filter_by(student_id=student_id).all()
        
        if not grades:
            return {
                "total_courses": 0,
                "total_grades": 0,
                "average_score": None,
                "pass_count": 0,
                "fail_count": 0,
                "pass_rate": None
            }
        
        # 按课程分组计算平均分
        course_grades: Dict[int, List[float]] = {}
        for grade in grades:
            if grade.course_id not in course_grades:
                course_grades[grade.course_id] = []
            course_grades[grade.course_id].append(float(grade.score))
        
        # 计算每个课程的平均分
        course_avg_scores = []
        pass_count = 0
        fail_count = 0
        
        for course_id, scores in course_grades.items():
            avg_score = sum(scores) / len(scores)
            course_avg_scores.append(avg_score)
            
            if avg_score >= 60:
                pass_count += 1
            else:
                fail_count += 1
        
        # 计算总平均分
        total_avg = sum(course_avg_scores) / len(course_avg_scores) if course_avg_scores else None
        pass_rate = (pass_count / len(course_grades)) * 100 if course_grades else None
        
        return {
            "total_courses": len(course_grades),
            "total_grades": len(grades),
            "average_score": round(total_avg, 2) if total_avg else None,
            "pass_count": pass_count,
            "fail_count": fail_count,
            "pass_rate": round(pass_rate, 2) if pass_rate else None
        }
