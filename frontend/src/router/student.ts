import type { RouteRecordRaw } from 'vue-router'

/**
 * 学生路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const studentRoutes: RouteRecordRaw[] = [
  // 后续添加学生页面路由：
  // {
  //   path: '/student/dashboard',
  //   name: 'StudentDashboard',
  //   component: () => import('@/pages/student/Dashboard.vue'),
  //   meta: {
  //     title: '学生首页',
  //     requiresAuth: true,
  //     roles: ['student']
  //   }
  // },
  // /student/courses - 我的课程
  // /student/materials - 学习资料
  // /student/attendance - 我的考勤
  // /student/grades - 我的成绩
  // /student/interaction - 课堂互动
]

export default studentRoutes
