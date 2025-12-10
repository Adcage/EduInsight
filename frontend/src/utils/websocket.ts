/**
 * WebSocket连接管理
 * 基于Socket.IO实现实时通信
 */
import { io, Socket } from 'socket.io-client'
import { message } from 'ant-design-vue'

const WS_URL = 'http://localhost:5030'

class WebSocketManager {
  private socket: Socket | null = null
  private token: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private eventHandlers: Map<string, Set<Function>> = new Map()

  /**
   * 连接WebSocket
   */
  connect(token?: string): void {
    if (this.socket?.connected) {
      console.log('[WebSocket] Already connected')
      return
    }

    this.token = token || null
    this.reconnectAttempts = 0

    console.log('[WebSocket] Creating connection to', WS_URL)

    // 创建Socket.IO连接
    // 使用withCredentials确保发送cookie（session认证）
    this.socket = io(WS_URL, {
      transports: ['websocket', 'polling'],
      withCredentials: true,  // 重要：发送cookie
      query: token ? { token } : {},  // token可选
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: this.maxReconnectAttempts
    })

    this.setupEventListeners()
  }

  /**
   * 设置事件监听器
   */
  private setupEventListeners(): void {
    if (!this.socket) return

    // 连接成功
    this.socket.on('connect', () => {
      console.log('[WebSocket] Connected successfully')
      this.reconnectAttempts = 0
      // message.success('实时连接已建立')  // 注释掉以减少干扰
    })

    // 连接成功响应
    this.socket.on('connected', (data) => {
      console.log('WebSocket authenticated:', data)
    })

    // 连接错误
    this.socket.on('connect_error', (error) => {
      console.error('[WebSocket] Connection error:', error)
      console.error('[WebSocket] Error message:', error.message)
      console.error('[WebSocket] Error type:', error.type)
      console.error('[WebSocket] Error description:', error.description)
      this.reconnectAttempts++
      
      if (this.reconnectAttempts >= this.maxReconnectAttempts) {
        message.error('实时连接失败，请刷新页面重试')
      } else {
        console.log(`[WebSocket] 重连尝试 ${this.reconnectAttempts}/${this.maxReconnectAttempts}`)
      }
    })

    // 断开连接
    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      if (reason === 'io server disconnect') {
        // 服务器主动断开，需要重新连接
        this.socket?.connect()
      }
    })

    // 错误处理
    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
      message.error(error.message || '实时连接出错')
    })

    // 考勤相关事件
    this.socket.on('attendance_created', (data) => {
      console.log('[WebSocket] Received attendance_created event:', data)
      this.emit('attendance_created', data)
    })

    this.socket.on('attendance_updated', (data) => {
      console.log('Attendance updated:', data)
      this.emit('attendance_updated', data)
    })

    this.socket.on('attendance_started', (data) => {
      console.log('Attendance started:', data)
      this.emit('attendance_started', data)
    })

    this.socket.on('attendance_ended', (data) => {
      console.log('Attendance ended:', data)
      this.emit('attendance_ended', data)
    })

    this.socket.on('check_in_success', (data) => {
      console.log('Check in success:', data)
      this.emit('check_in_success', data)
    })

    this.socket.on('student_checked_in', (data) => {
      console.log('Student checked in:', data)
      this.emit('student_checked_in', data)
    })

    this.socket.on('qrcode_refreshed', (data) => {
      console.log('QR code refreshed:', data)
      this.emit('qrcode_refreshed', data)
    })

    this.socket.on('joined_attendance', (data) => {
      console.log('Joined attendance room:', data)
    })
  }

  /**
   * 断开连接
   */
  disconnect(): void {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
      this.token = null
      this.eventHandlers.clear()
      console.log('WebSocket disconnected manually')
    }
  }

  /**
   * 加入考勤房间
   */
  joinAttendance(attendanceId: number): void {
    if (!this.socket?.connected) {
      console.warn('WebSocket not connected')
      return
    }

    this.socket.emit('join_attendance', { attendance_id: attendanceId })
  }

  /**
   * 离开考勤房间
   */
  leaveAttendance(attendanceId: number): void {
    if (!this.socket?.connected) {
      return
    }

    this.socket.emit('leave_attendance', { attendance_id: attendanceId })
  }

  /**
   * 注册事件处理器
   */
  on(event: string, handler: Function): void {
    if (!this.eventHandlers.has(event)) {
      this.eventHandlers.set(event, new Set())
    }
    this.eventHandlers.get(event)!.add(handler)
  }

  /**
   * 移除事件处理器
   */
  off(event: string, handler: Function): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.delete(handler)
    }
  }

  /**
   * 触发事件处理器
   */
  private emit(event: string, data: any): void {
    const handlers = this.eventHandlers.get(event)
    if (handlers) {
      handlers.forEach(handler => {
        try {
          handler(data)
        } catch (error) {
          console.error(`Error in event handler for ${event}:`, error)
        }
      })
    }
  }

  /**
   * 检查连接状态
   */
  isConnected(): boolean {
    return this.socket?.connected || false
  }

  /**
   * 获取Socket实例
   */
  getSocket(): Socket | null {
    return this.socket
  }
}

// 导出单例
export const websocketManager = new WebSocketManager()

// 导出类型
export type { Socket }
