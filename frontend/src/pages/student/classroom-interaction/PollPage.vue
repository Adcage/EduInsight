<template>
  <div class="poll-page">
    <!-- 顶部操作栏 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">
            <CheckCircleOutlined class="title-icon" />
            课堂投票
          </h1>
          <p class="page-subtitle">参与投票、查看结果</p>
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
            <a-button @click="loadPolls" :disabled="!courseId" size="large">
              <template #icon><ReloadOutlined /></template>
            </a-button>
          </a-space>
        </div>
      </div>
    </div>

    <div class="content-container">
      <!-- 筛选标签 -->
      <a-card :bordered="false" style="margin-bottom: 16px">
        <a-radio-group v-model:value="filterStatus" button-style="solid" @change="loadPolls">
          <a-radio-button value="all">全部</a-radio-button>
          <a-radio-button value="active">进行中</a-radio-button>
          <a-radio-button value="ended">已结束</a-radio-button>
          <a-radio-button value="voted">已投票</a-radio-button>
        </a-radio-group>
      </a-card>

      <!-- 投票列表 -->
      <a-spin :spinning="loading">
        <a-empty v-if="!courseId" description="请先选择课程" />
        <a-empty v-else-if="filteredPolls.length === 0 && !loading" description="暂无投票" />

        <a-row v-else :gutter="[16, 16]">
          <a-col v-for="poll in filteredPolls" :key="poll.id" :xs="24" :sm="24" :md="12" :lg="8">
            <a-card :hoverable="true" class="poll-card">
              <!-- 投票状态 -->
              <template #extra>
                <a-space>
                  <a-tag :color="poll.status === 'active' ? 'green' : 'default'">
                    {{ poll.status === 'active' ? '进行中' : '已结束' }}
                  </a-tag>
                  <a-tag v-if="poll.has_voted" color="blue">
                    <CheckCircleOutlined /> 已投票
                  </a-tag>
                </a-space>
              </template>

              <!-- 投票内容 -->
              <h3 class="poll-title">{{ poll.title }}</h3>
              <p class="poll-description">{{ poll.description }}</p>

              <!-- 投票信息 -->
              <a-space direction="vertical" :size="8" style="width: 100%; margin-top: 16px">
                <div class="poll-info">
                  <span class="info-label">类型：</span>
                  <a-tag :color="poll.poll_type === 'single' ? 'blue' : 'purple'">
                    {{ poll.poll_type === 'single' ? '单选' : '多选' }}
                  </a-tag>
                </div>

                <div class="poll-info">
                  <span class="info-label">截止时间：</span>
                  <span>{{ formatTime(poll.end_time) }}</span>
                </div>

                <div v-if="poll.results" class="poll-info">
                  <span class="info-label">参与人数：</span>
                  <span class="info-value">{{ poll.results.total_votes }} 人</span>
                </div>
              </a-space>

              <!-- 操作按钮 -->
              <div class="poll-actions">
                <a-space>
                  <a-button
                    v-if="poll.status === 'active' && !poll.has_voted"
                    type="primary"
                    block
                    @click="votePoll(poll)"
                  >
                    <CheckOutlined /> 立即投票
                  </a-button>

                  <a-button v-else-if="poll.has_voted" block disabled>
                    <CheckCircleOutlined /> 已投票
                  </a-button>

                  <a-button v-else block disabled> 投票已结束 </a-button>

                  <a-button type="link" @click="viewResults(poll)">
                    <BarChartOutlined /> 查看结果
                  </a-button>
                </a-space>
              </div>
            </a-card>
          </a-col>
        </a-row>
      </a-spin>
    </div>

    <!-- 投票对话框 -->
    <a-modal v-model:open="voteModalVisible" title="参与投票" width="600px" :confirm-loading="voteLoading" @ok="handleVote">
      <div v-if="currentPoll">
        <a-alert
          message="请仔细阅读题目，选择后提交"
          type="info"
          show-icon
          style="margin-bottom: 16px"
        />

        <h3 style="font-size: 18px; margin-bottom: 8px">{{ currentPoll.title }}</h3>
        <p style="color: #666; margin-bottom: 24px">{{ currentPoll.description }}</p>

        <a-divider>请选择</a-divider>

        <!-- 单选 -->
        <a-radio-group
          v-if="currentPoll.poll_type === 'single'"
          v-model:value="selectedOptions"
          style="width: 100%"
        >
          <a-space direction="vertical" style="width: 100%" :size="12">
            <a-radio
              v-for="option in currentPoll.options"
              :key="option.id"
              :value="option.id"
              style="display: flex; align-items: center; padding: 12px; border: 1px solid #d9d9d9; border-radius: 4px"
            >
              <span style="font-size: 16px">{{ option.text }}</span>
            </a-radio>
          </a-space>
        </a-radio-group>

        <!-- 多选 -->
        <a-checkbox-group v-else v-model:value="selectedOptions" style="width: 100%">
          <a-space direction="vertical" style="width: 100%" :size="12">
            <a-checkbox
              v-for="option in currentPoll.options"
              :key="option.id"
              :value="option.id"
              style="display: flex; align-items: center; padding: 12px; border: 1px solid #d9d9d9; border-radius: 4px"
            >
              <span style="font-size: 16px">{{ option.text }}</span>
            </a-checkbox>
          </a-space>
        </a-checkbox-group>
      </div>
    </a-modal>

    <!-- 结果展示对话框 -->
    <a-modal v-model:open="resultsModalVisible" title="投票结果" width="800px" :footer="null">
      <div v-if="pollResults">
        <a-statistic title="总投票数" :value="pollResults.total_votes" suffix="人" style="margin-bottom: 24px" />

        <a-divider>选项统计</a-divider>

        <!-- 图表 -->
        <div ref="chartRef" style="width: 100%; height: 350px; margin-bottom: 24px"></div>

        <!-- 详细列表 -->
        <a-list :data-source="pollResults.option_stats" bordered>
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta :title="item.option_text">
                <template #description>
                  <a-space>
                    <span>{{ item.count }} 票</span>
                    <a-progress
                      :percent="item.percentage"
                      :status="item.percentage > 50 ? 'success' : 'normal'"
                      style="width: 200px"
                    />
                  </a-space>
                </template>
              </a-list-item-meta>
            </a-list-item>
          </template>
        </a-list>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, onUnmounted, computed, watch } from 'vue'
import { message } from 'ant-design-vue'
import { ReloadOutlined, CheckOutlined, CheckCircleOutlined, BarChartOutlined, BookOutlined } from '@ant-design/icons-vue'
import { pollApiGet, pollApiIntPollIdVotePost, pollApiIntPollIdResultsGet, interactionCommonStudentCoursesGet } from '@/api/interactionController'
import { usePollSocket } from '@/composables/useSocket'
import socketService from '@/utils/socket'
import * as echarts from 'echarts'
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

// WebSocket - 注意：courseId初始为null，需要在加载课程后手动加入房间
const { isConnected, onNewPoll, onPollResultsUpdated, onPollEnded, notifyPollVoted, joinCourse: joinPollCourse } = usePollSocket(
  courseId.value,
  userId.value,
  userName.value
)

// 数据
const loading = ref(false)
const polls = ref<any[]>([])
const filterStatus = ref('all')

// 投票
const voteModalVisible = ref(false)
const voteLoading = ref(false)
const currentPoll = ref<any>(null)
const selectedOptions = ref<any>(null)

// 结果
const resultsModalVisible = ref(false)
const pollResults = ref<any>(null)
const chartRef = ref<HTMLElement>()

// 过滤后的投票列表
const filteredPolls = computed(() => {
  if (filterStatus.value === 'all') {
    return polls.value
  } else if (filterStatus.value === 'active') {
    return polls.value.filter((p) => p.status === 'active')
  } else if (filterStatus.value === 'ended') {
    return polls.value.filter((p) => p.status === 'ended')
  } else if (filterStatus.value === 'voted') {
    return polls.value.filter((p) => p.has_voted)
  }
  return polls.value
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
        
        // 加入WebSocket房间
        if (isConnected.value && courseId.value && userId.value) {
          joinPollCourse(courseId.value, userId.value, userName.value)
        }
        
        // 加载第一个课程的数据
        loadPolls()
      } else {
        message.warning('您还没有选修任何课程')
      }
    }
  } catch (error: any) {
    console.error('加载课程列表失败:', error)
    message.error(error.response?.data?.message || '加载课程列表失败')
  }
}

// 处理课程切换
const handleCourseChange = () => {
  // 切换课程时重新加载数据
  loadPolls()
}

// 加载投票列表
const loadPolls = async () => {
  if (!courseId.value) return
  
  loading.value = true
  try {
    const response = await pollApiGet({
      courseId: courseId.value,
      page: 1,
      perPage: 100,
    })

    // 后端返回的结构是 response.data.data.items，不是 polls
    const data = response.data?.data || response.data || {}
    polls.value = data.items || data.polls || []

    // has_voted 已经由后端在 list_polls 中设置好了，不需要手动设置
  } catch (error: any) {
    console.error('加载投票列表失败:', error)
    message.error(error.response?.data?.message || '加载投票列表失败')
    polls.value = []
  } finally {
    loading.value = false
  }
}

// 参与投票
const votePoll = (poll: any) => {
  currentPoll.value = poll
  selectedOptions.value = poll.poll_type === 'single' ? null : []
  voteModalVisible.value = true
}

// 提交投票
const handleVote = async () => {
  if (!currentPoll.value) return

  // 验证选择
  if (currentPoll.value.poll_type === 'single') {
    if (selectedOptions.value === null) {
      message.warning('请选择一个选项')
      return
    }
  } else {
    if (!selectedOptions.value || selectedOptions.value.length === 0) {
      message.warning('请至少选择一个选项')
      return
    }
  }

  voteLoading.value = true
  try {
    const data = {
      selectedOptions: Array.isArray(selectedOptions.value) ? selectedOptions.value : [selectedOptions.value],
    }

    await pollApiIntPollIdVotePost({ pollId: currentPoll.value.id }, data)

    // 获取最新结果并通知
    const resultsResponse = await pollApiIntPollIdResultsGet({ pollId: currentPoll.value.id })
    
    // 确保使用正确的courseId发送WebSocket事件
    if (courseId.value) {
      console.log('发送投票通知:', { courseId: courseId.value, pollId: currentPoll.value.id, results: resultsResponse.data.data })
      socketService.notifyPollVoted(courseId.value, currentPoll.value.id, resultsResponse.data.data)
    }

    message.success('投票成功！')
    voteModalVisible.value = false

    // 更新本地状态
    const poll = polls.value.find((p) => p.id === currentPoll.value!.id)
    if (poll) {
      poll.has_voted = true
    }

    loadPolls()
  } catch (error: any) {
    message.error(error.response?.data?.message || '投票失败')
  } finally {
    voteLoading.value = false
  }
}

// 查看结果
const viewResults = async (poll: any) => {
  try {
    const response = await pollApiIntPollIdResultsGet({ pollId: poll.id })
    pollResults.value = response.data.data
    resultsModalVisible.value = true

    setTimeout(() => {
      renderChart()
    }, 100)
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载结果失败')
  }
}

// 渲染图表
const renderChart = () => {
  if (!chartRef.value || !pollResults.value) return

  const chart = echarts.init(chartRef.value)

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} 票 ({d}%)',
    },
    legend: {
      orient: 'vertical',
      left: 'left',
    },
    series: [
      {
        name: '投票结果',
        type: 'pie',
        radius: '60%',
        data: pollResults.value.option_stats.map((s: any) => ({
          name: s.option_text,
          value: s.count,
        })),
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)',
          },
        },
      },
    ],
  }

  chart.setOption(option)

  window.addEventListener('resize', () => {
    chart.resize()
  })
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

  onNewPoll((data) => {
    message.info('教师发布了新投票')
    loadPolls()
  })

  onPollResultsUpdated((data) => {
    if (resultsModalVisible.value && pollResults.value) {
      pollResults.value = data.results
      renderChart()
    }
  })

  onPollEnded((data) => {
    message.info('投票已结束')
    loadPolls()
  })
})

// 监听 WebSocket 连接状态，连接成功后加入课程房间
watch(isConnected, (connected) => {
  if (connected && courseId.value && userId.value) {
    console.log('WebSocket 已连接，加入投票课程房间:', courseId.value)
    setTimeout(() => {
      if (courseId.value && userId.value) {
        joinPollCourse(courseId.value, userId.value, userName.value)
      }
    }, 100)
  }
})

onUnmounted(() => {
  if (chartRef.value) {
    const chart = echarts.getInstanceByDom(chartRef.value)
    chart?.dispose()
  }
})
</script>

<style scoped lang="scss">
.poll-page {
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

// 投票卡片样式
.poll-card {
  height: 100%;
  border-radius: 16px;
  border: none;
  overflow: hidden;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  background: #ffffff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);

  &:hover {
    transform: translateY(-8px);
    box-shadow: 0 12px 32px rgba(102, 126, 234, 0.2);
  }
}

.poll-title {
  font-size: 20px;
  font-weight: 700;
  margin: 0 0 12px 0;
  color: #1a1a1a;
  line-height: 1.4;
}

.poll-description {
  color: #666;
  margin: 0 0 20px 0;
  min-height: 44px;
  font-size: 14px;
  line-height: 1.6;
}

.poll-info {
  display: flex;
  align-items: center;
  font-size: 14px;
  padding: 8px 0;

  .info-label {
    color: #999;
    margin-right: 8px;
    font-weight: 500;
  }

  .info-value {
    font-weight: 700;
    color: #667eea;
    font-size: 16px;
  }
}

.poll-actions {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 2px solid #f0f0f0;
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
}
</style>
