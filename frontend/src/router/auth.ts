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
  }
]

export default authRoutes
