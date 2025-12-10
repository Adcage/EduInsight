<template>
  <div class="attendance-detail-page">
    <div class="page-header">
      <a-button type="text" @click="goBack">
        <template #icon>
          <ArrowLeftOutlined/>
        </template>
        返回
      </a-button>
      <h1 class="page-title">签到详情</h1>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" tip="加载中..."/>
    </div>

    <!-- 详情内容 -->
    <div v-else-if="attendance" class="detail-content">
      <a-card class="info-card" title="考勤信息">
        <div class="info-grid">
          <div class="info-item">
            <span class="label">考勤标题:</span>
            <span class="value">{{ attendance.title }}</span>
          </div>
          <div class="info-item">
            <span class="label">课程名称:</span>
            <span class="value">{{ courseName }}</span>
          </div>
          <div class="info-item">
            <span class="label">发起教师:</span>
            <span class="value">{{ teacherName }}</span>
          </div>
          <div class="info-item">
            <span class="label">签到方式:</span>
            <span class="value">{{ attendanceTypeText }}</span>
          </div>
          <div class="info-item">
            <span class="label">开始时间:</span>
            <span class="value">{{ formatTime(attendance.startTime || attendance.start_time) }}</span>
          </div>
          <div class="info-item">
            <span class="label">结束时间:</span>
            <span class="value">{{ formatTime(attendance.endTime || attendance.end_time) }}</span>
          </div>
          <div class="info-item">
            <span class="label">考勤状态:</span>
            <a-tag :color="statusColor">{{ statusText }}</a-tag>
          </div>
        </div>
      </a-card>

      <!-- 我的签到记录 -->
      <a-card v-if="myRecord" class="record-card" title="我的签到记录">
        <div class="record-info">
          <div class="record-item">
            <span class="label">签到状态:</span>
            <a-tag :color="recordStatusColor">{{ recordStatusText }}</a-tag>
          </div>
          <div v-if="myRecord.checkInTime || myRecord.check_in_time" class="record-item">
            <span class="label">签到时间:</span>
            <span class="value">{{ formatTime(myRecord.checkInTime || myRecord.check_in_time) }}</span>
          </div>
          <div v-if="myRecord.remark" class="record-item">
            <span class="label">备注:</span>
            <span class="value">{{ myRecord.remark }}</span>
          </div>
        </div>
      </a-card>

      <!-- 签到按钮 -->
      <div v-if="canCheckIn" class="action-section">
        <a-button block size="large" type="primary" @click="handleCheckIn">
          立即签到
        </a-button>
      </div>
    </div>

    <!-- 签到模态框 -->
    <CheckInModal
        v-model:visible="checkInModalVisible"
        :attendance="attendance"
        @success="handleCheckInSuccess"
    />
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {message} from 'ant-design-vue'
import {ArrowLeftOutlined} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import CheckInModal from './components/CheckInModal.vue'
import {
  AttendanceStatus,
  getStudentAttendanceDetail,
  type StudentAttendanceNotification
} from '@/api/attendanceController'

const route = useRoute()
const router = useRouter()

const loading = ref(false)
const attendance = ref<StudentAttendanceNotification | null>(null)
const checkInModalVisible = ref(false)

// 课程名称
const courseName = computed(() => {
  return attendance.value?.courseName || attendance.value?.course_name || '未知课程'
})

// 教师名称
const teacherName = computed(() => {
  return attendance.value?.teacherName || attendance.value?.teacher_name || '未知教师'
})

// 考勤类型文本
const attendanceTypeText = computed(() => {
  const type = attendance.value?.attendanceType || attendance.value?.attendance_type
  const typeMap: Record<string, string> = {
    'qrcode': '二维码签到',
    'gesture': '手势签到',
    'location': '位置签到',
    'face': '人脸识别签到',
    'manual': '手动签到'
  }
  return typeMap[type || ''] || '未知方式'
})

// 考勤状态
const attendanceStatus = computed(() => {
  return attendance.value?.status || AttendanceStatus.PENDING
})

// 状态文本
const statusText = computed(() => {
  const statusMap: Record<string, string> = {
    'pending': '待开始',
    'active': '进行中',
    'ended': '已结束'
  }
  return statusMap[attendanceStatus.value] || '未知'
})

// 状态颜色
const statusColor = computed(() => {
  const colorMap: Record<string, string> = {
    'pending': 'default',
    'active': 'processing',
    'ended': 'error'
  }
  return colorMap[attendanceStatus.value] || 'default'
})

// 我的签到记录
const myRecord = computed(() => {
  return attendance.value?.myRecord || attendance.value?.my_record
})

// 签到状态文本
const recordStatusText = computed(() => {
  if (!myRecord.value) return '未签到'
  const statusMap: Record<string, string> = {
    'present': '已签到',
    'late': '迟到',
    'absent': '缺勤',
    'leave': '请假'
  }
  return statusMap[myRecord.value.status] || '未签到'
})

// 签到状态颜色
const recordStatusColor = computed(() => {
  if (!myRecord.value) return 'default'
  const colorMap: Record<string, string> = {
    'present': 'success',
    'late': 'warning',
    'absent': 'error',
    'leave': 'processing'
  }
  return colorMap[myRecord.value.status] || 'default'
})

// 是否可以签到
const canCheckIn = computed(() => {
  const isActive = attendanceStatus.value === 'active'
  const isCheckedIn = myRecord.value?.status === 'present' || myRecord.value?.status === 'late'
  return isActive && !isCheckedIn
})

// 格式化时间
const formatTime = (time?: string) => {
  if (!time) return '--'
  // 移除UTC时区标记，确保显示为数据库存储的本地时间
  const localTime = time.replace('Z', '').replace('+00:00', '')
  return dayjs(localTime).format('YYYY-MM-DD HH:mm:ss')
}

// 获取考勤详情
const fetchAttendanceDetail = async () => {
  const id = Number(route.params.id)
  if (!id) {
    message.error('考勤ID无效')
    goBack()
    return
  }

  try {
    loading.value = true
    attendance.value = await getStudentAttendanceDetail(id)
  } catch (error: any) {
    console.error('获取考勤详情失败:', error)
    message.error(error.message || '获取考勤详情失败')
  } finally {
    loading.value = false
  }
}

// 返回
const goBack = () => {
  router.back()
}

// 处理签到
const handleCheckIn = () => {
  checkInModalVisible.value = true
}

// 处理签到成功
const handleCheckInSuccess = () => {
  message.success('签到成功！')
  checkInModalVisible.value = false
  // 刷新详情
  fetchAttendanceDetail()
}

// 页面加载时获取数据
onMounted(() => {
  fetchAttendanceDetail()
})
</script>

<style lang="scss" scoped>
.attendance-detail-page {
  min-height: 100vh;
  background: var(--background-color, #f5f5f5);
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;

  .page-title {
    font-size: 24px;
    font-weight: 600;
    color: var(--text-color, #262626);
    margin: 12px 0 0 0;
  }
}

.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.detail-content {
  max-width: 800px;
  margin: 0 auto;
}

.info-card,
.record-card {
  margin-bottom: 20px;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  :deep(.ant-card-head) {
    border-bottom: 1px solid #f0f0f0;
    font-weight: 600;
  }
}

.info-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;

  @media (max-width: 768px) {
    grid-template-columns: 1fr;
  }
}

.info-item,
.record-item {
  display: flex;
  align-items: center;
  padding: 8px 0;

  .label {
    color: var(--text-secondary-color, #8c8c8c);
    min-width: 80px;
    flex-shrink: 0;
  }

  .value {
    color: var(--text-color, #262626);
    font-weight: 500;
  }
}

.record-info {
  .record-item {
    padding: 12px 0;

    &:not(:last-child) {
      border-bottom: 1px dashed #f0f0f0;
    }
  }
}

.action-section {
  margin-top: 24px;
}
</style>
