<template>
  <div class="poll-page">
    <a-page-header title="课堂投票管理">
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
          <a-badge :status="isConnected ? 'success' : 'error'"
                   :text="isConnected ? 'WebSocket已连接' : 'WebSocket未连接'"/>
          <a-button v-if="isTeacher" :disabled="!courseId" type="primary" @click="showCreateModal">
            <template #icon>
              <PlusOutlined/>
            </template>
            创建投票
          </a-button>
          <a-button :disabled="!courseId" @click="loadPolls">
            <template #icon>
              <ReloadOutlined/>
            </template>
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-container">
      <!-- 投票列表 -->
      <a-spin :spinning="loading">
        <a-empty v-if="!courseId" description="请先选择课程"/>
        <a-empty v-else-if="polls.length === 0 && !loading" description="暂无投票"/>

        <a-row v-else :gutter="[16, 16]">
          <a-col v-for="poll in polls" :key="poll.id" :lg="8" :md="12" :sm="24" :xs="24">
            <a-card :hoverable="true" class="poll-card">
              <!-- 投票状态标签 -->
              <template #extra>
                <a-tag :color="poll.status === 'active' ? 'green' : 'default'">
                  {{ poll.status === 'active' ? '进行中' : '已结束' }}
                </a-tag>
              </template>

              <!-- 投票标题 -->
              <h3 class="poll-title">{{ poll.title }}</h3>
              <p class="poll-description">{{ poll.description }}</p>

              <!-- 投票信息 -->
              <a-space :size="8" direction="vertical" style="width: 100%; margin-top: 16px">
                <div class="poll-info">
                  <span class="info-label">类型：</span>
                  <a-tag :color="poll.poll_type === 'single' ? 'blue' : 'purple'">
                    {{ poll.poll_type === 'single' ? '单选' : '多选' }}
                  </a-tag>
                </div>

                <div class="poll-info">
                  <span class="info-label">时间：</span>
                  <span>{{ formatTime(poll.start_time) }} ~ {{ formatTime(poll.end_time) }}</span>
                </div>

                <div v-if="poll.results" class="poll-info">
                  <span class="info-label">投票数：</span>
                  <span class="info-value">{{ poll.results.total_votes }} 票</span>
                </div>
              </a-space>

              <!-- 操作按钮 -->
              <div class="poll-actions">
                <a-space>
                  <a-button size="small" type="link" @click="viewPollDetail(poll)">
                    <EyeOutlined/>
                    查看详情
                  </a-button>

                  <a-button
                      v-if="isStudent && poll.status === 'active' && !poll.has_voted"
                      size="small"
                      type="primary"
                      @click="votePoll(poll)"
                  >
                    <CheckOutlined/>
                    参与投票
                  </a-button>

                  <a-button v-if="isStudent && poll.has_voted" disabled size="small">
                    <CheckCircleOutlined/>
                    已投票
                  </a-button>

                  <a-button v-if="isTeacher" size="small" type="link" @click="viewResults(poll)">
                    <BarChartOutlined/>
                    查看结果
                  </a-button>

                  <a-button
                      v-if="isTeacher && poll.status === 'active'"
                      danger
                      size="small"
                      type="link"
                      @click="closePoll(poll)"
                  >
                    <StopOutlined/>
                    关闭投票
                  </a-button>
                </a-space>
              </div>
            </a-card>
          </a-col>
        </a-row>

        <!-- 分页 -->
        <div v-if="pagination.total > 0" class="pagination-container">
          <a-pagination
              v-model:current="pagination.current"
              v-model:page-size="pagination.pageSize"
              :show-size-changer="true"
              :show-total="(total) => `共 ${total} 条`"
              :total="pagination.total"
              @change="handlePageChange"
          />
        </div>
      </a-spin>
    </div>

    <!-- 创建投票对话框 -->
    <a-modal
        v-model:open="createModalVisible"
        :confirm-loading="createLoading"
        title="创建投票"
        width="700px"
        @ok="handleCreatePoll"
    >
      <a-form ref="createFormRef" :model="pollForm" :rules="pollRules" layout="vertical">
        <a-form-item label="投票标题" name="title">
          <a-input v-model:value="pollForm.title" :maxlength="100" placeholder="请输入投票标题" show-count/>
        </a-form-item>

        <a-form-item label="投票描述" name="description">
          <a-textarea
              v-model:value="pollForm.description"
              :maxlength="500"
              :rows="3"
              placeholder="请输入投票描述（可选）"
              show-count
          />
        </a-form-item>

        <a-form-item label="投票类型" name="pollType">
          <a-radio-group v-model:value="pollForm.pollType">
            <a-radio value="single">单选</a-radio>
            <a-radio value="multiple">多选</a-radio>
          </a-radio-group>
        </a-form-item>

        <a-form-item label="投票选项" required>
          <div v-for="(option, index) in pollForm.options" :key="index" class="option-item">
            <a-input
                v-model:value="option.text"
                :maxlength="100"
                :placeholder="`选项 ${index + 1}`"
                style="flex: 1"
            />
            <a-button :disabled="pollForm.options.length <= 2" danger type="text" @click="removeOption(index)">
              <DeleteOutlined/>
            </a-button>
          </div>
          <a-button block style="margin-top: 8px" type="dashed" @click="addOption">
            <PlusOutlined/>
            添加选项
          </a-button>
        </a-form-item>

        <a-form-item label="结束时间" name="endTime">
          <a-space direction="vertical" style="width: 100%">
            <a-space>
              <a-button size="small" @click="setEndTime(30)">30分钟后</a-button>
              <a-button size="small" @click="setEndTime(60)">1小时后</a-button>
              <a-button size="small" @click="setEndTime(120)">2小时后</a-button>
              <a-button size="small" @click="setEndTime(1440)">1天后</a-button>
            </a-space>
            <a-date-picker
                v-model:value="pollForm.endTime"
                :disabled-date="disabledDate"
                :show-time="{
                defaultValue: dayjs().hour(23).minute(59).second(59),
                format: 'HH:mm:ss'
              }"
                format="YYYY-MM-DD HH:mm:ss"
                placeholder="选择结束时间"
                show-time
                style="width: 100%"
                @ok="handleEndTimeOk"
            />
          </a-space>
        </a-form-item>

        <a-form-item name="isAnonymous">
          <a-checkbox v-model:checked="pollForm.isAnonymous"> 匿名投票</a-checkbox>
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 投票对话框 -->
    <a-modal v-model:open="voteModalVisible" :confirm-loading="voteLoading" title="参与投票" @ok="handleVote">
      <div v-if="currentPoll">
        <h3>{{ currentPoll.title }}</h3>
        <p style="color: #666">{{ currentPoll.description }}</p>

        <a-divider/>

        <a-radio-group
            v-if="currentPoll.poll_type === 'single'"
            v-model:value="selectedOptions"
            style="width: 100%"
        >
          <a-space direction="vertical" style="width: 100%">
            <a-radio v-for="option in currentPoll.options" :key="option.id" :value="option.id" style="display: block">
              {{ option.text }}
            </a-radio>
          </a-space>
        </a-radio-group>

        <a-checkbox-group v-else v-model:value="selectedOptions" style="width: 100%">
          <a-space direction="vertical" style="width: 100%">
            <a-checkbox v-for="option in currentPoll.options" :key="option.id" :value="option.id">
              {{ option.text }}
            </a-checkbox>
          </a-space>
        </a-checkbox-group>
      </div>
    </a-modal>

    <!-- 投票详情对话框 -->
    <a-modal v-model:open="detailModalVisible" :footer="null" title="投票详情" width="800px">
      <div v-if="currentPoll">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item :span="2" label="投票标题">
            {{ currentPoll.title }}
          </a-descriptions-item>
          <a-descriptions-item :span="2" label="投票描述">
            {{ currentPoll.description || '无' }}
          </a-descriptions-item>
          <a-descriptions-item label="投票类型">
            <a-tag :color="currentPoll.poll_type === 'single' ? 'blue' : 'purple'">
              {{ currentPoll.poll_type === 'single' ? '单选' : '多选' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="投票状态">
            <a-tag :color="currentPoll.status === 'active' ? 'green' : 'default'">
              {{ currentPoll.status === 'active' ? '进行中' : '已结束' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="开始时间">
            {{ formatTime(currentPoll.start_time) }}
          </a-descriptions-item>
          <a-descriptions-item label="结束时间">
            {{ formatTime(currentPoll.end_time) }}
          </a-descriptions-item>
          <a-descriptions-item label="是否匿名">
            {{ currentPoll.is_anonymous ? '是' : '否' }}
          </a-descriptions-item>
          <a-descriptions-item label="总投票数">
            {{ currentPoll.results?.total_votes || 0 }} 票
          </a-descriptions-item>
        </a-descriptions>

        <a-divider>投票选项</a-divider>

        <a-list :data-source="currentPoll.options" bordered>
          <template #renderItem="{ item, index }">
            <a-list-item>
              <span>选项 {{ index + 1 }}：{{ item.text }}</span>
            </a-list-item>
          </template>
        </a-list>

        <a-divider>学生投票详情</a-divider>

        <a-table
            :columns="responseColumns"
            :data-source="pollResponses"
            :pagination="{ pageSize: 10 }"
            :scroll="{ x: 600 }"
            bordered
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'selected_options'">
              <a-space>
                <a-tag v-for="optionIndex in record.selected_options" :key="optionIndex" color="blue">
                  {{ currentPoll.options[optionIndex]?.text || `选项${optionIndex + 1}` }}
                </a-tag>
              </a-space>
            </template>
            <template v-else-if="column.key === 'created_at'">
              {{ formatTime(record.created_at) }}
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>

    <!-- 结果展示对话框 -->
    <a-modal v-model:open="resultsModalVisible" :footer="null" title="投票结果" width="900px">
      <div v-if="pollResults">
        <a-statistic :value="pollResults.total_votes" style="margin-bottom: 24px" suffix="票" title="总投票数"/>

        <a-divider>选项统计</a-divider>

        <!-- 图表 -->
        <div ref="chartRef" style="width: 100%; height: 400px; margin-bottom: 24px"></div>

        <!-- 详细数据 -->
        <a-table :columns="resultColumns" :data-source="pollResults.option_stats" :pagination="false" bordered>
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'percentage'">
              <a-progress :percent="record.percentage" :status="record.percentage > 50 ? 'success' : 'normal'"/>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, onUnmounted, reactive, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {
  BarChartOutlined,
  CheckCircleOutlined,
  CheckOutlined,
  DeleteOutlined,
  EyeOutlined,
  PlusOutlined,
  ReloadOutlined,
  StopOutlined,
} from '@ant-design/icons-vue'
import {
  interactionCommonTeacherCoursesGet,
  pollApiGet,
  pollApiIntPollIdClosePut,
  pollApiIntPollIdResponsesGet,
  pollApiIntPollIdResultsGet,
  pollApiIntPollIdVotePost,
  pollApiPost,
} from '@/api/interactionController'
import {usePollSocket} from '@/composables/useSocket'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

// 用户信息（从store或路由获取）
const userRole = ref('teacher') // 'teacher' | 'student'
const userId = ref(1)
const userName = ref('测试用户')
const courseId = ref<number | null>(null) // 从课程列表选择
const courses = ref<any[]>([]) // 教师的课程列表

const isTeacher = computed(() => userRole.value === 'teacher')
const isStudent = computed(() => userRole.value === 'student')

// 从localStorage获取当前用户信息
const loadCurrentUser = () => {
  try {
    const userStr = localStorage.getItem('user')
    if (userStr) {
      const user = JSON.parse(userStr)
      userId.value = user.id
      userName.value = user.real_name || user.username || '教师'
      console.log('当前用户:', {id: userId.value, name: userName.value})
    }
  } catch (error) {
    console.error('加载用户信息失败:', error)
  }
}

// WebSocket连接
const {
  isConnected,
  onNewPoll,
  onPollResultsUpdated,
  onPollEnded,
  notifyPollCreated,
  notifyPollVoted,
  notifyPollClosed,
  joinCourse: joinPollCourse
} =
    usePollSocket(courseId.value, userId.value, userName.value)

// 数据
const loading = ref(false)
const polls = ref<any[]>([])
const pagination = reactive({
  current: 1,
  pageSize: 12,
  total: 0,
})

// 创建投票
const createModalVisible = ref(false)
const createLoading = ref(false)
const createFormRef = ref()
const pollForm = reactive({
  title: '',
  description: '',
  pollType: 'single' as 'single' | 'multiple',
  options: [
    {id: 1, text: ''},
    {id: 2, text: ''},
  ],
  endTime: null as any,
  isAnonymous: false,
})

const pollRules = {
  title: [{required: true, message: '请输入投票标题', trigger: 'blur'}],
  pollType: [{required: true, message: '请选择投票类型', trigger: 'change'}],
  endTime: [{required: true, message: '请选择结束时间', trigger: 'change'}],
}

// 投票
const voteModalVisible = ref(false)
const voteLoading = ref(false)
const currentPoll = ref<any>(null)
const selectedOptions = ref<any>(null)

// 详情
const detailModalVisible = ref(false)

// 结果
const resultsModalVisible = ref(false)
const pollResults = ref<any>(null)
const chartRef = ref<HTMLElement>()

const resultColumns = [
  {title: '选项', dataIndex: 'option_text', key: 'option_text'},
  {title: '票数', dataIndex: 'count', key: 'count'},
  {title: '百分比', dataIndex: 'percentage', key: 'percentage'},
]

// 响应列表表格列定义
const responseColumns = [
  {title: '学生姓名', dataIndex: 'student_name', key: 'student_name', width: 120},
  {title: '学号/用户名', dataIndex: 'student_username', key: 'student_username', width: 150},
  {title: '选择的选项', dataIndex: 'selected_options', key: 'selected_options', width: 300},
  {title: '投票时间', dataIndex: 'created_at', key: 'created_at', width: 180},
]

// 加载教师的课程列表
const loadCourses = async () => {
  try {
    const response = await interactionCommonTeacherCoursesGet()

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
      page: pagination.current,
      perPage: pagination.pageSize,
    })

    // 安全地访问数据
    const data = response.data?.data || response.data || {}
    polls.value = data.items || data.polls || []
    pagination.total = data.total || 0

    // 如果是学生，检查是否已投票（这里简化处理，实际应该从后端返回）
    if (isStudent.value) {
      polls.value.forEach((poll) => {
        poll.has_voted = false // 实际应该从后端获取
      })
    }
  } catch (error: any) {
    console.error('加载投票列表失败:', error)
    message.error(error.response?.data?.message || '加载投票列表失败')
    // 确保polls是数组
    polls.value = []
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateModal = () => {
  createModalVisible.value = true
  // 重置表单
  pollForm.title = ''
  pollForm.description = ''
  pollForm.pollType = 'single'
  pollForm.options = [
    {id: 1, text: ''},
    {id: 2, text: ''},
  ]
  pollForm.endTime = null
  pollForm.isAnonymous = false
}

// 设置结束时间（快捷按钮）
const setEndTime = (minutes: number) => {
  pollForm.endTime = dayjs().add(minutes, 'minute')
}

// 处理确认选择时间（当用户点击Ok按钮时）
const handleEndTimeOk = (value: any) => {
  if (value) {
    const selectedDate = dayjs(value)
    const today = dayjs().startOf('day')
    const selectedDay = selectedDate.startOf('day')

    // 如果选择的日期不是今天，无条件设置为23:59:59
    if (!selectedDay.isSame(today, 'day')) {
      pollForm.endTime = selectedDate.hour(23).minute(59).second(59)
    }
  }
}

// 添加选项
const addOption = () => {
  const newId = Math.max(...pollForm.options.map((o) => o.id)) + 1
  pollForm.options.push({id: newId, text: ''})
}

// 删除选项
const removeOption = (index: number) => {
  pollForm.options.splice(index, 1)
}

// 禁用过去的日期和时间
const disabledDate = (current: any) => {
  return current && current < dayjs().startOf('day')
}

// 创建投票
const handleCreatePoll = async () => {
  try {
    await createFormRef.value.validate()

    // 验证选项
    const validOptions = pollForm.options.filter((opt) => opt.text.trim())
    if (validOptions.length < 2) {
      message.error('至少需要2个有效选项')
      return
    }

    // 验证结束时间
    if (!pollForm.endTime) {
      message.error('请选择结束时间')
      return
    }

    createLoading.value = true

    const data = {
      title: pollForm.title,
      description: pollForm.description,
      courseId: courseId.value,
      pollType: pollForm.pollType,
      options: validOptions,
      isAnonymous: pollForm.isAnonymous,
      startTime: dayjs().toISOString(), // 开始时间为当前时间
      endTime: pollForm.endTime.toISOString(), // 结束时间由用户选择
    }

    const response = await pollApiPost(data)

    // 通过WebSocket通知其他用户
    notifyPollCreated(response.data.data)

    message.success('投票创建成功')
    createModalVisible.value = false
    loadPolls()
  } catch (error: any) {
    if (error.errorFields) {
      // 表单验证错误
      return
    }
    message.error(error.response?.data?.message || '创建投票失败')
  } finally {
    createLoading.value = false
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

    await pollApiIntPollIdVotePost({pollId: currentPoll.value.id}, data)

    // 获取最新结果并通知
    const resultsResponse = await pollApiIntPollIdResultsGet({pollId: currentPoll.value.id})
    notifyPollVoted(currentPoll.value.id, resultsResponse.data.data)

    message.success('投票成功')
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

// 投票响应列表
const pollResponses = ref<any[]>([])

// 查看详情
const viewPollDetail = async (poll: any) => {
  currentPoll.value = poll
  detailModalVisible.value = true

  // 加载最新结果
  try {
    const response = await pollApiIntPollIdResultsGet({pollId: poll.id})
    currentPoll.value.results = response.data.data
  } catch (error) {
    console.error('加载结果失败:', error)
  }

  // 加载投票响应列表
  try {
    const responsesData = await pollApiIntPollIdResponsesGet({pollId: poll.id})
    pollResponses.value = responsesData.data.data.responses
  } catch (error) {
    console.error('加载响应列表失败:', error)
    pollResponses.value = []
  }
}

// 查看结果
const viewResults = async (poll: any) => {
  try {
    const response = await pollApiIntPollIdResultsGet({pollId: poll.id})
    pollResults.value = response.data.data
    resultsModalVisible.value = true

    // 渲染图表
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
    title: {
      text: '投票结果统计',
      left: 'center',
    },
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow',
      },
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true,
    },
    xAxis: {
      type: 'category',
      data: pollResults.value.option_stats.map((s: any) => s.option_text),
      axisLabel: {
        interval: 0,
        rotate: 30,
      },
    },
    yAxis: {
      type: 'value',
      name: '票数',
    },
    series: [
      {
        name: '票数',
        type: 'bar',
        data: pollResults.value.option_stats.map((s: any) => s.count),
        itemStyle: {
          color: '#1890ff',
        },
        label: {
          show: true,
          position: 'top',
          formatter: '{c} 票',
        },
      },
    ],
  }

  chart.setOption(option)

  // 响应式
  window.addEventListener('resize', () => {
    chart.resize()
  })
}

// 关闭投票
const closePoll = async (poll: any) => {
  try {
    await pollApiIntPollIdClosePut({pollId: poll.id})

    // 通知其他用户
    notifyPollClosed(poll.id)

    message.success('投票已关闭')
    loadPolls()
  } catch (error: any) {
    message.error(error.response?.data?.message || '关闭投票失败')
  }
}

// 分页变化
const handlePageChange = (page: number, pageSize: number) => {
  pagination.current = page
  pagination.pageSize = pageSize
  loadPolls()
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm')
}

// WebSocket事件监听
onMounted(() => {
  // 先加载当前用户信息
  loadCurrentUser()

  // 然后加载课程列表
  loadCourses()

  // 监听新投票
  onNewPoll((data) => {
    message.info('有新的投票')
    loadPolls()
  })

  // 监听投票结果更新
  onPollResultsUpdated((data) => {
    console.log('投票结果更新:', data)

    // 更新投票列表中的统计信息
    const poll = polls.value.find((p) => p.id === data.poll_id)
    if (poll) {
      poll.results = data.results
      console.log(`更新投票 ${data.poll_id} 的统计信息:`, data.results)
    }

    // 如果正在查看结果对话框，也更新对话框中的数据
    if (resultsModalVisible.value && pollResults.value) {
      pollResults.value = data.results
      renderChart()
    }

    // 如果正在查看详情对话框，也更新详情中的数据
    if (detailModalVisible.value && currentPoll.value && currentPoll.value.id === data.poll_id) {
      currentPoll.value.results = data.results
    }
  })

  // 监听投票结束
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
  // 清理图表
  if (chartRef.value) {
    const chart = echarts.getInstanceByDom(chartRef.value)
    chart?.dispose()
  }
})
</script>

<style lang="scss" scoped>
.poll-page {
  min-height: 100vh;
  background: var(--bg-color);
}

.content-container {
  padding: 24px;
}

.poll-card {
  height: 100%;
  transition: all 0.3s;

  &:hover {
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  }
}

.poll-title {
  font-size: 18px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-color);
}

.poll-description {
  color: var(--text-color-secondary);
  margin: 0 0 16px 0;
  min-height: 40px;
}

.poll-info {
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

.poll-actions {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.option-item {
  display: flex;
  gap: 8px;
  margin-bottom: 8px;
  align-items: center;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}
</style>
