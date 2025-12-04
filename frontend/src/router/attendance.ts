import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/attendance',
    name: 'AttendanceDemo',
    component: () => import('@/pages/teacher/attendance/AttendanceDemo.vue'),
    meta: {
      title: '考勤演示'
    }
  },
  {
    path: '/',
    redirect: '/attendance'
  }
]

export default routes
