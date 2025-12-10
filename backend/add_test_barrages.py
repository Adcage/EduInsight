"""
添加测试弹幕数据
"""
import sys
from app import create_app
from app.extensions import db
from app.models.interaction import Barrage, Question
from datetime import datetime

app = create_app()

# 测试弹幕内容
test_contents = [
    "这节课讲得太好了！",
    "老师讲解得很清楚",
    "我学到了很多新知识",
    "这个知识点很重要",
    "感谢老师的耐心讲解",
    "课程内容很实用",
    "希望能多讲一些案例",
    "这个例子很生动",
    "我对这个概念有了更深的理解",
    "老师的教学方法很好",
    "课堂氛围很活跃",
    "这个问题很有启发性",
    "我会继续努力学习",
    "期待下节课的内容",
    "这个知识点需要多练习",
    "老师辛苦了！",
    "课程设计得很合理",
    "我对这门课很感兴趣",
    "希望能有更多互动",
    "这节课收获满满",
]

with app.app_context():
    # 获取第一个问题
    question = Question.query.first()
    
    if not question:
        print("错误：数据库中没有问题，请先创建问题")
        sys.exit(1)
    
    print(f"找到问题: {question.content}")
    print(f"问题ID: {question.id}")
    
    # 为这个问题添加20条测试弹幕
    added_count = 0
    for i, content in enumerate(test_contents):
        barrage = Barrage(
            content=content,
            user_id=2 + (i % 5),  # 使用用户ID 2-6
            course_id=question.course_id,
            question_id=question.id,
            is_anonymous=False
        )
        db.session.add(barrage)
        added_count += 1
    
    db.session.commit()
    print(f"\n成功添加 {added_count} 条测试弹幕！")
    print(f"课程ID: {question.course_id}")
    print(f"问题ID: {question.id}")
