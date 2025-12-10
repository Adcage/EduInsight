<template>
  <div class="question-page">
    <a-page-header title="课堂提问" sub-title="发布问题、查看回答、采纳答案">
      <template #extra>
        <a-space>
          <a-select
            v-model:value="courseId"
            placeholder="选择课程"
            style="width: 200px"
            @change="handleCourseChange"
          >
            <a-select-option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </a-select-option>
          </a-select>
          <a-badge :status="isConnected ? 'success' : 'error'" :text="isConnected ? '已连接' : '未连接'" />
          <a-button type="primary" @click="showCreateModal" :disabled="!courseId">
            <template #icon><PlusOutlined /></template>
            发布问题
          </a-button>
          <a-button type="primary" @click="handleRandomCallOn" :disabled="!courseId" :loading="callOnLoading">
            <template #icon><UserOutlined /></template>
            随机点名
          </a-button>
          <a-button @click="loadQuestions" :disabled="!courseId">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-container">
      <!-- 筛选标签 -->
      <a-card :bordered="false" style="margin-bottom: 16px">
        <a-radio-group v-model:value="filterStatus" button-style="solid" @change="loadQuestions">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="pending">待回答</a-radio-button>
          <a-radio-button value="answered">已回答</a-radio-button>
          <a-radio-button value="closed">已关闭</a-radio-button>
        </a-radio-group>
      </a-card>

      <!-- 问题列表 -->
      <a-spin :spinning="loading">
        <a-empty v-if="!courseId" description="请先选择课程" />
        <a-empty v-else-if="filteredQuestions.length === 0 && !loading" description="暂无问题" />

        <a-row v-else :gutter="[16, 16]">
          <a-col v-for="question in filteredQuestions" :key="question.id" :xs="24" :sm="24" :md="12" :lg="8">
            <a-card :hoverable="true" class="question-card">
              <!-- 问题内容 -->
              <h3 class="question-content">{{ question.content }}</h3>

              <!-- 统计信息 -->
              <a-space direction="vertical" :size="8" style="width: 100%; margin-top: 16px">
                <div class="question-info">
                  <span class="info-label">回答数：</span>
                  <span class="info-value">{{ question.answer_count || 0 }}</span>
                </div>

                <div class="question-info">
                  <span class="info-label">点赞数：</span>
                  <span class="info-value">{{ question.like_count }}</span>
                </div>

                <div class="question-info">
                  <span class="info-label">发布时间：</span>
                  <span>{{ formatTime(question.created_at) }}</span>
                </div>
              </a-space>

              <!-- 操作按钮 -->
              <div class="question-actions">
                <a-space direction="vertical" style="width: 100%" :size="8">
                  <a-space style="width: 100%">
                    <a-button type="primary" size="small" @click="viewAnswers(question)">
                      <EyeOutlined /> 查看回答
                    </a-button>

                    <a-badge :count="getQuestionBarrageCount(question.id)" :overflow-count="99" :offset="[-5, 5]">
                      <a-button size="small" @click="viewQuestionBarrages(question)">
                        <MessageOutlined /> 弹幕
                      </a-button>
                    </a-badge>


                  </a-space>

                  <a-button 
                    v-if="question.status === 'pending'" 
                    type="link" 
                    danger 
                    size="small" 
                    block
                    @click="closeQuestion(question)"
                  >
                    <StopOutlined /> 关闭问题
                  </a-button>
                </a-space>
              </div>
            </a-card>
          </a-col>
        </a-row>
      </a-spin>
    </div>

    <!-- 发布问题对话框 -->
    <a-modal
      v-model:open="createModalVisible"
      title="发布问题"
      width="600px"
      :confirm-loading="createLoading"
      @ok="handleCreateQuestion"
    >
      <a-form ref="createFormRef" :model="questionForm" :rules="questionRules" layout="vertical">
        <a-form-item label="问题内容" name="content">
          <a-textarea
            v-model:value="questionForm.content"
            placeholder="请输入问题内容，例如：请分享你在本节课中学到的最重要的知识点"
            :rows="4"
            :maxlength="500"
            show-count
          />
        </a-form-item>

        <a-form-item>
          <a-checkbox v-model:checked="questionForm.isAnonymous"> 匿名提问 </a-checkbox>
        </a-form-item>

        <a-alert
          message="提示"
          description="学生的回答将自动转换为弹幕，在大屏幕上实时展示"
          type="info"
          show-icon
        />
      </a-form>
    </a-modal>

    <!-- 随机点名动画对话框 -->
    <a-modal
      v-model:open="callOnModalVisible"
      title="随机点名"
      width="600px"
      :footer="null"
      :closable="!isRolling"
      :maskClosable="false"
    >
      <div class="call-on-container">
        <div class="student-display" :class="{ rolling: isRolling }">
          <div class="student-card">
            <a-avatar :size="120" :style="{ backgroundColor: '#1890ff', fontSize: '48px' }">
              {{ currentDisplayStudent?.real_name?.charAt(0) || '?' }}
            </a-avatar>
            <h2 class="student-name">{{ currentDisplayStudent?.real_name || '准备中...' }}</h2>
            <p class="student-info">
              <span v-if="currentDisplayStudent">学号：{{ currentDisplayStudent.username }}</span>
            </p>
            <p class="student-info">
              <span v-if="currentDisplayStudent">班级：{{ currentDisplayStudent.class_name }}</span>
            </p>
          </div>
        </div>

        <div class="action-buttons">
          <a-button
            v-if="!isRolling && !selectedStudent"
            type="primary"
            size="large"
            @click="startRolling"
            block
          >
            开始抽取
          </a-button>
          <a-button
            v-if="isRolling"
            type="primary"
            size="large"
            @click="stopRolling"
            block
          >
            停止
          </a-button>
          <a-space v-if="selectedStudent && !isRolling" style="width: 100%">
            <a-button size="large" @click="resetCallOn" block>
              重新抽取
            </a-button>
            <a-button type="primary" size="large" @click="confirmCallOn" block>
              确认点名
            </a-button>
          </a-space>
        </div>
      </div>
    </a-modal>

    <!-- 回答列表对话框 -->
    <a-modal v-model:open="answersModalVisible" title="学生回答" width="900px" :footer="null">
      <div v-if="currentQuestion">
        <a-alert
          :message="`共收到 ${answers.length} 个回答`"
          type="success"
          show-icon
          style="margin-bottom: 16px"
        />

        <a-spin :spinning="answersLoading">
          <a-empty v-if="answers.length === 0 && !answersLoading" description="暂无回答" />

          <a-list v-else :data-source="answers" :pagination="false">
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
                      <span>学生 {{ item.user_id }}</span>
                      <a-tag v-if="item.is_accepted" color="green">
                        <CheckCircleOutlined /> 已采纳
                      </a-tag>
                      <a-tag color="blue">
                        <MessageOutlined /> 已转弹幕
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
                  <a v-if="!item.is_accepted" @click="acceptAnswer(item)" style="color: #52c41a">
                    <CheckCircleOutlined /> 采纳
                  </a>
                  <a-popconfirm title="确定删除这个回答吗？" @confirm="deleteAnswer(item)">
                    <a style="color: #ff4d4f">
                      <DeleteOutlined /> 删除
                    </a>
                  </a-popconfirm>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </div>
    </a-modal>



    <!-- 弹幕墙抽屉 -->
    <a-drawer
      v-model:open="barrageDrawerVisible"
      :title="currentQuestion ? `问题弹幕：${currentQuestion.content}` : '实时弹幕墙'"
      placement="right"
      :width="900"
      :body-style="{ padding: '16px' }"
    >
      <template #extra>
        <a-statistic 
          v-if="currentQuestion"
          title="弹幕数" 
          :value="getQuestionBarrageCount(currentQuestion.id)" 
          :value-style="{ color: '#52c41a', fontSize: '14px' }"
        />
      </template>

      <div class="barrage-drawer-content">
        <a-alert
          v-if="currentQuestion"
          :message="`问题：${currentQuestion.content}`"
          description="以下是学生回答该问题产生的弹幕"
          type="info"
          show-icon
          style="margin-bottom: 16px"
        />

        <BarrageWall 
          ref="barrageWallRef" 
          :course-id="courseId" 
          :height="700" 
          :show-answer-only-prop="true"
          :total-count="currentQuestionBarrages.length"
        />
      </div>
    </a-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  PlusOutlined,
  ReloadOutlined,
  EyeOutlined,
  InfoCircleOutlined,
  StopOutlined,
  CheckCircleOutlined,
  MessageOutlined,
  LikeOutlined,
  DeleteOutlined,
  UserOutlined,
} from '@ant-design/icons-vue'
import {
  questionApiPost,
  questionApiGet,
  questionApiIntQuestionIdAnswersGet,
  questionApiIntQuestionIdAnswersIntAnswerIdAcceptPut,
  questionApiIntQuestionIdAnswersIntAnswerIdLikePost,
  questionApiIntQuestionIdAnswersIntAnswerIdDelete,
  questionApiIntQuestionIdPut,
  barrageApiGet,
  interactionCommonTeacherCoursesGet,
  interactionCommonCourseStudentsGet,
} from '@/api/interactionController'
import { useQuestionSocket, useBarrageSocket } from '@/composables/useSocket'
import socketService from '@/utils/socket'
import BarrageWall from '@/components/interaction/BarrageWall.vue'
import dayjs from 'dayjs'

// 用户信息
const userId = ref(1)
const userName = ref('教师')
const courseId = ref<number | null>(null)
const courses = ref<any[]>([]) // 教师的课程列表

// 从localStorage获取当前用户信息
const loadCurrentUser = () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      userId.value = user.id
      userName.value = user.real_name || user.username || '教师'
      console.log('当前用户:', { id: userId.value, name: userName.value })
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// WebSocket - 问题
const {
  isConnected,
  onNewQuestion,
  onNewAnswer,
  onAnswerAccepted,
  notifyQuestionCreated,
  notifyAnswerAccepted,
  joinCourse: joinQuestionCourse,
} = useQuestionSocket(1, userId.value, userName.value)

// WebSocket - 弹幕
const { 
  onNewBarrage, 
  onBarrageRemoved, 
  notifyBarrageDeleted,
  joinCourse: joinBarrageCourse,
} = useBarrageSocket(1, userId.value, userName.value)

// 数据
const loading = ref(false)
const questions = ref<any[]>([])
const answers = ref<any[]>([])
const filterStatus = ref('all')
const barrages = ref<any[]>([])
const barrageWallRef = ref()

const barrageDrawerVisible = ref(false)
const barrageLoopTimer = ref<any>(null)
const currentQuestionBarrages = ref<any[]>([])

// 对话框
const createModalVisible = ref(false)
const createLoading = ref(false)

// 随机点名
const callOnLoading = ref(false)
const callOnModalVisible = ref(false)
const students = ref<any[]>([])
const studentsLoading = ref(false)
const isRolling = ref(false)
const currentDisplayStudent = ref<any>(null)
const selectedStudent = ref<any>(null)
const rollingInterval = ref<any>(null)

const answersModalVisible = ref(false)
const answersLoading = ref(false)

const currentQuestion = ref<any>(null)
const createFormRef = ref()

const questionForm = reactive({
  content: '',
  isAnonymous: false,
})

const questionRules = {
  content: [
    { required: true, message: '请输入问题内容', trigger: 'blur' },
    { min: 10, message: '问题内容至少10个字符', trigger: 'blur' },
  ],
}

// 过滤后的问题列表
const filteredQuestions = computed(() => {
  if (filterStatus.value === 'all') {
    return questions.value
  }
  return questions.value.filter((q) => q.status === filterStatus.value)
})

// 弹幕统计
const barrageStats = computed(() => {
  const total = barrages.value.length
  const answer = barrages.value.filter((b) => b.question_id !== null).length
  return { total, answer }
})

// 加载教师的课程列表
const loadCourses = async () => {
  try {
    const response = await interactionCommonTeacherCoursesGet()
    
    if (response.data && response.data.data) {
      courses.value = response.data.data.courses
      
      // 默认选择第一个课程
      if (courses.value.length > 0) {
        courseId.value = courses.value[0].id
        
        // 加载第一个课程的数据
        loadQuestions()
        loadBarrages()
      } else {
        message.warning('您还没有任何课程')
      }
    }
  } catch (error: any) {
    console.error('加载课程列表失败:', error)
    message.error(error.response?.data?.message || '加载课程列表失败')
  }
}

// 处理课程切换
const handleCourseChange = () => {
  // 切换课程时重新加入WebSocket房间（如果已连接）
  if (courseId.value && userId.value && isConnected.value) {
    joinQuestionCourse(courseId.value, userId.value, userName.value)
    joinBarrageCourse(courseId.value, userId.value, userName.value)
  }
  
  // 切换课程时重新加载数据
  loadQuestions()
  loadBarrages()
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
    questions.value = data.items || data.questions || []

    // 为每个问题添加回答数量（简化处理）
    questions.value.forEach((q) => {
      q.answer_count = q.answer_count || 0
    })
  } catch (error: any) {
    console.error('加载问题列表失败:', error)
    message.error(error.response?.data?.message || '加载问题列表失败')
    questions.value = []
  } finally {
    loading.value = false
  }
}

// 加载弹幕列表
const loadBarrages = async () => {
  if (!courseId.value) return
  
  try {
    // 直接使用 limit 参数，不使用分页
    const response = await barrageApiGet({
      courseId: courseId.value,
      limit: 200,
    } as any)

    // 使用与BarragePage相同的数据访问方式
    barrages.value = response.data.data.barrages || []
  } catch (error: any) {
    console.error('加载弹幕列表失败:', error)
    barrages.value = []
  }
}





// 获取问题的弹幕数量
const getQuestionBarrageCount = (questionId: number) => {
  return barrages.value.filter((b) => b.question_id === questionId).length
}

// 停止弹幕循环
const stopBarrageLoop = () => {
  if (barrageLoopTimer.value) {
    clearInterval(barrageLoopTimer.value)
    barrageLoopTimer.value = null
  }
}

// 开始弹幕循环
const startBarrageLoop = (questionBarrages: any[]) => {
  if (questionBarrages.length === 0) return
  
  // 清除之前的定时器
  stopBarrageLoop()
  
  // 立即播放一次
  if (barrageWallRef.value) {
    barrageWallRef.value.clearBarrages()
    barrageWallRef.value.addBarrages(questionBarrages)
  }
  
  // 设置循环播放
  // 计算一轮弹幕播放完需要的时间（基础速度15秒 / 速度等级）
  const baseSpeed = 15
  const speed = 2 // 正常速度
  const duration = (baseSpeed / speed) * 1000 // 转换为毫秒
  
  // 每隔一定时间重新播放
  barrageLoopTimer.value = setInterval(() => {
    // 检查弹幕墙是否暂停，如果暂停则跳过本次循环
    if (barrageWallRef.value && barrageDrawerVisible.value) {
      // 获取弹幕墙的暂停状态
      const isPaused = barrageWallRef.value.isPaused
      
      // 只有在未暂停状态下才循环播放
      if (!isPaused) {
        barrageWallRef.value.clearBarrages()
        // 延迟一下再添加，让清空效果更明显
        setTimeout(() => {
          if (barrageWallRef.value && !barrageWallRef.value.isPaused) {
            barrageWallRef.value.addBarrages(questionBarrages)
          }
        }, 100)
      }
    }
  }, duration + questionBarrages.length * 800) // 加上弹幕间隔时间（800ms）
}

// 查看问题的弹幕
const viewQuestionBarrages = (question: any) => {
  currentQuestion.value = question
  barrageDrawerVisible.value = true
  
  // 停止之前的循环
  stopBarrageLoop()
  
  // 清空弹幕墙
  if (barrageWallRef.value) {
    barrageWallRef.value.clearBarrages()
  }
  
  // 加载该问题的弹幕
  setTimeout(() => {
    const questionBarrages = barrages.value.filter((b) => b.question_id === question.id)
    
    currentQuestionBarrages.value = questionBarrages
    
    if (questionBarrages.length > 0) {
      message.success(`加载了 ${questionBarrages.length} 条弹幕，将循环播放`)
      startBarrageLoop(questionBarrages)
    } else {
      message.info('该问题暂无弹幕')
    }
  }, 100)
}

// 显示创建对话框
const showCreateModal = () => {
  createModalVisible.value = true
  questionForm.content = ''
  questionForm.isAnonymous = false
}

// 加载课程学生列表
const loadStudents = async () => {
  if (!courseId.value) return
  
  studentsLoading.value = true
  try {
    const response = await interactionCommonCourseStudentsGet({ courseId: courseId.value })
    students.value = response.data.data.students
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载学生列表失败')
    students.value = []
  } finally {
    studentsLoading.value = false
  }
}

// 打开随机点名对话框
const handleRandomCallOn = async () => {
  if (!courseId.value) {
    message.warning('请先选择课程')
    return
  }
  
  callOnLoading.value = true
  
  try {
    // 加载学生列表
    await loadStudents()
    
    if (students.value.length === 0) {
      message.warning('该课程没有学生')
      return
    }
    
    // 重置状态
    isRolling.value = false
    selectedStudent.value = null
    currentDisplayStudent.value = students.value[0]
    
    // 打开对话框
    callOnModalVisible.value = true
  } catch (error: any) {
    message.error('加载学生列表失败')
  } finally {
    callOnLoading.value = false
  }
}

// 开始滚动
const startRolling = () => {
  if (students.value.length === 0) return
  
  isRolling.value = true
  let currentIndex = 0
  
  // 每100ms切换一次学生
  rollingInterval.value = setInterval(() => {
    currentIndex = (currentIndex + 1) % students.value.length
    currentDisplayStudent.value = students.value[currentIndex]
  }, 100)
}

// 停止滚动
const stopRolling = () => {
  if (rollingInterval.value) {
    clearInterval(rollingInterval.value)
    rollingInterval.value = null
  }
  
  isRolling.value = false
  
  // 随机选择最终的学生
  const randomIndex = Math.floor(Math.random() * students.value.length)
  selectedStudent.value = students.value[randomIndex]
  currentDisplayStudent.value = selectedStudent.value
}

// 重新抽取
const resetCallOn = () => {
  selectedStudent.value = null
  currentDisplayStudent.value = students.value[0]
}

// 确认点名
const confirmCallOn = () => {
  if (!selectedStudent.value || !courseId.value) return
  
  // 通过WebSocket发送点名通知
  socketService.emit('call_on_student', {
    course_id: courseId.value,
    student_id: selectedStudent.value.id,
    student_name: selectedStudent.value.real_name,
  })
  
  message.success(`已点名：${selectedStudent.value.real_name} (${selectedStudent.value.class_name})`)
  callOnModalVisible.value = false
}

// 发布问题
const handleCreateQuestion = async () => {
  try {
    await createFormRef.value.validate()

    createLoading.value = true

    const response = await questionApiPost({
      content: questionForm.content,
      courseId: courseId.value,
      isAnonymous: questionForm.isAnonymous,
    })

    // WebSocket通知
    notifyQuestionCreated(response.data.data)

    message.success('问题发布成功')
    createModalVisible.value = false
    loadQuestions()
  } catch (error: any) {
    if (error.errorFields) {
      return
    }
    message.error(error.response?.data?.message || '发布问题失败')
  } finally {
    createLoading.value = false
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

    answers.value = response.data.data.answers
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载回答失败')
  } finally {
    answersLoading.value = false
  }
}

// 采纳答案
const acceptAnswer = async (answer: any) => {
  try {
    await questionApiIntQuestionIdAnswersIntAnswerIdAcceptPut({
      questionId: currentQuestion.value.id,
      answerId: answer.id,
    })

    // WebSocket通知
    notifyAnswerAccepted(currentQuestion.value.id, answer.id)

    message.success('答案已采纳')

    // 刷新回答列表
    viewAnswers(currentQuestion.value)
  } catch (error: any) {
    message.error(error.response?.data?.message || '采纳失败')
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

// 删除回答
const deleteAnswer = async (answer: any) => {
  try {
    await questionApiIntQuestionIdAnswersIntAnswerIdDelete({
      questionId: currentQuestion.value.id,
      answerId: answer.id,
    })

    message.success('删除成功')

    // 刷新回答列表
    viewAnswers(currentQuestion.value)
  } catch (error: any) {
    message.error(error.response?.data?.message || '删除失败')
  }
}

// 关闭问题
const closeQuestion = async (question: any) => {
  try {
    await questionApiIntQuestionIdPut(
      { questionId: question.id },
      { status: 'closed' }
    )

    message.success('问题已关闭')
    loadQuestions()
  } catch (error: any) {
    message.error(error.response?.data?.message || '关闭失败')
  }
}



// 获取状态颜色
const getStatusColor = (status: string) => {
  const colors: Record<string, string> = {
    pending: 'orange',
    answered: 'green',
    closed: 'default',
  }
  return colors[status] || 'default'
}

// 获取状态文本
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
  
  // 课程加载后会自动加载问题和弹幕
  // loadQuestions()
  // loadBarrages()

  // 监听新问题（其他教师发布）
  onNewQuestion((data) => {
    console.log('收到新问题:', data)
    loadQuestions()
  })

  // 监听新回答
  onNewAnswer((data) => {
    message.info('收到新回答')

    // 如果正在查看回答列表，自动刷新
    if (answersModalVisible.value && currentQuestion.value?.id === data.question_id) {
      viewAnswers(currentQuestion.value)
    }

    // 更新问题的回答数
    const question = questions.value.find((q) => q.id === data.question_id)
    if (question) {
      question.answer_count = (question.answer_count || 0) + 1
      question.status = 'answered'
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
      }
    }
  })

  // 监听新弹幕（学生回答会自动转为弹幕）
  onNewBarrage((data) => {
    // 添加到列表
    barrages.value.unshift(data.barrage)

    // 如果是答案弹幕，添加到弹幕墙
    if (data.barrage.question_id) {
      barrageWallRef.value?.addBarrage(data.barrage)
      message.success('收到新的答案弹幕')
    }
  })

  // 监听弹幕删除
  onBarrageRemoved((data) => {
    // 从本地列表移除
    const index = barrages.value.findIndex((b) => b.id === data.barrage_id)
    if (index > -1) {
      barrages.value.splice(index, 1)
    }

    // 从弹幕墙移除
    barrageWallRef.value?.removeBarrage(data.barrage_id)
    
    // 如果删除的是当前问题的弹幕，更新循环播放列表
    if (currentQuestion.value && data.barrage_id) {
      const barrageIndex = currentQuestionBarrages.value.findIndex((b) => b.id === data.barrage_id)
      if (barrageIndex > -1) {
        currentQuestionBarrages.value.splice(barrageIndex, 1)
        // 重新开始循环
        if (barrageDrawerVisible.value && currentQuestionBarrages.value.length > 0) {
          startBarrageLoop(currentQuestionBarrages.value)
        }
      }
    }
  })
})

// 监听抽屉关闭，停止循环
watch(barrageDrawerVisible, (newVal) => {
  if (!newVal) {
    stopBarrageLoop()
  }
})

// 监听 WebSocket 连接状态，连接成功后加入课程房间
watch(isConnected, (connected) => {
  if (connected && courseId.value && userId.value) {
    console.log('WebSocket 已连接，加入课程房间:', courseId.value)
    // 添加小延迟确保两个 WebSocket 都已连接
    setTimeout(() => {
      if (courseId.value && userId.value) {
        joinQuestionCourse(courseId.value, userId.value, userName.value)
        joinBarrageCourse(courseId.value, userId.value, userName.value)
      }
    }, 100)
  }
})



// 组件卸载时清理
onUnmounted(() => {
  stopBarrageLoop()
  
  // 清理点名滚动定时器
  if (rollingInterval.value) {
    clearInterval(rollingInterval.value)
  }
})
</script>

<style scoped lang="scss">
.question-page {
  min-height: 100vh;
  background: var(--bg-color);
}

.content-container {
  padding: 24px;
}

.question-card {
  height: 100%;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.question-content {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 16px 0;
  color: var(--text-color);
  min-height: 60px;
  line-height: 1.5;
}

.question-info {
  display: flex;
  align-items: center;
  font-size: 14px;

  .info-label {
    color: var(--text-color-secondary);
    margin-right: 8px;
  }

  .info-value {
    font-weight: 600;
    color: var(--primary-color);
  }
}

.question-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.answer-content {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 8px;
  color: var(--text-color);
}

.answer-meta {
  font-size: 13px;
  color: var(--text-color-secondary);
}

.barrage-drawer-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

// 随机点名样式
.call-on-container {
  padding: 20px 0;
}

.student-display {
  min-height: 400px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 16px;
  padding: 40px;
  transition: all 0.3s ease;

  &.rolling {
    animation: pulse 0.5s ease-in-out infinite;
  }
}

@keyframes pulse {
  0%, 100% {
    transform: scale(1);
  }
  50% {
    transform: scale(1.05);
  }
}

.student-card {
  text-align: center;
  color: white;
  
  .student-name {
    font-size: 36px;
    font-weight: bold;
    margin: 20px 0 10px;
    color: white;
    text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.3);
  }
  
  .student-info {
    font-size: 18px;
    margin: 8px 0;
    color: rgba(255, 255, 255, 0.9);
    
    span {
      background: rgba(255, 255, 255, 0.2);
      padding: 4px 12px;
      border-radius: 12px;
      backdrop-filter: blur(10px);
    }
  }
}

.action-buttons {
  display: flex;
  flex-direction: column;
  gap: 12px;
}
</style>
