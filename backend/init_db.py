"""
数据库初始化脚本
用于创建所有数据库表并插入测试数据
"""
from app import create_app
from app.extensions import db
from app.models import (
    User, UserRole,
    Class,
    Course,
    Material, MaterialCategory, MaterialTag,
    DocumentKeyword, ClassificationLog,
    Grade, ExamType,
    Prediction, Intervention, PredictionConfig,
    RiskLevel, InterventionType, PredictFrequency, PredictTrigger
)
from werkzeug.security import generate_password_hash
from datetime import datetime, timedelta
import random


def init_database():
    """初始化数据库"""
    app = create_app()
    
    with app.app_context():
        # 创建所有表
        db.create_all()
        print("✅ 数据库表创建成功!")
        print(f"📁 数据库位置: {app.config['SQLALCHEMY_DATABASE_URI']}")
        
        # 显示创建的表
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        tables = inspector.get_table_names()
        
        if tables:
            print(f"\n📊 已创建 {len(tables)} 个数据表:")
            for table in tables:
                print(f"   - {table}")
        else:
            print("\n⚠️  警告: 没有找到任何数据表!")


def create_test_data():
    """创建测试数据"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("开始创建测试数据...")
        print("="*60)
        
        # 检查是否已有数据
        if User.query.first():
            print("\n⚠️  数据库中已存在数据，跳过测试数据创建")
            return
        
        # 1. 创建用户
        print("\n📝 创建用户...")
        users = create_users()
        print(f"   ✅ 创建了 {len(users)} 个用户")
        
        # 2. 创建班级
        print("\n📝 创建班级...")
        classes = create_classes(users)
        print(f"   ✅ 创建了 {len(classes)} 个班级")
        
        # 3. 创建课程
        print("\n📝 创建课程...")
        courses = create_courses(users, classes)
        print(f"   ✅ 创建了 {len(courses)} 个课程")
        
        # 4. 创建资料分类
        print("\n📝 创建资料分类...")
        categories = create_material_categories()
        print(f"   ✅ 创建了 {len(categories)} 个分类")
        
        # 5. 创建资料标签
        print("\n📝 创建资料标签...")
        tags = create_material_tags()
        print(f"   ✅ 创建了 {len(tags)} 个标签")
        
        # 6. 创建资料（模拟文件）
        print("\n📝 创建资料...")
        materials = create_materials(users, courses, categories, tags)
        print(f"   ✅ 创建了 {len(materials)} 个资料")
        
        # 7. 创建文档关键词
        print("\n📝 创建文档关键词...")
        keywords = create_document_keywords(materials)
        print(f"   ✅ 创建了 {len(keywords)} 个关键词")
        
        # 8. 创建分类日志
        print("\n📝 创建分类日志...")
        logs = create_classification_logs(materials, categories)
        print(f"   ✅ 创建了 {len(logs)} 个分类日志")
        
        print("\n" + "="*60)
        print("✅ 测试数据创建完成!")
        print("="*60)
        print("\n📊 数据统计:")
        print(f"   - 用户: {User.query.count()}")
        print(f"   - 班级: {Class.query.count()}")
        print(f"   - 课程: {Course.query.count()}")
        print(f"   - 资料分类: {MaterialCategory.query.count()}")
        print(f"   - 资料标签: {MaterialTag.query.count()}")
        print(f"   - 资料: {Material.query.count()}")
        print(f"   - 文档关键词: {DocumentKeyword.query.count()}")
        print(f"   - 分类日志: {ClassificationLog.query.count()}")
        print("\n💡 提示: 默认密码都是 'password123'")


def create_users():
    """创建测试用户"""
    users = []
    
    # 管理员
    admin = User(
        username='admin',
        user_code='ADMIN001',
        email='admin@eduinsight.com',
        password_hash=generate_password_hash('password123'),
        real_name='系统管理员',
        role=UserRole.ADMIN,
        status=True
    )
    users.append(admin)
    
    # 教师
    teachers_data = [
        ('teacher1', 'T001', 'teacher1@eduinsight.com', '张老师'),
        ('teacher2', 'T002', 'teacher2@eduinsight.com', '李老师'),
        ('teacher3', 'T003', 'teacher3@eduinsight.com', '王老师'),
        ('teacher4', 'T004', 'teacher4@eduinsight.com', '刘老师'),
    ]
    
    for username, user_code, email, real_name in teachers_data:
        teacher = User(
            username=username,
            user_code=user_code,
            email=email,
            password_hash=generate_password_hash(' '),
            real_name=real_name,
            role=UserRole.TEACHER,
            status=True
        )
        users.append(teacher)
    
    # 学生
    students_data = [
        ('student1', '2021001', 'student1@eduinsight.com', '陈同学', '2021'),
        ('student2', '2021002', 'student2@eduinsight.com', '赵同学', '2021'),
        ('student3', '2022001', 'student3@eduinsight.com', '周同学', '2022'),
        ('student4', '2022002', 'student4@eduinsight.com', '吴同学', '2022'),
        ('student5', '2023001', 'student5@eduinsight.com', '郑同学', '2023'),
        ('student6', '2023002', 'student6@eduinsight.com', '孙同学', '2023'),
    ]
    
    for username, user_code, email, real_name, grade in students_data:
        student = User(
            username=username,
            user_code=user_code,
            email=email,
            password_hash=generate_password_hash('password123'),
            real_name=real_name,
            role=UserRole.STUDENT,
            status=True
        )
        users.append(student)
    
    for user in users:
        db.session.add(user)
    
    db.session.commit()
    return users


def create_classes(users):
    """创建测试班级"""
    teachers = [u for u in users if u.role == UserRole.TEACHER]
    students = [u for u in users if u.role == UserRole.STUDENT]
    
    classes_data = [
        ('计算机2101班', 'CS2101', '计算机科学与技术专业2021级1班', '2021', '计算机科学'),
        ('数据2201班', 'DS2201', '数据科学与大数据技术专业2022级1班', '2022', '数据科学'),
        ('软工2301班', 'SE2301', '软件工程专业2023级1班', '2023', '软件工程'),
    ]
    
    classes = []
    for i, (name, code, desc, grade, major) in enumerate(classes_data):
        cls = Class(
            name=name,
            code=code,
            description=desc,
            grade=grade,
            major=major,
            teacher_id=teachers[i % len(teachers)].id if teachers else None,
            status=True
        )
        db.session.add(cls)
        db.session.flush()
        
        # 为班级添加学生（注意：User模型中没有grade字段，需要通过user_code判断）
        # 学生的user_code格式是 '2021001'，前4位是年级
        for student in students:
            if student.user_code.startswith(grade):
                student.class_id = cls.id
        
        classes.append(cls)
    
    db.session.commit()
    return classes


def create_courses(users, classes):
    """创建测试课程"""
    teachers = [u for u in users if u.role == UserRole.TEACHER]
    
    courses_data = [
        ('Python程序设计', 'CS101', 'Python编程基础课程', '2024-1', '2024', 3.0, 48),
        ('数据结构与算法', 'CS201', '数据结构与算法分析', '2024-1', '2024', 4.0, 64),
        ('机器学习基础', 'DS301', '机器学习理论与实践', '2024-1', '2024', 3.0, 48),
        ('Web开发技术', 'SE201', '前后端Web开发', '2024-1', '2024', 3.0, 48),
        ('数据库系统', 'CS202', '数据库原理与应用', '2024-2', '2024', 3.0, 48),
    ]
    
    courses = []
    for i, (name, code, desc, semester, year, credit, hours) in enumerate(courses_data):
        course = Course(
            name=name,
            code=code,
            description=desc,
            semester=semester,
            academic_year=year,
            credit=credit,
            total_hours=hours,
            teacher_id=teachers[i % len(teachers)].id if teachers else None,
            status=True
        )
        db.session.add(course)
        db.session.flush()
        
        # 为课程添加班级
        if classes:
            course.classes.append(classes[i % len(classes)])
        
        courses.append(course)
    
    db.session.commit()
    return courses


def create_material_categories():
    """创建资料分类（树形结构）"""
    categories = []
    
    # 顶级分类
    top_categories_data = [
        ('课程资料', '各类课程相关的学习资料', 0),
        ('考试资料', '考试相关的复习资料', 1),
        ('项目资料', '课程项目和实践资料', 2),
        ('参考资料', '参考书籍和文档', 3),
        ('多媒体资源', '视频、音频等多媒体学习资源', 4),
        ('作业与练习', '课后作业和练习题', 5),
    ]
    
    top_categories = []
    for name, desc, order in top_categories_data:
        category = MaterialCategory(
            name=name,
            description=desc,
            parent_id=None,
            sort_order=order
        )
        db.session.add(category)
        db.session.flush()
        top_categories.append(category)
        categories.append(category)
    
    # 二级分类
    sub_categories_data = [
        # 课程资料的子分类
        ('课件PPT', '教师上课使用的PPT课件', top_categories[0].id, 0),
        ('教学大纲', '课程教学大纲和计划', top_categories[0].id, 1),
        ('讲义笔记', '课程讲义和学习笔记', top_categories[0].id, 2),
        ('实验指导', '实验课程指导书', top_categories[0].id, 3),
        ('案例分析', '教学案例和分析', top_categories[0].id, 4),
        
        # 考试资料的子分类
        ('历年真题', '往年考试真题', top_categories[1].id, 0),
        ('模拟试卷', '模拟考试试卷', top_categories[1].id, 1),
        ('复习提纲', '考试复习重点', top_categories[1].id, 2),
        ('考点总结', '重要考点归纳总结', top_categories[1].id, 3),
        ('答题技巧', '考试答题方法和技巧', top_categories[1].id, 4),
        
        # 项目资料的子分类
        ('项目文档', '项目需求和设计文档', top_categories[2].id, 0),
        ('源代码', '项目源代码', top_categories[2].id, 1),
        ('演示文稿', '项目展示PPT', top_categories[2].id, 2),
        ('项目报告', '项目总结报告', top_categories[2].id, 3),
        ('开发文档', '开发规范和技术文档', top_categories[2].id, 4),
        
        # 参考资料的子分类
        ('电子书籍', '相关领域电子书', top_categories[3].id, 0),
        ('论文文献', '学术论文和文献', top_categories[3].id, 1),
        ('技术文档', '技术手册和API文档', top_categories[3].id, 2),
        ('行业报告', '行业分析和研究报告', top_categories[3].id, 3),
        ('标准规范', '技术标准和开发规范', top_categories[3].id, 4),
        
        # 多媒体资源的子分类
        ('教学视频', '课程录播和教学视频', top_categories[4].id, 0),
        ('演示动画', '概念演示动画', top_categories[4].id, 1),
        ('音频资料', '音频讲解和播客', top_categories[4].id, 2),
        ('在线课程', 'MOOC和在线课程链接', top_categories[4].id, 3),
        ('直播回放', '课程直播回放', top_categories[4].id, 4),
        
        # 作业与练习的子分类
        ('课后习题', '课后练习题和答案', top_categories[5].id, 0),
        ('编程作业', '编程练习和项目作业', top_categories[5].id, 1),
        ('思考题', '课程思考题和讨论题', top_categories[5].id, 2),
        ('实验报告', '实验报告模板和范例', top_categories[5].id, 3),
        ('小测验', '课堂小测验和随堂练习', top_categories[5].id, 4),
    ]
    
    for name, desc, parent_id, order in sub_categories_data:
        category = MaterialCategory(
            name=name,
            description=desc,
            parent_id=parent_id,
            sort_order=order
        )
        db.session.add(category)
        categories.append(category)
    
    db.session.commit()
    return categories


def create_material_tags():
    """创建资料标签"""
    tags_data = [
        'Python', 'Java', 'C++', 'JavaScript',
        '数据结构', '算法', '机器学习', '深度学习',
        'Web开发', '前端', '后端', '数据库',
        '考试', '复习', '重点', '难点',
        '项目', '实践', '案例', '教程',
        '基础', '进阶', '高级', '入门',
    ]
    
    tags = []
    for tag_name in tags_data:
        tag = MaterialTag(name=tag_name, usage_count=0)
        db.session.add(tag)
        tags.append(tag)
    
    db.session.commit()
    return tags


def create_materials(users, courses, categories, tags):
    """创建测试资料（模拟文件）"""
    teachers = [u for u in users if u.role == UserRole.TEACHER]
    
    # 获取二级分类
    ppt_category = MaterialCategory.query.filter_by(name='课件PPT').first()
    exercise_category = MaterialCategory.query.filter_by(name='课后习题').first()
    exam_category = MaterialCategory.query.filter_by(name='历年真题').first()
    project_category = MaterialCategory.query.filter_by(name='项目文档').first()
    
    materials_data = [
        # Python课程资料
        ('Python基础语法.pdf', 'Python基础语法讲解', 'python_basics.pdf', 1024000, 'pdf', 
         courses[0].id if courses else None, ppt_category.id if ppt_category else None,
         ['Python', '基础', '入门']),
        ('Python数据类型详解.pptx', 'Python数据类型和操作', 'python_datatypes.pptx', 2048000, 'ppt',
         courses[0].id if courses else None, ppt_category.id if ppt_category else None,
         ['Python', '基础']),
        ('Python练习题集.pdf', 'Python课后练习题', 'python_exercises.pdf', 512000, 'pdf',
         courses[0].id if courses else None, exercise_category.id if exercise_category else None,
         ['Python', '练习', '基础']),
        
        # 数据结构课程资料
        ('数据结构导论.pdf', '数据结构基本概念', 'ds_intro.pdf', 3072000, 'pdf',
         courses[1].id if courses else None, ppt_category.id if ppt_category else None,
         ['数据结构', '算法', '基础']),
        ('链表实现与应用.pptx', '链表的各种实现方式', 'linkedlist.pptx', 1536000, 'ppt',
         courses[1].id if courses else None, ppt_category.id if ppt_category else None,
         ['数据结构', '链表', '进阶']),
        ('树与图算法.pdf', '树和图的算法详解', 'tree_graph.pdf', 4096000, 'pdf',
         courses[1].id if courses else None, ppt_category.id if ppt_category else None,
         ['数据结构', '算法', '高级']),
        ('数据结构期末试题.pdf', '2023年期末考试真题', 'ds_exam_2023.pdf', 256000, 'pdf',
         courses[1].id if courses else None, exam_category.id if exam_category else None,
         ['数据结构', '考试', '真题']),
        
        # 机器学习课程资料
        ('机器学习概述.pdf', '机器学习基本概念和方法', 'ml_intro.pdf', 2560000, 'pdf',
         courses[2].id if courses else None, ppt_category.id if ppt_category else None,
         ['机器学习', '入门', '基础']),
        ('监督学习算法.pptx', '常见监督学习算法', 'supervised_learning.pptx', 3584000, 'ppt',
         courses[2].id if courses else None, ppt_category.id if ppt_category else None,
         ['机器学习', '算法', '进阶']),
        ('深度学习入门.pdf', '神经网络和深度学习', 'deep_learning.pdf', 5120000, 'pdf',
         courses[2].id if courses else None, ppt_category.id if ppt_category else None,
         ['机器学习', '深度学习', '高级']),
        
        # Web开发课程资料
        ('HTML与CSS基础.pdf', 'Web前端基础知识', 'html_css.pdf', 1024000, 'pdf',
         courses[3].id if courses else None, ppt_category.id if ppt_category else None,
         ['Web开发', '前端', '基础']),
        ('JavaScript高级编程.pdf', 'JavaScript进阶内容', 'js_advanced.pdf', 3072000, 'pdf',
         courses[3].id if courses else None, ppt_category.id if ppt_category else None,
         ['Web开发', '前端', 'JavaScript', '进阶']),
        ('Flask Web开发.pdf', 'Flask框架实战', 'flask_dev.pdf', 2048000, 'pdf',
         courses[3].id if courses else None, ppt_category.id if ppt_category else None,
         ['Web开发', '后端', 'Python', '实践']),
        ('Web项目实战文档.docx', '完整Web项目开发文档', 'web_project.docx', 512000, 'doc',
         courses[3].id if courses else None, project_category.id if project_category else None,
         ['Web开发', '项目', '实践']),
        
        # 数据库课程资料
        ('数据库系统概论.pdf', '数据库基本原理', 'db_intro.pdf', 2560000, 'pdf',
         courses[4].id if courses else None, ppt_category.id if ppt_category else None,
         ['数据库', '基础', '入门']),
        ('SQL语言详解.pptx', 'SQL查询语言教程', 'sql_tutorial.pptx', 1536000, 'ppt',
         courses[4].id if courses else None, ppt_category.id if ppt_category else None,
         ['数据库', 'SQL', '基础']),
    ]
    
    materials = []
    for i, (title, desc, filename, size, ftype, course_id, category_id, tag_names) in enumerate(materials_data):
        # 模拟文件路径
        file_path = f'uploads/materials/2024/12/{filename}'
        
        material = Material(
            title=title,
            description=desc,
            file_name=filename,
            file_path=file_path,
            file_size=size,
            file_type=ftype,
            course_id=course_id,
            uploader_id=teachers[i % len(teachers)].id if teachers else None,
            category_id=category_id,
            download_count=random.randint(0, 100),
            view_count=random.randint(0, 500),
            keywords=', '.join(tag_names[:3]),
            auto_classified=random.choice([True, False])
        )
        db.session.add(material)
        db.session.flush()
        
        # 添加标签
        for tag_name in tag_names:
            tag = MaterialTag.query.filter_by(name=tag_name).first()
            if tag:
                material.tags.append(tag)
                tag.usage_count += 1
        
        materials.append(material)
    
    db.session.commit()
    return materials


def create_document_keywords(materials):
    """创建文档关键词"""
    keywords_data = []
    
    extraction_methods = ['TF-IDF', 'TextRank', 'BERT', 'KeyBERT']
    
    for material in materials[:10]:  # 只为前10个资料创建关键词
        # 从资料的keywords字段提取
        if material.keywords:
            keyword_list = [k.strip() for k in material.keywords.split(',')]
            for i, keyword in enumerate(keyword_list):
                weight = 1.0 - (i * 0.2)  # 权重递减
                doc_keyword = DocumentKeyword(
                    material_id=material.id,
                    keyword=keyword,
                    weight=max(0.1, weight),
                    extraction_method=random.choice(extraction_methods)
                )
                db.session.add(doc_keyword)
                keywords_data.append(doc_keyword)
    
    db.session.commit()
    return keywords_data


def create_classification_logs(materials, categories):
    """创建分类日志"""
    logs = []
    algorithms = ['NaiveBayes', 'SVM', 'RandomForest', 'BERT']
    
    # 为部分资料创建分类建议
    for material in materials[:8]:  # 只为前8个资料创建日志
        # 随机选择一个不同的分类作为建议
        suggested_category = random.choice([c for c in categories if c.id != material.category_id])
        
        log = ClassificationLog(
            material_id=material.id,
            original_category_id=material.category_id,
            suggested_category_id=suggested_category.id,
            confidence=random.uniform(0.6, 0.95),
            is_accepted=random.choice([True, False, None]),
            algorithm_used=random.choice(algorithms),
            features={'word_count': random.randint(100, 1000), 'page_count': random.randint(10, 100)}
        )
        db.session.add(log)
        logs.append(log)
    
    db.session.commit()
    return logs


if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == '--with-data':
        # 初始化数据库并创建测试数据
        init_database()
        create_test_data()
    else:
        # 只初始化数据库
        init_database()
        print("\n💡 提示: 使用 'python init_db.py --with-data' 可以同时创建测试数据")
