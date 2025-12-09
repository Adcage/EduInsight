import type { RouteRecordRaw } from 'vue-router'

/**
 * 教师路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const teacherRoutes: RouteRecordRaw[] = [
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
  // 后续可以添加其他教师页面路由：
  // /teacher/dashboard - 教师首页
  // /teacher/courses - 课程管理
  // /teacher/attendance - 考勤管理
  // /teacher/grades - 成绩管理
  // /teacher/interaction - 课堂互动
  // /teacher/analysis - 学情分析
]

export default teacherRoutes
