<template>
  <div class="grade-list-page">
    <a-card :bordered="false" title="📋 成绩列表">
      <!-- 筛选区域 -->
      <div class="filter-section">
        <a-form :model="filterForm" layout="inline">
          <a-form-item label="课程">
            <a-select
                v-model:value="filterForm.courseId"
                :loading="loading.courses"
                allow-clear
                placeholder="请选择课程"
                style="width: 200px"
                @change="handleSearch"
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

          <a-form-item label="考试类型">
            <a-select
                v-model:value="filterForm.examType"
                allow-clear
                placeholder="全部"
                style="width: 150px"
                @change="handleSearch"
            >
              <a-select-option value="daily">平时成绩</a-select-option>
              <a-select-option value="midterm">期中考试</a-select-option>
              <a-select-option value="final">期末考试</a-select-option>
              <a-select-option value="homework">作业</a-select-option>
            </a-select>
          </a-form-item>

          <a-form-item label="学生">
            <a-input
                v-model:value="filterForm.keyword"
                allow-clear
                placeholder="学号或姓名"
                style="width: 200px"
                @press-enter="handleSearch"
            />
          </a-form-item>

          <a-form-item>
            <a-space>
              <a-button type="primary" @click="handleSearch">
                <template #icon>
                  <SearchOutlined/>
                </template>
                查询
              </a-button>
              <a-button @click="handleReset">
                <template #icon>
                  <ReloadOutlined/>
                </template>
                重置
              </a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </div>

      <!-- 操作按钮 -->
      <div class="action-section">
        <a-space>
          <a-button type="primary" @click="handleAdd">
            <template #icon>
              <PlusOutlined/>
            </template>
            单条录入
          </a-button>
          <a-button @click="handleImport">
            <template #icon>
              <UploadOutlined/>
            </template>
            批量导入
          </a-button>
          <a-button
              :disabled="!filterForm.courseId"
              :loading="loading.export"
              @click="handleExport"
          >
            <template #icon>
              <DownloadOutlined/>
            </template>
            导出Excel
          </a-button>
        </a-space>
      </div>

      <!-- 数据表格 -->
      <a-table
          :columns="columns"
          :data-source="dataSource"
          :loading="loading.table"
          :pagination="pagination"
          :scroll="{ x: 1200 }"
          row-key="id"
          @change="handleTableChange"
      >
        <template #bodyCell="{ column, record }">
          <!-- 考试类型 -->
          <template v-if="column.key === 'examType'">
            <a-tag :color="getExamTypeColor(record.examType)">
              {{ getExamTypeText(record.examType) }}
            </a-tag>
          </template>

          <!-- 分数 -->
          <template v-if="column.key === 'score'">
            <span :style="{ color: record.isPass ? '#52c41a' : '#ff4d4f', fontWeight: 'bold' }">
              {{ record.score }}
            </span>
            <span style="color: #999"> / {{ record.fullScore }}</span>
          </template>

          <!-- 百分比 -->
          <template v-if="column.key === 'percentage'">
            <a-progress
                :percent="record.percentage"
                :show-info="true"
                :status="record.isPass ? 'success' : 'exception'"
                size="small"
            />
          </template>

          <!-- 是否及格 -->
          <template v-if="column.key === 'isPass'">
            <a-tag :color="record.isPass ? 'success' : 'error'">
              {{ record.isPass ? '及格' : '不及格' }}
            </a-tag>
          </template>

          <!-- 操作 -->
          <template v-if="column.key === 'action'">
            <a-space>
              <a-button size="small" type="link" @click="handleEdit(record)">
                编辑
              </a-button>
              <a-popconfirm
                  cancel-text="取消"
                  ok-text="确定"
                  title="确定要删除这条成绩吗?"
                  @confirm="handleDelete(record)"
              >
                <a-button danger size="small" type="link">
                  删除
                </a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 编辑对话框 -->
    <a-modal
        v-model:open="editModal.visible"
        :confirm-loading="editModal.loading"
        title="编辑成绩"
        @cancel="handleEditCancel"
        @ok="handleEditSubmit"
    >
      <a-form :model="editModal.form" layout="vertical">
        <a-form-item label="分数">
          <a-input-number
              v-model:value="editModal.form.score"
              :max="editModal.form.fullScore"
              :min="0"
              :precision="1"
              style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="满分">
          <a-input-number
              v-model:value="editModal.form.fullScore"
              :min="1"
              :precision="0"
              style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="权重">
          <a-input-number
              v-model:value="editModal.form.weight"
              :max="10"
              :min="0"
              :precision="2"
              :step="0.1"
              style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="备注">
          <a-textarea
              v-model:value="editModal.form.remark"
              :maxlength="255"
              :rows="3"
              show-count
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, reactive, ref} from 'vue'
import {message} from 'ant-design-vue'
import {useRouter} from 'vue-router'
import {DownloadOutlined, PlusOutlined, ReloadOutlined, SearchOutlined, UploadOutlined} from '@ant-design/icons-vue'
import {gradeApiGet, gradeApiIntGradeIdDelete, gradeApiIntGradeIdPut} from '@/api/gradeController'
import type {API} from '@/api/typings'

const router = useRouter()

// 筛选表单
const filterForm = reactive({
  courseId: undefined as number | undefined,
  examType: undefined as string | undefined,
  keyword: ''
})

// 加载状态
const loading = reactive({
  courses: false,
  table: false,
  export: false
})

// 数据
const courses = ref<any[]>([])
const dataSource = ref<any[]>([])

// 分页
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`
})

// 编辑对话框
const editModal = reactive({
  visible: false,
  loading: false,
  id: 0,
  form: {
    score: 0,
    fullScore: 100,
    weight: 1.0,
    remark: ''
  }
})

// 表格列定义
const columns = [
  {title: '学号', dataIndex: 'studentCode', key: 'studentCode', width: 120, fixed: 'left'},
  {title: '姓名', dataIndex: 'studentName', key: 'studentName', width: 100, fixed: 'left'},
  {title: '课程', dataIndex: 'courseName', key: 'courseName', width: 150},
  {title: '考试类型', key: 'examType', width: 100},
  {title: '考试名称', dataIndex: 'examName', key: 'examName', width: 150, ellipsis: true},
  {title: '分数', key: 'score', width: 100},
  {title: '百分比', key: 'percentage', width: 150},
  {title: '是否及格', key: 'isPass', width: 100},
  {title: '考试日期', dataIndex: 'examDate', key: 'examDate', width: 120},
  {title: '备注', dataIndex: 'remark', key: 'remark', ellipsis: true},
  {title: '操作', key: 'action', width: 150, fixed: 'right'}
]

// 获取考试类型颜色
const getExamTypeColor = (type: string) => {
  const colors: Record<string, string> = {
    daily: 'blue',
    midterm: 'orange',
    final: 'red',
    homework: 'green'
  }
  return colors[type] || 'default'
}

// 获取考试类型文本
const getExamTypeText = (type: string) => {
  const texts: Record<string, string> = {
    daily: '平时成绩',
    midterm: '期中考试',
    final: '期末考试',
    homework: '作业'
  }
  return texts[type] || type
}

// 加载课程列表
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

// 加载成绩列表
const loadGrades = async () => {
  loading.table = true
  try {
    const params: API.gradeApiGetParams = {
      page: pagination.current,
      perPage: pagination.pageSize,
      courseId: filterForm.courseId,
      examType: filterForm.examType as any
    }

    console.log('📤 请求参数:', params)
    const response = await gradeApiGet(params)
    console.log('📥 响应数据:', response)

    // 从axios响应中提取实际数据
    const data = response.data || response

    // 转换字段名:下划线 -> 驼峰
    const grades = (data.grades || []).map((grade: any) => ({
      id: grade.id,
      studentCode: grade.student_code,
      studentName: grade.student_name,
      courseName: grade.course_name,
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

    console.log('📊 数据源:', dataSource.value)
    console.log('📈 总数:', pagination.total)
  } catch (error: any) {
    console.error('❌ 加载失败:', error)
    let errorMsg = '加载成绩列表失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.message) {
      errorMsg = error.message
    }
    message.error(errorMsg)
  } finally {
    loading.table = false
  }
}

// 查询
const handleSearch = () => {
  pagination.current = 1
  loadGrades()
}

// 重置
const handleReset = () => {
  filterForm.courseId = undefined
  filterForm.examType = undefined
  filterForm.keyword = ''
  handleSearch()
}

// 表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadGrades()
}

// 新增
const handleAdd = () => {
  router.push('/teacher/grades/input/add')
}

// 导入
const handleImport = () => {
  router.push('/teacher/grades/input/import')
}

// 导出
const handleExport = async () => {
  if (!filterForm.courseId) {
    message.warning('请先选择课程')
    return
  }

  loading.export = true
  try {
    const params = new URLSearchParams({
      courseId: String(filterForm.courseId)
    })
    if (filterForm.examType) {
      params.append('examType', filterForm.examType)
    }

    const response = await fetch(
        `http://localhost:5000/api/v1/grades/export?${params.toString()}`,
        {
          method: 'GET',
          credentials: 'include'
        }
    )

    if (!response.ok) {
      throw new Error('导出失败')
    }

    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `成绩单_${new Date().getTime()}.xlsx`
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)

    message.success('导出成功')
  } catch (error: any) {
    message.error(error.message || '导出失败')
  } finally {
    loading.export = false
  }
}

// 编辑
const handleEdit = (record: any) => {
  editModal.id = record.id
  editModal.form.score = record.score
  editModal.form.fullScore = record.fullScore
  editModal.form.weight = record.weight
  editModal.form.remark = record.remark || ''
  editModal.visible = true
}

// 提交编辑
const handleEditSubmit = async () => {
  editModal.loading = true
  try {
    await gradeApiIntGradeIdPut(
        {grade_id: editModal.id},
        editModal.form
    )

    message.success('修改成功')
    editModal.visible = false
    loadGrades()
  } catch (error: any) {
    let errorMsg = '修改失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.message) {
      errorMsg = error.message
    }
    message.error(errorMsg)
  } finally {
    editModal.loading = false
  }
}

// 取消编辑
const handleEditCancel = () => {
  editModal.visible = false
}

// 删除
const handleDelete = async (record: any) => {
  try {
    await gradeApiIntGradeIdDelete({grade_id: record.id})

    message.success('删除成功')
    loadGrades()
  } catch (error: any) {
    let errorMsg = '删除失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.message) {
      errorMsg = error.message
    }
    message.error(errorMsg)
  }
}

// 页面加载
onMounted(() => {
  loadCourses()
  loadGrades()
})
</script>

<style lang="less" scoped>
.grade-list-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);

  :deep(.ant-card) {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .filter-section {
    margin-bottom: 16px;
  }

  .action-section {
    margin-bottom: 16px;
  }
}
</style>
