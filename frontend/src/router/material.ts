import type { RouteRecordRaw } from 'vue-router'

const materialRoutes: RouteRecordRaw[] = [
  {
    path: '/teacher/materials',
    name: 'MaterialCenter',
    component: () => import('@/pages/teacher/materials/MaterialCenter.vue'),
    meta: {
      title: '资料中心',
      requiresAuth: true,
      roles: ['teacher']
    }
  },
  {
    path: '/teacher/materials/upload',
    name: 'MaterialUpload',
    component: () => import('@/pages/teacher/materials/MaterialUpload.vue'),
    meta: {
      title: '上传资料',
      requiresAuth: true,
      roles: ['teacher']
    }
  },
  {
    path: '/teacher/materials/my',
    name: 'MyMaterials',
    component: () => import('@/pages/teacher/materials/MyMaterials.vue'),
    meta: {
      title: '我的资料',
      requiresAuth: true,
      roles: ['teacher']
    }
  },
  {
    path: '/teacher/material/:id',
    name: 'MaterialDetail',
    component: () => import('@/pages/teacher/materials/MaterialDetail.vue'),
    meta: {
      title: '资料详情',
      requiresAuth: true,
      roles: ['teacher']
    }
  }
]

export default materialRoutes
