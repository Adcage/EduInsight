import type {RouteRecordRaw} from 'vue-router'

/**
 * 管理员路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const adminRoutes: RouteRecordRaw[] = [
    // 个人资料页面 - 所有已认证用户可访问
    {
        path: '/admin/profile',
        name: 'AdminProfile',
        component: () => import('@/pages/shared/profile/ProfilePage.vue'),
        meta: {
            title: '个人资料',
            requiresAuth: true,
            roles: ['admin']
        }
    },
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
    // 控制台

    // 课程管理

    // 班级管理

    // 系统设置
]

export default adminRoutes
