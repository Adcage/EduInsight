import type {RouteRecordRaw} from 'vue-router'

/**
 * 学生路由配置
 * 扁平路由结构,布局由 App.vue 根据路径前缀控制
 */
const studentRoutes: RouteRecordRaw[] = [
    // 个人资料页面 - 所有已认证用户可访问
    {
        path: '/student/profile',
        name: 'StudentProfile',
        component: () => import('@/pages/shared/profile/ProfilePage.vue'),
        meta: {
            title: '个人资料',
            requiresAuth: true,
            roles: ['student']
        }
    },
    // 学生资料中心
    {
        path: '/student/materials',
        name: 'StudentMaterialCenter',
        component: () => import('@/pages/student/materials/MaterialCenter.vue'),
        meta: {
            title: '资料中心',
            requiresAuth: true,
            roles: ['student']
        }
    },
    {
        path: '/student/materials/:id',
        name: 'StudentMaterialDetail',
        component: () => import('@/pages/student/materials/MaterialDetail.vue'),
        meta: {
            title: '资料详情',
            requiresAuth: true,
            roles: ['student']
        }
    },

    // 学生首页

    // 我的课程

    // 我的考勤

    // 我的成绩

    // 课堂互动

    // 学生人脸照片上传
    {
        path: '/student/face-upload',
        name: 'StudentFaceUpload',
        component: () => import('@/pages/student/FaceUpload.vue'),
        meta: {
            title: '上传人脸照片',
            requiresAuth: true,
            role: 'student'
        }
    },
    // 二维码人脸验证签到
    {
        path: '/student/qr-face-verification',
        name: 'QRCodeFaceVerification',
        component: () => import('@/pages/student/attendance/QRCodeFaceVerification.vue'),
        meta: {
            title: '二维码签到',
            requiresAuth: false  // 扫码前可能未登录
        }
    }
]

export default studentRoutes
