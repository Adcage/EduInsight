/**
 * WebSocket Composable
 * 在Vue组件中使用WebSocket的便捷方法
 */
import type {Ref} from 'vue'
import {onMounted, onUnmounted, ref} from 'vue'
import type {SocketEvents} from '@/utils/socket'
import socketService from '@/utils/socket'

export interface UseSocketOptions {
    /** 是否自动连接 */
    autoConnect?: boolean
    /** WebSocket服务器URL */
    url?: string
    /** 课程ID（自动加入课程） */
    courseId?: number
    /** 用户ID */
    userId?: number
    /** 用户名 */
    userName?: string
}

export function useSocket(options: UseSocketOptions = {}) {
    const {
        autoConnect = true,
        url = 'http://localhost:5030',
        courseId,
        userId,
        userName,
    } = options

    // 连接状态
    const isConnected: Ref<boolean> = ref(false)
    const isConnecting: Ref<boolean> = ref(false)
    const error: Ref<string | null> = ref(null)

    /**
     * 连接WebSocket
     */
    const connect = async () => {
        if (isConnected.value || isConnecting.value) {
            return
        }

        isConnecting.value = true
        error.value = null

        try {
            await socketService.connect(url)
            isConnected.value = true

            // 如果提供了课程ID，自动加入课程
            if (courseId && userId) {
                socketService.joinCourse(courseId, userId, userName)
            }
        } catch (err: any) {
            error.value = err.message || 'WebSocket连接失败'
            console.error('[useSocket] 连接失败:', err)
        } finally {
            isConnecting.value = false
        }
    }

    /**
     * 断开连接
     */
    const disconnect = () => {
        socketService.disconnect()
        isConnected.value = false
    }

    /**
     * 加入课程
     */
    const joinCourse = (cId: number, uId: number, uName?: string) => {
        socketService.joinCourse(cId, uId, uName)
    }

    /**
     * 离开课程
     */
    const leaveCourse = (cId: number, uId: number, uName?: string) => {
        socketService.leaveCourse(cId, uId, uName)
    }

    /**
     * 监听事件
     */
    const on = <K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]) => {
        socketService.on(event, callback)
    }

    /**
     * 取消监听事件
     */
    const off = <K extends keyof SocketEvents>(event: K, callback: SocketEvents[K]) => {
        socketService.off(event, callback)
    }

    // 生命周期钩子
    onMounted(() => {
        if (autoConnect) {
            connect()
        }
    })

    onUnmounted(() => {
        // 组件卸载时离开课程（但不断开连接，其他组件可能还在使用）
        if (courseId && userId) {
            socketService.leaveCourse(courseId, userId, userName)
        }
    })

    return {
        // 状态
        isConnected,
        isConnecting,
        error,

        // 方法
        connect,
        disconnect,
        joinCourse,
        leaveCourse,
        on,
        off,

        // 直接访问socketService
        socketService,
    }
}

/**
 * 投票相关的Composable
 */
export function usePollSocket(courseId: number, userId: number, userName?: string) {
    const {isConnected, connect, on, off, socketService: socket} = useSocket({
        autoConnect: true,
        courseId,
        userId,
        userName,
    })

    /**
     * 监听新投票
     */
    const onNewPoll = (callback: (data: any) => void) => {
        on('new_poll', callback)
    }

    /**
     * 监听投票结果更新
     */
    const onPollResultsUpdated = (callback: (data: any) => void) => {
        on('poll_results_updated', callback)
    }

    /**
     * 监听投票结束
     */
    const onPollEnded = (callback: (data: any) => void) => {
        on('poll_ended', callback)
    }

    /**
     * 通知投票创建
     */
    const notifyPollCreated = (poll: any) => {
        socket.notifyPollCreated(courseId, poll)
    }

    /**
     * 通知投票响应
     */
    const notifyPollVoted = (pollId: number, results: any) => {
        socket.notifyPollVoted(courseId, pollId, results)
    }

    /**
     * 通知投票关闭
     */
    const notifyPollClosed = (pollId: number) => {
        socket.notifyPollClosed(courseId, pollId)
    }

    /**
     * 加入课程房间
     */
    const joinCourse = (cId: number, uId: number, uName?: string) => {
        socket.joinCourse(cId, uId, uName)
    }

    /**
     * 离开课程房间
     */
    const leaveCourse = (cId: number, uId: number, uName?: string) => {
        socket.leaveCourse(cId, uId, uName)
    }

    return {
        isConnected,
        connect,
        onNewPoll,
        onPollResultsUpdated,
        onPollEnded,
        notifyPollCreated,
        notifyPollVoted,
        notifyPollClosed,
        joinCourse,
        leaveCourse,
        on,
        off,
    }
}

/**
 * 提问相关的Composable
 */
export function useQuestionSocket(courseId: number, userId: number, userName?: string) {
    const {isConnected, connect, joinCourse, leaveCourse, on, off, socketService: socket} = useSocket({
        autoConnect: true,
        courseId,
        userId,
        userName,
    })

    /**
     * 监听新问题
     */
    const onNewQuestion = (callback: (data: any) => void) => {
        on('new_question', callback)
    }

    /**
     * 监听新回答
     */
    const onNewAnswer = (callback: (data: any) => void) => {
        on('new_answer', callback)
    }

    /**
     * 监听答案采纳
     */
    const onAnswerAccepted = (callback: (data: any) => void) => {
        on('answer_was_accepted', callback)
    }

    /**
     * 监听问题点赞更新
     */
    const onQuestionLikesUpdated = (callback: (data: any) => void) => {
        on('question_likes_updated', callback)
    }

    /**
     * 监听回答点赞更新
     */
    const onAnswerLikesUpdated = (callback: (data: any) => void) => {
        on('answer_likes_updated', callback)
    }

    /**
     * 通知问题创建
     */
    const notifyQuestionCreated = (question: any) => {
        socket.notifyQuestionCreated(courseId, question)
    }

    /**
     * 通知答案提交
     */
    const notifyAnswerSubmitted = (questionId: number, answer: any) => {
        socket.notifyAnswerSubmitted(courseId, questionId, answer)
    }

    /**
     * 通知答案采纳
     */
    const notifyAnswerAccepted = (questionId: number, answerId: number) => {
        socket.notifyAnswerAccepted(courseId, questionId, answerId)
    }

    /**
     * 通知问题点赞
     */
    const notifyQuestionLiked = (questionId: number, likeCount: number) => {
        socket.notifyQuestionLiked(courseId, questionId, likeCount)
    }

    /**
     * 通知回答点赞
     */
    const notifyAnswerLiked = (answerId: number, likeCount: number) => {
        socket.notifyAnswerLiked(courseId, answerId, likeCount)
    }

    return {
        isConnected,
        connect,
        joinCourse,
        leaveCourse,
        onNewQuestion,
        onNewAnswer,
        onAnswerAccepted,
        onQuestionLikesUpdated,
        onAnswerLikesUpdated,
        notifyQuestionCreated,
        notifyAnswerSubmitted,
        notifyAnswerAccepted,
        notifyQuestionLiked,
        notifyAnswerLiked,
        on,
        off,
    }
}

/**
 * 弹幕相关的Composable
 */
export function useBarrageSocket(courseId: number, userId: number, userName?: string) {
    const {isConnected, connect, joinCourse, on, off, socketService: socket} = useSocket({
        autoConnect: true,
        courseId,
        userId,
        userName,
    })

    /**
     * 监听新弹幕
     */
    const onNewBarrage = (callback: (data: any) => void) => {
        on('new_barrage', callback)
    }

    /**
     * 监听弹幕删除
     */
    const onBarrageRemoved = (callback: (data: any) => void) => {
        on('barrage_removed', callback)
    }

    /**
     * 发送弹幕
     */
    const sendBarrage = (barrage: any) => {
        socket.sendBarrage(courseId, barrage)
    }

    /**
     * 通知弹幕删除
     */
    const notifyBarrageDeleted = (barrageId: number) => {
        socket.notifyBarrageDeleted(courseId, barrageId)
    }

    return {
        isConnected,
        connect,
        joinCourse,
        onNewBarrage,
        onBarrageRemoved,
        sendBarrage,
        notifyBarrageDeleted,
        on,
        off,
    }
}
