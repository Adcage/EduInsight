export type AttendanceStatus = 'pending' | 'active' | 'ended';
export type CheckInStatus = 'present' | 'absent' | 'late' | 'leave';

export type AttendanceType = 'qrcode' | 'gesture' | 'manual' | 'face' | 'location';

export interface AttendanceTask {
  id: string;
  courseId: string;
  courseName: string;
  classId?: string;
  className: string;
  teacherId: string;
  title: string;
  type: AttendanceType;
  qrCode?: string;
  startTime?: string;
  endTime?: string;
  location?: string;
  requireLocation: boolean;
  status: AttendanceStatus;
  totalStudents: number;
  attendedCount: number;
  createTime: string;
}

export interface Student {
  id: string;
  name: string;
  studentId: string; // 学号
  class: string;
}

export interface AttendanceRecord {
  id: string;
  taskId: string;
  studentId: string;
  studentName: string;
  studentNumber: string;
  status: CheckInStatus;
  checkInTime?: string;
  remark?: string;
}

// API Response types structure based on rules
export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  timestamp: number;
}
