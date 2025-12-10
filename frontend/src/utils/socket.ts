/**
 * WebSocket服务类
 * 处理课堂互动的实时通信
 */
import { io, Socket } from 'socket.io-client'

// WebSocket事件类型定义
export interface SocketEvents {
  // 连接事件
  connected: (data: { message: string; client_id: string }) => void
  joined_course: (data: { message: string; room: string; course_id: number }) => void
  left_course: (data: { message: string; room: string; course_id: number }) => void
  user_joined: (data: { user_id: number; user_name: string; message: string }) => void
  user_left: (data: { user_id: number; user_name: string; message: string }) => void

  // 投票事件
  new_poll: (data: { message: string; poll: any }) => void
  poll_results_updated: (data: { poll_id: number; results: any; message: string }) => void
  poll_ended: (data: { poll_id: number; message: string }) => void

  // 提问事件
  new_question: (data: { message: string; question: any }) => void
  new_answer: (data: { question_id: number; answer: any; message: string }) => void
  answer_was_accepted: (data: { question_id: number; answer_id: number; message: string }) => void

  // 弹幕事件
  new_barrage: (data: { barrage: any; message: string }) => void
  barrage_removed: (data: { barrage_id: number; message: string }) => void

  // 点赞事件
  question_likes_updated: (data: { question_id: number; like_count: number }) => void
  answer_likes_updated: (data: { answer_id: number; like_count: number }) => void

  // 错误事件
  error: (data: { message: string }) => void

  // 调试事件
  pong: (data: { message: string; timestamp: string }) => void
  room_info: (data: { room: string; client_rooms: string[]; client_id: string }) => void
}

class SocketService {
  private socket: Socket | null = null
  private currentCourseId: number | null = null
  private currentUserId: number | null = null
  private currentUserName: string | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000 // 1秒
  private isManualDisconnect = false

  // 事件监听器存储
  private eventListeners: Map<string, Set<Function>> = new Map()

  /**
   * 获取WebSocket连接状态
   */
  get isConnected(): boolean {
    return this.socket?.connected || false
  }

  /**
   * 获取当前课程ID
   */
  get courseId(): number | null {
    return this.currentCourseId
  }

  /**
   * 连接WebSocket服务器
   */
  connect(url: string = 'http://localhost:5030'): Promise<void> {
    return new Promise((resolve, reject) => {
      if (this.socket?.connected) {
        console.log('[WebSocket] 已经连接')
        resolve()
        return
      }

      console.log('[WebSocket] 正在连接...', url)

      this.socket = io(url, {
        transports: ['websocket'],
        autoConnect: true,
        reconnection: true,
        reconnectionAttempts: this.maxReconnectAttempts,
        reconnectionDelay: this.reconnectDelay,
      })

      // 连接成功
      this.socket.on('connect', () => {
        console.log('[WebSocket] 连接成功', this.socket?.id)
        this.reconnectAttempts = 0
        this.isManualDisconnect = false

        // 如果之前在某个课程中，自动重新加入
        if (this.currentCourseId && this.currentUserId) {
          this.joinCourse(this.currentCourseId, this.currentUserId, this.currentUserName || undefined)
        }

        resolve()
      })

      // 连接成功事件
      this.socket.on('connected', (data: any) => {
        console.log('[WebSocket] 收到连接确认:', data)
        this.emit('connected', data)
      })

      // 连接错误
      this.socket.on('connect_error', (error: Error) => {
        console.error('[WebSocket] 连接错误:', error.message)
        this.reconnectAttempts++

        if (this.reconnectAttempts >= this.maxReconnectAttempts) {
          console.error('[WebSocket] 达到最大重连次数，停止重连')
          reject(new Error('WebSocket连接失败'))
        }
      })

      // 断开连接
      this.socket.on('disconnect', (reason: string) => {
        console.log('[WebSocket] 断开连接:', reason)

        if (!this.isManualDisconnect && reason === 'io server disconnect') {
          // 服务器主动断开，尝试重连
          console.log('[WebSocket] 服务器断开连接，尝试重连...')
          this.socket?.connect()
        }
      })

      // 错误处理
      this.socket.on('error', (error: any) => {
        console.error('[WebSocket] 错误:', error)
        this.emit('error', error)
      })

      // 注册所有事件监听器
      this.registerAllEventListeners()
    })
  }

  /**
   * 断开WebSocket连接
   */
  disconnect(): void {
    if (this.socket) {
      console.log('[WebSocket] 主动断开连接')
      this.isManualDisconnect = true

      // 如果在课程中，先离开
      if (this.currentCourseId && this.currentUserId) {
        this.leaveCourse(this.currentCourseId, this.currentUserId, this.currentUserName || undefined)
      }

      this.socket.disconnect()
      this.socket = null
      this.currentCourseId = null
      this.currentUserId = null
      this.currentUserName = null
    }
  }

  /**
   * 注册所有事件监听器
   */
  private registerAllEventListeners(): void {
    if (!this.socket) return

    // 房间事件
    this.socket.on('joined_course', (data: any) => this.emit('joined_course', data))
    this.socket.on('left_course', (data: any) => this.emit('left_course', data))
    this.socket.on('user_joined', (data: any) => this.emit('user_joined', data))
    this.socket.on('user_left', (data: any) => this.emit('user_left', data))

    // 投票事件
    this.socket.on('new_poll', (data: any) => this.emit('new_poll', data))
    this.socket.on('poll_results_updated', (data: any) => this.emit('poll_results_updated', data))
    this.socket.on('poll_ended', (data: any) => this.emit('poll_ended', data))

    // 提问事件
    this.socket.on('new_question', (data: any) => this.emit('new_question', data))
    this.socket.on('new_answer', (data: any) => this.emit('new_answer', data))
    this.socket.on('answer_was_accepted', (data: any) => this.emit('answer_was_accepted', data))

    // 弹幕事件
    this.socket.on('new_barrage', (data: any) => this.emit('new_barrage', data))
    this.socket.on('barrage_removed', (data: any) => this.emit('barrage_removed', data))

    // 点赞事件
    this.socket.on('question_likes_updated', (data: any) => this.emit('question_likes_updated', data))
    this.socket.on('answer_likes_updated', (data: any) => this.emit('answer_likes_updated', data))

    // 调试事件
    this.socket.on('pong', (data: any) => this.emit('pong', data))
    this.socket.on('room_info', (data: any) => this.emit('room_info', data))
  }

  /**
   * 加入课程房间
   */
  joinCourse(courseId: number, userId: number, userName?: string): void {
    if (!this.socket?.connected) {
      console.error('[WebSocket] 未连接，无法加入课程')
      return
    }

    console.log(`[WebSocket] 加入课程房间: ${courseId}`)

    this.currentCourseId = courseId
    this.currentUserId = userId
    this.currentUserName = userName || `User${userId}`

    this.socket.emit('join_course', {
      course_id: courseId,
      user_id: userId,
      user_name: this.currentUserName,
    })
  }

  /**
   * 离开课程房间
   */
  leaveCourse(courseId: number, userId: number, userName?: string): void {
    if (!this.socket?.connected) {
      console.error('[WebSocket] 未连接')
      return
    }

    console.log(`[WebSocket] 离开课程房间: ${courseId}`)

    this.socket.emit('leave_course', {
      course_id: courseId,
      user_id: userId,
      user_name: userName || this.currentUserName || `User${userId}`,
    })

    this.currentCourseId = null
    this.currentUserId = null
    this.currentUserName = null
  }

  // ==================== 投票相关方法 ====================

  /**
   * 通知投票创建
   */
  notifyPollCreated(courseId: number, poll: any): void {
    this.socket?.emit('poll_created', {
      course_id: courseId,
      poll,
    })
  }

  /**
   * 通知投票响应
   */
  notifyPollVoted(courseId: number, pollId: number, results: any): void {
    this.socket?.emit('poll_voted', {
      course_id: courseId,
      poll_id: pollId,
      results,
    })
  }

  /**
   * 通知投票关闭
   */
  notifyPollClosed(courseId: number, pollId: number): void {
    this.socket?.emit('poll_closed', {
      course_id: courseId,
      poll_id: pollId,
    })
  }

  // ==================== 提问相关方法 ====================

  /**
   * 通知问题创建
   */
  notifyQuestionCreated(courseId: number, question: any): void {
    this.socket?.emit('question_created', {
      course_id: courseId,
      question,
    })
  }

  /**
   * 通知答案提交
   */
  notifyAnswerSubmitted(courseId: number, questionId: number, answer: any): void {
    this.socket?.emit('answer_submitted', {
      course_id: courseId,
      question_id: questionId,
      answer,
    })
  }

  /**
   * 通知答案采纳
   */
  notifyAnswerAccepted(courseId: number, questionId: number, answerId: number): void {
    this.socket?.emit('answer_accepted', {
      course_id: courseId,
      question_id: questionId,
      answer_id: answerId,
    })
  }

  // ==================== 弹幕相关方法 ====================

  /**
   * 发送弹幕
   */
  sendBarrage(courseId: number, barrage: any): void {
    this.socket?.emit('barrage_sent', {
      course_id: courseId,
      barrage,
    })
  }

  /**
   * 通知弹幕删除
   */
  notifyBarrageDeleted(courseId: number, barrageId: number): void {
    this.socket?.emit('barrage_deleted', {
      course_id: courseId,
      barrage_id: barrageId,
    })
  }

  // ==================== 点赞相关方法 ====================

  /**
   * 通知问题点赞
   */
  notifyQuestionLiked(courseId: number, questionId: number, likeCount: number): void {
    this.socket?.emit('question_liked', {
      course_id: courseId,
      question_id: questionId,
      like_count: likeCount,
    })
  }

  /**
   * 通知回答点赞
   */
  notifyAnswerLiked(courseId: number, answerId: number, likeCount: number): void {
    this.socket?.emit('answer_liked', {
      course_id: courseId,
      answer_id: answerId,
      like_count: likeCount,
    })
  }

  // ==================== 调试方法 ====================

  /**
   * 发送心跳
   */
  ping(): void {
    this.socket?.emit('ping')
  }

  /**
   * 获取房间信息
   */
  getRoomInfo(courseId: number): void {
    this.socket?.emit('get_room_info', {
      course_id: courseId,
    })
  }

  // ==================== 事件监听管理 ====================

  /**
   * 监听事件
   */
  on<K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]): void {
    if (!this.eventListeners.has(event)) {
      this.eventListeners.set(event, new Set())
    }
    this.eventListeners.get(event)!.add(callback)
  }

  /**
   * 取消监听事件
   */
  off<K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.delete(callback)
    }
  }

  /**
   * 触发事件
   */
  private emit<K extends keyof SocketEvents>(event: K, data: any): void {
    const listeners = this.eventListeners.get(event)
    if (listeners) {
      listeners.forEach((callback) => {
        try {
          callback(data)
        } catch (error) {
          console.error(`[WebSocket] 事件处理错误 (${event}):`, error)
        }
      })
    }
  }

  /**
   * 清除所有事件监听器
   */
  clearAllListeners(): void {
    this.eventListeners.clear()
  }

  /**
   * 清除指定事件的所有监听器
   */
  clearListeners<K extends keyof SocketEvents>(event: K): void {
    this.eventListeners.delete(event)
  }
}

// 导出单例
export const socketService = new SocketService()

// 默认导出
export default socketService
