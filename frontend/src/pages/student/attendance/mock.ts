import type { AttendanceTask, AttendanceRecord } from './types';
import dayjs from 'dayjs';

export const MOCK_COURSES = [
  { id: 'c1', name: '高等数学' },
  { id: 'c2', name: 'Python程序设计' },
  { id: 'c3', name: '数据结构' },
];

export const MOCK_CLASSES = [
  { id: 'cl1', name: '计算机科学与技术2101' },
  { id: 'cl2', name: '软件工程2102' },
];

export const MOCK_TASKS: AttendanceTask[] = [
  {
    id: 't1',
    courseId: 'c2',
    courseName: 'Python程序设计',
    className: '计算机科学与技术2101',
    teacherId: 't001',
    title: '第一周课堂考勤',
    requireLocation: false,
    createTime: dayjs().subtract(2, 'hour').format('YYYY-MM-DD HH:mm:ss'),
    status: 'ended',
    totalStudents: 40,
    attendedCount: 38,
    type: 'qrcode'
  },
  {
    id: 't2',
    courseId: 'c3',
    courseName: '数据结构',
    className: '软件工程2102',
    teacherId: 't001',
    title: '第6周平时成绩考勤',
    requireLocation: true,
    createTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
    status: 'active',
    totalStudents: 35,
    attendedCount: 12,
    type: 'qrcode'
  }
];

export const MOCK_RECORDS: AttendanceRecord[] = Array.from({ length: 35 }).map((_, index) => ({
  id: `r${index}`,
  taskId: 't2',
  studentId: `s${index}`,
  studentName: `学生${index + 1}`,
  studentNumber: `202100${100 + index}`,
  status: index < 12 ? 'present' : 'absent',
  checkInTime: index < 12 ? dayjs().subtract(Math.random() * 10, 'minute').format('YYYY-MM-DD HH:mm:ss') : undefined
}));
