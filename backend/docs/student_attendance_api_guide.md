# 学生端考勤API使用指南

## 概述

学生端考勤API提供了学生查看考勤通知和完成签到的接口。学生可以查看自己所在班级的所有考勤任务，并查看自己的签到状态。

## API端点

### 1. 获取学生考勤通知列表

**接口**: `GET /api/v1/students/attendances`

**权限**: 学生

**请求参数**:
```
page: int (可选，默认1) - 页码
perPage: int (可选，默认20) - 每页数量
status: string (可选) - 状态筛选 (pending/active/ended)
```

**响应示例**:
```json
{
  "attendances": [
    {
      "id": 1,
      "title": "第一节课考勤",
      "description": "请准时签到",
      "courseId": 1,
      "courseName": "数据结构",
      "classId": 1,
      "teacherId": 2,
      "teacherName": "张老师",
      "attendanceType": "qrcode",
      "startTime": "2024-12-09 10:00:00",
      "endTime": "2024-12-09 12:00:00",
      "status": "active",
      "myRecord": {
        "id": 10,
        "attendanceId": 1,
        "studentId": 5,
        "status": "present",
        "checkInTime": "2024-12-09 10:05:00",
        "checkInMethod": "qrcode"
      },
      "isCheckedIn": true,
      "createdAt": "2024-12-09 09:00:00",
      "updatedAt": "2024-12-09 09:00:00"
    }
  ],
  "total": 10,
  "page": 1,
  "perPage": 20,
  "pages": 1
}
```

**字段说明**:
- `myRecord`: 学生自己的签到记录，如果未签到则为null
- `isCheckedIn`: 是否已签到（present或late状态为true）
- `courseName`: 课程名称
- `teacherName`: 教师名称

### 2. 获取学生考勤详情

**接口**: `GET /api/v1/students/attendances/{attendance_id}`

**权限**: 学生

**路径参数**:
```
attendance_id: int - 考勤ID
```

**响应示例**:
```json
{
  "id": 1,
  "title": "第一节课考勤",
  "description": "请准时签到",
  "courseId": 1,
  "courseName": "数据结构",
  "classId": 1,
  "teacherId": 2,
  "teacherName": "张老师",
  "attendanceType": "qrcode",
  "qrCode": "abc123...",
  "startTime": "2024-12-09 10:00:00",
  "endTime": "2024-12-09 12:00:00",
  "status": "active",
  "myRecord": {
    "id": 10,
    "attendanceId": 1,
    "studentId": 5,
    "status": "present",
    "checkInTime": "2024-12-09 10:05:00",
    "checkInMethod": "qrcode",
    "remark": null
  },
  "isCheckedIn": true,
  "createdAt": "2024-12-09 09:00:00",
  "updatedAt": "2024-12-09 09:00:00"
}
```

**错误响应**:
```json
{
  "message": "考勤不存在或无权访问"
}
```

## 业务逻辑

### 考勤范围验证

学生只能查看和访问自己所在班级的考勤任务。系统通过以下方式验证：

1. 获取学生的 `class_id`
2. 查询该班级的所有考勤任务
3. 验证学生是否有权访问特定考勤

### 签到状态判断

- `isCheckedIn = true`: 签到状态为 `present` 或 `late`
- `isCheckedIn = false`: 签到状态为 `absent` 或 `leave`，或未签到

### 状态筛选

支持按考勤状态筛选：
- `pending`: 待开始
- `active`: 进行中
- `ended`: 已结束

## 数据模型

### 学生考勤通知响应

```typescript
interface StudentAttendanceNotification {
  id: number
  title: string
  description?: string
  courseId: number
  courseName?: string
  classId: number
  teacherId: number
  teacherName?: string
  attendanceType: 'qrcode' | 'gesture' | 'location' | 'face'
  startTime: string
  endTime: string
  status: 'pending' | 'active' | 'ended'
  myRecord?: AttendanceRecord
  isCheckedIn?: boolean
  createdAt: string
  updatedAt: string
}
```

### 签到记录

```typescript
interface AttendanceRecord {
  id: number
  attendanceId: number
  studentId: number
  status: 'present' | 'late' | 'absent' | 'leave'
  checkInTime?: string
  checkInMethod?: string
  remark?: string
  createdAt: string
  updatedAt: string
}
```

## 使用示例

### JavaScript/TypeScript

```typescript
// 获取考勤通知列表
async function getAttendances(token: string, page: number = 1) {
  const response = await fetch(
    `http://localhost:5030/api/v1/students/attendances?page=${page}&perPage=12`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
}

// 获取考勤详情
async function getAttendanceDetail(token: string, attendanceId: number) {
  const response = await fetch(
    `http://localhost:5030/api/v1/students/attendances/${attendanceId}`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
}

// 按状态筛选
async function getActiveAttendances(token: string) {
  const response = await fetch(
    `http://localhost:5030/api/v1/students/attendances?status=active`,
    {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    }
  );
  return await response.json();
}
```

### Python

```python
import requests

BASE_URL = "http://localhost:5030/api/v1"

# 获取考勤通知列表
def get_attendances(token, page=1, per_page=12, status=None):
    url = f"{BASE_URL}/students/attendances"
    headers = {"Authorization": f"Bearer {token}"}
    params = {"page": page, "perPage": per_page}
    if status:
        params["status"] = status
    
    response = requests.get(url, headers=headers, params=params)
    return response.json()

# 获取考勤详情
def get_attendance_detail(token, attendance_id):
    url = f"{BASE_URL}/students/attendances/{attendance_id}"
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.get(url, headers=headers)
    return response.json()
```

## 测试

### 运行测试脚本

```bash
cd backend
python test_student_attendance_api.py
```

测试脚本会执行以下测试：
1. 学生登录
2. 获取考勤通知列表
3. 获取考勤详情
4. 状态筛选功能

### 手动测试

使用curl命令测试：

```bash
# 1. 学生登录
curl -X POST http://localhost:5030/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"student1","password":"123456"}'

# 2. 获取考勤列表（使用返回的token）
curl -X GET "http://localhost:5030/api/v1/students/attendances?page=1&perPage=12" \
  -H "Authorization: Bearer {token}"

# 3. 获取考勤详情
curl -X GET "http://localhost:5030/api/v1/students/attendances/1" \
  -H "Authorization: Bearer {token}"

# 4. 按状态筛选
curl -X GET "http://localhost:5030/api/v1/students/attendances?status=active" \
  -H "Authorization: Bearer {token}"
```

## 错误处理

### 常见错误

| 状态码 | 错误信息 | 原因 | 解决方案 |
|--------|---------|------|---------|
| 401 | Unauthorized | 未登录或token无效 | 重新登录获取token |
| 403 | Forbidden | 非学生身份 | 使用学生账号登录 |
| 404 | 考勤不存在或无权访问 | 考勤ID无效或不在班级范围内 | 检查考勤ID和班级 |
| 500 | 服务器错误 | 后端异常 | 查看服务器日志 |

## 实现文件

### 后端文件

- **API层**: `app/api/student_attendance_api.py`
- **Service层**: `app/services/student_attendance_service.py`
- **注册**: `app/api/__init__.py`

### 关键代码

**API蓝图注册**:
```python
# app/api/__init__.py
from app.api.student_attendance_api import student_attendance_api_bp

api_blueprints = [
    # ...
    student_attendance_api_bp,
    # ...
]
```

**Service层逻辑**:
```python
# app/services/student_attendance_service.py
class StudentAttendanceService:
    @staticmethod
    def get_student_attendances(student_id, page, per_page, status):
        # 获取学生班级
        student = User.query.get(student_id)
        # 查询该班级的考勤
        query = Attendance.query.filter_by(class_id=student.class_id)
        # 添加学生签到记录
        # ...
```

## 注意事项

1. **权限验证**: 所有接口都需要学生身份认证
2. **数据隔离**: 学生只能看到自己班级的考勤
3. **签到记录**: 自动关联学生的签到记录
4. **状态同步**: 实时反映考勤和签到状态
5. **分页处理**: 大量数据时使用分页

## 相关文档

- 前端集成文档: `frontend/docs/学生端签到通知功能说明.md`
- 二维码签到: `backend/docs/qrcode_attendance_guide.md`
- 考勤API: `backend/docs/attendance_api_guide.md`
