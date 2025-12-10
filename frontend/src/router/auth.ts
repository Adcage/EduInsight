import type { RouteRecordRaw } from 'vue-router'

/**
 * 认证相关路由配置
 */
const authRoutes: RouteRecordRaw[] = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/pages/auth/LoginPage.vue'),
    meta: {
      title: '登录',
      requiresAuth: false
    }
  },
  // 个人资料页面 - 所有已认证用户可访问
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/pages/shared/profile/ProfilePage.vue'),
    meta: {
      title: '个人资料',
      requiresAuth: true,
      roles: ['student', 'teacher', 'admin']
    }
  }
]

export default authRoutes
