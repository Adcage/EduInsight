import type {RouteRecordRaw} from 'vue-router'

/**
 * 教师路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const teacherRoutes: RouteRecordRaw[] = [
    // 个人资料页面 - 所有已认证用户可访问
    {
        path: '/teacher/profile',
        name: 'TeacherProfile',
        component: () => import('@/pages/shared/profile/ProfilePage.vue'),
        meta: {
            title: '个人资料',
            requiresAuth: true,
            roles: ['teacher']
        }
    },
    {
        path: '/teacher/materials',
        name: 'TeacherMaterialCenter',
        component: () => import('@/pages/teacher/materials/MaterialCenter.vue'),
        meta: {
            title: '资料中心',
            requiresAuth: true,
            roles: ['teacher']
        }
    },
    {
        path: '/teacher/materials/upload',
        name: 'TeacherMaterialUpload',
        component: () => import('@/pages/teacher/materials/MaterialUpload.vue'),
        meta: {
            title: '上传资料',
            requiresAuth: true,
            roles: ['teacher']
        }
    },
    {
        path: '/teacher/materials/my',
        name: 'TeacherMyMaterials',
        component: () => import('@/pages/teacher/materials/MyMaterials.vue'),
        meta: {
            title: '我的资料',
            requiresAuth: true,
            roles: ['teacher']
        }
    },
    {
        path: '/teacher/material/:id',
        name: 'TeacherMaterialDetail',
        component: () => import('@/pages/teacher/materials/MaterialDetail.vue'),
        meta: {
            title: '资料详情',
            requiresAuth: true,
            roles: ['teacher']
        }
    }

    // 教师首页

    // 课程管理

    // 考勤管理

    // 成绩管理

    // 课堂互动

    // 学情分析

]

export default teacherRoutes
