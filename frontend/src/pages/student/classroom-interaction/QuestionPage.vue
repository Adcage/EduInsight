<template>
  <div class="question-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <QuestionCircleOutlined class="title-icon" />
            课堂提问
          </h1>
          <p class="page-subtitle">查看问题、提交回答、获取采纳</p>
        </div>
        <div class="header-right">
          <a-space :size="12">
            <a-select
              v-model:value="courseId"
              placeholder="选择课程"
              class="course-select"
              @change="handleCourseChange"
            >
              <template #suffixIcon>
                <BookOutlined />
              </template>
              <a-select-option v-for="course in courses" :key="course.id" :value="course.id">
                {{ course.name }}
              </a-select-option>
            </a-select>
            <a-badge 
              :status="isConnected ? 'success' : 'error'" 
              :text="isConnected ? '实时连接' : '连接断开'" 
              class="connection-badge"
            />
            <a-button @click="loadQuestions" :disabled="!courseId" size="large">
              <template #icon><ReloadOutlined /></template>
            </a-button>
          </a-space>
        </div>
      </div>
    </div>

    <div class="content-container">
      <!-- 筛选标签 -->
      <a-card :bordered="false" style="margin-bottom: 16px">
        <a-radio-group v-model:value="filterStatus" button-style="solid" @change="loadQuestions">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="pending">待回答</a-radio-button>
          <a-radio-button value="answered">已回答</a-radio-button>
          <a-radio-button value="my_answered">我的回答</a-radio-button>
        </a-radio-group>
      </a-card>

      <!-- 问题列表 -->
      <a-spin :spinning="loading">
        <a-empty v-if="!courseId" description="请先选择课程" />
        <a-empty v-else-if="filteredQuestions.length === 0 && !loading" description="暂无问题" />

        <a-list v-else :data-source="filteredQuestions" :pagination="false">
          <template #renderItem="{ item }">
            <a-list-item class="question-item">
              <a-list-item-meta>
                <template #avatar>
                  <a-avatar :style="{ backgroundColor: item.status === 'pending' ? '#faad14' : '#52c41a' }">
                    <QuestionCircleOutlined />
                  </a-avatar>
                </template>

                <template #title>
                  <a-space>
                    <span class="question-title">{{ item.content }}</span>
                    <a-tag :color="getQuestionStatusColor(item)">
                      {{ getQuestionStatusText(item) }}
                    </a-tag>
                    <a-tag v-if="item.has_answered" color="green">
                      <CheckCircleOutlined /> 已回答
                    </a-tag>
                  </a-space>
                </template>

                <template #description>
                  <a-space>
                    <span>回答数: {{ item.answer_count || 0 }}</span>
                    <span>点赞数: {{ item.like_count }}</span>
                    <span>{{ formatTime(item.created_at) }}</span>
                  </a-space>
                </template>
              </a-list-item-meta>

              <template #actions>
                <a-button
                  v-if="item.status === 'pending' && !item.has_answered"
                  type="primary"
                  @click="answerQuestion(item)"
                >
                  <EditOutlined /> 回答问题
                </a-button>

                <a-button v-else-if="item.has_answered" disabled>
                  <CheckCircleOutlined /> 已回答
                </a-button>

                <a-button @click="viewAnswers(item)">
                  <EyeOutlined /> 查看回答
                </a-button>

                <a-button @click="likeQuestion(item)">
                  <LikeOutlined /> 点赞 ({{ item.like_count }})
                </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-spin>
    </div>

    <!-- 回答问题对话框 -->
    <a-modal
      v-model:open="answerModalVisible"
      title="提交回答"
      width="700px"
      :confirm-loading="answerLoading"
      @ok="handleSubmitAnswer"
    >
      <div v-if="currentQuestion">
        <a-alert
          message="重要提示"
          description="你的回答将自动转换为弹幕，在大屏幕上实时展示给全班同学！"
          type="info"
          show-icon
          style="margin-bottom: 16px"
        />

        <h3 style="font-size: 16px; margin-bottom: 8px">问题：</h3>
        <p style="font-size: 15px; color: #666; margin-bottom: 24px">{{ currentQuestion.content }}</p>

        <a-divider>请输入你的回答</a-divider>

        <a-textarea
          v-model:value="answerContent"
          :rows="6"
          placeholder="请输入你的回答..."
        />

        <a-alert
          message="提示"
          description="回答将以弹幕形式展示，建议简洁明了"
          type="warning"
          show-icon
          style="margin-top: 16px"
        />
      </div>
    </a-modal>

    <!-- 回答列表对话框 -->
    <a-modal v-model:open="answersModalVisible" title="我的回答" width="800px" :footer="null">
      <div v-if="currentQuestion">
        <a-alert
          :message="answers.length > 0 ? `你已提交 ${answers.length} 个回答` : '你还没有回答这个问题'"
          :type="answers.length > 0 ? 'success' : 'info'"
          show-icon
          style="margin-bottom: 16px"
        />

        <a-spin :spinning="answersLoading">
          <a-empty v-if="answers.length === 0 && !answersLoading" description="暂无回答" />

          <a-list v-else :data-source="answers">
            <template #renderItem="{ item, index }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: item.is_accepted ? '#52c41a' : '#1890ff' }">
                      {{ index + 1 }}
                    </a-avatar>
                  </template>

                  <template #title>
                    <a-space>
                      <span>{{ item.is_anonymous ? '匿名用户' : (item.user_name || item.real_name || `学生 ${item.user_id}`) }}</span>
                      <a-tag v-if="item.is_accepted" color="green">
                        <CheckCircleOutlined /> 已采纳
                      </a-tag>
                      <a-tag v-if="item.user_id === userId" color="blue">
                        我的回答
                      </a-tag>
                    </a-space>
                  </template>

                  <template #description>
                    <div class="answer-content">{{ item.content }}</div>
                    <div class="answer-meta">
                      <a-space>
                        <span>点赞数: {{ item.like_count }}</span>
                        <span>{{ formatTime(item.created_at) }}</span>
                      </a-space>
                    </div>
                  </template>
                </a-list-item-meta>

                <template #actions>
                  <a @click="likeAnswer(item)">
                    <LikeOutlined /> 点赞 ({{ item.like_count }})
                  </a>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined,
  QuestionCircleOutlined,
  CheckCircleOutlined,
  EditOutlined,
  EyeOutlined,
  LikeOutlined,
  BookOutlined,
} from '@ant-design/icons-vue'
import {
  questionApiGet,
  questionApiIntQuestionIdAnswersPost,
  questionApiIntQuestionIdAnswersGet,
  questionApiIntQuestionIdLikePost,
  questionApiIntQuestionIdAnswersIntAnswerIdLikePost,
  interactionCommonStudentCoursesGet,
} from '@/api/interactionController'
import { useQuestionSocket } from '@/composables/useSocket'
import socketService from '@/utils/socket'
import dayjs from 'dayjs'

// 用户信息
const userId = ref(1)
const userName = ref('学生')
const courseId = ref<number | null>(null)
const courses = ref<any[]>([]) // 学生的课程列表

// 从localStorage获取当前用户信息
const loadCurrentUser = () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      userId.value = user.id
      userName.value = user.real_name || user.username || '学生'
      console.log('当前用户:', { id: userId.value, name: userName.value })
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// WebSocket
const {
  isConnected,
  onNewQuestion,
  onNewAnswer,
  onAnswerAccepted,
  notifyAnswerSubmitted,
  joinCourse: joinQuestionCourse,
  leaveCourse: leaveQuestionCourse,
} = useQuestionSocket(1, userId.value, userName.value)

// 数据
const loading = ref(false)
const questions = ref<any[]>([])
const answers = ref<any[]>([])
const filterStatus = ref('all')

// 对话框
const answerModalVisible = ref(false)
const answerLoading = ref(false)
const answersModalVisible = ref(false)
const answersLoading = ref(false)

const currentQuestion = ref<any>(null)
const answerContent = ref('')

// 过滤后的问题列表
const filteredQuestions = computed(() => {
  if (filterStatus.value === 'all') {
    return questions.value
  } else if (filterStatus.value === 'my_answered') {
    return questions.value.filter((q) => q.has_answered)
  }
  return questions.value.filter((q) => q.status === filterStatus.value)
})

// 加载学生的课程列表
const loadCourses = async () => {
  try {
    const response = await interactionCommonStudentCoursesGet()
    
    if (response.data && response.data.data) {
      courses.value = response.data.data.courses
      
      // 默认选择第一个课程
      if (courses.value.length > 0) {
        courseId.value = courses.value[0].id
        previousCourseId.value = courseId.value // 记录初始课程ID
        
        // 加载第一个课程的数据
        loadQuestions()
      } else {
        message.warning('您还没有选修任何课程')
      }
    }
  } catch (error: any) {
    console.error('加载课程列表失败:', error)
    message.error(error.response?.data?.message || '加载课程列表失败')
  }
}

// 保存上一个课程ID，用于离开旧房间
const previousCourseId = ref<number | null>(null)

// 处理课程切换
const handleCourseChange = () => {
  // 切换课程时，先离开旧课程房间，再加入新课程房间
  if (isConnected.value && userId.value) {
    // 如果有旧课程，先离开
    if (previousCourseId.value && previousCourseId.value !== courseId.value) {
      console.log('离开旧课程房间:', previousCourseId.value)
      leaveQuestionCourse(previousCourseId.value, userId.value, userName.value)
    }
    
    // 加入新课程房间
    if (courseId.value) {
      console.log('加入新课程房间:', courseId.value)
      joinQuestionCourse(courseId.value, userId.value, userName.value)
      previousCourseId.value = courseId.value
    }
  }
  
  // 切换课程时重新加载数据
  loadQuestions()
}

// 加载问题列表
const loadQuestions = async () => {
  if (!courseId.value) return
  
  loading.value = true
  try {
    const response = await questionApiGet({
      courseId: courseId.value,
      page: 1,
      perPage: 100,
    })

    // 后端返回的结构是 response.data.data.items，不是 questions
    const data = response.data?.data || response.data || {}
    const questionList = data.items || data.questions || []

    // 批量检查当前用户是否已回答每个问题
    // 为了性能，我们并行发起所有请求
    const checkPromises = questionList.map(async (question: any) => {
      question.answer_count = question.answer_count || 0
      
      try {
        const answersResponse = await questionApiIntQuestionIdAnswersGet({
          questionId: question.id,
        })
        const answers = answersResponse.data.data.answers || []
        question.has_answered = answers.some((a: any) => a.user_id === userId.value)
      } catch (error) {
        console.error(`检查问题 ${question.id} 的回答状态失败:`, error)
        question.has_answered = false
      }
      
      return question
    })
    
    // 等待所有检查完成
    questions.value = await Promise.all(checkPromises)
  } catch (error: any) {
    console.error('加载问题列表失败:', error)
    message.error(error.response?.data?.message || '加载问题列表失败')
    questions.value = []
  } finally {
    loading.value = false
  }
}

// 回答问题
const answerQuestion = (question: any) => {
  currentQuestion.value = question
  answerContent.value = ''
  answerModalVisible.value = true
}

// 提交回答 ⭐ 核心功能：答案自动转弹幕
const handleSubmitAnswer = async () => {
  if (!answerContent.value.trim()) {
    message.warning('请输入回答内容')
    return
  }

  answerLoading.value = true
  try {
    const response = await questionApiIntQuestionIdAnswersPost(
      { questionId: currentQuestion.value.id },
      { content: answerContent.value }
    )

    // 返回的数据包含答案和弹幕
    const { answer, barrage } = response.data.data

    console.log('答案:', answer)
    console.log('弹幕:', barrage) // 自动生成的弹幕

    // WebSocket通知
    notifyAnswerSubmitted(currentQuestion.value.id, answer)

    message.success('回答成功！你的答案已转为弹幕展示')
    answerModalVisible.value = false

    // 更新本地状态
    const question = questions.value.find((q) => q.id === currentQuestion.value.id)
    if (question) {
      question.has_answered = true
      question.answer_count = (question.answer_count || 0) + 1
      // 注意：不要修改 question.status，让它保持原状态
      // 问题状态应该由后端控制，不应该在前端随意修改
    }

    // 不需要重新加载问题列表，因为我们已经更新了本地状态
    // loadQuestions()
  } catch (error: any) {
    message.error(error.response?.data?.message || '回答失败')
  } finally {
    answerLoading.value = false
  }
}

// 查看回答
const viewAnswers = async (question: any) => {
  currentQuestion.value = question
  answersModalVisible.value = true
  answersLoading.value = true

  try {
    const response = await questionApiIntQuestionIdAnswersGet({
      questionId: question.id,
    })

    // 学生只能看到自己的回答，不能看到其他学生的回答
    const allAnswers = response.data.data.answers
    answers.value = allAnswers.filter((answer: any) => answer.user_id === userId.value)
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载回答失败')
  } finally {
    answersLoading.value = false
  }
}

// 点赞问题
const likeQuestion = async (question: any) => {
  try {
    const response = await questionApiIntQuestionIdLikePost({
      questionId: question.id,
    })

    message.success('点赞成功')

    // 更新本地数据
    question.like_count = response.data.data.like_count
  } catch (error: any) {
    message.error(error.response?.data?.message || '点赞失败')
  }
}

// 点赞回答
const likeAnswer = async (answer: any) => {
  try {
    const response = await questionApiIntQuestionIdAnswersIntAnswerIdLikePost({
      questionId: currentQuestion.value.id,
      answerId: answer.id,
    })

    message.success('点赞成功')

    // 更新本地数据
    answer.like_count = response.data.data.like_count
  } catch (error: any) {
    message.error(error.response?.data?.message || '点赞失败')
  }
}

// 获取问题状态颜色
const getQuestionStatusColor = (question: any) => {
  // 如果问题已关闭
  if (question.status === 'closed') {
    return 'default'
  }
  // 问题开放中，显示橙色
  return 'orange'
}

// 获取问题状态文本
const getQuestionStatusText = (question: any) => {
  // 如果问题已关闭
  if (question.status === 'closed') {
    return '已关闭'
  }
  // 问题开放中
  return '开放中'
}

// 保留旧的函数以防其他地方使用
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'orange',
    answered: 'green',
    closed: 'default',
  }
  return colors[status] || 'default'
}

const getStatusText = (status: string) => {
  const texts: Record<string, string> = {
    pending: '待回答',
    answered: '已回答',
    closed: '已关闭',
  }
  return texts[status] || status
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// WebSocket事件监听
onMounted(() => {
  // 先加载当前用户信息
  loadCurrentUser()
  
  // 然后加载课程列表
  loadCourses()

  // 监听新问题
  onNewQuestion((data) => {
    console.log('收到新问题事件:', data)
    message.info('教师发布了新问题')
    loadQuestions()
  })

  // 监听新回答
  onNewAnswer((data) => {
    // 如果正在查看回答列表，自动刷新
    if (answersModalVisible.value && currentQuestion.value?.id === data.question_id) {
      viewAnswers(currentQuestion.value)
    }

    // 更新问题的回答数
    const question = questions.value.find((q) => q.id === data.question_id)
    if (question) {
      question.answer_count = (question.answer_count || 0) + 1
      // 注意：不要修改 question.status，让它保持 'pending' 状态
      // 这样其他学生仍然可以回答
      
      // 只有当回答是当前用户提交的时候，才标记为已回答
      // data.answer 包含回答信息，其中有 user_id
      if (data.answer && data.answer.user_id === userId.value) {
        question.has_answered = true
      }
    }
  })

  // 监听答案采纳
  onAnswerAccepted((data) => {
    console.log('答案被采纳:', data)

    // 如果正在查看回答列表，更新本地数据
    if (answersModalVisible.value) {
      const answer = answers.value.find((a) => a.id === data.answer_id)
      if (answer) {
        // 取消其他答案的采纳状态
        answers.value.forEach((a) => (a.is_accepted = false))
        // 设置当前答案为采纳
        answer.is_accepted = true

        // 如果是自己的答案被采纳
        if (answer.user_id === userId.value) {
          message.success('恭喜！你的答案被教师采纳了！')
        }
      }
    }
  })
  
  // 监听点名通知
  socketService.on('student_called_on', (data: any) => {
    console.log('收到点名通知:', data)
    
    // 只有被点名的学生才显示通知
    if (data.student_id === userId.value) {
      message.success({
        content: `🎯 教师随机点名：${data.student_name}`,
        duration: 8,
      })
    }
  })
})

// 监听 WebSocket 连接状态，连接成功后加入课程房间
watch(isConnected, (connected) => {
  if (connected && courseId.value && userId.value) {
    console.log('WebSocket 已连接，加入课程房间:', courseId.value)
    // 添加小延迟确保 WebSocket 已连接
    setTimeout(() => {
      if (courseId.value && userId.value) {
        joinQuestionCourse(courseId.value, userId.value, userName.value)
      }
    }, 100)
  }
})
</script>

<style scoped lang="scss">
.question-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8eef5 100%);
}

// 页面头部样式
.page-header {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 32px 40px;
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.25);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
}

.header-left {
  .page-title {
    font-size: 32px;
    font-weight: 700;
    color: #ffffff;
    margin: 0 0 8px 0;
    display: flex;
    align-items: center;
    gap: 12px;

    .title-icon {
      font-size: 36px;
    }
  }

  .page-subtitle {
    font-size: 15px;
    color: rgba(255, 255, 255, 0.85);
    margin: 0;
    padding-left: 48px;
  }
}

.header-right {
  .course-select {
    width: 220px;
    :deep(.ant-select-selector) {
      border-radius: 8px;
      border: 2px solid rgba(255, 255, 255, 0.3);
      background: rgba(255, 255, 255, 0.15);
      backdrop-filter: blur(10px);
      color: #fff;
      font-weight: 500;

      &:hover {
        border-color: rgba(255, 255, 255, 0.5);
      }
    }

    :deep(.ant-select-arrow) {
      color: #fff;
    }
  }

  .connection-badge {
    padding: 8px 16px;
    background: rgba(255, 255, 255, 0.15);
    backdrop-filter: blur(10px);
    border-radius: 8px;
    color: #fff;
    font-weight: 500;
  }
}

.content-container {
  padding: 0 40px 40px;
  max-width: 1400px;
  margin: 0 auto;
}

// 问题列表项样式
.question-item {
  background: #fff;
  padding: 24px;
  margin-bottom: 16px;
  border-radius: 16px;
  border: none;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-4px);
    box-shadow: 0 8px 24px rgba(102, 126, 234, 0.15);
  }

  :deep(.ant-list-item-meta-avatar) {
    .ant-avatar {
      width: 48px;
      height: 48px;
      font-size: 24px;
    }
  }

  :deep(.ant-list-item-action) {
    margin-left: 24px;

    li {
      padding: 0 8px;
    }

    .ant-btn {
      border-radius: 8px;
      font-weight: 600;
      
      &:hover {
        transform: translateY(-2px);
      }
    }
  }
}

.question-title {
  font-size: 18px;
  font-weight: 700;
  color: #1a1a1a;
  line-height: 1.5;
}

.answer-content {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 8px;
  color: #333;
}

.answer-meta {
  font-size: 13px;
  color: #999;
}

// 响应式设计
@media (max-width: 768px) {
  .page-header {
    padding: 24px 20px;
  }

  .header-content {
    flex-direction: column;
    gap: 20px;
  }

  .header-left .page-title {
    font-size: 24px;
  }

  .content-container {
    padding: 0 20px 20px;
  }

  .question-item {
    padding: 16px;
  }
}
</style>
