#!/usr/bin/env python3
"""
创建测试数据脚本
"""
import os
import sys

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app
from app.extensions import db
from app.models import Class

def create_test_classes():
    """创建测试班级数据"""
    app = create_app('development')
    
    with app.app_context():
        # 检查是否已存在班级
        existing_class = Class.query.first()
        if existing_class:
            print(f"✅ 班级数据已存在: {existing_class.name}")
            return
        
        # 创建测试班级
        test_classes = [
            Class(
                name="计算机科学与技术2021级1班",
                code="CS2021-1",
                description="计算机科学与技术专业2021级第1班",
                grade="2021",
                major="计算机科学与技术"
            ),
            Class(
                name="软件工程2021级1班", 
                code="SE2021-1",
                description="软件工程专业2021级第1班",
                grade="2021",
                major="软件工程"
            ),
            Class(
                name="数据科学与大数据技术2021级1班",
                code="DS2021-1", 
                description="数据科学与大数据技术专业2021级第1班",
                grade="2021",
                major="数据科学与大数据技术"
            )
        ]
        
        try:
            for class_obj in test_classes:
                db.session.add(class_obj)
            
            db.session.commit()
            print(f"✅ 成功创建 {len(test_classes)} 个测试班级:")
            
            for class_obj in test_classes:
                print(f"   - ID: {class_obj.id}, 名称: {class_obj.name}, 代码: {class_obj.code}")
                
        except Exception as e:
            db.session.rollback()
            print(f"❌ 创建班级失败: {str(e)}")
            raise

if __name__ == '__main__':
    create_test_classes()
