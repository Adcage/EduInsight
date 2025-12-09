import type { RouteRecordRaw } from 'vue-router'

/**
 * 管理员路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const adminRoutes: RouteRecordRaw[] = [
  {
    path: '/admin/users',
    name: 'AdminUsers',
    component: () => import('@/pages/admin/users/UserManagement.vue'),
    meta: {
      title: '用户管理',
      requiresAuth: true,
      roles: ['admin']
    }
  },
  // 后续添加其他管理员页面路由：
  // /admin/dashboard - 控制台
  // /admin/courses - 课程管理
  // /admin/classes - 班级管理
  // /admin/settings - 系统设置
]

export default adminRoutes
