import type {RouteRecordRaw} from 'vue-router'

/**
 * 课堂互动模块路由配置
 * 包含投票、提问、弹幕三大功能
 */
const interactionRoutes: RouteRecordRaw[] = [
    // ==================== 教师端路由 ====================
    {
        path: '/teacher/interaction/poll',
        name: 'TeacherPoll',
        component: () => import('@/pages/teacher/classroom-interaction/PollPage.vue'),
        meta: {
            title: '投票管理',
            requiresAuth: true,
            roles: ['teacher']
        }
    },
    {
        path: '/teacher/interaction/question',
        name: 'TeacherQuestion',
        component: () => import('@/pages/teacher/classroom-interaction/QuestionPage.vue'),
        meta: {
            title: '提问管理',
            requiresAuth: true,
            roles: ['teacher']
        }
    },
    {
        path: '/teacher/interaction/barrage',
        name: 'TeacherBarrage',
        component: () => import('@/pages/teacher/classroom-interaction/BarragePage.vue'),
        meta: {
            title: '弹幕管理',
            requiresAuth: true,
            roles: ['teacher']
        }
    },

    // ==================== 学生端路由 ====================
    {
        path: '/student/interaction/poll',
        name: 'StudentPoll',
        component: () => import('@/pages/student/classroom-interaction/PollPage.vue'),
        meta: {
            title: '投票参与',
            requiresAuth: true,
            roles: ['student']
        }
    },
    {
        path: '/student/interaction/question',
        name: 'StudentQuestion',
        component: () => import('@/pages/student/classroom-interaction/QuestionPage.vue'),
        meta: {
            title: '提问回答',
            requiresAuth: true,
            roles: ['student']
        }
    },
    {
        path: '/student/interaction/barrage',
        name: 'StudentBarrage',
        component: () => import('@/pages/student/classroom-interaction/BarragePage.vue'),
        meta: {
            title: '弹幕互动',
            requiresAuth: true,
            roles: ['student']
        }
    }
]

export default interactionRoutes
