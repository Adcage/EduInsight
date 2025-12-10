<template>
  <div class="grade-import-page">
    <a-card title="📊 Excel批量导入成绩" :bordered="false">
      <!-- 步骤条 -->
      <a-steps :current="currentStep" class="steps">
        <a-step title="填写信息" />
        <a-step title="上传文件" />
        <a-step title="预览确认" />
        <a-step title="导入完成" />
      </a-steps>

      <!-- 步骤1: 填写基本信息 -->
      <div v-if="currentStep === 0" class="step-content">
        <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          layout="vertical"
        >
          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="课程" name="courseId" required>
                <a-select
                  v-model:value="formState.courseId"
                  placeholder="请选择课程"
                  :loading="loading.courses"
                  show-search
                  :filter-option="filterOption"
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
            </a-col>

            <a-col :span="12">
              <a-form-item label="考试类型" name="examType" required>
                <a-select v-model:value="formState.examType" placeholder="请选择考试类型">
                  <a-select-option value="daily">平时成绩</a-select-option>
                  <a-select-option value="midterm">期中考试</a-select-option>
                  <a-select-option value="final">期末考试</a-select-option>
                  <a-select-option value="homework">作业</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item label="考试名称" name="examName">
                <a-input v-model:value="formState.examName" placeholder="例如:期中考试" />
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item label="考试日期" name="examDate" required>
                <a-date-picker
                  v-model:value="formState.examDate"
                  style="width: 100%"
                  placeholder="请选择考试日期"
                  :disabled-date="disabledDate"
                />
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item label="满分" name="fullScore">
                <a-input-number
                  v-model:value="formState.fullScore"
                  :min="1"
                  :precision="0"
                  style="width: 100%"
                  placeholder="默认100分"
                />
              </a-form-item>
            </a-col>

            <a-col :span="12">
              <a-form-item label="权重" name="weight">
                <a-input-number
                  v-model:value="formState.weight"
                  :min="0"
                  :max="10"
                  :precision="2"
                  :step="0.1"
                  style="width: 100%"
                  placeholder="默认1.0"
                />
              </a-form-item>
            </a-col>
          </a-row>
        </a-form>

        <a-divider />

        <a-space>
          <a-button type="primary" @click="handleNext" :disabled="!canNext">
            下一步
          </a-button>
          <a-button @click="handleDownloadTemplate" :loading="loading.template">
            <template #icon><DownloadOutlined /></template>
            下载Excel模板
          </a-button>
        </a-space>
      </div>

      <!-- 步骤2: 上传文件 -->
      <div v-if="currentStep === 1" class="step-content">
        <a-upload-dragger
          v-model:fileList="fileList"
          name="file"
          :multiple="false"
          :before-upload="beforeUpload"
          :remove="handleRemove"
          accept=".xlsx,.xls"
        >
          <p class="ant-upload-drag-icon">
            <InboxOutlined />
          </p>
          <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
          <p class="ant-upload-hint">
            支持 .xlsx 和 .xls 格式的Excel文件
          </p>
        </a-upload-dragger>

        <a-divider />

        <a-space>
          <a-button @click="handlePrev">上一步</a-button>
          <a-button
            type="primary"
            @click="handleParseFile"
            :disabled="fileList.length === 0"
            :loading="loading.parse"
          >
            解析文件
          </a-button>
        </a-space>
      </div>

      <!-- 步骤3: 预览数据 -->
      <div v-if="currentStep === 2" class="step-content">
        <a-alert
          v-if="previewData.length > 0"
          :message="`共解析到 ${previewData.length} 条数据`"
          type="info"
          show-icon
          style="margin-bottom: 16px"
        />

        <a-table
          :columns="previewColumns"
          :data-source="previewData"
          :pagination="{ pageSize: 10 }"
          :scroll="{ x: 800 }"
          size="small"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'status'">
              <a-tag v-if="record.error" color="error">错误</a-tag>
              <a-tag v-else-if="record.warning" color="warning">警告</a-tag>
              <a-tag v-else color="success">正常</a-tag>
            </template>
            <template v-if="column.key === 'message'">
              <span v-if="record.error" style="color: #ff4d4f">{{ record.error }}</span>
              <span v-else-if="record.warning" style="color: #faad14">{{ record.warning }}</span>
              <span v-else style="color: #52c41a">✓</span>
            </template>
          </template>
        </a-table>

        <a-divider />

        <a-space>
          <a-button @click="handlePrev">上一步</a-button>
          <a-button
            type="primary"
            @click="handleImport"
            :loading="loading.import"
            :disabled="previewData.length === 0"
          >
            确认导入
          </a-button>
        </a-space>
      </div>

      <!-- 步骤4: 导入结果 -->
      <div v-if="currentStep === 3" class="step-content">
        <a-result
          :status="importResult.failCount === 0 ? 'success' : 'warning'"
          :title="importResult.failCount === 0 ? '导入成功' : '导入完成(部分失败)'"
        >
          <template #subTitle>
            <div class="result-stats">
              <a-statistic
                title="总计"
                :value="importResult.totalRows"
                style="margin-right: 32px"
              />
              <a-statistic
                title="成功"
                :value="importResult.successCount"
                :value-style="{ color: '#3f8600' }"
                style="margin-right: 32px"
              />
              <a-statistic
                title="跳过重复"
                :value="importResult.skipCount"
                :value-style="{ color: '#faad14' }"
                style="margin-right: 32px"
              />
              <a-statistic
                title="失败"
                :value="importResult.failCount"
                :value-style="{ color: '#cf1322' }"
              />
            </div>
          </template>

          <template #extra>
            <a-space>
              <a-button type="primary" @click="handleReset">继续导入</a-button>
              <a-button @click="handleViewList">查看成绩列表</a-button>
            </a-space>
          </template>
        </a-result>

        <!-- 错误详情 -->
        <a-collapse v-if="importResult.errors.length > 0" style="margin-top: 24px">
          <a-collapse-panel key="errors" header="查看错误详情">
            <a-list :data-source="importResult.errors" size="small">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      第 {{ item.row }} 行 - 学号: {{ item.studentCode || '未知' }}
                    </template>
                    <template #description>
                      <span style="color: #ff4d4f">{{ item.error }}</span>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-collapse-panel>
        </a-collapse>

        <!-- 警告详情 -->
        <a-collapse v-if="importResult.warnings.length > 0" style="margin-top: 16px">
          <a-collapse-panel key="warnings" header="查看警告详情">
            <a-list :data-source="importResult.warnings" size="small">
              <template #renderItem="{ item }">
                <a-list-item>
                  <a-list-item-meta>
                    <template #title>
                      第 {{ item.row }} 行 - 学号: {{ item.studentCode || '未知' }}
                    </template>
                    <template #description>
                      <span style="color: #faad14">{{ item.warning }}</span>
                    </template>
                  </a-list-item-meta>
                </a-list-item>
              </template>
            </a-list>
          </a-collapse-panel>
        </a-collapse>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { message } from 'ant-design-vue'
import { useRouter } from 'vue-router'
import { InboxOutlined, DownloadOutlined } from '@ant-design/icons-vue'
import type { Dayjs } from 'dayjs'
import dayjs from 'dayjs'
import type { UploadProps } from 'ant-design-vue'
import type { API } from '@/api/typings'

const router = useRouter()
const formRef = ref()

// 当前步骤
const currentStep = ref(0)

// 表单状态
const formState = reactive({
  courseId: undefined as number | undefined,
  examType: undefined as string | undefined,
  examName: '',
  examDate: dayjs() as Dayjs,
  fullScore: 100,
  weight: 1.0
})

// 加载状态
const loading = reactive({
  courses: false,
  template: false,
  parse: false,
  import: false
})

// 数据
const courses = ref<any[]>([])
const fileList = ref<any[]>([])
const previewData = ref<any[]>([])
const importResult = reactive({
  totalRows: 0,
  successCount: 0,
  skipCount: 0,
  failCount: 0,
  errors: [] as any[],
  warnings: [] as any[]
})

// 表单验证规则
const rules = {
  courseId: [{ required: true, message: '请选择课程', trigger: 'change' }],
  examType: [{ required: true, message: '请选择考试类型', trigger: 'change' }],
  examDate: [{ required: true, message: '请选择考试日期', trigger: 'change' }]
}

// 预览表格列
const previewColumns = [
  { title: '行号', dataIndex: 'row', key: 'row', width: 80 },
  { title: '学号', dataIndex: 'studentCode', key: 'studentCode', width: 120 },
  { title: '姓名', dataIndex: 'studentName', key: 'studentName', width: 100 },
  { title: '分数', dataIndex: 'score', key: 'score', width: 80 },
  { title: '备注', dataIndex: 'remark', key: 'remark', ellipsis: true },
  { title: '状态', key: 'status', width: 80 },
  { title: '信息', key: 'message', ellipsis: true }
]

// 是否可以进入下一步
const canNext = computed(() => {
  return formState.courseId && formState.examType && formState.examDate
})

// 禁用未来日期
const disabledDate = (current: Dayjs) => {
  return current && current > dayjs().endOf('day')
}

// 过滤选项
const filterOption = (input: string, option: any) => {
  return option.children[0].children.toLowerCase().indexOf(input.toLowerCase()) >= 0
}

// 加载教师课程列表
const loadCourses = async () => {
  loading.courses = true
  try {
    const response = await fetch('http://localhost:5030/api/v1/grades/teacher-courses', {
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

// 下载模板
const handleDownloadTemplate = async () => {
  loading.template = true
  try {
    const courseName = courses.value.find(c => c.id === formState.courseId)?.name || '示例课程'
    
    // 调用下载模板API
    const response = await fetch(
      `http://localhost:5030/api/v1/grades/template?courseName=${encodeURIComponent(courseName)}`,
      {
        method: 'GET',
        credentials: 'include'
      }
    )
    
    if (!response.ok) {
      throw new Error('下载模板失败')
    }
    
    const blob = await response.blob()
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = '成绩导入模板.xlsx'
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    window.URL.revokeObjectURL(url)
    
    message.success('模板下载成功')
  } catch (error: any) {
    message.error(error.message || '下载模板失败')
  } finally {
    loading.template = false
  }
}

// 上传前验证
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isExcel = file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
                  file.type === 'application/vnd.ms-excel'
  if (!isExcel) {
    message.error('只能上传Excel文件!')
    return false
  }
  const isLt5M = file.size / 1024 / 1024 < 5
  if (!isLt5M) {
    message.error('文件大小不能超过5MB!')
    return false
  }
  return false // 阻止自动上传
}

// 移除文件
const handleRemove = () => {
  fileList.value = []
  previewData.value = []
}

// 解析文件
const handleParseFile = async () => {
  if (fileList.value.length === 0) {
    message.warning('请先上传文件')
    return
  }

  loading.parse = true
  try {
    const file = fileList.value[0].originFileObj
    
    // 发送到后端解析并验证
    const formData = new FormData()
    formData.append('file', file)
    formData.append('courseId', String(formState.courseId))
    
    const response = await fetch('http://localhost:5030/api/v1/grades/parse-excel', {
      method: 'POST',
      credentials: 'include',
      body: formData
    })
    
    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '文件解析失败')
    }
    
    const result = await response.json()
    
    // 转换数据格式用于预览
    previewData.value = result.data.map((item: any, index: number) => ({
      row: index + 2, // Excel从第2行开始(第1行是表头)
      studentCode: item.student_code,
      studentName: item.student_name,
      score: item.score,
      remark: item.remark || '',
      valid: item.valid, // 是否有效(学生存在于课程中)
      error: item.error // 错误信息
    }))
    
    currentStep.value = 2
    message.success(`文件解析成功,共${previewData.value.length}条数据`)
  } catch (error: any) {
    message.error(error.message || '文件解析失败')
  } finally {
    loading.parse = false
  }
}

// 导入数据
const handleImport = async () => {
  loading.import = true
  try {
    const formData = new FormData()
    formData.append('file', fileList.value[0].originFileObj)
    formData.append('courseId', String(formState.courseId))
    formData.append('examType', formState.examType!)
    formData.append('examName', formState.examName || '')
    formData.append('examDate', formState.examDate.format('YYYY-MM-DD'))
    formData.append('fullScore', String(formState.fullScore))
    formData.append('weight', String(formState.weight))

    const response = await fetch('http://localhost:5030/api/v1/grades/import', {
      method: 'POST',
      credentials: 'include',
      body: formData
    })

    if (!response.ok) {
      const error = await response.json()
      throw new Error(error.message || '导入失败')
    }

    const result = await response.json()
    
    console.log('📊 导入结果:', result)
    
    // 更新导入结果 - 转换字段名
    importResult.totalRows = result.total_rows || 0
    importResult.successCount = result.success_count || 0
    importResult.skipCount = result.skip_count || 0
    importResult.failCount = result.fail_count || 0
    importResult.errors = result.errors || []
    importResult.warnings = result.warnings || []
    
    currentStep.value = 3
    message.success('导入完成')
  } catch (error: any) {
    message.error(error.message || '导入失败')
  } finally {
    loading.import = false
  }
}

// 下一步
const handleNext = async () => {
  try {
    await formRef.value?.validate()
    currentStep.value++
  } catch (error) {
    message.warning('请填写必填项')
  }
}

// 上一步
const handlePrev = () => {
  currentStep.value--
}

// 重置
const handleReset = () => {
  currentStep.value = 0
  fileList.value = []
  previewData.value = []
  Object.assign(importResult, {
    totalRows: 0,
    successCount: 0,
    skipCount: 0,
    failCount: 0,
    errors: [],
    warnings: []
  })
}

// 查看列表
const handleViewList = () => {
  router.push('/teacher/grades/list')
}

// 页面加载
onMounted(() => {
  loadCourses()
})
</script>

<style scoped lang="less">
.grade-import-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);

  :deep(.ant-card) {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  .steps {
    margin-bottom: 32px;
  }

  .step-content {
    margin-top: 32px;
    min-height: 400px;
  }

  .result-stats {
    display: flex;
    justify-content: center;
    margin-top: 24px;
  }
}
</style>
