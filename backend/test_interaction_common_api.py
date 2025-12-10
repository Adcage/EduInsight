"""
测试课堂互动通用API
"""
import requests

# 创建session以保持cookie
session = requests.Session()

# 测试获取教师课程列表
url = 'http://localhost:5030/api/v1/interaction/common/teacher-courses'

# 需要先登录
login_url = 'http://localhost:5030/api/v1/auth/login'
login_data = {
    'loginIdentifier': 'teacher.test@edu.com',
    'password': 'test123456'
}

print("1. 登录测试教师账号...")
login_response = session.post(login_url, json=login_data)
if login_response.status_code == 200:
    print(f"   登录成功")
    
    print("\n2. 获取教师课程列表...")
    courses_response = session.get(url)
    
    if courses_response.status_code == 200:
        data = courses_response.json()
        print(f"   成功！返回数据:")
        print(f"   - 课程数量: {data['data']['total']}")
        for course in data['data']['courses']:
            print(f"   - {course['name']} (ID: {course['id']})")
    else:
        print(f"   失败: {courses_response.status_code}")
        print(f"   响应: {courses_response.text}")
else:
    print(f"   登录失败: {login_response.status_code}")
    print(f"   响应: {login_response.text}")
