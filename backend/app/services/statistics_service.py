"""
统计分析服务层
"""
from typing import Optional, List, Dict, Any
from sqlalchemy import func
from app.models.grade import Grade, ExamType
from app.models.course import Course
from app.models.class_model import Class
from app.models.user import User
from app.extensions import db
import logging
import statistics

logger = logging.getLogger(__name__)


class StatisticsService:
    """统计分析服务类"""
    
    @staticmethod
    def get_course_statistics(course_id: int, class_id: Optional[int] = None, 
                             exam_type: Optional[str] = None) -> Dict[str, Any]:
        """
        获取课程统计分析数据
        
        Args:
            course_id: 课程ID
            class_id: 班级ID(可选)
            exam_type: 考试类型(可选,如果为'comprehensive'则进行综合统计)
            
        Returns:
            统计分析数据字典
        """
        # 验证课程存在
        course = Course.query.get(course_id)
        if not course:
            raise ValueError("课程不存在")
        
        # 构建查询
        query = Grade.query.filter_by(course_id=course_id)
        
        # 如果指定班级,筛选该班级的学生
        class_obj = None
        if class_id:
            class_obj = Class.query.get(class_id)
            if not class_obj:
                raise ValueError("班级不存在")
            
            # 获取班级学生ID列表
            student_ids = [s.id for s in class_obj.students.all()]
            query = query.filter(Grade.student_id.in_(student_ids))
        
        # 如果指定考试类型且不是综合统计,筛选该类型
        is_comprehensive = exam_type == 'comprehensive'
        if exam_type and not is_comprehensive:
            query = query.filter_by(exam_type=ExamType(exam_type))
        
        # 获取所有成绩
        grades = query.all()
        
        if not grades:
            # 没有成绩数据,返回空统计
            return {
                "basic_statistics": {
                    "total_count": 0,
                    "average_score": 0.0,
                    "max_score": 0.0,
                    "min_score": 0.0,
                    "median_score": 0.0,
                    "std_deviation": 0.0,
                    "pass_rate": 0.0,
                    "excellent_rate": 0.0
                },
                "score_distribution": {
                    "fail_count": 0,
                    "pass_count": 0,
                    "medium_count": 0,
                    "good_count": 0,
                    "excellent_count": 0,
                    "fail_rate": 0.0,
                    "pass_rate": 0.0,
                    "medium_rate": 0.0,
                    "good_rate": 0.0,
                    "excellent_rate": 0.0
                },
                "trend_data": [],
                "course_name": course.name,
                "class_name": class_obj.name if class_id and class_obj else None,
                "exam_type_filter": exam_type,
                "is_comprehensive": is_comprehensive
            }
        
        # 如果是综合统计,按学生去重并计算平均分
        if is_comprehensive:
            basic_stats = StatisticsService._calculate_comprehensive_statistics(grades)
            score_dist = StatisticsService._calculate_comprehensive_distribution(grades)
        else:
            # 普通统计
            basic_stats = StatisticsService._calculate_basic_statistics(grades)
            score_dist = StatisticsService._calculate_score_distribution(grades)
        
        # 计算趋势数据
        trend_data = StatisticsService._calculate_trend_data(course_id, class_id)
        
        return {
            "basic_statistics": basic_stats,
            "score_distribution": score_dist,
            "trend_data": trend_data,
            "course_name": course.name,
            "class_name": class_obj.name if class_id and class_obj else None,
            "exam_type_filter": exam_type,
            "is_comprehensive": is_comprehensive
        }
    
    @staticmethod
    def _calculate_comprehensive_statistics(grades: List[Grade]) -> Dict[str, Any]:
        """
        计算综合统计数据(按学生去重)
        每个学生的所有成绩取平均,再计算总体统计
        """
        # 按学生分组
        student_grades = {}
        for grade in grades:
            student_id = grade.student_id
            if student_id not in student_grades:
                student_grades[student_id] = []
            student_grades[student_id].append(float(grade.score))
        
        # 计算每个学生的平均分
        student_avg_scores = []
        for student_id, scores in student_grades.items():
            avg_score = sum(scores) / len(scores)
            student_avg_scores.append(avg_score)
        
        total_count = len(student_avg_scores)
        
        if total_count == 0:
            return {
                "total_count": 0,
                "average_score": 0.0,
                "max_score": 0.0,
                "min_score": 0.0,
                "median_score": 0.0,
                "std_deviation": 0.0,
                "pass_rate": 0.0,
                "excellent_rate": 0.0
            }
        
        # 平均分
        average_score = round(sum(student_avg_scores) / total_count, 2)
        
        # 最高分/最低分
        max_score = round(max(student_avg_scores), 2)
        min_score = round(min(student_avg_scores), 2)
        
        # 中位数
        median_score = round(statistics.median(student_avg_scores), 2)
        
        # 标准差
        std_deviation = round(statistics.stdev(student_avg_scores) if total_count > 1 else 0.0, 2)
        
        # 及格率(>=60分)
        pass_count = sum(1 for s in student_avg_scores if s >= 60)
        pass_rate = round((pass_count / total_count) * 100, 2)
        
        # 优秀率(>=90分)
        excellent_count = sum(1 for s in student_avg_scores if s >= 90)
        excellent_rate = round((excellent_count / total_count) * 100, 2)
        
        return {
            "total_count": total_count,
            "average_score": average_score,
            "max_score": max_score,
            "min_score": min_score,
            "median_score": median_score,
            "std_deviation": std_deviation,
            "pass_rate": pass_rate,
            "excellent_rate": excellent_rate
        }
    
    @staticmethod
    def _calculate_comprehensive_distribution(grades: List[Grade]) -> Dict[str, Any]:
        """
        计算综合分数段分布(按学生去重)
        每个学生的所有成绩取平均,再统计分数段
        """
        # 按学生分组
        student_grades = {}
        for grade in grades:
            student_id = grade.student_id
            if student_id not in student_grades:
                student_grades[student_id] = []
            student_grades[student_id].append(float(grade.score))
        
        # 计算每个学生的平均分
        student_avg_scores = []
        for student_id, scores in student_grades.items():
            avg_score = sum(scores) / len(scores)
            student_avg_scores.append(avg_score)
        
        total_count = len(student_avg_scores)
        
        if total_count == 0:
            return {
                "fail_count": 0,
                "pass_count": 0,
                "medium_count": 0,
                "good_count": 0,
                "excellent_count": 0,
                "fail_rate": 0.0,
                "pass_rate": 0.0,
                "medium_rate": 0.0,
                "good_rate": 0.0,
                "excellent_rate": 0.0
            }
        
        # 统计各分数段人数
        fail_count = sum(1 for s in student_avg_scores if s < 60)
        pass_count = sum(1 for s in student_avg_scores if 60 <= s < 70)
        medium_count = sum(1 for s in student_avg_scores if 70 <= s < 80)
        good_count = sum(1 for s in student_avg_scores if 80 <= s < 90)
        excellent_count = sum(1 for s in student_avg_scores if s >= 90)
        
        # 计算各分数段比例
        fail_rate = round((fail_count / total_count) * 100, 2)
        pass_rate = round((pass_count / total_count) * 100, 2)
        medium_rate = round((medium_count / total_count) * 100, 2)
        good_rate = round((good_count / total_count) * 100, 2)
        excellent_rate = round((excellent_count / total_count) * 100, 2)
        
        return {
            "fail_count": fail_count,
            "pass_count": pass_count,
            "medium_count": medium_count,
            "good_count": good_count,
            "excellent_count": excellent_count,
            "fail_rate": fail_rate,
            "pass_rate": pass_rate,
            "medium_rate": medium_rate,
            "good_rate": good_rate,
            "excellent_rate": excellent_rate
        }
    
    @staticmethod
    def _calculate_basic_statistics(grades: List[Grade]) -> Dict[str, Any]:
        """计算基础统计数据"""
        scores = [float(g.score) for g in grades]
        total_count = len(scores)
        
        # 平均分
        average_score = round(sum(scores) / total_count, 2)
        
        # 最高分/最低分
        max_score = round(max(scores), 2)
        min_score = round(min(scores), 2)
        
        # 中位数
        median_score = round(statistics.median(scores), 2)
        
        # 标准差
        std_deviation = round(statistics.stdev(scores) if total_count > 1 else 0.0, 2)
        
        # 及格率(>=60分)
        pass_count = sum(1 for s in scores if s >= 60)
        pass_rate = round((pass_count / total_count) * 100, 2)
        
        # 优秀率(>=90分)
        excellent_count = sum(1 for s in scores if s >= 90)
        excellent_rate = round((excellent_count / total_count) * 100, 2)
        
        return {
            "total_count": total_count,
            "average_score": average_score,
            "max_score": max_score,
            "min_score": min_score,
            "median_score": median_score,
            "std_deviation": std_deviation,
            "pass_rate": pass_rate,
            "excellent_rate": excellent_rate
        }
    
    @staticmethod
    def _calculate_score_distribution(grades: List[Grade]) -> Dict[str, Any]:
        """计算分数段分布"""
        scores = [float(g.score) for g in grades]
        total_count = len(scores)
        
        # 统计各分数段人数
        fail_count = sum(1 for s in scores if s < 60)  # 不及格
        pass_count = sum(1 for s in scores if 60 <= s < 70)  # 及格
        medium_count = sum(1 for s in scores if 70 <= s < 80)  # 中等
        good_count = sum(1 for s in scores if 80 <= s < 90)  # 良好
        excellent_count = sum(1 for s in scores if s >= 90)  # 优秀
        
        # 计算各分数段比例
        fail_rate = round((fail_count / total_count) * 100, 2)
        pass_rate = round((pass_count / total_count) * 100, 2)
        medium_rate = round((medium_count / total_count) * 100, 2)
        good_rate = round((good_count / total_count) * 100, 2)
        excellent_rate = round((excellent_count / total_count) * 100, 2)
        
        return {
            "fail_count": fail_count,
            "pass_count": pass_count,
            "medium_count": medium_count,
            "good_count": good_count,
            "excellent_count": excellent_count,
            "fail_rate": fail_rate,
            "pass_rate": pass_rate,
            "medium_rate": medium_rate,
            "good_rate": good_rate,
            "excellent_rate": excellent_rate
        }
    
    @staticmethod
    def _calculate_trend_data(course_id: int, class_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """计算成绩趋势数据"""
        # 按考试类型和日期分组统计
        query = db.session.query(
            Grade.exam_type,
            Grade.exam_name,
            Grade.exam_date,
            func.avg(Grade.score).label('avg_score'),
            func.max(Grade.score).label('max_score'),
            func.min(Grade.score).label('min_score')
        ).filter_by(course_id=course_id)
        
        # 如果指定班级,筛选该班级的学生
        if class_id:
            class_obj = Class.query.get(class_id)
            if class_obj:
                student_ids = [s.id for s in class_obj.students.all()]
                query = query.filter(Grade.student_id.in_(student_ids))
        
        # 按考试类型和日期分组
        query = query.group_by(Grade.exam_type, Grade.exam_name, Grade.exam_date)
        query = query.order_by(Grade.exam_date)
        
        results = query.all()
        
        trend_data = []
        for result in results:
            trend_data.append({
                "exam_type": result.exam_type.value,
                "exam_name": result.exam_name,
                "exam_date": result.exam_date.isoformat() if result.exam_date else None,
                "average_score": round(float(result.avg_score), 2),
                "max_score": round(float(result.max_score), 2),
                "min_score": round(float(result.min_score), 2)
            })
        
        return trend_data
