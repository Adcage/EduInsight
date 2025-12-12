<template>
  <div class="student-statistics">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" tip="加载统计数据中..." />
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="statistics" class="statistics-content">
      <!-- 核心指标卡片 -->
      <div class="stats-overview">
        <div class="stat-card stat-primary">
          <div class="stat-icon">
            <CheckCircleOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-label">总考勤次数</div>
            <div class="stat-value">{{ statistics.totalRecords || statistics.total_records || 0 }}</div>
          </div>
        </div>

        <div class="stat-card stat-success">
          <div class="stat-icon">
            <SmileOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-label">出勤次数</div>
            <div class="stat-value">{{ statistics.presentCount || statistics.present_count || 0 }}</div>
          </div>
        </div>

        <div class="stat-card stat-warning">
          <div class="stat-icon">
            <ClockCircleOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-label">迟到次数</div>
            <div class="stat-value">{{ statistics.lateCount || statistics.late_count || 0 }}</div>
          </div>
        </div>

        <div class="stat-card stat-danger">
          <div class="stat-icon">
            <CloseCircleOutlined />
          </div>
          <div class="stat-info">
            <div class="stat-label">缺勤次数</div>
            <div class="stat-value">{{ statistics.absentCount || statistics.absent_count || 0 }}</div>
          </div>
        </div>
      </div>

      <!-- 出勤率卡片 -->
      <div class="attendance-rate-card">
        <h3 class="card-title">我的出勤率</h3>
        <div class="rate-display">
          <div class="rate-circle">
            <svg viewBox="0 0 100 100" class="circle-svg">
              <circle cx="50" cy="50" r="45" class="circle-bg" />
              <circle 
                cx="50" cy="50" r="45" 
                class="circle-progress"
                :style="{ strokeDashoffset: circleOffset }"
              />
            </svg>
            <div class="rate-text">
              <span class="rate-value">{{ attendanceRate }}%</span>
            </div>
          </div>
          <div class="rate-details">
            <div class="detail-item">
              <span class="detail-label">出勤</span>
              <span class="detail-value success">{{ statistics.presentCount || statistics.present_count || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">迟到</span>
              <span class="detail-value warning">{{ statistics.lateCount || statistics.late_count || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">缺勤</span>
              <span class="detail-value danger">{{ statistics.absentCount || statistics.absent_count || 0 }}</span>
            </div>
            <div class="detail-item">
              <span class="detail-label">请假</span>
              <span class="detail-value">{{ statistics.leaveCount || statistics.leave_count || 0 }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <!-- 最近30天趋势 -->
        <div class="chart-card">
          <h3 class="card-title">
            <LineChartOutlined class="title-icon" />
            最近30天考勤趋势
          </h3>
          <div class="chart-content">
            <div v-if="dateStats.length > 0" class="trend-chart">
              <div class="chart-legend">
                <span class="legend-item legend-present">出勤</span>
                <span class="legend-item legend-late">迟到</span>
                <span class="legend-item legend-absent">缺勤</span>
              </div>
              <div class="chart-wrapper">
                <div class="chart-bars">
                  <div v-for="(item, index) in displayDateStats" :key="index" class="bar-group">
                    <div class="bar-stack">
                      <div 
                        class="bar bar-present" 
                        :style="{ height: getBarHeight(item.present) }"
                        :title="`${item.dateDisplay || item.date_display}: 出勤 ${item.present}`"
                      ></div>
                      <div 
                        class="bar bar-late" 
                        :style="{ height: getBarHeight(item.late) }"
                        :title="`${item.dateDisplay || item.date_display}: 迟到 ${item.late}`"
                      ></div>
                      <div 
                        class="bar bar-absent" 
                        :style="{ height: getBarHeight(item.absent) }"
                        :title="`${item.dateDisplay || item.date_display}: 缺勤 ${item.absent}`"
                      ></div>
                    </div>
                    <div class="bar-label">{{ item.dateDisplay || item.date_display }}</div>
                  </div>
                </div>
              </div>
            </div>
            <div v-else class="empty-chart">
              <BarChartOutlined class="empty-icon" />
              <p>暂无数据</p>
            </div>
          </div>
        </div>

        <!-- 按课程统计 -->
        <div class="chart-card">
          <h3 class="card-title">
            <BookOutlined class="title-icon" />
            各课程出勤情况
          </h3>
          <div class="chart-content">
            <div v-if="courseStats.length > 0" class="course-stats">
              <div v-for="(course, index) in courseStats" :key="index" class="course-item">
                <div class="course-header">
                  <span class="course-name">{{ course.courseName || course.course_name }}</span>
                  <span class="course-rate" :class="getRateClass(course.attendanceRate || course.attendance_rate)">
                    {{ (course.attendanceRate || course.attendance_rate || 0).toFixed(1) }}%
                  </span>
                </div>
                <div class="course-progress">
                  <div class="progress-bar">
                    <div 
                      class="progress-fill" 
                      :style="{ width: (course.attendanceRate || course.attendance_rate || 0) + '%' }"
                      :class="getRateClass(course.attendanceRate || course.attendance_rate)"
                    ></div>
                  </div>
                </div>
                <div class="course-details">
                  <span class="detail-text">出勤 {{ course.present }}</span>
                  <span class="detail-text">迟到 {{ course.late }}</span>
                  <span class="detail-text">缺勤 {{ course.absent }}</span>
                  <span class="detail-text">共 {{ course.total }} 次</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-chart">
              <BookOutlined class="empty-icon" />
              <p>暂无数据</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 最近考勤记录 -->
      <div class="recent-records-card">
        <h3 class="card-title">
          <HistoryOutlined class="title-icon" />
          最近考勤记录
        </h3>
        <div class="records-list">
          <div v-if="recentRecords.length > 0">
            <div v-for="record in recentRecords" :key="record.id" class="record-item">
              <div class="record-icon" :class="getStatusClass(record.status)">
                <CheckCircleOutlined v-if="record.status === 'present'" />
                <ClockCircleOutlined v-else-if="record.status === 'late'" />
                <CloseCircleOutlined v-else-if="record.status === 'absent'" />
                <FileTextOutlined v-else />
              </div>
              <div class="record-content">
                <div class="record-title">{{ record.courseName || record.course_name }} - {{ record.title }}</div>
                <div class="record-time">
                  {{ record.checkInTime || record.check_in_time || record.createdAt || record.created_at }}
                </div>
              </div>
              <div class="record-status">
                <a-tag :color="getStatusColor(record.status)">
                  {{ getStatusText(record.status) }}
                </a-tag>
              </div>
            </div>
          </div>
          <div v-else class="empty-records">
            <InboxOutlined class="empty-icon" />
            <p>暂无考勤记录</p>
          </div>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="empty-state">
      <BarChartOutlined class="empty-icon" />
      <p>暂无统计数据</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import { 
  CheckCircleOutlined, 
  SmileOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  LineChartOutlined,
  BarChartOutlined,
  BookOutlined,
  HistoryOutlined,
  InboxOutlined,
  FileTextOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import request from '@/request';

// 临时 API 函数
const getStudentAttendanceStatistics = async (): Promise<any> => {
  const response = await request.get('/api/v1/attendances/students/statistics');
  return (response as any)?.data || response;
};

// State
const loading = ref(false);
const statistics = ref<any>(null);

// Computed
const attendanceRate = computed(() => {
  if (!statistics.value) return 0;
  return (statistics.value.attendanceRate || statistics.value.attendance_rate || 0).toFixed(1);
});

const circleOffset = computed(() => {
  const rate = parseFloat(attendanceRate.value);
  const circumference = 2 * Math.PI * 45;
  return circumference - (rate / 100) * circumference;
});

const dateStats = computed(() => {
  if (!statistics.value) return [];
  return statistics.value.dateStatistics || statistics.value.date_statistics || [];
});

// 只显示最近15天的数据
const displayDateStats = computed(() => {
  return dateStats.value.slice(-15);
});

const courseStats = computed(() => {
  if (!statistics.value) return [];
  return statistics.value.courseStatistics || statistics.value.course_statistics || [];
});

const recentRecords = computed(() => {
  if (!statistics.value) return [];
  return statistics.value.recentRecords || statistics.value.recent_records || [];
});

const maxDateValue = computed(() => {
  if (displayDateStats.value.length === 0) return 5;
  const max = Math.max(...displayDateStats.value.map((item: any) => item.present + item.late + item.absent));
  return Math.ceil(max / 5) * 5 || 5;
});

// Methods
const loadStatistics = async () => {
  try {
    loading.value = true;
    const data = await getStudentAttendanceStatistics();
    statistics.value = data;
  } catch (error) {
    console.error('获取统计数据失败:', error);
    message.error('获取统计数据失败');
  } finally {
    loading.value = false;
  }
};

const getBarHeight = (value: number): string => {
  if (maxDateValue.value === 0) return '0%';
  return `${(value / maxDateValue.value) * 100}%`;
};

const getRateClass = (rate: number): string => {
  if (rate >= 90) return 'rate-excellent';
  if (rate >= 75) return 'rate-good';
  if (rate >= 60) return 'rate-normal';
  return 'rate-poor';
};

const getStatusClass = (status: string): string => {
  const classes: Record<string, string> = {
    'present': 'status-success',
    'late': 'status-warning',
    'absent': 'status-danger',
    'leave': 'status-info'
  };
  return classes[status] || 'status-default';
};

const getStatusColor = (status: string): string => {
  const colors: Record<string, string> = {
    'present': 'success',
    'late': 'warning',
    'absent': 'error',
    'leave': 'default'
  };
  return colors[status] || 'default';
};

const getStatusText = (status: string): string => {
  const texts: Record<string, string> = {
    'present': '出勤',
    'late': '迟到',
    'absent': '缺勤',
    'leave': '请假'
  };
  return texts[status] || status;
};

// Lifecycle
onMounted(() => {
  loadStatistics();
});

// Expose
defineExpose({
  refresh: loadStatistics
});
</script>

<style scoped lang="scss">
.student-statistics {
  padding: 24px;
  min-height: 600px;
}

.loading-container,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  color: var(--text-secondary, #8c8c8c);
  
  .empty-icon {
    font-size: 64px;
    margin-bottom: 16px;
    opacity: 0.3;
  }
}

.statistics-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 核心指标
.stats-overview {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
}

.stat-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 16px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  transition: transform 0.2s;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  .stat-icon {
    width: 48px;
    height: 48px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 24px;
    flex-shrink: 0;
  }

  .stat-info {
    flex: 1;
  }

  .stat-label {
    font-size: 14px;
    color: var(--text-secondary, #8c8c8c);
    margin-bottom: 4px;
  }

  .stat-value {
    font-size: 24px;
    font-weight: 600;
  }
}

.stat-primary {
  .stat-icon {
    background: #e6f7ff;
    color: #1890ff;
  }
  .stat-value {
    color: #1890ff;
  }
}

.stat-success {
  .stat-icon {
    background: #f6ffed;
    color: #52c41a;
  }
  .stat-value {
    color: #52c41a;
  }
}

.stat-warning {
  .stat-icon {
    background: #fffbe6;
    color: #faad14;
  }
  .stat-value {
    color: #faad14;
  }
}

.stat-danger {
  .stat-icon {
    background: #fff1f0;
    color: #ff4d4f;
  }
  .stat-value {
    color: #ff4d4f;
  }
}

// 出勤率卡片
.attendance-rate-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.rate-display {
  display: flex;
  align-items: center;
  gap: 40px;
  margin-top: 20px;

  @media (max-width: 768px) {
    flex-direction: column;
  }
}

.rate-circle {
  position: relative;
  width: 180px;
  height: 180px;
  flex-shrink: 0;
}

.circle-svg {
  width: 100%;
  height: 100%;
  transform: rotate(-90deg);
}

.circle-bg {
  fill: none;
  stroke: #f0f0f0;
  stroke-width: 8;
}

.circle-progress {
  fill: none;
  stroke: #52c41a;
  stroke-width: 8;
  stroke-linecap: round;
  stroke-dasharray: 283;
  transition: stroke-dashoffset 1s ease;
}

.rate-text {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
}

.rate-value {
  font-size: 36px;
  font-weight: 600;
  color: #52c41a;
}

.rate-details {
  flex: 1;
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-label {
  font-size: 14px;
  color: var(--text-secondary, #8c8c8c);
}

.detail-value {
  font-size: 28px;
  font-weight: 600;
  
  &.success {
    color: #52c41a;
  }
  
  &.warning {
    color: #faad14;
  }
  
  &.danger {
    color: #ff4d4f;
  }
}

// 图表区域
.charts-section {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card,
.recent-records-card {
  background: white;
  border-radius: 12px;
  padding: 24px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.card-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 20px 0;
  display: flex;
  align-items: center;
  gap: 8px;

  .title-icon {
    font-size: 18px;
    color: #1890ff;
  }
}

.chart-content {
  min-height: 300px;
}

// 趋势图
.trend-chart {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.chart-legend {
  display: flex;
  gap: 16px;
  margin-bottom: 20px;
  justify-content: center;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 12px;
  
  &::before {
    content: '';
    width: 12px;
    height: 12px;
    border-radius: 2px;
  }
}

.legend-present::before {
  background: #52c41a;
}

.legend-late::before {
  background: #faad14;
}

.legend-absent::before {
  background: #ff4d4f;
}

.chart-wrapper {
  flex: 1;
  overflow-x: auto;
}

.chart-bars {
  display: flex;
  align-items: flex-end;
  gap: 8px;
  min-height: 200px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  min-width: 100%;
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  min-width: 30px;
}

.bar-stack {
  width: 100%;
  height: 180px;
  display: flex;
  align-items: flex-end;
  justify-content: center;
  gap: 2px;
}

.bar {
  flex: 1;
  min-height: 2px;
  border-radius: 4px 4px 0 0;
  transition: all 0.3s ease;
  cursor: pointer;

  &:hover {
    opacity: 0.8;
    transform: scaleY(1.05);
  }
}

.bar-present {
  background: #52c41a;
}

.bar-late {
  background: #faad14;
}

.bar-absent {
  background: #ff4d4f;
}

.bar-label {
  font-size: 11px;
  color: var(--text-secondary, #8c8c8c);
  text-align: center;
  white-space: nowrap;
}

// 课程统计
.course-stats {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.course-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.course-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.course-name {
  font-size: 14px;
  font-weight: 500;
}

.course-rate {
  font-size: 16px;
  font-weight: 600;
  
  &.rate-excellent {
    color: #52c41a;
  }
  
  &.rate-good {
    color: #1890ff;
  }
  
  &.rate-normal {
    color: #faad14;
  }
  
  &.rate-poor {
    color: #ff4d4f;
  }
}

.course-progress {
  .progress-bar {
    height: 8px;
    background: #f0f0f0;
    border-radius: 4px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    border-radius: 4px;
    transition: width 0.5s ease;
    
    &.rate-excellent {
      background: #52c41a;
    }
    
    &.rate-good {
      background: #1890ff;
    }
    
    &.rate-normal {
      background: #faad14;
    }
    
    &.rate-poor {
      background: #ff4d4f;
    }
  }
}

.course-details {
  display: flex;
  gap: 16px;
  font-size: 12px;
  color: var(--text-secondary, #8c8c8c);
}

// 最近记录
.records-list {
  max-height: 500px;
  overflow-y: auto;
}

.record-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: background 0.2s;

  &:hover {
    background: #fafafa;
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.record-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  flex-shrink: 0;
  
  &.status-success {
    background: #f6ffed;
    color: #52c41a;
  }
  
  &.status-warning {
    background: #fffbe6;
    color: #faad14;
  }
  
  &.status-danger {
    background: #fff1f0;
    color: #ff4d4f;
  }
  
  &.status-info {
    background: #e6f7ff;
    color: #1890ff;
  }
}

.record-content {
  flex: 1;
  min-width: 0;
}

.record-title {
  font-size: 14px;
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.record-time {
  font-size: 12px;
  color: var(--text-secondary, #8c8c8c);
}

.record-status {
  flex-shrink: 0;
}

.empty-chart,
.empty-records {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 250px;
  color: var(--text-secondary, #8c8c8c);

  .empty-icon {
    font-size: 48px;
    margin-bottom: 12px;
    opacity: 0.3;
  }

  p {
    margin: 0;
    font-size: 14px;
  }
}
</style>
