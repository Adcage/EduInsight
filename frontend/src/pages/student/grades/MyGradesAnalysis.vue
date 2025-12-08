<template>
  <div class="my-grades-analysis-page">
    <a-card title="个人成绩分析" :bordered="false">
      <!-- 总体统计卡片 -->
      <a-row :gutter="[16, 16]" class="statistics-cards">
        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card">
            <a-statistic
              title="总课程数"
              :value="statistics.totalCourses"
              :value-style="{ color: 'var(--primary-color)' }"
            >
              <template #prefix>
                <BookOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card">
            <a-statistic
              title="总成绩数"
              :value="statistics.totalGrades"
              :value-style="{ color: 'var(--primary-color)' }"
            >
              <template #prefix>
                <FileTextOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card">
            <a-statistic
              title="平均分"
              :value="statistics.averageScore"
              :precision="2"
              :value-style="{ color: getScoreColor(statistics.averageScore) }"
            >
              <template #prefix>
                <TrophyOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card">
            <a-statistic
              title="及格率"
              :value="statistics.passRate"
              suffix="%"
              :precision="1"
              :value-style="{ color: statistics.passRate >= 60 ? 'var(--success-color)' : 'var(--error-color)' }"
            >
              <template #prefix>
                <CheckCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <!-- 课程成绩对比图 -->
      <a-card title="课程成绩对比" class="chart-card" :bordered="false">
        <div ref="courseChartRef" style="width: 100%; height: 400px"></div>
      </a-card>

      <!-- 成绩趋势图 -->
      <a-card title="成绩趋势分析" class="chart-card" :bordered="false">
        <div ref="trendChartRef" style="width: 100%; height: 400px"></div>
      </a-card>

      <!-- 分数段分布图 -->
      <a-card title="分数段分布" class="chart-card" :bordered="false">
        <div ref="distributionChartRef" style="width: 100%; height: 400px"></div>
      </a-card>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { message } from 'ant-design-vue'
import {
  BookOutlined,
  FileTextOutlined,
  TrophyOutlined,
  CheckCircleOutlined
} from '@ant-design/icons-vue'
import * as echarts from 'echarts'
import {
  gradeApiStudentCoursesGet,
  gradeApiStudentStatisticsGet,
  gradeApiStudentMyGradesGet
} from '@/api/gradeController'

// 统计数据
const statistics = reactive({
  totalCourses: 0,
  totalGrades: 0,
  averageScore: 0,
  passRate: 0,
  passCount: 0,
  failCount: 0
})

// 课程数据
const courses = ref<any[]>([])

// 所有成绩数据
const allGrades = ref<any[]>([])

// 图表引用
const courseChartRef = ref<HTMLElement>()
const trendChartRef = ref<HTMLElement>()
const distributionChartRef = ref<HTMLElement>()

// 图表实例
let courseChart: echarts.ECharts | null = null
let trendChart: echarts.ECharts | null = null
let distributionChart: echarts.ECharts | null = null

// 获取分数颜色
const getScoreColor = (score: number) => {
  if (score >= 90) return 'var(--success-color)'
  if (score >= 80) return 'var(--primary-color)'
  if (score >= 60) return 'var(--warning-color)'
  return 'var(--error-color)'
}

// 加载统计数据
const loadStatistics = async () => {
  try {
    const response = await gradeApiStudentStatisticsGet()
    const data = response.data || response

    // 转换字段名
    statistics.totalCourses = data.total_courses || 0
    statistics.totalGrades = data.total_grades || 0
    statistics.averageScore = data.average_score || 0
    statistics.passRate = data.pass_rate || 0
    statistics.passCount = data.pass_count || 0
    statistics.failCount = data.fail_count || 0
  } catch (error: any) {
    console.error('加载统计数据失败:', error)
    message.error('加载统计数据失败')
  }
}

// 加载课程数据
const loadCourses = async () => {
  try {
    const response = await gradeApiStudentCoursesGet()
    const data = response.data || response

    // 转换字段名
    const courseList = (data || []).map((course: any) => ({
      courseId: course.course_id,
      courseName: course.course_name,
      courseCode: course.course_code,
      semester: course.semester,
      gradeCount: course.grade_count,
      averageScore: course.average_score,
      highestScore: course.highest_score,
      lowestScore: course.lowest_score,
      passRate: course.pass_rate
    }))

    courses.value = courseList
  } catch (error: any) {
    console.error('加载课程数据失败:', error)
    message.error('加载课程数据失败')
  }
}

// 加载所有成绩数据
const loadAllGrades = async () => {
  try {
    // 由于API限制每页最多100条，需要分页加载所有数据
    let allGradesData: any[] = []
    let currentPage = 1
    let hasMore = true

    while (hasMore) {
      const response = await gradeApiStudentMyGradesGet({
        page: currentPage,
        perPage: 100 // API最大限制
      })
      const data = response.data || response

      // 转换字段名
      const grades = (data.grades || []).map((grade: any) => ({
        id: grade.id,
        courseName: grade.course_name,
        courseCode: grade.course_code,
        examType: grade.exam_type,
        examName: grade.exam_name,
        score: grade.score,
        fullScore: grade.full_score,
        percentage: grade.percentage,
        isPass: grade.is_pass,
        examDate: grade.exam_date,
        remark: grade.remark
      }))

      allGradesData = allGradesData.concat(grades)

      // 检查是否还有更多数据
      const total = data.total || 0
      const loadedCount = currentPage * 100
      hasMore = loadedCount < total

      currentPage++
    }

    allGrades.value = allGradesData
  } catch (error: any) {
    console.error('加载成绩数据失败:', error)
    message.error('加载成绩数据失败')
  }
}

// 初始化课程成绩对比图
const initCourseChart = () => {
  if (!courseChartRef.value) return

  courseChart = echarts.init(courseChartRef.value)

  const courseNames = courses.value.map((c) => c.courseName)
  const averageScores = courses.value.map((c) => c.averageScore || 0)
  const highestScores = courses.value.map((c) => c.highestScore || 0)
  const lowestScores = courses.value.map((c) => c.lowestScore || 0)

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['平均分', '最高分', '最低分']
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: courseNames,
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        name: '平均分',
        type: 'bar',
        data: averageScores,
        itemStyle: {
          color: '#1890ff'
        }
      },
      {
        name: '最高分',
        type: 'bar',
        data: highestScores,
        itemStyle: {
          color: '#52c41a'
        }
      },
      {
        name: '最低分',
        type: 'bar',
        data: lowestScores,
        itemStyle: {
          color: '#faad14'
        }
      }
    ]
  }

  courseChart.setOption(option)
}

// 初始化成绩趋势图
const initTrendChart = () => {
  if (!trendChartRef.value) return

  trendChart = echarts.init(trendChartRef.value)

  // 按日期排序
  const sortedGrades = [...allGrades.value].sort(
    (a, b) => new Date(a.examDate).getTime() - new Date(b.examDate).getTime()
  )

  const dates = sortedGrades.map((g) => g.examDate)
  const scores = sortedGrades.map((g) => g.score)

  const option = {
    tooltip: {
      trigger: 'axis',
      formatter: (params: any) => {
        const param = params[0]
        const grade = sortedGrades[param.dataIndex]
        return `
          ${param.name}<br/>
          课程: ${grade.courseName}<br/>
          考试: ${grade.examName || grade.examType}<br/>
          分数: ${param.value}
        `
      }
    },
    grid: {
      left: '3%',
      right: '4%',
      bottom: '3%',
      containLabel: true
    },
    xAxis: {
      type: 'category',
      data: dates,
      axisLabel: {
        rotate: 30
      }
    },
    yAxis: {
      type: 'value',
      min: 0,
      max: 100
    },
    series: [
      {
        name: '成绩',
        type: 'line',
        data: scores,
        smooth: true,
        itemStyle: {
          color: '#1890ff'
        },
        areaStyle: {
          color: new echarts.graphic.LinearGradient(0, 0, 0, 1, [
            { offset: 0, color: 'rgba(24, 144, 255, 0.3)' },
            { offset: 1, color: 'rgba(24, 144, 255, 0.1)' }
          ])
        }
      }
    ]
  }

  trendChart.setOption(option)
}

// 初始化分数段分布图
const initDistributionChart = () => {
  if (!distributionChartRef.value) return

  distributionChart = echarts.init(distributionChartRef.value)

  // 统计分数段
  const distribution = {
    excellent: 0, // 90-100
    good: 0, // 80-89
    medium: 0, // 70-79
    pass: 0, // 60-69
    fail: 0 // 0-59
  }

  allGrades.value.forEach((grade) => {
    const score = grade.score
    if (score >= 90) distribution.excellent++
    else if (score >= 80) distribution.good++
    else if (score >= 70) distribution.medium++
    else if (score >= 60) distribution.pass++
    else distribution.fail++
  })

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{a} <br/>{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '分数段',
        type: 'pie',
        radius: '50%',
        data: [
          { value: distribution.excellent, name: '优秀(90-100)', itemStyle: { color: '#52c41a' } },
          { value: distribution.good, name: '良好(80-89)', itemStyle: { color: '#1890ff' } },
          { value: distribution.medium, name: '中等(70-79)', itemStyle: { color: '#faad14' } },
          { value: distribution.pass, name: '及格(60-69)', itemStyle: { color: '#fa8c16' } },
          { value: distribution.fail, name: '不及格(0-59)', itemStyle: { color: '#ff4d4f' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  distributionChart.setOption(option)
}

// 初始化所有图表
const initCharts = async () => {
  await nextTick()
  initCourseChart()
  initTrendChart()
  initDistributionChart()
}

// 窗口大小改变时重新渲染图表
const handleResize = () => {
  courseChart?.resize()
  trendChart?.resize()
  distributionChart?.resize()
}

// 初始化
onMounted(async () => {
  await Promise.all([loadStatistics(), loadCourses(), loadAllGrades()])
  await initCharts()

  window.addEventListener('resize', handleResize)
})

// 清理
import { onUnmounted } from 'vue'
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
  courseChart?.dispose()
  trendChart?.dispose()
  distributionChart?.dispose()
})
</script>

<style scoped lang="scss">
.my-grades-analysis-page {
  padding: 24px;

  .statistics-cards {
    margin-bottom: 24px;

    .stat-card {
      background-color: var(--background-color-container);
      border: 1px solid var(--border-color-base);
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 2px 8px var(--shadow-color);
      }
    }
  }

  .chart-card {
    margin-bottom: 24px;
    background-color: var(--background-color-container);
    border: 1px solid var(--border-color-base);
    border-radius: 8px;
  }
}
</style>
