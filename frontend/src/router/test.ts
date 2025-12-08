import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/test-auth',
    name: 'AuthTest',
    component: () => import('@/pages/test_page/AuthTestPage.vue'),
    meta: {
      title: '用户认证测试页面'
    }
  },
  {
    path: '/test-route',
    name: 'RouteTest',
    component: () => import('@/pages/test_page/RouteTest.vue'),
    meta: {
      title: '路由测试页面'
    }
  }
]

export default routes
