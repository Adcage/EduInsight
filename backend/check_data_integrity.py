"""
数据完整性检查脚本
用于验证测试数据的外键关系和必填字段
"""
from app import create_app
from app.extensions import db
from app.models import (
    User, UserRole,
    Class,
    Course,
    Material, MaterialCategory, MaterialTag,
    DocumentKeyword, ClassificationLog
)


def check_data_integrity():
    """检查数据完整性"""
    app = create_app()
    
    with app.app_context():
        print("\n" + "="*60)
        print("开始检查数据完整性...")
        print("="*60)
        
        issues = []
        
        # 1. 检查用户数据
        print("\n📝 检查用户数据...")
        users = User.query.all()
        for user in users:
            # 检查必填字段
            if not user.user_code:
                issues.append(f"用户 {user.username} 缺少 user_code")
            if not user.email:
                issues.append(f"用户 {user.username} 缺少 email")
            if not user.real_name:
                issues.append(f"用户 {user.username} 缺少 real_name")
            
            # 检查学生的班级关联
            if user.role == UserRole.STUDENT and user.class_id:
                cls = Class.query.get(user.class_id)
                if not cls:
                    issues.append(f"学生 {user.username} 的班级ID {user.class_id} 不存在")
        
        print(f"   ✅ 检查了 {len(users)} 个用户")
        
        # 2. 检查班级数据
        print("\n📝 检查班级数据...")
        classes = Class.query.all()
        for cls in classes:
            # 检查必填字段
            if not cls.name:
                issues.append(f"班级 {cls.id} 缺少 name")
            if not cls.code:
                issues.append(f"班级 {cls.id} 缺少 code")
            
            # 检查班主任关联
            if cls.teacher_id:
                teacher = User.query.get(cls.teacher_id)
                if not teacher:
                    issues.append(f"班级 {cls.name} 的班主任ID {cls.teacher_id} 不存在")
                elif teacher.role != UserRole.TEACHER:
                    issues.append(f"班级 {cls.name} 的班主任 {teacher.username} 不是教师角色")
        
        print(f"   ✅ 检查了 {len(classes)} 个班级")
        
        # 3. 检查课程数据
        print("\n📝 检查课程数据...")
        courses = Course.query.all()
        for course in courses:
            # 检查必填字段
            if not course.name:
                issues.append(f"课程 {course.id} 缺少 name")
            if not course.code:
                issues.append(f"课程 {course.id} 缺少 code")
            
            # 检查教师关联
            if course.teacher_id:
                teacher = User.query.get(course.teacher_id)
                if not teacher:
                    issues.append(f"课程 {course.name} 的教师ID {course.teacher_id} 不存在")
                elif teacher.role != UserRole.TEACHER:
                    issues.append(f"课程 {course.name} 的教师 {teacher.username} 不是教师角色")
            
            # 检查课程-班级关联
            for cls in course.classes:
                if not Class.query.get(cls.id):
                    issues.append(f"课程 {course.name} 关联的班级ID {cls.id} 不存在")
        
        print(f"   ✅ 检查了 {len(courses)} 个课程")
        
        # 4. 检查资料分类
        print("\n📝 检查资料分类...")
        categories = MaterialCategory.query.all()
        for category in categories:
            # 检查必填字段
            if not category.name:
                issues.append(f"分类 {category.id} 缺少 name")
            
            # 检查父分类关联
            if category.parent_id:
                parent = MaterialCategory.query.get(category.parent_id)
                if not parent:
                    issues.append(f"分类 {category.name} 的父分类ID {category.parent_id} 不存在")
                
                # 检查是否有循环引用
                if category.parent_id == category.id:
                    issues.append(f"分类 {category.name} 的父分类指向自己")
        
        print(f"   ✅ 检查了 {len(categories)} 个分类")
        
        # 5. 检查资料标签
        print("\n📝 检查资料标签...")
        tags = MaterialTag.query.all()
        for tag in tags:
            # 检查必填字段
            if not tag.name:
                issues.append(f"标签 {tag.id} 缺少 name")
        
        print(f"   ✅ 检查了 {len(tags)} 个标签")
        
        # 6. 检查资料数据
        print("\n📝 检查资料数据...")
        materials = Material.query.all()
        for material in materials:
            # 检查必填字段
            if not material.title:
                issues.append(f"资料 {material.id} 缺少 title")
            if not material.file_name:
                issues.append(f"资料 {material.id} 缺少 file_name")
            if not material.file_path:
                issues.append(f"资料 {material.id} 缺少 file_path")
            if not material.file_type:
                issues.append(f"资料 {material.id} 缺少 file_type")
            if material.file_size is None:
                issues.append(f"资料 {material.id} 缺少 file_size")
            
            # 检查上传者关联
            if not material.uploader_id:
                issues.append(f"资料 {material.title} 缺少 uploader_id")
            else:
                uploader = User.query.get(material.uploader_id)
                if not uploader:
                    issues.append(f"资料 {material.title} 的上传者ID {material.uploader_id} 不存在")
            
            # 检查课程关联
            if material.course_id:
                course = Course.query.get(material.course_id)
                if not course:
                    issues.append(f"资料 {material.title} 的课程ID {material.course_id} 不存在")
            
            # 检查分类关联
            if material.category_id:
                category = MaterialCategory.query.get(material.category_id)
                if not category:
                    issues.append(f"资料 {material.title} 的分类ID {material.category_id} 不存在")
            
            # 检查标签关联
            for tag in material.tags:
                if not MaterialTag.query.get(tag.id):
                    issues.append(f"资料 {material.title} 关联的标签ID {tag.id} 不存在")
        
        print(f"   ✅ 检查了 {len(materials)} 个资料")
        
        # 7. 检查文档关键词
        print("\n📝 检查文档关键词...")
        keywords = DocumentKeyword.query.all()
        for keyword in keywords:
            # 检查必填字段
            if not keyword.material_id:
                issues.append(f"关键词 {keyword.id} 缺少 material_id")
            if not keyword.keyword:
                issues.append(f"关键词 {keyword.id} 缺少 keyword")
            
            # 检查资料关联
            if keyword.material_id:
                material = Material.query.get(keyword.material_id)
                if not material:
                    issues.append(f"关键词 {keyword.keyword} 的资料ID {keyword.material_id} 不存在")
        
        print(f"   ✅ 检查了 {len(keywords)} 个关键词")
        
        # 8. 检查分类日志
        print("\n📝 检查分类日志...")
        logs = ClassificationLog.query.all()
        for log in logs:
            # 检查必填字段
            if not log.material_id:
                issues.append(f"分类日志 {log.id} 缺少 material_id")
            if not log.suggested_category_id:
                issues.append(f"分类日志 {log.id} 缺少 suggested_category_id")
            
            # 检查资料关联
            if log.material_id:
                material = Material.query.get(log.material_id)
                if not material:
                    issues.append(f"分类日志 {log.id} 的资料ID {log.material_id} 不存在")
            
            # 检查原分类关联
            if log.original_category_id:
                category = MaterialCategory.query.get(log.original_category_id)
                if not category:
                    issues.append(f"分类日志 {log.id} 的原分类ID {log.original_category_id} 不存在")
            
            # 检查建议分类关联
            if log.suggested_category_id:
                category = MaterialCategory.query.get(log.suggested_category_id)
                if not category:
                    issues.append(f"分类日志 {log.id} 的建议分类ID {log.suggested_category_id} 不存在")
        
        print(f"   ✅ 检查了 {len(logs)} 个分类日志")
        
        # 输出结果
        print("\n" + "="*60)
        if issues:
            print(f"❌ 发现 {len(issues)} 个问题:")
            for i, issue in enumerate(issues, 1):
                print(f"   {i}. {issue}")
        else:
            print("✅ 数据完整性检查通过，没有发现问题！")
        print("="*60)
        
        return len(issues) == 0


if __name__ == '__main__':
    success = check_data_integrity()
    exit(0 if success else 1)
