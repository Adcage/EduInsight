/**
 * 考勤管理API
 */
import request from '@/request'

// 考勤方式枚举
export enum AttendanceType {
  QRCODE = 'qrcode',      // 二维码签到
  GESTURE = 'gesture',    // 手势签到
  LOCATION = 'location',  // 位置签到
  FACE = 'face',          // 人脸识别签到
  MANUAL = 'manual'       // 手动签到
}

// 考勤状态枚举
export enum AttendanceStatus {
  PENDING = 'pending',  // 待开始
  ACTIVE = 'active',    // 进行中
  ENDED = 'ended'       // 已结束
}

// 手势路径数据接口
export interface GesturePattern {
  points: Array<{ x: number; y: number; timestamp?: number }>
  width: number
  height: number
  duration?: number
}

// 位置配置接口
export interface LocationConfig {
  name: string
  latitude: number
  longitude: number
  radius: number
}

// 创建考勤任务请求接口
export interface CreateAttendanceRequest {
  title: string
  description?: string
  courseId: number
  course_id?: number
  classIds: number[]
  class_ids?: number[]
  studentIds?: number[]
  student_ids?: number[]
  attendanceType: AttendanceType
  attendance_type?: AttendanceType
  
  // 手势签到配置
  gesturePattern?: GesturePattern
  gesture_pattern?: GesturePattern
  
  // 位置签到配置
  locationConfig?: LocationConfig
  location_config?: LocationConfig
  
  // 人脸识别配置
  faceRecognitionThreshold?: number
  face_recognition_threshold?: number
  
  startTime: string
  start_time?: string
  endTime: string
  end_time?: string
}

// 考勤任务响应接口
export interface AttendanceResponse {
  id: number
  title: string
  description?: string
  courseId?: number
  course_id?: number
  classId?: number
  class_id?: number
  teacherId?: number
  teacher_id?: number
  attendanceType?: string
  attendance_type?: string
  
  // 二维码配置
  qrCode?: string
  qr_code?: string
  
  // 手势配置
  gesturePattern?: GesturePattern
  gesture_pattern?: GesturePattern
  
  // 位置配置
  locationName?: string
  location_name?: string
  locationLatitude?: number
  location_latitude?: number
  locationLongitude?: number
  location_longitude?: number
  locationRadius?: number
  location_radius?: number
  
  // 人脸识别配置
  faceRecognitionThreshold?: number
  face_recognition_threshold?: number
  
  startTime?: string
  start_time?: string
  endTime?: string
  end_time?: string
  status?: string
  createdAt?: string
  created_at?: string
  updatedAt?: string
  updated_at?: string
}

// 考勤列表响应接口
export interface AttendanceListResponse {
  attendances: AttendanceResponse[]
  total: number
  page: number
  perPage?: number
  per_page?: number
  pages: number
}

/**
 * 创建考勤任务
 */
export function createAttendance(data: CreateAttendanceRequest): Promise<{
  message: string
  data: AttendanceResponse
}> {
  return request.post('/api/v1/attendances/', data)
}

/**
 * 获取考勤列表
 */
export function getAttendanceList(params?: {
  page?: number
  perPage?: number
  per_page?: number
  courseId?: number
  course_id?: number
  teacherId?: number
  teacher_id?: number
  status?: AttendanceStatus
}): Promise<AttendanceListResponse> {
  return request.get('/api/v1/attendances/', { params })
}

/**
 * 获取考勤详情
 */
export function getAttendanceDetail(attendanceId: number): Promise<AttendanceResponse> {
  return request.get(`/api/v1/attendances/${attendanceId}`)
}

/**
 * 更新考勤任务
 */
export function updateAttendance(
  attendanceId: number,
  data: Partial<CreateAttendanceRequest>
): Promise<{
  message: string
  data: AttendanceResponse
}> {
  return request.put(`/api/v1/attendances/${attendanceId}`, data)
}

/**
 * 删除考勤任务
 */
export function deleteAttendance(attendanceId: number): Promise<{
  message: string
}> {
  return request.delete(`/api/v1/attendances/${attendanceId}`)
}

/**
 * 开始考勤
 */
export function startAttendance(attendanceId: number): Promise<{
  message: string
  data: AttendanceResponse
}> {
  return request.post(`/api/v1/attendances/${attendanceId}/start`)
}

/**
 * 结束考勤
 */
export function endAttendance(attendanceId: number): Promise<{
  message: string
  data: AttendanceResponse
}> {
  return request.post(`/api/v1/attendances/${attendanceId}/end`)
}

/**
 * 考勤记录接口
 */
export interface AttendanceRecord {
  id: number
  attendanceId: number
  attendance_id?: number
  studentId: number
  student_id?: number
  studentName?: string
  student_name?: string
  studentCode?: string
  student_code?: string
  studentAvatar?: string
  student_avatar?: string
  status: 'absent' | 'present' | 'late' | 'leave'
  checkInTime?: string
  check_in_time?: string
  distance?: number
  gestureSimilarity?: number
  gesture_similarity?: number
  faceSimilarity?: number
  face_similarity?: number
  remark?: string
  createdAt: string
  created_at?: string
  updatedAt: string
  updated_at?: string
}

export interface AttendanceRecordListResponse {
  records: AttendanceRecord[]
  total: number
}

/**
 * 获取考勤记录列表
 */
export function getAttendanceRecords(attendanceId: number): Promise<AttendanceRecordListResponse> {
  return request.get(`/api/v1/attendances/${attendanceId}/records`)
}

/**
 * 更新考勤记录（教师手动标记）
 */
export function updateAttendanceRecord(
  attendanceId: number,
  recordId: number,
  data: {
    status: 'absent' | 'present' | 'late' | 'leave'
    remark?: string
  }
): Promise<AttendanceRecord> {
  return request.put(`/api/v1/attendances/${attendanceId}/records/${recordId}`, data)
}

/**
 * 学生端考勤通知接口
 */

// 学生考勤通知响应接口
export interface StudentAttendanceNotification extends AttendanceResponse {
  courseName?: string
  course_name?: string
  teacherName?: string
  teacher_name?: string
  myRecord?: AttendanceRecord
  my_record?: AttendanceRecord
  isCheckedIn?: boolean
  is_checked_in?: boolean
  // 位置签到相关
  locationLatitude?: number
  location_latitude?: number
  locationLongitude?: number
  location_longitude?: number
  locationRange?: number
  location_range?: number
}

/**
 * 获取学生的考勤通知列表
 */
export function getStudentAttendances(params?: {
  page?: number
  perPage?: number
  per_page?: number
  status?: AttendanceStatus
}): Promise<{
  attendances: StudentAttendanceNotification[]
  total: number
  page: number
  perPage?: number
  per_page?: number
  pages: number
}> {
  return request.get('/api/v1/students/attendances', { params })
}

/**
 * 获取学生的考勤详情
 */
export function getStudentAttendanceDetail(attendanceId: number): Promise<StudentAttendanceNotification> {
  return request.get(`/api/v1/students/attendances/${attendanceId}`)
}

/**
 * 二维码签到接口
 */

// 二维码验证请求
export interface QRCodeVerifyRequest {
  attendanceId: number
  attendance_id?: number
  qrCodeToken: string
  qr_code_token?: string
  studentNumber?: string  // 学号（不登录时必填）
  student_number?: string
}

/**
 * 生成/刷新二维码token
 */
export interface GenerateQRCodeRequest {
  attendanceId: number
  token: string  // 前端生成的token
}

export interface GenerateQRCodeResponse {
  message: string
  qrCodeToken: string
  qr_code_token?: string
}

export function generateQRCodeToken(data: GenerateQRCodeRequest): Promise<GenerateQRCodeResponse> {
  return request.post(`/api/v1/attendances/${data.attendanceId}/qrcode/generate`, {
    token: data.token
  })
}

/**
 * 验证二维码并签到
 */
export function verifyQRCodeAndCheckIn(data: QRCodeVerifyRequest): Promise<{
  message: string
  data: AttendanceRecord
}> {
  return request.post('/api/v1/attendances/qrcode/verify', data)
}

/**
 * 位置签到接口
 */
export interface LocationCheckInRequest {
  attendanceId: number
  attendance_id?: number
  latitude: number
  longitude: number
}

/**
 * 位置签到
 */
export function locationCheckIn(data: LocationCheckInRequest): Promise<{
  message: string
  data: AttendanceRecord
}> {
  return request.post('/api/v1/attendances/location/verify', data)
}

/**
 * 手势签到接口
 */
export interface GestureCheckInRequest {
  attendanceId: number
  attendance_id?: number
  gestureData: GesturePattern
  gesture_data?: GesturePattern
}

/**
 * 手势签到
 */
export function gestureCheckIn(data: GestureCheckInRequest): Promise<{
  message: string
  data: AttendanceRecord
}> {
  return request.post('/api/v1/attendances/gesture/verify', data)
}

/**
 * 人脸验证签到接口
 */
export interface FaceVerificationRequest {
  studentNumber: string
  student_number?: string
  faceImageBase64: string
  face_image_base64?: string
  attendanceId: number
  attendance_id?: number
}

/**
 * 人脸验证响应接口
 */
export interface FaceVerificationResponse {
  verified: boolean
  similarity: number
  message: string
  hasFaceImage: boolean
  has_face_image?: boolean
}

/**
 * 人脸验证签到
 */
export function attendanceApiFaceVerificationPost(data: FaceVerificationRequest): Promise<FaceVerificationResponse> {
  return request.post('/api/v1/attendances/face-verification', data)
}
