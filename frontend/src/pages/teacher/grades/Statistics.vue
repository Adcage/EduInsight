<template>
  <div class="statistics-page">
    <a-card :bordered="false" title="成绩统计分析">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <a-form layout="inline">
          <a-form-item label="课程" required>
            <a-select
                v-model:value="filterForm.courseId"
                :loading="loading.courses"
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
                :loading="loading.classes"
                allowClear
                placeholder="全部班级"
                style="width: 200px"
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

          <a-form-item label="考试类型">
            <a-select
                v-model:value="filterForm.examType"
                placeholder="请选择类型"
                style="width: 180px"
            >
              <a-select-option value="daily">平时成绩</a-select-option>
              <a-select-option value="midterm">期中考试</a-select-option>
              <a-select-option value="final">期末考试</a-select-option>
              <a-select-option value="homework">作业</a-select-option>
              <a-select-option value="comprehensive">
                <span style="color: #1890ff; font-weight: 500">📊 综合统计</span>
              </a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item>
            <a-button
                :disabled="!filterForm.courseId"
                :loading="loading.statistics"
                type="primary"
                @click="loadStatistics"
            >
              查询统计
            </a-button>
          </a-form-item>

          <!-- TODO: PDF导出功能 - 待后续实现 -->
          <!-- <a-form-item>
            <a-button
              @click="handleExportPDF"
              :loading="loading.export"
              :disabled="!statisticsData"
            >
              导出PDF报告
            </a-button>
          </a-form-item> -->
        </a-form>
      </div>

      <a-divider/>

      <!-- 统计说明(综合统计时显示) -->
      <a-alert
          v-if="statisticsData && statisticsData.isComprehensive"
          message="综合统计说明"
          show-icon
          style="margin-bottom: 16px"
          type="info"
      >
        <template #description>
          <div>
            <p style="margin: 0">• 总人数: 参与该课程的学生数(按学生去重)</p>
            <p style="margin: 0">• 平均分: 每个学生所有考试类型成绩的平均值,再求总平均</p>
            <p style="margin: 0">• 分数段: 基于学生的平均分进行统计</p>
          </div>
        </template>
      </a-alert>

      <!-- 统计数据展示 -->
      <div v-if="statisticsData" class="statistics-content">
        <!-- 基础统计卡片 -->
        <a-row :gutter="16" style="margin-bottom: 16px">
          <a-col :span="6">
            <a-card>
              <a-statistic
                  :value="statisticsData.basicStatistics.totalCount"
                  :value-style="{ color: '#1890ff' }"
                  title="总人数"
              >
                <template #prefix>
                  <UserOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card>
              <a-statistic
                  :precision="2"
                  :value="statisticsData.basicStatistics.averageScore"
                  :value-style="{ color: '#52c41a' }"
                  title="平均分"
              >
                <template #prefix>
                  <LineChartOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card>
              <a-statistic
                  :precision="2"
                  :value="statisticsData.basicStatistics.passRate"
                  :value-style="{ color: '#faad14' }"
                  suffix="%"
                  title="及格率"
              >
                <template #prefix>
                  <CheckCircleOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card>
              <a-statistic
                  :precision="2"
                  :value="statisticsData.basicStatistics.excellentRate"
                  :value-style="{ color: '#f5222d' }"
                  suffix="%"
                  title="优秀率"
              >
                <template #prefix>
                  <TrophyOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
        </a-row>

        <!-- 详细统计表格 -->
        <a-card style="margin-bottom: 16px" title="详细统计">
          <a-descriptions :column="3" bordered>
            <a-descriptions-item label="最高分">
              {{ statisticsData.basicStatistics.maxScore }}
            </a-descriptions-item>
            <a-descriptions-item label="最低分">
              {{ statisticsData.basicStatistics.minScore }}
            </a-descriptions-item>
            <a-descriptions-item label="中位数">
              {{ statisticsData.basicStatistics.medianScore }}
            </a-descriptions-item>
            <a-descriptions-item label="标准差">
              {{ statisticsData.basicStatistics.stdDeviation }}
            </a-descriptions-item>
            <a-descriptions-item label="课程">
              {{ statisticsData.courseName }}
            </a-descriptions-item>
            <a-descriptions-item label="班级">
              {{ statisticsData.className || '全部班级' }}
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- 图表区域 -->
        <a-row :gutter="16">
          <!-- 分数段分布图 -->
          <a-col :span="12">
            <a-card title="分数段分布">
              <div ref="distributionChartRef" style="width: 100%; height: 400px"></div>
            </a-card>
          </a-col>

          <!-- 成绩趋势图 -->
          <a-col :span="12">
            <a-card title="成绩趋势">
              <div ref="trendChartRef" style="width: 100%; height: 400px"></div>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <!-- 空状态 -->
      <a-empty
          v-else
          description="请选择课程并点击查询统计"
          style="margin: 60px 0"
      />
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import {nextTick, onBeforeUnmount, onMounted, reactive, ref} from 'vue'
import {message} from 'ant-design-vue'
import {CheckCircleOutlined, LineChartOutlined, TrophyOutlined, UserOutlined} from '@ant-design/icons-vue'
import type {ECharts} from 'echarts'
import * as echarts from 'echarts'
import {statisticsApiCourseGet} from '@/api/statisticsController'

// 响应式数据
const filterForm = reactive({
  courseId: undefined as number | undefined,
  classId: undefined as number | undefined,
  examType: undefined as string | undefined
})

const loading = reactive({
  courses: false,
  classes: false,
  statistics: false,
  export: false
})

const courses = ref<any[]>([])
const classes = ref<any[]>([])
const statisticsData = ref<any>(null)

// 图表引用
const distributionChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
let distributionChart: ECharts | null = null
let trendChart: ECharts | null = null

// 加载教师课程列表
const loadCourses = async () => {
  loading.courses = true
  try {
    const response = await fetch('http://localhost:5000/api/v1/grades/teacher-courses', {
      method: 'GET',
      credentials: 'include'
    })

    if (!response.ok) {
      throw new Error('加载课程列表失败')
    }

    courses.value = await response.json()
  } catch (error: any) {
    message.error(error.message || '加载课程列表失败')
  } finally {
    loading.courses = false
  }
}

// 课程变化时加载班级列表
const handleCourseChange = async () => {
  filterForm.classId = undefined
  classes.value = []

  if (!filterForm.courseId) return

  loading.classes = true
  try {
    // 获取课程的班级列表
    const response = await fetch(
        `http://localhost:5000/api/v1/grades/course-students?courseId=${filterForm.courseId}`,
        {
          method: 'GET',
          credentials: 'include'
        }
    )

    if (!response.ok) {
      throw new Error('加载班级列表失败')
    }

    const students = await response.json()
    // 从学生数据中提取唯一的班级
    const classMap = new Map()
    students.forEach((student: any) => {
      if (student.class_id && !classMap.has(student.class_id)) {
        classMap.set(student.class_id, {
          id: student.class_id,  // 使用班级ID
          name: student.class_name || `班级${student.class_id}`
        })
      }
    })
    classes.value = Array.from(classMap.values())
  } catch (error: any) {
    message.error(error.message || '加载班级列表失败')
  } finally {
    loading.classes = false
  }
}

// 加载统计数据
const loadStatistics = async () => {
  if (!filterForm.courseId) {
    message.warning('请先选择课程')
    return
  }

  if (!filterForm.examType) {
    message.warning('请选择考试类型')
    return
  }

  loading.statistics = true
  try {
    const params: any = {
      courseId: filterForm.courseId,
      examType: filterForm.examType
    }

    if (filterForm.classId) {
      params.classId = filterForm.classId
    }

    const response = await statisticsApiCourseGet(params)
    const data = response.data || response

    console.log('📊 原始数据:', data)

    // 转换字段名:下划线 -> 驼峰
    statisticsData.value = {
      basicStatistics: {
        totalCount: data.basic_statistics?.total_count || 0,
        averageScore: data.basic_statistics?.average_score || 0,
        maxScore: data.basic_statistics?.max_score || 0,
        minScore: data.basic_statistics?.min_score || 0,
        medianScore: data.basic_statistics?.median_score || 0,
        stdDeviation: data.basic_statistics?.std_deviation || 0,
        passRate: data.basic_statistics?.pass_rate || 0,
        excellentRate: data.basic_statistics?.excellent_rate || 0
      },
      scoreDistribution: {
        failCount: data.score_distribution?.fail_count || 0,
        passCount: data.score_distribution?.pass_count || 0,
        mediumCount: data.score_distribution?.medium_count || 0,
        goodCount: data.score_distribution?.good_count || 0,
        excellentCount: data.score_distribution?.excellent_count || 0,
        failRate: data.score_distribution?.fail_rate || 0,
        passRate: data.score_distribution?.pass_rate || 0,
        mediumRate: data.score_distribution?.medium_rate || 0,
        goodRate: data.score_distribution?.good_rate || 0,
        excellentRate: data.score_distribution?.excellent_rate || 0
      },
      trendData: (data.trend_data || []).map((item: any) => ({
        examType: item.exam_type,
        examName: item.exam_name,
        examDate: item.exam_date,
        averageScore: item.average_score,
        maxScore: item.max_score,
        minScore: item.min_score
      })),
      courseName: data.course_name,
      className: data.class_name,
      examTypeFilter: data.exam_type_filter,
      isComprehensive: data.is_comprehensive || false
    }

    console.log('📊 转换后数据:', statisticsData.value)

    // 等待DOM更新后渲染图表
    await nextTick()
    renderCharts()

    message.success('统计数据加载成功')
  } catch (error: any) {
    console.error('加载统计失败:', error)
    let errorMsg = '加载统计数据失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.message) {
      errorMsg = error.message
    }
    message.error(errorMsg)
  } finally {
    loading.statistics = false
  }
}

// 渲染图表
const renderCharts = () => {
  if (!statisticsData.value) return

  renderDistributionChart()
  renderTrendChart()
}

// 渲染分数段分布图
const renderDistributionChart = () => {
  if (!distributionChartRef.value) return

  // 销毁旧图表
  if (distributionChart) {
    distributionChart.dispose()
  }

  // 创建新图表
  distributionChart = echarts.init(distributionChartRef.value)

  const dist = statisticsData.value.scoreDistribution

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['人数', '比例']
    },
    xAxis: [
      {
        type: 'category',
        data: ['不及格\n(0-59)', '及格\n(60-69)', '中等\n(70-79)', '良好\n(80-89)', '优秀\n(90-100)'],
        axisPointer: {
          type: 'shadow'
        }
      }
    ],
    yAxis: [
      {
        type: 'value',
        name: '人数',
        min: 0,
        axisLabel: {
          formatter: '{value}'
        }
      },
      {
        type: 'value',
        name: '比例(%)',
        min: 0,
        max: 100,
        axisLabel: {
          formatter: '{value}%'
        }
      }
    ],
    series: [
      {
        name: '人数',
        type: 'bar',
        data: [
          dist.failCount,
          dist.passCount,
          dist.mediumCount,
          dist.goodCount,
          dist.excellentCount
        ],
        itemStyle: {
          color: (params: any) => {
            const colors = ['#ff4d4f', '#faad14', '#1890ff', '#52c41a', '#722ed1']
            return colors[params.dataIndex]
          }
        }
      },
      {
        name: '比例',
        type: 'line',
        yAxisIndex: 1,
        data: [
          dist.failRate,
          dist.passRate,
          dist.mediumRate,
          dist.goodRate,
          dist.excellentRate
        ],
        itemStyle: {
          color: '#f5222d'
        }
      }
    ]
  }

  distributionChart.setOption(option)
}

// 渲染成绩趋势图
const renderTrendChart = () => {
  if (!trendChartRef.value) return

  // 销毁旧图表
  if (trendChart) {
    trendChart.dispose()
  }

  // 创建新图表
  trendChart = echarts.init(trendChartRef.value)

  const trendData = statisticsData.value.trendData

  if (!trendData || trendData.length === 0) {
    // 没有趋势数据
    const option = {
      title: {
        text: '暂无趋势数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    }
    trendChart.setOption(option)
    return
  }

  // 准备数据
  const dates = trendData.map((item: any) => item.examDate || item.examName)
  const avgScores = trendData.map((item: any) => item.averageScore)
  const maxScores = trendData.map((item: any) => item.maxScore)
  const minScores = trendData.map((item: any) => item.minScore)

  const option = {
    tooltip: {
      trigger: 'axis'
    },
    legend: {
      data: ['平均分', '最高分', '最低分']
    },
    xAxis: {
      type: 'category',
      boundaryGap: false,
      data: dates
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        name: '平均分',
        type: 'line',
        data: avgScores,
        smooth: true,
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '最高分',
        type: 'line',
        data: maxScores,
        smooth: true,
        itemStyle: {
          color: '#52c41a'
        }
      },
      {
        name: '最低分',
        type: 'line',
        data: minScores,
        smooth: true,
        itemStyle: {
          color: '#ff4d4f'
        }
      }
    ]
  }

  trendChart.setOption(option)
}

// 窗口大小变化时重新渲染图表
const handleResize = () => {
  distributionChart?.resize()
  trendChart?.resize()
}

// 页面加载
onMounted(() => {
  loadCourses()
  window.addEventListener('resize', handleResize)
})

// 页面卸载
onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  distributionChart?.dispose()
  trendChart?.dispose()
})
</script>

<style lang="less" scoped>
.statistics-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);

  :deep(.ant-card) {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    margin-bottom: 16px;
  }

  .filter-section {
    margin-bottom: 16px;
  }

  .statistics-content {
    .ant-card {
      height: 100%;
    }
  }
}
</style>
