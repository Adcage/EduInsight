import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
  {
    path: '/teacher/grades/list',
    name: 'GradeList',
    component: () => import('@/pages/teacher/grades/GradeList.vue'),
    meta: { title: '成绩列表', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/grades/input/add',
    name: 'GradeAdd',
    component: () => import('@/pages/teacher/grades/input/GradeAdd.vue'),
    meta: { title: '单条录入', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/grades/input/import',
    name: 'GradeImport',
    component: () => import('@/pages/teacher/grades/input/GradeImport.vue'),
    meta: { title: '批量导入', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/grades/statistics',
    name: 'GradeStatistics',
    component: () => import('@/pages/teacher/grades/Statistics.vue'),
    meta: { title: '统计分析', requiresAuth: true, role: 'teacher' }
  },
  {
    path: '/teacher/grades/warnings',
    name: 'GradeWarnings',
    component: () => import('@/pages/teacher/grades/Warnings.vue'),
    meta: { title: '学情预警', requiresAuth: true, role: 'teacher' }
  }
]

export default routes
