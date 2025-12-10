import type { RouteRecordRaw } from 'vue-router'

const routes: Array<RouteRecordRaw> = [
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

export default routes
