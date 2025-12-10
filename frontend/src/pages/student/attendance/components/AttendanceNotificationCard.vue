<template>
  <div class="attendance-card" :class="cardClass">
    <div class="card-header">
      <div class="header-left">
        <div class="attendance-icon" :class="iconClass">
          <component :is="attendanceIcon" class="icon" />
        </div>
        <div class="header-info">
          <h3 class="attendance-title">{{ attendance.title }}</h3>
          <p class="course-name">{{ courseName }}</p>
        </div>
      </div>
      <div class="header-right">
        <a-tag :color="statusColor" class="status-tag">
          {{ statusText }}
        </a-tag>
      </div>
    </div>

    <div class="card-body">
      <div class="info-row">
        <ClockCircleOutlined class="info-icon" />
        <span class="info-label">考勤时间:</span>
        <span class="info-value">{{ formatTime(attendance.startTime || attendance.start_time) }}</span>
      </div>

      <div class="info-row">
        <UserOutlined class="info-icon" />
        <span class="info-label">发起教师:</span>
        <span class="info-value">{{ teacherName }}</span>
      </div>

      <div class="info-row">
        <TagOutlined class="info-icon" />
        <span class="info-label">签到方式:</span>
        <span class="info-value">{{ attendanceTypeText }}</span>
      </div>

      <div v-if="myRecord" class="info-row check-in-status">
        <CheckCircleOutlined v-if="isCheckedIn" class="info-icon success" />
        <CloseCircleOutlined v-else class="info-icon error" />
        <span class="info-label">签到状态:</span>
        <span class="info-value" :class="checkInStatusClass">
          {{ checkInStatusText }}
        </span>
        <span v-if="myRecord.checkInTime || myRecord.check_in_time" class="check-in-time">
          {{ formatTime(myRecord.checkInTime || myRecord.check_in_time) }}
        </span>
      </div>
    </div>

    <div class="card-footer">
      <a-button 
        v-if="canCheckIn" 
        type="primary" 
        block 
        size="large"
        @click="handleCheckIn"
      >
        立即签到
      </a-button>
      <a-button 
        v-else-if="isCheckedIn" 
        block 
        size="large"
        disabled
      >
        已签到
      </a-button>
      <a-button 
        v-else 
        block 
        size="large"
        @click="handleViewDetail"
      >
        查看详情
      </a-button>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { computed } from 'vue'
import { 
  ClockCircleOutlined, 
  UserOutlined, 
  TagOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  QrcodeOutlined,
  EnvironmentOutlined,
  FormOutlined,
  ScanOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import type { StudentAttendanceNotification } from '@/api/attendanceController'
import { AttendanceStatus } from '@/api/attendanceController'

interface Props {
  attendance: StudentAttendanceNotification
}

interface Emits {
  (e: 'checkIn', attendance: StudentAttendanceNotification): void
  (e: 'viewDetail', attendance: StudentAttendanceNotification): void
}

const props = defineProps<Props>()
const emits = defineEmits<Emits>()

// 课程名称
const courseName = computed(() => {
  return props.attendance.courseName || props.attendance.course_name || '未知课程'
})

// 教师名称
const teacherName = computed(() => {
  return props.attendance.teacherName || props.attendance.teacher_name || '未知教师'
})

// 考勤类型文本
const attendanceTypeText = computed(() => {
  const type = props.attendance.attendanceType || props.attendance.attendance_type
  const typeMap: Record<string, string> = {
    'qrcode': '二维码签到',
    'gesture': '手势签到',
    'location': '位置签到',
    'face': '人脸识别签到',
    'manual': '手动签到'
  }
  return typeMap[type || ''] || '未知方式'
})

// 考勤图标
const attendanceIcon = computed(() => {
  const type = props.attendance.attendanceType || props.attendance.attendance_type
  const iconMap: Record<string, any> = {
    'qrcode': QrcodeOutlined,
    'gesture': FormOutlined,
    'location': EnvironmentOutlined,
    'face': ScanOutlined,
    'manual': CheckCircleOutlined
  }
  return iconMap[type || ''] || QrcodeOutlined
})

// 图标样式类
const iconClass = computed(() => {
  const type = props.attendance.attendanceType || props.attendance.attendance_type
  return `icon-${type || 'default'}`
})

// 考勤状态
const attendanceStatus = computed(() => {
  return props.attendance.status || AttendanceStatus.PENDING
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

// 卡片样式类
const cardClass = computed(() => {
  return {
    'status-pending': attendanceStatus.value === 'pending',
    'status-active': attendanceStatus.value === 'active',
    'status-ended': attendanceStatus.value === 'ended',
    'checked-in': isCheckedIn.value
  }
})

// 我的签到记录
const myRecord = computed(() => {
  return props.attendance.myRecord || props.attendance.my_record
})

// 是否已签到
const isCheckedIn = computed(() => {
  if (props.attendance.isCheckedIn !== undefined) {
    return props.attendance.isCheckedIn
  }
  if (props.attendance.is_checked_in !== undefined) {
    return props.attendance.is_checked_in
  }
  if (myRecord.value) {
    const status = myRecord.value.status
    return status === 'present' || status === 'late'
  }
  return false
})

// 签到状态文本
const checkInStatusText = computed(() => {
  if (!myRecord.value) return '未签到'
  const statusMap: Record<string, string> = {
    'present': '已签到',
    'late': '迟到',
    'absent': '缺勤',
    'leave': '请假'
  }
  return statusMap[myRecord.value.status] || '未签到'
})

// 签到状态样式类
const checkInStatusClass = computed(() => {
  if (!myRecord.value) return ''
  return `status-${myRecord.value.status}`
})

// 是否可以签到
const canCheckIn = computed(() => {
  return attendanceStatus.value === 'active' && !isCheckedIn.value
})

// 格式化时间
const formatTime = (time?: string) => {
  if (!time) return '--'
  // 如果时间字符串没有时区信息，dayjs会当作本地时间
  // 但如果数据库存储的就是本地时间，需要明确告诉dayjs不要转换
  // 使用 .replace('Z', '') 移除可能的UTC标记
  const localTime = time.replace('Z', '').replace('+00:00', '')
  return dayjs(localTime).format('MM-DD HH:mm')
}

// 处理签到
const handleCheckIn = () => {
  console.log('[AttendanceNotificationCard] handleCheckIn clicked, attendance:', props.attendance)
  console.log('[AttendanceNotificationCard] Emitting checkIn event')
  emits('checkIn', props.attendance)
}

// 查看详情
const handleViewDetail = () => {
  emits('viewDetail', props.attendance)
}
</script>

<style scoped lang="scss">
.attendance-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: all 0.3s ease;
  border: 2px solid transparent;

  &:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
    transform: translateY(-2px);
  }

  &.status-active {
    border-color: var(--primary-color, #1890ff);
  }

  &.checked-in {
    background: linear-gradient(135deg, #f6ffed 0%, #ffffff 100%);
  }
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid #f0f0f0;
}

.header-left {
  display: flex;
  align-items: center;
  flex: 1;
  min-width: 0;
}

.attendance-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  margin-right: 12px;
  flex-shrink: 0;

  .icon {
    font-size: 24px;
  }

  &.icon-qrcode {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    .icon {
      color: white;
    }
  }

  &.icon-gesture {
    background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
    .icon {
      color: white;
    }
  }

  &.icon-location {
    background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
    .icon {
      color: white;
    }
  }

  &.icon-face {
    background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
    .icon {
      color: white;
    }
  }

  &.icon-default {
    background: linear-gradient(135deg, #a8edea 0%, #fed6e3 100%);
    .icon {
      color: #666;
    }
  }
}

.header-info {
  flex: 1;
  min-width: 0;
}

.attendance-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-color, #262626);
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.course-name {
  font-size: 14px;
  color: var(--text-secondary-color, #8c8c8c);
  margin: 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.header-right {
  flex-shrink: 0;
  margin-left: 12px;
}

.status-tag {
  font-size: 12px;
  padding: 2px 8px;
  border-radius: 4px;
}

.card-body {
  margin-bottom: 16px;
}

.info-row {
  display: flex;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;

  &.check-in-status {
    margin-top: 8px;
    padding-top: 12px;
    border-top: 1px dashed #f0f0f0;
  }
}

.info-icon {
  font-size: 16px;
  color: var(--text-secondary-color, #8c8c8c);
  margin-right: 8px;
  flex-shrink: 0;

  &.success {
    color: #52c41a;
  }

  &.error {
    color: #ff4d4f;
  }
}

.info-label {
  color: var(--text-secondary-color, #8c8c8c);
  margin-right: 8px;
  flex-shrink: 0;
}

.info-value {
  color: var(--text-color, #262626);
  font-weight: 500;

  &.status-present {
    color: #52c41a;
  }

  &.status-late {
    color: #faad14;
  }

  &.status-absent {
    color: #ff4d4f;
  }

  &.status-leave {
    color: #1890ff;
  }
}

.check-in-time {
  margin-left: auto;
  font-size: 12px;
  color: var(--text-secondary-color, #8c8c8c);
}

.card-footer {
  margin-top: 16px;
}
</style>
