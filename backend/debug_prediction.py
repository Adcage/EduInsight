"""
预警功能调试脚本
用于排查预警生成问题
"""
from app import create_app
from app.models.grade import Grade
from app.models.user import User
from app.models.course import Course
from app.services.prediction_service import PredictionService
from app.extensions import db

app = create_app()

with app.app_context():
    print("=" * 60)
    print("🔍 预警功能调试")
    print("=" * 60)
    
    # 1. 检查成绩数据
    print("\n📊 检查成绩数据:")
    grades = Grade.query.all()
    print(f"总成绩记录数: {len(grades)}")
    
    if grades:
        print("\n最近5条成绩记录:")
        for grade in grades[-5:]:
            student = User.query.get(grade.student_id)
            course = Course.query.get(grade.course_id)
            print(f"  - 学生: {student.real_name if student else 'Unknown'} | "
                  f"课程: {course.name if course else 'Unknown'} | "
                  f"分数: {grade.score} | "
                  f"类型: {grade.exam_type.value if hasattr(grade.exam_type, 'value') else grade.exam_type} | "
                  f"日期: {grade.exam_date}")
    
    # 2. 按学生分组统计成绩
    print("\n👥 按学生统计成绩数量:")
    from sqlalchemy import func
    student_grade_counts = db.session.query(
        Grade.student_id,
        Grade.course_id,
        func.count(Grade.id).label('count')
    ).group_by(Grade.student_id, Grade.course_id).all()
    
    for student_id, course_id, count in student_grade_counts:
        student = User.query.get(student_id)
        course = Course.query.get(course_id)
        print(f"  - 学生: {student.real_name if student else f'ID:{student_id}'} | "
              f"课程: {course.name if course else f'ID:{course_id}'} | "
              f"成绩数: {count}")
        
        # 如果成绩数>=2，显示详细成绩
        if count >= 2:
            student_grades = Grade.query.filter_by(
                student_id=student_id,
                course_id=course_id
            ).order_by(Grade.exam_date).all()
            
            scores = [float(g.score) for g in student_grades]
            print(f"    成绩列表: {scores}")
            
            # 模拟预测
            try:
                predicted_score, confidence = PredictionService._predict_final_score(student_grades)
                risk_level = PredictionService._determine_risk_level(predicted_score)
                print(f"    ✅ 预测分数: {predicted_score} | 置信度: {confidence}% | 风险等级: {risk_level.value}")
            except Exception as e:
                print(f"    ❌ 预测失败: {str(e)}")
    
    # 3. 检查现有预警记录
    print("\n⚠️ 现有预警记录:")
    from app.models.prediction import Prediction
    predictions = Prediction.query.all()
    print(f"总预警记录数: {len(predictions)}")
    
    if predictions:
        print("\n预警详情:")
        for pred in predictions:
            student = User.query.get(pred.student_id)
            course = Course.query.get(pred.course_id)
            print(f"  - 学生: {student.real_name if student else 'Unknown'} | "
                  f"课程: {course.name if course else 'Unknown'} | "
                  f"预测分数: {pred.predicted_score} | "
                  f"风险等级: {pred.risk_level.value} | "
                  f"日期: {pred.prediction_date}")
    
    print("\n" + "=" * 60)
    print("✅ 调试完成")
    print("=" * 60)
