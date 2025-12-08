<template>
  <div style="padding: 40px; text-align: center;">
    <h1>✅ 路由测试成功!</h1>
    <p>当前路径: {{ $route.path }}</p>
    <p>当前路由名称: {{ $route.name }}</p>
    
    <a-space direction="vertical" size="large" style="margin-top: 40px;">
      <a-button type="primary" size="large" @click="$router.push('/teacher/grades/list')">
        跳转到成绩列表
      </a-button>
      <a-button size="large" @click="$router.push('/teacher/grades/input/add')">
        跳转到成绩录入
      </a-button>
      <a-button size="large" @click="$router.push('/teacher/grades/input/import')">
        跳转到批量导入
      </a-button>
    </a-space>
    
    <div style="margin-top: 40px;">
      <h3>所有已注册的路由:</h3>
      <pre style="text-align: left; background: #f5f5f5; padding: 20px; border-radius: 4px;">
{{ JSON.stringify($router.getRoutes().map(r => ({ path: r.path, name: r.name })), null, 2) }}
      </pre>
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted } from 'vue'

onMounted(() => {
  console.log('🔍 所有路由:', router.getRoutes())
})
</script>
