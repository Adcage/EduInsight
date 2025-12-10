<template>
  <div class="grade-add-page">
    <a-card :bordered="false" title="📝 成绩录入">
      <a-form
          ref="formRef"
          :model="formState"
          :rules="rules"
          layout="vertical"
          @finish="handleSubmit"
      >
        <a-row :gutter="16">
          <!-- 课程选择 -->
          <a-col :span="12">
            <a-form-item label="课程" name="courseId" required>
              <a-select
                  v-model:value="formState.courseId"
                  :filter-option="filterOption"
                  :loading="loading.courses"
                  placeholder="请选择课程"
                  show-search
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
          </a-col>

          <!-- 学生选择 -->
          <a-col :span="12">
            <a-form-item label="学生" name="studentId" required>
              <a-select
                  v-model:value="formState.studentId"
                  :disabled="!formState.courseId"
                  :filter-option="filterOption"
                  :loading="loading.students"
                  placeholder="请先选择课程"
                  show-search
              >
                <a-select-option
                    v-for="student in students"
                    :key="student.id"
                    :value="student.id"
                >
                  {{ student.real_name }} ({{ student.user_code }})
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <!-- 考试类型 -->
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

          <!-- 考试名称 -->
          <a-col :span="12">
            <a-form-item label="考试名称" name="examName">
              <a-input v-model:value="formState.examName" placeholder="例如:第一次月考"/>
            </a-form-item>
          </a-col>

          <!-- 分数 -->
          <a-col :span="8">
            <a-form-item label="分数" name="score" required>
              <a-input-number
                  v-model:value="formState.score"
                  :max="formState.fullScore"
                  :min="0"
                  :precision="1"
                  placeholder="请输入分数"
                  style="width: 100%"
              />
            </a-form-item>
          </a-col>

          <!-- 满分 -->
          <a-col :span="8">
            <a-form-item label="满分" name="fullScore">
              <a-input-number
                  v-model:value="formState.fullScore"
                  :min="1"
                  :precision="0"
                  placeholder="默认100分"
                  style="width: 100%"
              />
            </a-form-item>
          </a-col>

          <!-- 权重 -->
          <a-col :span="8">
            <a-form-item label="权重" name="weight">
              <a-input-number
                  v-model:value="formState.weight"
                  :max="10"
                  :min="0"
                  :precision="2"
                  :step="0.1"
                  placeholder="默认1.0"
                  style="width: 100%"
              />
            </a-form-item>
          </a-col>

          <!-- 考试日期 -->
          <a-col :span="12">
            <a-form-item label="考试日期" name="examDate">
              <a-date-picker
                  v-model:value="formState.examDate"
                  :disabled-date="disabledDate"
                  placeholder="请选择考试日期"
                  style="width: 100%"
              />
            </a-form-item>
          </a-col>

          <!-- 备注 -->
          <a-col :span="24">
            <a-form-item label="备注" name="remark">
              <a-textarea
                  v-model:value="formState.remark"
                  :maxlength="255"
                  :rows="3"
                  placeholder="请输入备注信息(选填)"
                  show-count
              />
            </a-form-item>
          </a-col>
        </a-row>

        <!-- 操作按钮 -->
        <a-form-item>
          <a-space>
            <a-button :loading="loading.submit" html-type="submit" type="primary">
              提交
            </a-button>
            <a-button @click="handleReset">重置</a-button>
            <a-button @click="handleCancel">取消</a-button>
          </a-space>
        </a-form-item>
      </a-form>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, reactive, ref} from 'vue'
import {message} from 'ant-design-vue'
import {useRouter} from 'vue-router'
import type {Dayjs} from 'dayjs'
import dayjs from 'dayjs'
import {gradeApiPost} from '@/api/gradeController'
import type {API} from '@/api/typings'

const router = useRouter()
const formRef = ref()

// 表单状态
const formState = reactive({
  courseId: undefined as number | undefined,
  studentId: undefined as number | undefined,
  examType: undefined as string | undefined,
  examName: '',
  score: undefined as number | undefined,
  fullScore: 100,
  weight: 1.0,
  examDate: dayjs() as Dayjs,
  remark: ''
})

// 加载状态
const loading = reactive({
  courses: false,
  students: false,
  submit: false
})

// 数据列表
const courses = ref<any[]>([])
const students = ref<any[]>([])

// 表单验证规则
const rules = {
  courseId: [{required: true, message: '请选择课程', trigger: 'change'}],
  studentId: [{required: true, message: '请选择学生', trigger: 'change'}],
  examType: [{required: true, message: '请选择考试类型', trigger: 'change'}],
  score: [
    {required: true, message: '请输入分数', trigger: 'blur'},
    {type: 'number', min: 0, message: '分数不能小于0', trigger: 'blur'}
  ]
}

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

// 课程变化时加载学生列表
const handleCourseChange = async (courseId: number) => {
  formState.studentId = undefined
  students.value = []

  if (!courseId) return

  loading.students = true
  try {
    const response = await fetch(
        `http://localhost:5000/api/v1/grades/course-students?courseId=${courseId}`,
        {
          method: 'GET',
          credentials: 'include'
        }
    )

    if (!response.ok) {
      throw new Error('加载学生列表失败')
    }

    students.value = await response.json()
  } catch (error: any) {
    message.error(error.message || '加载学生列表失败')
  } finally {
    loading.students = false
  }
}

// 提交表单
const handleSubmit = async () => {
  loading.submit = true
  try {
    const params: API.GradeCreateModel = {
      courseId: formState.courseId!,
      studentId: formState.studentId!,
      examType: formState.examType as any,
      examName: formState.examName || undefined,
      score: formState.score!,
      fullScore: formState.fullScore,
      weight: formState.weight,
      examDate: formState.examDate.format('YYYY-MM-DD'),
      remark: formState.remark || undefined
    }

    await gradeApiPost(params)

    message.success('成绩录入成功')
    handleReset()

    // 可选: 跳转到成绩列表
    // router.push('/teacher/grades/list')
  } catch (error: any) {
    // 提取后端返回的错误信息
    let errorMsg = '成绩录入失败'
    if (error.response?.data?.message) {
      errorMsg = error.response.data.message
    } else if (error.message) {
      errorMsg = error.message
    }
    message.error(errorMsg)
  } finally {
    loading.submit = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
  formState.courseId = undefined
  formState.studentId = undefined
  formState.examType = undefined
  formState.examName = ''
  formState.score = undefined
  formState.fullScore = 100
  formState.weight = 1.0
  formState.examDate = dayjs()
  formState.remark = ''
  students.value = []
}

// 取消
const handleCancel = () => {
  router.back()
}

// 页面加载时获取课程列表
onMounted(() => {
  loadCourses()
})
</script>

<style lang="less" scoped>
.grade-add-page {
  padding: 24px;
  background: #f0f2f5;
  min-height: calc(100vh - 64px);

  :deep(.ant-card) {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  }

  :deep(.ant-card-head-title) {
    font-size: 18px;
    font-weight: 600;
  }
}
</style>
