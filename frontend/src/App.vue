<script setup lang="ts">
import { computed } from 'vue'
import { ConfigProvider, theme } from 'ant-design-vue'
import { BasicLayout } from '@/layouts'
import { useTheme } from '@/composables/useTheme'
import { authApiProfileIntUserIdGet } from './api/authController'
import { userApiHealthGet } from './api/userController'

// 使用主题管理
const { isDark } = useTheme()

// Ant Design Vue 主题配置
const antdTheme = computed(() => ({
  algorithm: isDark.value ? theme.darkAlgorithm : theme.defaultAlgorithm,
  token: {
    colorPrimary: '#1890ff',
    borderRadius: 6,
    wireframe: false,
  },
}))

userApiHealthGet().then((res) => {
  console.log(res);
  
})
</script>

<template>
  <ConfigProvider :theme="antdTheme">
    <BasicLayout />
  </ConfigProvider>
</template>

<style>
/* 全局样式已在 main.ts 中引入 */
</style>
