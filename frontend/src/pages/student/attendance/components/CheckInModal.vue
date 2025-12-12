<template>
  <a-modal
      :footer="null"
      :maskClosable="false"
      :open="visible"
      :title="modalTitle"
      width="500px"
      @cancel="handleCancel"
  >
    <div v-if="attendance" class="check-in-modal-content">
      <!-- 考勤信息 -->
      <div class="attendance-info">
        <div class="info-item">
          <span class="label">考勤标题:</span>
          <span class="value">{{ attendance.title }}</span>
        </div>
        <div class="info-item">
          <span class="label">课程名称:</span>
          <span class="value">{{ courseName }}</span>
        </div>
        <div class="info-item">
          <span class="label">签到方式:</span>
          <span class="value">{{ attendanceTypeText }}</span>
        </div>
        <div class="info-item">
          <span class="label">考勤时间:</span>
          <span class="value">{{ formatTimeRange }}</span>
        </div>
      </div>

      <!-- 签到提示 -->
      <a-alert
          :message="checkInTip"
          class="check-in-tip"
          show-icon
          type="info"
      />

      <!-- 手势签到输入 -->
      <div v-if="isGestureType" class="gesture-input-section">
        <GestureInput
            v-model="gestureCode"
            :show-actions="false"
            :show-code="false"
            :size="300"
            hint="请连接与教师相同的点（至少4个点）"
            @gesture-data-change="handleGestureDataChange"
        />
      </div>

      <!-- 位置签到信息 -->
      <div v-if="isLocationType" class="location-info-section">
        <div class="location-tip">
          <a-alert show-icon type="info">
            <template #message>
              <div>
                <div>点击"定位当前位置"按钮获取您的位置，系统将自动计算与签到点的距离</div>
                <div style="margin-top: 4px; font-size: 12px; opacity: 0.8;">
                  提示：如果定位失败，可以使用搜索功能手动选择您的位置
                </div>
              </div>
            </template>
          </a-alert>
        </div>

        <MapLocationPicker
            v-model="locationData"
            :default-radius="props.attendance?.locationRange || props.attendance?.location_range || 100"
            :editable="true"
            :show-radius="false"
            :target-location="targetLocation"
            :use-browser-fallback="false"
            height="400px"
        />

        <div v-if="distance !== null" class="distance-display">
          <a-alert :type="isInRange ? 'success' : 'error'" show-icon>
            <template #message>
              <div class="distance-content">
                <span class="distance-label">距离签到点：</span>
                <span class="distance-value">{{ distance.toFixed(0) }} 米</span>
                <span class="distance-status">{{ isInRange ? '✓ 在范围内' : '✗ 超出范围' }}</span>
              </div>
            </template>
          </a-alert>
        </div>
      </div>

      <!-- 签到按钮 -->
      <div class="action-buttons">
        <a-button block @click="handleCancel">取消</a-button>
        <a-button
            :loading="checking"
            block
            type="primary"
            @click="handleCheckIn"
        >
          {{ checkInButtonText }}
        </a-button>
      </div>
    </div>
  </a-modal>
</template>

<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import dayjs from 'dayjs'
import type {StudentAttendanceNotification} from '@/api/attendanceController'
import request from '@/request'
import GestureInput from '@/components/GestureInput.vue'
import MapLocationPicker from '@/components/MapLocationPicker.vue'

interface Props {
  visible: boolean
  attendance: StudentAttendanceNotification | null
}

interface Emits {
  (e: 'update:visible', value: boolean): void

  (e: 'success'): void
}

const props = defineProps<Props>()
const emits = defineEmits<Emits>()

const checking = ref(false)
const gestureCode = ref('')
const gestureData = ref<any>(null)
const locationData = ref<{ lng: number; lat: number; address?: string } | null>(null)
const targetLocation = ref<{ lng: number; lat: number; address?: string } | null>(null)
const distance = ref<number | null>(null)

// 模态框标题
const modalTitle = computed(() => {
  const type = props.attendance?.attendanceType || props.attendance?.attendance_type
  const typeMap: Record<string, string> = {
    'qrcode': '二维码签到',
    'gesture': '手势签到',
    'location': '位置签到',
    'face': '人脸识别签到'
  }
  return typeMap[type || ''] || '签到'
})

// 课程名称
const courseName = computed(() => {
  return props.attendance?.courseName || props.attendance?.course_name || '未知课程'
})

// 考勤类型文本
const attendanceTypeText = computed(() => {
  const type = props.attendance?.attendanceType || props.attendance?.attendance_type
  const typeMap: Record<string, string> = {
    'qrcode': '二维码签到',
    'gesture': '手势签到',
    'location': '位置签到',
    'face': '人脸识别签到'
  }
  return typeMap[type || ''] || '未知方式'
})

// 格式化时间范围
const formatTimeRange = computed(() => {
  if (!props.attendance) return '--'
  const start = props.attendance.startTime || props.attendance.start_time
  const end = props.attendance.endTime || props.attendance.end_time
  if (!start || !end) return '--'
  // 移除UTC时区标记
  const localStart = start.replace('Z', '').replace('+00:00', '')
  const localEnd = end.replace('Z', '').replace('+00:00', '')
  return `${dayjs(localStart).format('MM-DD HH:mm')} ~ ${dayjs(localEnd).format('HH:mm')}`
})

// 判断签到类型
const isGestureType = computed(() => {
  const type = props.attendance?.attendanceType || props.attendance?.attendance_type
  return type === 'gesture'
})

const isLocationType = computed(() => {
  const type = props.attendance?.attendanceType || props.attendance?.attendance_type
  return type === 'location'
})

const isInRange = computed(() => {
  if (distance.value === null) return false
  const range = props.attendance?.locationRange || props.attendance?.location_range || 100
  return distance.value <= range
})

// 签到提示
const checkInTip = computed(() => {
  const type = props.attendance?.attendanceType || props.attendance?.attendance_type
  const tipMap: Record<string, string> = {
    'qrcode': '请扫描教师展示的二维码完成签到',
    'gesture': '请输入教师提供的手势码完成签到',
    'location': '系统将自动获取您的位置信息，请确保在签到范围内',
    'face': '请进行人脸识别完成签到'
  }
  return tipMap[type || ''] || '请按照要求完成签到'
})

// 签到按钮文本
const checkInButtonText = computed(() => {
  const type = props.attendance?.attendanceType || props.attendance?.attendance_type
  const textMap: Record<string, string> = {
    'qrcode': '扫码签到',
    'gesture': '手势签到',
    'location': '位置签到',
    'face': '人脸签到'
  }
  return textMap[type || ''] || '开始签到'
})

// 处理取消
const handleCancel = () => {
  emits('update:visible', false)
}


// 计算两点间距离（Haversine公式）
const calculateDistance = (lat1: number, lon1: number, lat2: number, lon2: number): number => {
  const R = 6371000 // 地球半径（米）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLon = (lon2 - lon1) * Math.PI / 180
  const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a))
  return R * c
}

// 处理手势数据变化
const handleGestureDataChange = (data: any) => {
  gestureData.value = data
  console.log('[CheckInModal] Gesture data received:', data)
}

// 手势签到
const handleGestureCheckIn = async () => {
  if (!gestureData.value || !gestureData.value.points || gestureData.value.points.length < 4) {
    message.warning('请绘制手势（至少连接4个点）')
    return
  }

  try {
    checking.value = true
    // 发送完整的手势数据，与教师端格式一致
    const response = await request.post('/api/v1/students/attendances/gesture/verify', {
      attendance_id: props.attendance!.id,
      gesture_code: gestureData.value.points.join('-'),  // 保持兼容性
      gesture_pattern: gestureData.value  // 发送完整数据
    })

    if (response.data) {
      message.success('签到成功！')
      emits('success')
      emits('update:visible', false)
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '签到失败，请重试')
  } finally {
    checking.value = false
  }
}

// 位置签到
const handleLocationCheckIn = async () => {
  console.log('[CheckInModal] handleLocationCheckIn - locationData:', locationData.value)
  console.log('[CheckInModal] handleLocationCheckIn - targetLocation:', targetLocation.value)
  console.log('[CheckInModal] handleLocationCheckIn - distance:', distance.value)
  console.log('[CheckInModal] handleLocationCheckIn - isInRange:', isInRange.value)

  if (!locationData.value) {
    message.warning('请先获取位置信息')
    return
  }

  if (!isInRange.value) {
    message.warning('您不在签到范围内，无法完成签到')
    return
  }

  try {
    checking.value = true
    const requestData = {
      attendance_id: props.attendance!.id,
      latitude: locationData.value.lat,
      longitude: locationData.value.lng
    }
    console.log('[CheckInModal] 发送签到请求:', requestData)

    const response = await request.post('/api/v1/students/attendances/location/verify', requestData)

    if (response.data) {
      message.success('签到成功！')
      emits('success')
      emits('update:visible', false)
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '签到失败，请重试')
  } finally {
    checking.value = false
  }
}

// 处理签到
const handleCheckIn = async () => {
  if (!props.attendance) return

  const type = props.attendance.attendanceType || props.attendance.attendance_type

  switch (type) {
    case 'qrcode':
      message.info('请使用手机扫描二维码')
      // TODO: 实现二维码扫描功能
      break
    case 'gesture':
      await handleGestureCheckIn()
      break
    case 'location':
      await handleLocationCheckIn()
      break
    case 'face':
      message.info('人脸识别功能开发中')
      break
    default:
      message.warning('未知的签到方式')
  }
}

// 监听locationData变化，计算距离
watch(locationData, (newVal) => {
  console.log('[CheckInModal] locationData changed:', newVal)
  if (newVal && targetLocation.value) {
    const calculatedDistance = calculateDistance(
        newVal.lat,
        newVal.lng,
        targetLocation.value.lat,
        targetLocation.value.lng
    )
    distance.value = calculatedDistance
    console.log('[CheckInModal] 计算距离:', calculatedDistance, '米')
    console.log('[CheckInModal] 签到范围:', props.attendance?.locationRange || props.attendance?.location_range, '米')
  }
})

// 监听模态框打开，自动获取位置
watch(() => props.visible, (newVal, oldVal) => {
  console.log('[CheckInModal] visible changed from', oldVal, 'to', newVal)
  console.log('[CheckInModal] attendance:', props.attendance)

  if (newVal) {
    // 如果是位置签到，设置目标位置
    if (isLocationType.value && props.attendance) {
      const targetLat = props.attendance.locationLatitude || props.attendance.location_latitude
      const targetLon = props.attendance.locationLongitude || props.attendance.location_longitude
      if (targetLat && targetLon) {
        // 保存目标位置（用于距离计算）
        targetLocation.value = {
          lng: targetLon,
          lat: targetLat,
          address: props.attendance.locationName || props.attendance.location_name || '签到位置'
        }
        console.log('[CheckInModal] 设置目标位置:', targetLocation.value)
        // 不设置locationData，让学生点击定位按钮后才获取当前位置
        // locationData会在MapLocationPicker定位成功后自动更新
      }
    }
  } else {
    // 重置状态
    gestureCode.value = ''
    locationData.value = null
    targetLocation.value = null
    distance.value = null
  }
})
</script>

<style lang="scss" scoped>
.check-in-modal-content {
  padding: 8px 0;
}

.attendance-info {
  background: var(--background-color, #fafafa);
  border-radius: 8px;
  padding: 16px;
  margin-bottom: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  padding: 8px 0;
  font-size: 14px;

  &:not(:last-child) {
    border-bottom: 1px dashed #f0f0f0;
  }

  .label {
    color: var(--text-secondary-color, #8c8c8c);
    min-width: 80px;
    flex-shrink: 0;
  }

  .value {
    color: var(--text-color, #262626);
    font-weight: 500;
    flex: 1;
  }
}

.check-in-tip {
  margin-bottom: 24px;
}

.action-buttons {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.gesture-input-section {
  margin-bottom: 24px;
}

.location-info-section {
  margin-bottom: 24px;
}

.location-tip {
  margin-bottom: 16px;
}

.distance-display {
  margin-top: 16px;

  .distance-content {
    display: flex;
    align-items: center;
    gap: 8px;

    .distance-label {
      font-weight: 600;
    }

    .distance-value {
      font-family: monospace;
      font-size: 18px;
      font-weight: 700;
    }

    .distance-status {
      margin-left: auto;
      font-weight: 600;
    }
  }
}
</style>
