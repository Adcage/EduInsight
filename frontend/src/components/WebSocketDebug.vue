<template>
  <div v-if="showDebug" class="websocket-debug">
    <div class="debug-header" @click="toggleExpand">
      <span class="debug-title">🔌 WebSocket</span>
      <span :class="['status-dot', { connected: isConnected }]"></span>
      <span class="status-text">{{ statusText }}</span>
      <span class="toggle-icon">{{ expanded ? '▼' : '▶' }}</span>
    </div>

    <div v-if="expanded" class="debug-content">
      <div class="debug-item">
        <strong>连接状态:</strong> {{ isConnected ? '已连接' : '未连接' }}
      </div>
      <div class="debug-item">
        <strong>认证方式:</strong> Session Cookie
      </div>
      <div class="debug-item">
        <strong>接收事件数:</strong> {{ eventCount }}
      </div>
      <div class="debug-actions">
        <button class="debug-btn" @click="reconnect">重新连接</button>
        <button class="debug-btn" @click="clearLog">清空日志</button>
      </div>
      <div class="debug-log">
        <div v-for="(log, index) in logs" :key="index" class="log-item">
          {{ log }}
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, onUnmounted, ref} from 'vue'
import {useWebSocketStore} from '@/stores/websocket'

const wsStore = useWebSocketStore()
const showDebug = ref(true)
const expanded = ref(false)
const eventCount = ref(0)
const logs = ref<string[]>([])

const isConnected = computed(() => wsStore.isConnected)
const statusText = computed(() => isConnected.value ? '已连接' : '未连接')

const toggleExpand = () => {
  expanded.value = !expanded.value
}

const addLog = (message: string) => {
  const time = new Date().toLocaleTimeString()
  logs.value.unshift(`[${time}] ${message}`)
  if (logs.value.length > 20) {
    logs.value.pop()
  }
}

const reconnect = () => {
  addLog('手动重新连接...')
  wsStore.disconnect()
  setTimeout(() => {
    wsStore.connect()
  }, 1000)
}

const clearLog = () => {
  logs.value = []
  eventCount.value = 0
}

// 监听WebSocket事件
const handleEvent = (eventName: string) => {
  return (data: any) => {
    eventCount.value++
    addLog(`收到事件: ${eventName}`)
    console.log(`[WebSocket Debug] ${eventName}:`, data)
  }
}

onMounted(() => {
  addLog('调试组件已加载')

  // 监听所有WebSocket事件
  wsStore.on('attendance_created', handleEvent('attendance_created'))
  wsStore.on('attendance_updated', handleEvent('attendance_updated'))
  wsStore.on('check_in_success', handleEvent('check_in_success'))
  wsStore.on('student_checked_in', handleEvent('student_checked_in'))
})

onUnmounted(() => {
  // 清理事件监听
  wsStore.off('attendance_created', handleEvent('attendance_created'))
  wsStore.off('attendance_updated', handleEvent('attendance_updated'))
  wsStore.off('check_in_success', handleEvent('check_in_success'))
  wsStore.off('student_checked_in', handleEvent('student_checked_in'))
})
</script>

<style lang="scss" scoped>
.websocket-debug {
  position: fixed;
  bottom: 20px;
  right: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  z-index: 9999;
  min-width: 300px;
  max-width: 400px;
}

.debug-header {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  cursor: pointer;
  user-select: none;
  border-bottom: 1px solid #f0f0f0;

  &:hover {
    background: #fafafa;
  }
}

.debug-title {
  font-weight: 600;
  font-size: 14px;
}

.status-dot {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  background: #ccc;

  &.connected {
    background: #52c41a;
    animation: pulse 2s infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

.status-text {
  font-size: 12px;
  color: #666;
  flex: 1;
}

.toggle-icon {
  font-size: 12px;
  color: #999;
}

.debug-content {
  padding: 12px 16px;
  max-height: 400px;
  overflow-y: auto;
}

.debug-item {
  margin-bottom: 8px;
  font-size: 13px;

  strong {
    color: #333;
  }
}

.debug-actions {
  display: flex;
  gap: 8px;
  margin: 12px 0;
}

.debug-btn {
  flex: 1;
  padding: 6px 12px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  background: white;
  cursor: pointer;
  font-size: 12px;

  &:hover {
    border-color: #40a9ff;
    color: #40a9ff;
  }
}

.debug-log {
  margin-top: 12px;
  padding: 8px;
  background: #f5f5f5;
  border-radius: 4px;
  max-height: 200px;
  overflow-y: auto;
}

.log-item {
  font-size: 11px;
  font-family: monospace;
  color: #666;
  padding: 2px 0;
  border-bottom: 1px solid #e8e8e8;

  &:last-child {
    border-bottom: none;
  }
}
</style>
