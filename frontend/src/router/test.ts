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
]

export default routes
