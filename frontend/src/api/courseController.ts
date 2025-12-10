/**
 * 课程管理API
 */
import request from '@/request'

// 课程信息接口
export interface Course {
  id: number
  name: string
  code: string
  description?: string
  semester: string
  academicYear: string
  credit?: number
  totalHours?: number
  teacherId: number
  status: boolean
  classCount?: number
  studentCount?: number
  createdAt: string
  updatedAt: string
}

// 课程详情接口
export interface CourseDetail extends Course {
  teacherName?: string
  teacherEmail?: string
}

// 班级信息接口
export interface ClassInfo {
  classId?: number
  class_id?: number
  className?: string
  class_name?: string
  classCode?: string
  class_code?: string
  grade?: string
  major?: string
  studentCount?: number
  student_count?: number
  startDate?: string
  start_date?: string
  endDate?: string
  end_date?: string
  status: boolean
}

// 课程列表响应接口
export interface CourseListResponse {
  courses: Course[]
  total: number
  page: number
  perPage: number
  pages: number
}

// 课程班级列表响应接口
export interface CourseClassListResponse {
  classes: ClassInfo[]
  total: number
  totalStudents?: number
  total_students?: number
}

// 查询参数接口
export interface CourseQueryParams {
  page?: number
  perPage?: number
  semester?: string
  status?: boolean
  includeStats?: boolean
}

/**
 * 获取教师的课程列表
 */
export function getTeacherCourses(
  teacherId: number,
  params?: CourseQueryParams
): Promise<CourseListResponse> {
  return request.get(`/api/v1/courses/teacher/${teacherId}`, { params })
}

/**
 * 获取课程详情
 */
export function getCourseDetail(courseId: number): Promise<CourseDetail> {
  return request.get(`/api/v1/courses/${courseId}`)
}

/**
 * 获取课程关联的班级列表
 */
export function getCourseClasses(courseId: number): Promise<CourseClassListResponse> {
  return request.get(`/api/v1/courses/${courseId}/classes`)
}

/**
 * 为课程添加班级
 */
export function addClassesToCourse(
  courseId: number,
  data: {
    classIds: number[]
    startDate?: string
    endDate?: string
  }
): Promise<{ message: string }> {
  return request.post(`/api/v1/courses/${courseId}/classes`, data)
}

/**
 * 从课程中移除班级
 */
export function removeClassFromCourse(
  courseId: number,
  classId: number
): Promise<{ message: string }> {
  return request.delete(`/api/v1/courses/${courseId}/classes/${classId}`)
}
