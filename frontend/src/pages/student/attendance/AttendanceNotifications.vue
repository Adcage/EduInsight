<template>
  <div class="attendance-notifications-page">
    <div class="page-header">
      <div class="header-content">
        <div class="header-text">
          <h1 class="page-title">签到通知</h1>
          <p class="page-description">查看所有课程的签到通知，及时完成签到</p>
        </div>
        <a-button 
          type="primary" 
          size="large"
          @click="handleGoToFaceUpload"
          class="face-upload-btn"
        >
          <template #icon><CameraOutlined /></template>
          上传人脸照片
        </a-button>
      </div>
    </div>

    <!-- 筛选器 -->
    <div class="filter-section">
      <a-tabs v-model:activeKey="activeTab" @change="handleTabChange">
        <a-tab-pane key="all" tab="全部" />
        <a-tab-pane key="active" tab="进行中">
          <template #tab>
            <a-badge :count="activeCount" :offset="[10, 0]">
              <span>进行中</span>
            </a-badge>
          </template>
        </a-tab-pane>
        <a-tab-pane key="pending" tab="待开始" />
        <a-tab-pane key="ended" tab="已结束" />
        <a-tab-pane key="statistics" tab="数据统计" />
      </a-tabs>
    </div>

    <!-- 数据统计Tab -->
    <StudentStatistics v-if="activeTab === 'statistics'" />

    <!-- 加载状态 -->
    <div v-else-if="loading" class="loading-container">
      <a-spin size="large" tip="加载中..." />
    </div>

    <!-- 空状态 -->
    <div v-else-if="attendances.length === 0" class="empty-container">
      <a-empty description="暂无签到通知">
        <template #image>
          <InboxOutlined style="font-size: 64px; color: #d9d9d9" />
        </template>
      </a-empty>
    </div>

    <!-- 签到通知列表 -->
    <div v-else class="attendance-list">
      <div class="list-grid">
        <AttendanceNotificationCard
          v-for="attendance in attendances"
          :key="attendance.id"
          :attendance="attendance"
          @check-in="handleCheckIn"
          @view-detail="handleViewDetail"
        />
      </div>

      <!-- 分页 -->
      <div v-if="total > perPage" class="pagination-container">
        <a-pagination
          v-model:current="currentPage"
          v-model:page-size="perPage"
          :total="total"
          :show-size-changer="false"
          :show-total="(total: number) => `共 ${total} 条`"
          @change="handlePageChange"
        />
      </div>
    </div>

    <!-- 签到模态框 -->
    <CheckInModal
      v-model:visible="checkInModalVisible"
      :attendance="selectedAttendance"
      @success="handleCheckInSuccess"
    />

    <!-- WebSocket调试组件 -->
    <WebSocketDebug />
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { InboxOutlined, CameraOutlined } from '@ant-design/icons-vue'
import AttendanceNotificationCard from './components/AttendanceNotificationCard.vue'
import CheckInModal from './components/CheckInModal.vue'
import WebSocketDebug from '@/components/WebSocketDebug.vue'
import StudentStatistics from './StudentStatistics.vue'
import { 
  getStudentAttendances, 
  type StudentAttendanceNotification,
  AttendanceStatus 
} from '@/api/attendanceController'
import { useWebSocketStore } from '@/stores/websocket'

const router = useRouter()

// 数据状态
const loading = ref(false)
const attendances = ref<StudentAttendanceNotification[]>([])
const total = ref(0)
const currentPage = ref(1)
const perPage = ref(12)
const activeTab = ref('all')

// 模态框状态
const checkInModalVisible = ref(false)
const selectedAttendance = ref<StudentAttendanceNotification | null>(null)

// 进行中的考勤数量
const activeCount = computed(() => {
  return attendances.value.filter(a => a.status === AttendanceStatus.ACTIVE).length
})

// 获取签到通知列表
const fetchAttendances = async () => {
  try {
    loading.value = true
    
    const params: any = {
      page: currentPage.value,
      perPage: perPage.value
    }
    
    // 根据标签页筛选状态
    if (activeTab.value !== 'all' && activeTab.value !== 'statistics') {
      params.status = activeTab.value
    }
    
    const response = await getStudentAttendances(params)
    const res = (response as any).data ? (response as any).data : response;
    
    attendances.value = res.attendances || []
    total.value = res.total || 0
    
  } catch (error: any) {
    console.error('获取签到通知失败:', error)
    message.error(error.message || '获取签到通知失败')
  } finally {
    loading.value = false
  }
}

// 处理标签页切换
const handleTabChange = (key: string) => {
  activeTab.value = key
  currentPage.value = 1
  
  // 如果切换到数据统计标签页，不需要加载签到通知列表
  if (key !== 'statistics') {
    fetchAttendances()
  }
}

// 处理分页变化
const handlePageChange = (page: number) => {
  currentPage.value = page
  fetchAttendances()
  // 滚动到顶部
  window.scrollTo({ top: 0, behavior: 'smooth' })
}

// 处理签到
const handleCheckIn = (attendance: StudentAttendanceNotification) => {
  console.log('[AttendanceNotifications] handleCheckIn called with:', attendance)
  selectedAttendance.value = attendance
  checkInModalVisible.value = true
  console.log('[AttendanceNotifications] Modal visible set to:', checkInModalVisible.value)
}

// 处理查看详情
const handleViewDetail = (attendance: StudentAttendanceNotification) => {
  router.push({
    name: 'StudentAttendanceDetail',
    params: { id: attendance.id }
  })
}

// 处理签到成功
const handleCheckInSuccess = () => {
  message.success('签到成功！')
  checkInModalVisible.value = false
  // 刷新列表
  fetchAttendances()
}

// 跳转到人脸照片上传页面
const handleGoToFaceUpload = () => {
  router.push({ name: 'StudentFaceUpload' })
}

// WebSocket store
const wsStore = useWebSocketStore()

// WebSocket事件处理
const handleNewAttendance = (data: any) => {
  console.log('[Student Page] 收到新的签到通知:', data)
  const title = data?.attendance?.title || data?.title || '新考勤'
  message.info(`新的签到通知：${title}`)
  // 刷新列表
  console.log('[Student Page] 开始刷新考勤列表...')
  fetchAttendances()
}

const handleAttendanceUpdated = (data: any) => {
  console.log('签到已更新:', data)
  // 更新列表中的对应项
  const index = attendances.value.findIndex(a => a.id === data.attendance.id)
  if (index !== -1) {
    attendances.value[index] = { ...attendances.value[index], ...data.attendance }
  }
}

const handleCheckInSuccessWS = (data: any) => {
  console.log('签到成功:', data)
  message.success('签到成功！')
  // 刷新列表
  fetchAttendances()
}

// 页面加载时获取数据并连接WebSocket
onMounted(() => {
  console.log('[Student Page] 页面加载，初始化WebSocket连接...')
  fetchAttendances()
  
  // 连接WebSocket
  wsStore.connect()
  console.log('[Student Page] WebSocket连接状态:', wsStore.isConnected)
  
  // 注册事件监听
  console.log('[Student Page] 注册WebSocket事件监听器...')
  wsStore.on('attendance_created', handleNewAttendance)
  wsStore.on('attendance_updated', handleAttendanceUpdated)
  wsStore.on('check_in_success', handleCheckInSuccessWS)
  console.log('[Student Page] 事件监听器注册完成')
})

// 页面卸载时清理
onUnmounted(() => {
  // 移除事件监听
  wsStore.off('attendance_created', handleNewAttendance)
  wsStore.off('attendance_updated', handleAttendanceUpdated)
  wsStore.off('check_in_success', handleCheckInSuccessWS)
})
</script>

<style scoped lang="scss">
.attendance-notifications-page {
  min-height: 100vh;
  background: var(--background-color, #f5f5f5);
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 24px;

  @media (max-width: 768px) {
    flex-direction: column;
    align-items: flex-start;
  }
}

.header-text {
  flex: 1;
}

.page-title {
  font-size: 28px;
  font-weight: 600;
  color: var(--text-color, #262626);
  margin: 0 0 8px 0;
}

.page-description {
  font-size: 14px;
  color: var(--text-secondary-color, #8c8c8c);
  margin: 0;
}

.face-upload-btn {
  height: 44px;
  padding: 0 24px;
  font-size: 15px;
  font-weight: 500;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.2);
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
  }

  @media (max-width: 768px) {
    width: 100%;
  }
}

.filter-section {
  background: white;
  border-radius: 12px;
  padding: 0 24px;
  margin-bottom: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);

  :deep(.ant-tabs) {
    .ant-tabs-nav {
      margin-bottom: 0;
    }

    .ant-tabs-tab {
      padding: 16px 0;
      margin-right: 32px;
      font-size: 15px;

      &:hover {
        color: var(--primary-color, #1890ff);
      }
    }

    .ant-tabs-tab-active {
      .ant-tabs-tab-btn {
        color: var(--primary-color, #1890ff);
        font-weight: 600;
      }
    }

    .ant-tabs-ink-bar {
      background: var(--primary-color, #1890ff);
    }
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

.empty-container {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.attendance-list {
  .list-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(360px, 1fr));
    gap: 20px;
    margin-bottom: 24px;

    @media (max-width: 768px) {
      grid-template-columns: 1fr;
    }
  }
}

.pagination-container {
  display: flex;
  justify-content: center;
  padding: 24px 0;
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}
</style>
