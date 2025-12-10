<script lang="ts" setup>
import {computed} from 'vue'
import {useRoute} from 'vue-router'
import {ConfigProvider, theme} from 'ant-design-vue'
import {BasicLayout} from '@/layouts'
import CommonLayout from '@/layouts/CommonLayout.vue'
import TeacherLayout from '@/layouts/TeacherLayout.vue'
import StudentLayout from '@/layouts/StudentLayout.vue'
import AdminLayout from '@/layouts/AdminLayout.vue'
import {useTheme} from '@/composables/useTheme'

// 使用主题管理
const {isDark} = useTheme()

// 获取当前路由
const route = useRoute()

// 使用计算属性获取当前路径
const currentPath = computed(() => {
  return route.path
})

// 判断是否为公共页面(登录/注册/404/403)
const isPublicPage = computed(() => {
  return currentPath.value.startsWith('/login') ||
      currentPath.value.startsWith('/register') ||
      currentPath.value === '/404' ||
      currentPath.value === '/403'
})

// 判断是否为教师页面
const isTeacherPage = computed(() => {
  return currentPath.value.startsWith('/teacher')
})

// 判断是否为学生页面
const isStudentPage = computed(() => {
  return currentPath.value.startsWith('/student')
})

// 判断是否为管理员页面
const isAdminPage = computed(() => {
  return currentPath.value.startsWith('/admin')
})

// Ant Design Vue 主题配置
const antdTheme = computed(() => ({
  algorithm: isDark.value ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    wireframe: false,
  },
}))
</script>

<template>
  <ConfigProvider :theme="antdTheme">
    <router-view v-if="isNoLayoutPage ?? false" />
    <CommonLayout v-if="isPublicPage ?? false"/>
    <TeacherLayout v-else-if="isTeacherPage ?? false"/>
    <StudentLayout v-else-if="isStudentPage ?? false"/>
    <AdminLayout v-else-if="isAdminPage ?? false"/>
    <BasicLayout v-else/>
  </ConfigProvider>
</template>

<style>
/* 全局样式已在 main.ts 中引入 */
</style>
