/**
 * 班级管理API
 */
import request from '@/request'

// 学生信息接口
export interface StudentInfo {
  id: number
  userCode?: string
  user_code?: string
  realName?: string
  real_name?: string
  username: string
  email: string
  phone?: string
  avatar?: string
  status: boolean
  lastLoginTime?: string
  last_login_time?: string
  createdAt?: string
  created_at?: string
}

// 班级学生列表响应接口
export interface ClassStudentsResponse {
  classId?: number
  class_id?: number
  className?: string
  class_name?: string
  classCode?: string
  class_code?: string
  grade?: string
  major?: string
  students: StudentInfo[]
  total: number
}

// 班级信息接口
export interface ClassInfo {
  id: number
  name: string
  code: string
  description?: string
  grade?: string
  major?: string
  teacherId?: number
  teacher_id?: number
  status: boolean
  studentCount?: number
  student_count?: number
  createdAt?: string
  created_at?: string
  updatedAt?: string
  updated_at?: string
}

// 班级列表响应接口
export interface ClassListResponse {
  classes: ClassInfo[]
  total: number
  page: number
  perPage?: number
  per_page?: number
  pages: number
}

/**
 * 获取班级学生列表
 */
export function getClassStudents(classId: number): Promise<ClassStudentsResponse> {
  return request.get(`/api/v1/classes/${classId}/students`)
}

/**
 * 获取班级列表
 */
export function getClassList(params?: {
  page?: number
  perPage?: number
  status?: boolean
  grade?: string
  major?: string
}): Promise<ClassListResponse> {
  return request.get('/api/v1/classes', { params })
}
