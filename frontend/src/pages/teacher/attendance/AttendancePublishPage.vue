<template>
  <div class="attendance-publish-page">
    <div class="page-header">
      <h1 class="page-title">考勤管理</h1>
      <p class="page-subtitle">创建和管理考勤任务</p>
    </div>

    <div class="page-content">
      <AttendancePublish
        @success="handlePublishSuccess"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { message } from 'ant-design-vue'
import AttendancePublish from './components/AttendancePublish.vue'

const handlePublishSuccess = (data: any) => {
  message.success('考勤发布成功！')
  console.log('Published attendance:', data)
  // 可以在这里添加刷新列表或其他逻辑
}
</script>

<style scoped>
.attendance-publish-page {
  background: var(--background-color);
  min-height: 100vh;
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: var(--text-color);
  margin: 0 0 8px 0;
}

.page-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
  margin: 0;
}

.page-content {
  max-width: 1400px;
  margin: 0 auto;
}
</style>
