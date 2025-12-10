import type { RouteRecordRaw } from 'vue-router'

/**
 * 学生路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const studentRoutes: RouteRecordRaw[] = [
  // 学生资料中心
  {
    path: '/student/materials',
    name: 'StudentMaterialCenter',
    component: () => import('@/pages/student/materials/MaterialCenter.vue'),
    meta: {
      title: '资料中心',
      requiresAuth: true,
      roles: ['student']
    }
  },
  {
    path: '/student/materials/:id',
    name: 'StudentMaterialDetail',
    component: () => import('@/pages/student/materials/MaterialDetail.vue'),
    meta: {
      title: '资料详情',
      requiresAuth: true,
      roles: ['student']
    }
  }
  // 后续添加学生页面路由：
  // /student/dashboard - 学生首页
  // /student/courses - 我的课程
  // /student/attendance - 我的考勤
  // /student/grades - 我的成绩
  // /student/interaction - 课堂互动
]

export default studentRoutes
