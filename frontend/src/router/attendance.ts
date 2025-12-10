import type {RouteRecordRaw} from 'vue-router'

const routes: Array<RouteRecordRaw> = [
    // 教师端考勤路由
    {
        path: '/attendance',
        name: 'AttendanceDemo',
        component: () => import('@/pages/teacher/attendance/AttendanceDemo.vue'),
        meta: {
            title: '考勤演示',
            requiresAuth: true,
            role: 'teacher'
        }
    },
    // 学生端考勤路由
    {
        path: '/student/attendance',
        name: 'StudentAttendanceNotifications',
        component: () => import('@/pages/student/attendance/AttendanceNotifications.vue'),
        meta: {
            title: '签到通知',
            requiresAuth: true,
            role: 'student'
        }
    },
    {
        path: '/student/attendance/:id',
        name: 'StudentAttendanceDetail',
        component: () => import('@/pages/student/attendance/AttendanceDetail.vue'),
        meta: {
            title: '签到详情',
            requiresAuth: true,
            role: 'student'
        }
    },
    // 二维码扫描页面
    {
        path: '/student/attendance/scanner',
        name: 'QRCodeScanner',
        component: () => import('@/pages/student/attendance/QRCodeScanner.vue'),
        meta: {
            title: '扫描签到',
            requiresAuth: false // 扫码前可能未登录，允许访问
        }
    },
    // 移动端签到页面
    {
        path: '/student/attendance/mobile',
        name: 'AttendanceMobile',
        component: () => import('@/pages/student/attendance/AttendanceMobile.vue'),
        meta: {
            title: '学生签到',
            requiresAuth: false // 扫码后可能未登录，允许访问
        }
    },
    {
        path: '/',
        redirect: '/attendance'
    }
]

export default routes
