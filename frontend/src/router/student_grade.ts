import type {RouteRecordRaw} from 'vue-router'

const studentGradeRoutes: RouteRecordRaw[] = [
    {
        path: '/student/grades',
        name: 'StudentGrades',
        redirect: '/student/grades/my-grades',
        meta: {
            title: '成绩管理',
            requiresAuth: true,
            roles: ['student']
        },
        children: [
            {
                path: 'my-grades',
                name: 'StudentMyGrades',
                component: () => import('@/pages/student/grades/MyGrades.vue'),
                meta: {
                    title: '我的成绩',
                    requiresAuth: true,
                    roles: ['student']
                }
            },
            {
                path: 'analysis',
                name: 'StudentGradesAnalysis',
                component: () => import('@/pages/student/grades/MyGradesAnalysis.vue'),
                meta: {
                    title: '个人成绩分析',
                    requiresAuth: true,
                    roles: ['student']
                }
            },
            {
                path: 'warnings',
                name: 'StudentWarnings',
                component: () => import('@/pages/student/grades/MyWarnings.vue'),
                meta: {
                    title: '预警与通知',
                    requiresAuth: true,
                    roles: ['student']
                }
            }
        ]
    }
]

export default studentGradeRoutes
