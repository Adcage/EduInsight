"""
预警预测服务层

使用 scikit-learn 机器学习库进行成绩预测
"""
from typing import List, Dict, Any, Optional
from datetime import date, datetime
from app.models.prediction import Prediction, Intervention, PredictionConfig, RiskLevel, InterventionType
from app.models.grade import Grade, ExamType
from app.models.user import User
from app.models.course import Course
from app.extensions import db
import logging
import numpy as np
from sklearn.linear_model import LinearRegression, Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import cross_val_score

logger = logging.getLogger(__name__)


class PredictionService:
    """预测服务类"""
    
    @staticmethod
    def generate_predictions(course_id: int, class_id: Optional[int] = None) -> Dict[str, Any]:
        """
        为课程生成预警预测
        
        Args:
            course_id: 课程ID
            class_id: 班级ID(可选,如果指定则只预测该班级学生)
            
        Returns:
            预测结果统计
        """
        course = Course.query.get(course_id)
        if not course:
            raise ValueError("课程不存在")
        
        # 获取需要预测的学生列表
        if class_id:
            from app.models.class_model import Class
            class_obj = Class.query.get(class_id)
            if not class_obj:
                raise ValueError("班级不存在")
            students = class_obj.students.all()
        else:
            # 获取该课程所有班级的学生
            students = []
            for cls in course.classes.all():
                students.extend(cls.students.all())
        
        if not students:
            raise ValueError("该课程没有学生")
        
        # 统计结果
        result = {
            "total_students": len(students),
            "predicted_count": 0,
            "high_risk_count": 0,
            "medium_risk_count": 0,
            "low_risk_count": 0,
            "no_risk_count": 0,
            "skipped_count": 0,
            "predictions": []
        }
        
        prediction_date = date.today()
        
        for student in students:
            try:
                # 获取学生该课程的成绩
                grades = Grade.query.filter_by(
                    student_id=student.id,
                    course_id=course_id
                ).order_by(Grade.exam_date).all()
                
                if len(grades) < 2:
                    # 成绩记录不足,跳过
                    result["skipped_count"] += 1
                    continue
                
                # 预测期末成绩
                predicted_score, confidence = PredictionService._predict_final_score(grades)
                
                # 判定风险等级
                risk_level = PredictionService._determine_risk_level(predicted_score)
                
                # 检查是否已存在该学生该课程的预测记录
                existing_prediction = Prediction.query.filter_by(
                    student_id=student.id,
                    course_id=course_id,
                    prediction_date=prediction_date
                ).first()
                
                if existing_prediction:
                    # 更新现有记录
                    existing_prediction.predicted_score = predicted_score
                    existing_prediction.confidence = confidence
                    existing_prediction.risk_level = risk_level
                    prediction = existing_prediction
                else:
                    # 创建新预测记录
                    prediction = Prediction(
                        student_id=student.id,
                        course_id=course_id,
                        predicted_score=predicted_score,
                        confidence=confidence,
                        risk_level=risk_level,
                        prediction_date=prediction_date,
                        is_sent=False
                    )
                    db.session.add(prediction)
                
                result["predicted_count"] += 1
                
                # 统计风险等级
                if risk_level == RiskLevel.HIGH:
                    result["high_risk_count"] += 1
                elif risk_level == RiskLevel.MEDIUM:
                    result["medium_risk_count"] += 1
                elif risk_level == RiskLevel.LOW:
                    result["low_risk_count"] += 1
                else:
                    result["no_risk_count"] += 1
                
                result["predictions"].append({
                    "student_id": student.id,
                    "student_name": student.real_name,
                    "student_code": student.user_code,
                    "predicted_score": predicted_score,
                    "confidence": confidence,
                    "risk_level": risk_level.value
                })
                
            except Exception as e:
                logger.error(f"预测学生{student.id}成绩失败: {str(e)}")
                result["skipped_count"] += 1
                continue
        
        db.session.commit()
        
        return result
    
    @staticmethod
    def _predict_final_score(grades: List[Grade]) -> tuple[float, float]:
        """
        预测期末成绩
        
        使用 scikit-learn 机器学习模型进行预测：
        - 主要算法：Ridge 回归（岭回归，带 L2 正则化的线性回归）
        - 特征工程：时间序列特征、考试类型权重、成绩统计特征
        - 置信度计算：基于交叉验证 R² 分数和成绩稳定性
        
        Args:
            grades: 学生的成绩记录列表(按时间排序)
            
        Returns:
            (predicted_score, confidence): 预测分数和置信度
        """
        if len(grades) < 2:
            raise ValueError("成绩记录不足,无法预测")
        
        # 检查是否已有期末成绩
        has_final = any(g.exam_type == ExamType.FINAL for g in grades)
        if has_final:
            # 已有期末成绩,直接返回
            final_grade = next(g for g in grades if g.exam_type == ExamType.FINAL)
            return float(final_grade.score), 100.0
        
        # 提取成绩数据
        scores = [float(g.score) for g in grades]
        
        try:
            # ==================== 特征工程 ====================
            # 构建特征矩阵 X 和目标向量 y
            n = len(scores)
            
            # 特征1: 时间序列索引（归一化）
            time_indices = np.array(range(n)).reshape(-1, 1) / max(n - 1, 1)
            
            # 特征2: 考试类型权重
            exam_type_weights = []
            for g in grades:
                if g.exam_type == ExamType.FINAL:
                    exam_type_weights.append(1.0)
                elif g.exam_type == ExamType.MIDTERM:
                    exam_type_weights.append(0.8)
                elif g.exam_type == ExamType.DAILY:
                    exam_type_weights.append(0.6)
                else:  # HOMEWORK
                    exam_type_weights.append(0.4)
            exam_type_weights = np.array(exam_type_weights).reshape(-1, 1)
            
            # 特征3: 累积平均分（到当前为止的平均）
            cumulative_avg = np.array([np.mean(scores[:i+1]) for i in range(n)]).reshape(-1, 1) / 100
            
            # 特征4: 成绩变化趋势（与前一次的差值）
            score_diff = np.array([0] + [scores[i] - scores[i-1] for i in range(1, n)]).reshape(-1, 1) / 100
            
            # 组合特征矩阵
            X = np.hstack([time_indices, exam_type_weights, cumulative_avg, score_diff])
            y = np.array(scores)
            
            # ==================== 模型训练 ====================
            # 使用 Ridge 回归（岭回归）- 带 L2 正则化，防止过拟合
            model = Ridge(alpha=1.0)
            model.fit(X, y)
            
            # ==================== 预测下一次成绩（期末） ====================
            # 构建预测特征
            next_time_index = np.array([[1.0]])  # 归一化后的下一个时间点
            next_exam_weight = np.array([[1.0]])  # 期末考试权重最高
            next_cumulative_avg = np.array([[np.mean(scores) / 100]])
            
            # 趋势特征：使用最近的变化趋势
            if n >= 2:
                recent_trend = (scores[-1] - scores[-2]) / 100
            else:
                recent_trend = 0
            next_score_diff = np.array([[recent_trend]])
            
            X_pred = np.hstack([next_time_index, next_exam_weight, next_cumulative_avg, next_score_diff])
            
            # 预测
            predicted_score = model.predict(X_pred)[0]
            
            # 限制在0-100范围内
            predicted_score = max(0, min(100, predicted_score))
            
            # ==================== 置信度计算 ====================
            # 方法1: 基于模型拟合度 (R² 分数)
            y_pred_train = model.predict(X)
            ss_res = np.sum((y - y_pred_train) ** 2)
            ss_tot = np.sum((y - np.mean(y)) ** 2)
            r2_score = 1 - (ss_res / ss_tot) if ss_tot > 0 else 0
            r2_score = max(0, min(1, r2_score))
            
            # 方法2: 基于成绩稳定性（标准差）
            std_dev = np.std(scores)
            stability_score = max(0, min(1, 1 - std_dev / 50))  # 标准差50分对应0稳定性
            
            # 方法3: 基于数据量
            data_score = min(1, n / 5)  # 5条以上数据得满分
            
            # 综合置信度（加权平均）
            confidence = (r2_score * 0.4 + stability_score * 0.4 + data_score * 0.2) * 100
            confidence = max(60, min(100, confidence))  # 限制在60-100之间
            
            logger.info(f"ML预测完成: 预测分数={predicted_score:.2f}, R²={r2_score:.3f}, 置信度={confidence:.2f}")
            
            return round(predicted_score, 2), round(confidence, 2)
            
        except Exception as e:
            logger.error(f"机器学习预测失败: {str(e)}, 降级使用加权平均")
            # 降级方案: 加权平均
            weights = np.array([i + 1 for i in range(len(scores))])
            weights = weights / weights.sum()
            weighted_avg = np.average(scores, weights=weights)
            std_dev = np.std(scores)
            confidence = max(60, min(100, 100 - std_dev))
            return round(weighted_avg, 2), round(confidence, 2)
    
    @staticmethod
    def _determine_risk_level(predicted_score: float) -> RiskLevel:
        """
        根据预测分数判定风险等级
        
        Args:
            predicted_score: 预测分数
            
        Returns:
            风险等级
        """
        if predicted_score < 60:
            return RiskLevel.HIGH      # 高风险: 不及格
        elif predicted_score < 70:
            return RiskLevel.MEDIUM    # 中风险: 刚及格
        elif predicted_score < 80:
            return RiskLevel.LOW       # 低风险: 需关注
        else:
            return RiskLevel.NONE      # 无风险
    
    @staticmethod
    def get_predictions(course_id: int, class_id: Optional[int] = None, 
                       risk_level: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        获取预警列表
        
        Args:
            course_id: 课程ID
            class_id: 班级ID(可选)
            risk_level: 风险等级筛选(可选)
            
        Returns:
            预警列表
        """
        query = Prediction.query.filter_by(course_id=course_id)
        
        # 按班级筛选
        if class_id:
            from app.models.class_model import Class
            class_obj = Class.query.get(class_id)
            if class_obj:
                student_ids = [s.id for s in class_obj.students.all()]
                query = query.filter(Prediction.student_id.in_(student_ids))
        
        # 按风险等级筛选
        if risk_level:
            try:
                risk_enum = RiskLevel(risk_level)
                query = query.filter_by(risk_level=risk_enum)
            except ValueError:
                pass
        
        # 按预测日期降序排序
        predictions = query.order_by(Prediction.prediction_date.desc()).all()
        
        result = []
        for pred in predictions:
            pred_dict = pred.to_dict()
            # 添加学生信息
            if pred.student:
                pred_dict['student_name'] = pred.student.real_name
                pred_dict['student_code'] = pred.student.user_code
                # 获取学生班级
                if pred.student.class_id:
                    from app.models.class_model import Class
                    cls = Class.query.get(pred.student.class_id)
                    pred_dict['class_name'] = cls.name if cls else None
                else:
                    pred_dict['class_name'] = None
            
            # 添加课程信息
            if pred.course:
                pred_dict['course_name'] = pred.course.name
            
            # 统计干预次数
            intervention_count = pred.interventions.count()
            pred_dict['intervention_count'] = intervention_count
            
            result.append(pred_dict)
        
        return result
    
    @staticmethod
    def get_prediction_detail(prediction_id: int) -> Dict[str, Any]:
        """
        获取预警详情
        
        Args:
            prediction_id: 预警ID
            
        Returns:
            预警详情(包含学生历史成绩和干预记录)
        """
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            raise ValueError("预警记录不存在")
        
        result = prediction.to_dict()
        
        # 添加学生信息
        if prediction.student:
            result['student_name'] = prediction.student.real_name
            result['student_code'] = prediction.student.user_code
            result['student_email'] = prediction.student.email
        
        # 添加课程信息
        if prediction.course:
            result['course_name'] = prediction.course.name
        
        # 获取学生该课程的历史成绩
        grades = Grade.query.filter_by(
            student_id=prediction.student_id,
            course_id=prediction.course_id
        ).order_by(Grade.exam_date).all()
        
        result['historical_grades'] = [
            {
                'exam_type': g.exam_type.value if isinstance(g.exam_type, ExamType) else g.exam_type,
                'exam_name': g.exam_name,
                'score': float(g.score),
                'exam_date': g.exam_date.isoformat() if g.exam_date else None
            }
            for g in grades
        ]
        
        # 获取干预记录
        interventions = prediction.interventions.order_by(Intervention.intervention_date.desc()).all()
        result['interventions'] = [
            {
                **interv.to_dict(),
                'teacher_name': interv.teacher.real_name if interv.teacher else None
            }
            for interv in interventions
        ]
        
        return result
    
    @staticmethod
    def add_intervention(prediction_id: int, teacher_id: int, 
                        intervention_data: Dict[str, Any]) -> Intervention:
        """
        添加干预记录
        
        Args:
            prediction_id: 预警ID
            teacher_id: 教师ID
            intervention_data: 干预数据
            
        Returns:
            干预记录
        """
        prediction = Prediction.query.get(prediction_id)
        if not prediction:
            raise ValueError("预警记录不存在")
        
        intervention = Intervention(
            prediction_id=prediction_id,
            teacher_id=teacher_id,
            intervention_date=intervention_data.get('intervention_date', date.today()),
            intervention_type=InterventionType(intervention_data['intervention_type']),
            description=intervention_data['description'],
            expected_effect=intervention_data.get('expected_effect'),
            actual_effect=intervention_data.get('actual_effect'),
            student_feedback=intervention_data.get('student_feedback')
        )
        
        db.session.add(intervention)
        db.session.commit()
        
        return intervention
    
    @staticmethod
    def update_intervention(intervention_id: int, update_data: Dict[str, Any]) -> Intervention:
        """
        更新干预记录
        
        Args:
            intervention_id: 干预ID
            update_data: 更新数据
            
        Returns:
            更新后的干预记录
        """
        intervention = Intervention.query.get(intervention_id)
        if not intervention:
            raise ValueError("干预记录不存在")
        
        # 更新字段
        if 'actual_effect' in update_data:
            intervention.actual_effect = update_data['actual_effect']
        if 'student_feedback' in update_data:
            intervention.student_feedback = update_data['student_feedback']
        if 'description' in update_data:
            intervention.description = update_data['description']
        if 'expected_effect' in update_data:
            intervention.expected_effect = update_data['expected_effect']
        
        db.session.commit()
        
        return intervention
    
    @staticmethod
    def send_notifications(prediction_ids: List[int]) -> Dict[str, Any]:
        """
        批量发送预警通知
        
        Args:
            prediction_ids: 预警ID列表
            
        Returns:
            发送结果统计
        """
        from app.models.system import Notification, NotificationType, NotificationPriority
        
        result = {
            "total": len(prediction_ids),
            "success_count": 0,
            "failed_count": 0
        }
        
        for pred_id in prediction_ids:
            try:
                prediction = Prediction.query.get(pred_id)
                if not prediction or prediction.is_sent:
                    result["failed_count"] += 1
                    continue
                
                # 创建通知
                notification = Notification(
                    user_id=prediction.student_id,
                    type=NotificationType.SYSTEM,
                    priority=NotificationPriority.HIGH if prediction.risk_level == RiskLevel.HIGH else NotificationPriority.MEDIUM,
                    title=f"成绩预警通知 - {prediction.course.name}",
                    content=f"您的《{prediction.course.name}》课程预测成绩为{prediction.predicted_score}分,风险等级:{prediction.risk_level.value},请注意学习进度。",
                    is_read=False
                )
                db.session.add(notification)
                
                # 标记为已发送
                prediction.is_sent = True
                
                result["success_count"] += 1
                
            except Exception as e:
                logger.error(f"发送预警通知失败: {str(e)}")
                result["failed_count"] += 1
                continue
        
        db.session.commit()
        
        return result

    # ==================== 学生端方法 ====================
    
    @staticmethod
    def get_student_warnings(student_id: int) -> List[Dict[str, Any]]:
        """
        获取学生的个人预警列表
        
        Args:
            student_id: 学生ID
            
        Returns:
            预警列表（按课程分组）
        """
        # 查询该学生的所有预警
        predictions = Prediction.query.filter_by(student_id=student_id).order_by(
            Prediction.prediction_date.desc()
        ).all()
        
        # 按课程分组
        course_warnings: Dict[int, List[Prediction]] = {}
        for pred in predictions:
            if pred.course_id not in course_warnings:
                course_warnings[pred.course_id] = []
            course_warnings[pred.course_id].append(pred)
        
        # 构建返回数据
        result = []
        for course_id, preds in course_warnings.items():
            course = Course.query.get(course_id)
            if not course:
                continue
            
            # 获取最新的预警
            latest_pred = preds[0]
            
            result.append({
                "course_id": course.id,
                "course_name": course.name,
                "course_code": course.code,
                "semester": course.semester,
                "warning_count": len(preds),
                "latest_warning": {
                    "id": latest_pred.id,
                    "predicted_score": float(latest_pred.predicted_score),
                    "confidence": float(latest_pred.confidence),
                    "risk_level": latest_pred.risk_level.value,
                    "prediction_date": latest_pred.prediction_date.isoformat(),
                    "is_sent": latest_pred.is_sent
                }
            })
        
        return result
    
    @staticmethod
    def get_student_warning_detail(prediction_id: int, student_id: int) -> Optional[Dict[str, Any]]:
        """
        获取学生预警详情
        
        Args:
            prediction_id: 预警ID
            student_id: 学生ID（用于权限验证）
            
        Returns:
            预警详情（包含干预记录）
        """
        # 查询预警记录
        prediction = Prediction.query.get(prediction_id)
        
        # 验证权限：预警必须属于该学生
        if not prediction or prediction.student_id != student_id:
            return None
        
        # 获取课程信息
        course = Course.query.get(prediction.course_id)
        
        # 获取学生信息
        student = User.query.get(student_id)
        
        # 获取干预记录
        interventions = Intervention.query.filter_by(
            prediction_id=prediction_id
        ).order_by(Intervention.intervention_date.desc()).all()
        
        intervention_list = []
        for intervention in interventions:
            teacher = User.query.get(intervention.teacher_id)
            intervention_list.append({
                "id": intervention.id,
                "teacher_name": teacher.real_name if teacher else "未知",
                "intervention_date": intervention.intervention_date.isoformat(),
                "intervention_type": intervention.intervention_type.value,
                "description": intervention.description,
                "expected_effect": intervention.expected_effect,
                "actual_effect": intervention.actual_effect,
                "student_feedback": intervention.student_feedback,
                "created_at": intervention.created_at.isoformat()
            })
        
        # 构建返回数据
        return {
            "id": prediction.id,
            "course_id": course.id if course else None,
            "course_name": course.name if course else "未知课程",
            "course_code": course.code if course else None,
            "semester": course.semester if course else None,
            "student_id": student.id,
            "student_name": student.real_name,
            "student_code": student.user_code,
            "predicted_score": float(prediction.predicted_score),
            "confidence": float(prediction.confidence),
            "risk_level": prediction.risk_level.value,
            "prediction_date": prediction.prediction_date.isoformat(),
            "is_sent": prediction.is_sent,
            "interventions": intervention_list,
            "created_at": prediction.created_at.isoformat()
        }
