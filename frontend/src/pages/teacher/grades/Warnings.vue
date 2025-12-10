<template>
  <div class="warnings-container">
    <a-card :bordered="false" title="📊 学情预警管理">
      <!-- 筛选区域 -->
      <a-form :model="filterForm" class="filter-form" layout="inline">
        <a-form-item label="课程">
          <a-select
              v-model:value="filterForm.courseId"
              :loading="coursesLoading"
              placeholder="请选择课程"
              style="width: 200px"
              @change="handleCourseChange"
          >
            <a-select-option
                v-for="course in courses"
                :key="course.id"
                :value="course.id"
            >
              {{ course.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="班级">
          <a-select
              v-model:value="filterForm.classId"
              :disabled="!filterForm.courseId"
              allowClear
              placeholder="全部班级"
              style="width: 150px"
          >
            <a-select-option
                v-for="cls in classes"
                :key="cls.id"
                :value="cls.id"
            >
              {{ cls.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="风险等级">
          <a-select
              v-model:value="filterForm.riskLevel"
              allowClear
              placeholder="全部等级"
              style="width: 150px"
          >
            <a-select-option value="high">🔴 高风险</a-select-option>
            <a-select-option value="medium">🟡 中风险</a-select-option>
            <a-select-option value="low">🟢 低风险</a-select-option>
            <a-select-option value="none">⚪ 无风险</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item>
          <a-space>
            <a-button
                :disabled="!filterForm.courseId"
                :loading="loading"
                type="primary"
                @click="loadWarnings"
            >
              <SearchOutlined/>
              查询
            </a-button>
            <a-button
                :disabled="!filterForm.courseId"
                type="primary"
                @click="showGenerateModal"
            >
              <ThunderboltOutlined/>
              生成预警
            </a-button>
            <a-button
                :disabled="selectedRowKeys.length === 0"
                @click="handleBatchSend"
            >
              <MailOutlined/>
              批量发送通知
            </a-button>
          </a-space>
        </a-form-item>
      </a-form>

      <!-- 统计信息 -->
      <a-alert
          v-if="statistics"
          :message="`共 ${statistics.total} 条预警记录`"
          class="statistics-alert"
          closable
          show-icon
          type="info"
      >
        <template #description>
          <a-space>
            <span>🔴 高风险: {{ statistics.highRisk }}</span>
            <span>🟡 中风险: {{ statistics.mediumRisk }}</span>
            <span>🟢 低风险: {{ statistics.lowRisk }}</span>
            <span>⚪ 无风险: {{ statistics.noRisk }}</span>
          </a-space>
        </template>
      </a-alert>

      <!-- 预警列表 -->
      <a-table
          :columns="columns"
          :data-source="warnings"
          :loading="loading"
          :pagination="false"
          :row-selection="{
          selectedRowKeys: selectedRowKeys,
          onChange: onSelectChange,
        }"
          :scroll="{ x: 1200 }"
          class="warnings-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'riskLevel'">
            <a-tag :color="getRiskColor(record.riskLevel)">
              {{ getRiskText(record.riskLevel) }}
            </a-tag>
          </template>

          <template v-if="column.key === 'predictedScore'">
            <span :style="{ color: getScoreColor(record.predictedScore) }">
              {{ record.predictedScore }}
            </span>
          </template>

          <template v-if="column.key === 'confidence'">
            <a-progress
                :percent="record.confidence"
                :stroke-color="getConfidenceColor(record.confidence)"
                size="small"
            />
          </template>

          <template v-if="column.key === 'isSent'">
            <a-tag :color="record.isSent ? 'green' : 'default'">
              {{ record.isSent ? '已发送' : '未发送' }}
            </a-tag>
          </template>

          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" type="link" @click="viewDetail(record)">
                查看详情
              </a-button>
              <a-button
                  size="small"
                  type="link"
                  @click="showInterventionModal(record)"
              >
                记录干预
              </a-button>
              <a-button
                  :disabled="record.isSent"
                  size="small"
                  type="link"
                  @click="sendNotification(record.id)"
              >
                发送通知
              </a-button>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 生成预警对话框 -->
    <a-modal
        v-model:open="generateModalVisible"
        :confirm-loading="generating"
        title="生成预警预测"
        @ok="handleGenerate"
    >
      <a-form :model="generateForm" layout="vertical">
        <a-form-item label="课程">
          <a-select v-model:value="generateForm.courseId" disabled>
            <a-select-option
                v-for="course in courses"
                :key="course.id"
                :value="course.id"
            >
              {{ course.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="班级(可选)">
          <a-select
              v-model:value="generateForm.classId"
              allowClear
              placeholder="不选择则为全部班级"
          >
            <a-select-option
                v-for="cls in classes"
                :key="cls.id"
                :value="cls.id"
            >
              {{ cls.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-alert
            description="系统将基于学生的历史成绩(平时、期中等)预测期末成绩,并根据预测结果生成预警。至少需要2次成绩记录才能进行预测。"
            message="预测说明"
            show-icon
            type="info"
        />
      </a-form>
    </a-modal>

    <!-- 添加干预记录对话框 -->
    <a-modal
        v-model:open="interventionModalVisible"
        :confirm-loading="addingIntervention"
        title="记录干预措施"
        width="600px"
        @ok="handleAddIntervention"
    >
      <a-form :model="interventionForm" layout="vertical">
        <a-form-item label="学生信息">
          <a-input
              :value="`${currentWarning?.studentName} (${currentWarning?.studentCode})`"
              disabled
          />
        </a-form-item>

        <a-form-item label="干预日期" required>
          <a-date-picker
              v-model:value="interventionForm.interventionDate"
              style="width: 100%"
          />
        </a-form-item>

        <a-form-item label="干预方式" required>
          <a-select v-model:value="interventionForm.interventionType">
            <a-select-option value="talk">💬 谈话</a-select-option>
            <a-select-option value="tutoring">📚 辅导</a-select-option>
            <a-select-option value="homework">📝 作业</a-select-option>
            <a-select-option value="other">🔧 其他</a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="干预内容" required>
          <a-textarea
              v-model:value="interventionForm.description"
              :rows="4"
              placeholder="请详细描述干预措施的具体内容..."
          />
        </a-form-item>

        <a-form-item label="预期效果">
          <a-textarea
              v-model:value="interventionForm.expectedEffect"
              :rows="2"
              placeholder="预期达到的效果..."
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 预警详情抽屉 -->
    <a-drawer
        v-model:open="detailDrawerVisible"
        :body-style="{ paddingBottom: '80px' }"
        title="预警详情"
        width="800"
    >
      <div v-if="currentDetail" class="detail-content">
        <!-- 学生基本信息 -->
        <a-descriptions :column="2" bordered title="学生信息">
          <a-descriptions-item label="姓名">
            {{ currentDetail.studentName }}
          </a-descriptions-item>
          <a-descriptions-item label="学号">
            {{ currentDetail.studentCode }}
          </a-descriptions-item>
          <a-descriptions-item :span="2" label="邮箱">
            {{ currentDetail.studentEmail || '未设置' }}
          </a-descriptions-item>
        </a-descriptions>

        <!-- 预测信息 -->
        <a-descriptions
            :column="2"
            bordered
            style="margin-top: 20px"
            title="预测信息"
        >
          <a-descriptions-item label="课程">
            {{ currentDetail.courseName }}
          </a-descriptions-item>
          <a-descriptions-item label="预测日期">
            {{ currentDetail.predictionDate }}
          </a-descriptions-item>
          <a-descriptions-item label="预测分数">
            <span :style="{ color: getScoreColor(currentDetail.predictedScore) }">
              {{ currentDetail.predictedScore }} 分
            </span>
          </a-descriptions-item>
          <a-descriptions-item label="置信度">
            {{ currentDetail.confidence }}%
          </a-descriptions-item>
          <a-descriptions-item label="风险等级">
            <a-tag :color="getRiskColor(currentDetail.riskLevel)">
              {{ getRiskText(currentDetail.riskLevel) }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="通知状态">
            <a-tag :color="currentDetail.isSent ? 'green' : 'default'">
              {{ currentDetail.isSent ? '已发送' : '未发送' }}
            </a-tag>
          </a-descriptions-item>
        </a-descriptions>

        <!-- 历史成绩趋势 -->
        <div style="margin-top: 20px">
          <h3>📈 历史成绩趋势</h3>
          <div ref="chartRef" style="width: 100%; height: 300px"></div>
        </div>

        <!-- 干预记录 -->
        <div style="margin-top: 20px">
          <h3>📋 干预记录 ({{ currentDetail.interventions?.length || 0 }})</h3>
          <a-timeline v-if="currentDetail.interventions?.length > 0">
            <a-timeline-item
                v-for="intervention in currentDetail.interventions"
                :key="intervention.id"
                :color="getInterventionColor(intervention.interventionType)"
            >
              <p>
                <strong>{{ formatInterventionType(intervention.interventionType) }}</strong>
                <span style="margin-left: 10px; color: #999">
                  {{ intervention.interventionDate }}
                </span>
                <span style="margin-left: 10px; color: #999">
                  教师: {{ intervention.teacherName }}
                </span>
              </p>
              <p>{{ intervention.description }}</p>
              <p v-if="intervention.expectedEffect">
                <strong>预期效果:</strong> {{ intervention.expectedEffect }}
              </p>
              <p v-if="intervention.actualEffect">
                <strong>实际效果:</strong> {{ intervention.actualEffect }}
              </p>
              <p v-if="intervention.studentFeedback">
                <strong>学生反馈:</strong> {{ intervention.studentFeedback }}
              </p>
            </a-timeline-item>
          </a-timeline>
          <a-empty v-else description="暂无干预记录"/>
        </div>
      </div>
    </a-drawer>
  </div>
</template>

<script lang="ts" setup>
import {nextTick, onMounted, reactive, ref} from 'vue'
import {message} from 'ant-design-vue'
import {MailOutlined, SearchOutlined, ThunderboltOutlined,} from '@ant-design/icons-vue'
import axios from '@/request'
import type {ECharts} from 'echarts'
import * as echarts from 'echarts'
import dayjs, {Dayjs} from 'dayjs'

// 接口定义
interface Course {
  id: number
  name: string
}

interface Class {
  id: number
  name: string
}

interface Warning {
  id: number
  studentId: number
  studentName: string
  studentCode: string
  className?: string
  courseId: number
  courseName: string
  predictedScore: number
  confidence: number
  riskLevel: string
  predictionDate: string
  isSent: boolean
  interventionCount: number
  createdAt: string
}

interface WarningDetail {
  id: number
  studentId: number
  studentName: string
  studentCode: string
  studentEmail?: string
  courseId: number
  courseName: string
  predictedScore: number
  confidence: number
  riskLevel: string
  predictionDate: string
  isSent: boolean
  historicalGrades: Array<{
    examType: string
    examName?: string
    score: number
    examDate: string
  }>
  interventions: Array<{
    id: number
    predictionId: number
    teacherId: number
    teacherName: string
    interventionDate: string
    interventionType: string
    description: string
    expectedEffect?: string
    actualEffect?: string
    studentFeedback?: string
    createdAt: string
  }>
  createdAt: string
}

// 响应式数据
const courses = ref<Course[]>([])
const classes = ref<Class[]>([])
const warnings = ref<Warning[]>([])
const coursesLoading = ref(false)
const loading = ref(false)
const generating = ref(false)
const addingIntervention = ref(false)

const filterForm = reactive({
  courseId: undefined as number | undefined,
  classId: undefined as number | undefined,
  riskLevel: undefined as string | undefined,
})

const generateForm = reactive({
  courseId: undefined as number | undefined,
  classId: undefined as number | undefined,
})

const interventionForm = reactive({
  interventionDate: dayjs() as Dayjs,
  interventionType: 'talk' as string,
  description: '' as string,
  expectedEffect: '' as string,
})

const generateModalVisible = ref(false)
const interventionModalVisible = ref(false)
const detailDrawerVisible = ref(false)
const currentWarning = ref<Warning | null>(null)
const currentDetail = ref<WarningDetail | null>(null)
const selectedRowKeys = ref<number[]>([])
const chartRef = ref<HTMLElement>()
let chartInstance: ECharts | null = null

// 统计信息
const statistics = ref<{
  total: number
  highRisk: number
  mediumRisk: number
  lowRisk: number
  noRisk: number
} | null>(null)

// 表格列定义
const columns = [
  {
    title: '学号',
    dataIndex: 'studentCode',
    key: 'studentCode',
    width: 120,
  },
  {
    title: '姓名',
    dataIndex: 'studentName',
    key: 'studentName',
    width: 100,
  },
  {
    title: '班级',
    dataIndex: 'className',
    key: 'className',
    width: 120,
  },
  {
    title: '预测分数',
    dataIndex: 'predictedScore',
    key: 'predictedScore',
    width: 100,
  },
  {
    title: '置信度',
    dataIndex: 'confidence',
    key: 'confidence',
    width: 120,
  },
  {
    title: '风险等级',
    dataIndex: 'riskLevel',
    key: 'riskLevel',
    width: 100,
  },
  {
    title: '预测日期',
    dataIndex: 'predictionDate',
    key: 'predictionDate',
    width: 120,
  },
  {
    title: '通知状态',
    dataIndex: 'isSent',
    key: 'isSent',
    width: 100,
  },
  {
    title: '干预次数',
    dataIndex: 'interventionCount',
    key: 'interventionCount',
    width: 100,
  },
  {
    title: '操作',
    key: 'action',
    fixed: 'right' as const,
    width: 250,
  },
]

// 加载课程列表
const loadCourses = async () => {
  coursesLoading.value = true
  try {
    const response = await axios.get('/api/v1/grades/teacher-courses')
    // 后端直接返回数组,axios响应在response.data中
    const data = response.data || response
    courses.value = Array.isArray(data) ? data : []
    console.log('加载课程列表成功:', courses.value)
  } catch (error: any) {
    console.error('加载课程列表失败:', error)
    message.error(error.response?.data?.message || '加载课程列表失败')
  } finally {
    coursesLoading.value = false
  }
}

// 课程变化处理
const handleCourseChange = async (courseId: number) => {
  filterForm.classId = undefined
  classes.value = []

  if (!courseId) return

  try {
    const response = await axios.get('/api/v1/grades/course-students', {
      params: {courseId},
    })

    // 提取唯一的班级列表
    const classMap = new Map<number, string>()
    response.data.forEach((student: any) => {
      if (student.class_id && student.class_name) {
        classMap.set(student.class_id, student.class_name)
      }
    })

    classes.value = Array.from(classMap.entries()).map(([id, name]) => ({
      id,
      name,
    }))
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载班级列表失败')
  }
}

// 加载预警列表
const loadWarnings = async () => {
  if (!filterForm.courseId) {
    message.warning('请先选择课程')
    return
  }

  loading.value = true
  try {
    const response = await axios.get('/api/v1/predictions/list', {
      params: {
        courseId: filterForm.courseId,
        classId: filterForm.classId,
        riskLevel: filterForm.riskLevel,
      },
    })

    warnings.value = response.data.map((item: any) => ({
      id: item.id,
      studentId: item.student_id,
      studentName: item.student_name,
      studentCode: item.student_code,
      className: item.class_name,
      courseId: item.course_id,
      courseName: item.course_name,
      predictedScore: item.predicted_score,
      confidence: item.confidence,
      riskLevel: item.risk_level,
      predictionDate: item.prediction_date,
      isSent: item.is_sent,
      interventionCount: item.intervention_count,
      createdAt: item.created_at,
    }))

    // 计算统计信息
    statistics.value = {
      total: warnings.value.length,
      highRisk: warnings.value.filter((w) => w.riskLevel === 'high').length,
      mediumRisk: warnings.value.filter((w) => w.riskLevel === 'medium').length,
      lowRisk: warnings.value.filter((w) => w.riskLevel === 'low').length,
      noRisk: warnings.value.filter((w) => w.riskLevel === 'none').length,
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载预警列表失败')
  } finally {
    loading.value = false
  }
}

// 显示生成预警对话框
const showGenerateModal = () => {
  generateForm.courseId = filterForm.courseId
  generateForm.classId = filterForm.classId
  generateModalVisible.value = true
}

// 生成预警
const handleGenerate = async () => {
  if (!generateForm.courseId) {
    message.warning('请选择课程')
    return
  }

  generating.value = true
  try {
    const response = await axios.post('/api/v1/predictions/generate', {
      courseId: generateForm.courseId,
      classId: generateForm.classId,
    })

    const result = response.data
    message.success(
        `预警生成成功! 共预测 ${result.predicted_count} 人, ` +
        `高风险 ${result.high_risk_count} 人, ` +
        `中风险 ${result.medium_risk_count} 人, ` +
        `低风险 ${result.low_risk_count} 人, ` +
        `跳过 ${result.skipped_count} 人(成绩不足)`
    )

    generateModalVisible.value = false
    loadWarnings()
  } catch (error: any) {
    message.error(error.response?.data?.message || '生成预警失败')
  } finally {
    generating.value = false
  }
}

// 显示干预记录对话框
const showInterventionModal = (warning: Warning) => {
  currentWarning.value = warning
  interventionForm.interventionDate = dayjs()
  interventionForm.interventionType = 'talk'
  interventionForm.description = ''
  interventionForm.expectedEffect = ''
  interventionModalVisible.value = true
}

// 添加干预记录
const handleAddIntervention = async () => {
  if (!currentWarning.value) return

  if (!interventionForm.description) {
    message.warning('请填写干预内容')
    return
  }

  addingIntervention.value = true
  try {
    await axios.post('/api/v1/predictions/interventions', {
      predictionId: currentWarning.value.id,
      interventionDate: interventionForm.interventionDate.format('YYYY-MM-DD'),
      interventionType: interventionForm.interventionType,
      description: interventionForm.description,
      expectedEffect: interventionForm.expectedEffect || undefined,
    })

    message.success('干预记录添加成功')
    interventionModalVisible.value = false
    loadWarnings()
  } catch (error: any) {
    message.error(error.response?.data?.message || '添加干预记录失败')
  } finally {
    addingIntervention.value = false
  }
}

// 查看详情
const viewDetail = async (warning: Warning) => {
  try {
    const response = await axios.get(`/api/v1/predictions/${warning.id}`)

    currentDetail.value = {
      id: response.data.id,
      studentId: response.data.student_id,
      studentName: response.data.student_name,
      studentCode: response.data.student_code,
      studentEmail: response.data.student_email,
      courseId: response.data.course_id,
      courseName: response.data.course_name,
      predictedScore: response.data.predicted_score,
      confidence: response.data.confidence,
      riskLevel: response.data.risk_level,
      predictionDate: response.data.prediction_date,
      isSent: response.data.is_sent,
      historicalGrades: response.data.historical_grades.map((g: any) => ({
        examType: g.exam_type,
        examName: g.exam_name,
        score: g.score,
        examDate: g.exam_date,
      })),
      interventions: response.data.interventions.map((i: any) => ({
        id: i.id,
        predictionId: i.prediction_id,
        teacherId: i.teacher_id,
        teacherName: i.teacher_name,
        interventionDate: i.intervention_date,
        interventionType: i.intervention_type,
        description: i.description,
        expectedEffect: i.expected_effect,
        actualEffect: i.actual_effect,
        studentFeedback: i.student_feedback,
        createdAt: i.created_at,
      })),
      createdAt: response.data.created_at,
    }

    detailDrawerVisible.value = true

    // 等待DOM更新后渲染图表
    await nextTick()
    renderChart()
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载详情失败')
  }
}

// 渲染成绩趋势图
const renderChart = () => {
  if (!chartRef.value || !currentDetail.value) return

  if (chartInstance) {
    chartInstance.dispose()
  }

  chartInstance = echarts.init(chartRef.value)

  const grades = currentDetail.value.historicalGrades
  const examTypes = grades.map((g) => g.examName || g.examType)
  const scores = grades.map((g) => g.score)

  const option = {
    tooltip: {
      trigger: 'axis',
    },
    xAxis: {
      type: 'category',
      data: examTypes,
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100,
    },
    series: [
      {
        name: '成绩',
        type: 'line',
        data: scores,
        smooth: true,
        itemStyle: {
          color: '#1890ff',
        },
        markLine: {
          data: [
            {yAxis: 60, name: '及格线', lineStyle: {color: '#ff4d4f'}},
          ],
        },
      },
    ],
  }

  chartInstance.setOption(option)
}

// 发送单个通知
const sendNotification = async (predictionId: number) => {
  try {
    await axios.post('/api/v1/predictions/send-notifications', {
      predictionIds: [predictionId],
    })
    message.success('通知发送成功')
    loadWarnings()
  } catch (error: any) {
    message.error(error.response?.data?.message || '发送通知失败')
  }
}

// 批量发送通知
const handleBatchSend = async () => {
  if (selectedRowKeys.value.length === 0) {
    message.warning('请选择要发送通知的预警记录')
    return
  }

  try {
    const response = await axios.post('/api/v1/predictions/send-notifications', {
      predictionIds: selectedRowKeys.value,
    })

    message.success(
        `批量发送完成! 成功 ${response.data.success_count} 条, ` +
        `失败 ${response.data.failed_count} 条`
    )
    selectedRowKeys.value = []
    loadWarnings()
  } catch (error: any) {
    message.error(error.response?.data?.message || '批量发送失败')
  }
}

// 选择变化
const onSelectChange = (keys: number[]) => {
  selectedRowKeys.value = keys
}

// 工具函数
const getRiskColor = (level: string) => {
  const colors: Record<string, string> = {
    high: 'red',
    medium: 'orange',
    low: 'blue',
    none: 'default',
  }
  return colors[level] || 'default'
}

const getRiskText = (level: string) => {
  const texts: Record<string, string> = {
    high: '🔴 高风险',
    medium: '🟡 中风险',
    low: '🟢 低风险',
    none: '⚪ 无风险',
  }
  return texts[level] || level
}

const getScoreColor = (score: number) => {
  if (score < 60) return '#ff4d4f'
  if (score < 70) return '#faad14'
  if (score < 80) return '#1890ff'
  return '#52c41a'
}

const getConfidenceColor = (confidence: number) => {
  if (confidence >= 90) return '#52c41a'
  if (confidence >= 80) return '#1890ff'
  if (confidence >= 70) return '#faad14'
  return '#ff4d4f'
}

const getInterventionColor = (type: string) => {
  const colors: Record<string, string> = {
    talk: 'blue',
    tutoring: 'green',
    homework: 'orange',
    other: 'gray',
  }
  return colors[type] || 'gray'
}

const formatInterventionType = (type: string) => {
  const types: Record<string, string> = {
    talk: '💬 谈话',
    tutoring: '📚 辅导',
    homework: '📝 作业',
    other: '🔧 其他',
  }
  return types[type] || type
}

// 生命周期
onMounted(() => {
  loadCourses()
})
</script>

<style lang="less" scoped>
.warnings-container {
  padding: 24px;
}

.filter-form {
  margin-bottom: 16px;
}

.statistics-alert {
  margin-bottom: 16px;
}

.warnings-table {
  margin-top: 16px;
}

.detail-content {
  h3 {
    margin-top: 20px;
    margin-bottom: 12px;
    font-size: 16px;
    font-weight: 600;
  }
}
</style>
