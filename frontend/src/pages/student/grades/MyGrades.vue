<template>
  <div class="my-grades-page">
    <a-card title="我的成绩" :bordered="false">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <a-form layout="inline">
          <a-form-item label="课程">
            <a-select
              v-model:value="filterForm.courseId"
              placeholder="请选择课程"
              style="width: 200px"
              allow-clear
              @change="handleCourseChange"
            >
              <a-select-option
                v-for="course in courses"
                :key="course.courseId"
                :value="course.courseId"
              >
                {{ course.courseName }}
              </a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="考试类型">
            <a-select
              v-model:value="filterForm.examType"
              placeholder="请选择类型"
              style="width: 150px"
              allow-clear
              @change="loadGrades"
            >
              <a-select-option value="daily">平时成绩</a-select-option>
              <a-select-option value="midterm">期中考试</a-select-option>
              <a-select-option value="final">期末考试</a-select-option>
              <a-select-option value="homework">作业</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item>
            <a-button type="primary" @click="loadGrades">
              <template #icon><SearchOutlined /></template>
              查询
            </a-button>
          </a-form-item>

          <a-form-item>
            <a-button @click="handleReset">
              <template #icon><ReloadOutlined /></template>
              重置
            </a-button>
          </a-form-item>
        </a-form>
      </div>

      <!-- 成绩列表 -->
      <a-table
        :columns="columns"
        :data-source="dataSource"
        :loading="loading"
        :pagination="pagination"
        :row-key="(record) => record.id"
        @change="handleTableChange"
        class="grades-table"
      >
        <!-- 考试类型 -->
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'examType'">
            <a-tag :color="getExamTypeColor(record.examType)">
              {{ getExamTypeName(record.examType) }}
            </a-tag>
          </template>

          <!-- 分数 -->
          <template v-else-if="column.key === 'score'">
            <span :class="{ 'score-fail': !record.isPass, 'score-pass': record.isPass }">
              {{ record.score }} / {{ record.fullScore }}
            </span>
          </template>

          <!-- 百分比 -->
          <template v-else-if="column.key === 'percentage'">
            <a-progress
              :percent="record.percentage"
              :status="record.isPass ? 'success' : 'exception'"
              :stroke-color="record.isPass ? '#52c41a' : '#ff4d4f'"
            />
          </template>

          <!-- 是否及格 -->
          <template v-else-if="column.key === 'isPass'">
            <a-tag :color="record.isPass ? 'success' : 'error'">
              {{ record.isPass ? '及格' : '不及格' }}
            </a-tag>
          </template>
        </template>
      </a-table>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import { gradeApiStudentMyGradesGet, gradeApiStudentCoursesGet } from '@/api/gradeController'

// 筛选表单
const filterForm = reactive({
  courseId: undefined as number | undefined,
  examType: undefined as string | undefined
})

// 课程列表
const courses = ref<any[]>([])

// 表格数据
const dataSource = ref<any[]>([])
const loading = ref(false)

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  pageSizeOptions: ['10', '20', '50', '100'],
  showTotal: (total: number) => `共 ${total} 条记录`
})

// 表格列定义
const columns = [
  {
    title: '课程名称',
    dataIndex: 'courseName',
    key: 'courseName',
    width: 150
  },
  {
    title: '考试类型',
    dataIndex: 'examType',
    key: 'examType',
    width: 120
  },
  {
    title: '考试名称',
    dataIndex: 'examName',
    key: 'examName',
    width: 150
  },
  {
    title: '分数',
    dataIndex: 'score',
    key: 'score',
    width: 120
  },
  {
    title: '百分比',
    dataIndex: 'percentage',
    key: 'percentage',
    width: 150
  },
  {
    title: '是否及格',
    dataIndex: 'isPass',
    key: 'isPass',
    width: 100
  },
  {
    title: '考试日期',
    dataIndex: 'examDate',
    key: 'examDate',
    width: 120
  },
  {
    title: '备注',
    dataIndex: 'remark',
    key: 'remark',
    ellipsis: true
  }
]

// 获取考试类型名称
const getExamTypeName = (type: string) => {
  const typeMap: Record<string, string> = {
    daily: '平时成绩',
    midterm: '期中考试',
    final: '期末考试',
    homework: '作业'
  }
  return typeMap[type] || type
}

// 获取考试类型颜色
const getExamTypeColor = (type: string) => {
  const colorMap: Record<string, string> = {
    daily: 'blue',
    midterm: 'orange',
    final: 'red',
    homework: 'green'
  }
  return colorMap[type] || 'default'
}

// 加载课程列表
const loadCourses = async () => {
  try {
    const response = await gradeApiStudentCoursesGet()
    const data = response.data || response
    
    // 转换字段名：后端下划线 -> 前端驼峰
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
    console.error('加载课程列表失败:', error)
    message.error('加载课程列表失败')
  }
}

// 加载成绩列表
const loadGrades = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.current,
      perPage: pagination.pageSize
    }

    if (filterForm.courseId) {
      params.courseId = filterForm.courseId
    }

    if (filterForm.examType) {
      params.examType = filterForm.examType
    }

    const response = await gradeApiStudentMyGradesGet(params)
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
      weight: grade.weight,
      percentage: grade.percentage,
      isPass: grade.is_pass,
      examDate: grade.exam_date,
      remark: grade.remark
    }))

    dataSource.value = grades
    pagination.total = data.total || 0
  } catch (error: any) {
    console.error('加载成绩列表失败:', error)
    let errorMsg = '加载成绩列表失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    }
    message.error(errorMsg)
  } finally {
    loading.value = false
  }
}

// 课程变化
const handleCourseChange = () => {
  pagination.current = 1
  loadGrades()
}

// 表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadGrades()
}

// 重置筛选
const handleReset = () => {
  filterForm.courseId = undefined
  filterForm.examType = undefined
  pagination.current = 1
  loadGrades()
}

// 初始化
onMounted(() => {
  loadCourses()
  loadGrades()
})
</script>

<style scoped lang="scss">
.my-grades-page {
  padding: 24px;

  .filter-section {
    margin-bottom: 16px;
    padding: 16px;
    background-color: var(--background-color-light);
    border-radius: 4px;
  }

  .grades-table {
    margin-top: 16px;

    .score-pass {
      color: var(--success-color);
      font-weight: 600;
    }

    .score-fail {
      color: var(--error-color);
      font-weight: 600;
    }
  }
}
</style>
