/**
 * WebSocket状态管理
 */
import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import { websocketManager } from '@/utils/websocket'

export const useWebSocketStore = defineStore('websocket', () => {
  // 状态
  const connected = ref(false)
  const reconnecting = ref(false)

  // 计算属性
  const isConnected = computed(() => connected.value)

  /**
   * 初始化WebSocket连接
   */
  const connect = () => {
    console.log('[WebSocket Store] 开始连接...')
    console.log('[WebSocket Store] 使用session认证（cookie）')

    if (websocketManager.isConnected()) {
      console.log('[WebSocket Store] WebSocket already connected')
      connected.value = true
      return
    }

    try {
      console.log('[WebSocket Store] 调用 websocketManager.connect()')
      // 不需要传递token，使用session cookie认证
      websocketManager.connect()
      
      // 监听连接状态变化
      websocketManager.on('connect', () => {
        console.log('[WebSocket Store] 连接成功事件触发')
        connected.value = true
        reconnecting.value = false
      })

      websocketManager.on('disconnect', () => {
        console.log('[WebSocket Store] 断开连接事件触发')
        connected.value = false
      })

      websocketManager.on('reconnecting', () => {
        console.log('[WebSocket Store] 重连中...')
        reconnecting.value = true
      })
    } catch (error) {
      console.error('[WebSocket Store] Failed to connect WebSocket:', error)
      connected.value = false
    }
  }

  /**
   * 断开WebSocket连接
   */
  const disconnect = () => {
    websocketManager.disconnect()
    connected.value = false
    reconnecting.value = false
  }

  /**
   * 加入考勤房间
   */
  const joinAttendance = (attendanceId: number) => {
    if (!connected.value) {
      console.warn('WebSocket not connected, cannot join attendance room')
      return
    }
    websocketManager.joinAttendance(attendanceId)
  }

  /**
   * 离开考勤房间
   */
  const leaveAttendance = (attendanceId: number) => {
    if (!connected.value) {
      return
    }
    websocketManager.leaveAttendance(attendanceId)
  }

  /**
   * 注册事件监听器
   */
  const on = (event: string, handler: Function) => {
    websocketManager.on(event, handler)
  }

  /**
   * 移除事件监听器
   */
  const off = (event: string, handler: Function) => {
    websocketManager.off(event, handler)
  }

  return {
    // 状态
    connected,
    reconnecting,
    isConnected,

    // 方法
    connect,
    disconnect,
    joinAttendance,
    leaveAttendance,
    on,
    off
  }
})
