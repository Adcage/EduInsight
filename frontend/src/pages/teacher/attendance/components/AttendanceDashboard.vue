<template>
  <div class="attendance-dashboard">
    <!-- Loading State -->
    <div v-if="loading" class="loading-container">
      <a-spin size="large" tip="加载统计数据中..." />
    </div>

    <!-- Dashboard Content -->
    <div v-else-if="statistics" class="dashboard-content">
      <!-- 核心指标卡片 -->
      <div class="stats-grid">
        <div class="stat-card stat-card-blue">
          <div class="stat-icon">
            <CheckCircleOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-label">累计签到人次</div>
            <div class="stat-value">{{ statistics.totalCheckIns || statistics.total_check_ins || 0 }}</div>
            <div class="stat-detail">
              出勤 {{ statistics.presentCount || statistics.present_count || 0 }} · 
              迟到 {{ statistics.lateCount || statistics.late_count || 0 }}
            </div>
          </div>
        </div>

        <div class="stat-card stat-card-green">
          <div class="stat-icon">
            <TrophyOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-label">全勤学生数</div>
            <div class="stat-value">{{ statistics.perfectAttendanceCount || statistics.perfect_attendance_count || 0 }}</div>
            <div class="stat-detail">
              共 {{ statistics.totalStudents || statistics.total_students || 0 }} 名学生
            </div>
          </div>
        </div>

        <div class="stat-card stat-card-red">
          <div class="stat-icon">
            <WarningOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-label">预警学生数</div>
            <div class="stat-value">{{ statistics.warningCount || statistics.warning_count || 0 }}</div>
            <div class="stat-detail">缺勤 ≥ 3 次</div>
          </div>
        </div>

        <div class="stat-card stat-card-purple">
          <div class="stat-icon">
            <PercentageOutlined />
          </div>
          <div class="stat-content">
            <div class="stat-label">平均出勤率</div>
            <div class="stat-value">{{ (statistics.attendanceRate || statistics.attendance_rate || 0).toFixed(1) }}%</div>
            <div class="stat-detail">
              共 {{ statistics.totalTasks || statistics.total_tasks || 0 }} 次考勤
            </div>
          </div>
        </div>
      </div>

      <!-- 图表区域 -->
      <div class="charts-grid">
        <!-- 最近7天考勤趋势 -->
        <div class="chart-card chart-card-large">
          <div class="chart-header">
            <h3 class="chart-title">
              <LineChartOutlined class="title-icon" />
              最近7天考勤趋势
            </h3>
            <a-tooltip title="显示最近7天的考勤情况">
              <QuestionCircleOutlined class="help-icon" />
            </a-tooltip>
          </div>
          <div class="chart-body">
            <div v-if="dateStats.length > 0" class="line-chart">
              <div class="chart-legend">
                <span class="legend-item legend-present">
                  <CheckCircleOutlined /> 出勤
                </span>
                <span class="legend-item legend-late">
                  <ClockCircleOutlined /> 迟到
                </span>
                <span class="legend-item legend-absent">
                  <CloseCircleOutlined /> 缺勤
                </span>
              </div>
              <div class="chart-container">
                <div class="chart-y-axis">
                  <span v-for="i in 5" :key="i" class="y-label">{{ Math.round(maxValue - (i - 1) * (maxValue / 4)) }}</span>
                </div>
                <div class="chart-bars">
                  <div v-for="(item, index) in dateStats" :key="index" class="bar-group">
                    <div class="bar-stack">
                      <a-tooltip :title="`出勤: ${item.present}人`">
                        <div 
                          class="bar bar-present" 
                          :style="{ height: getBarHeight(item.present) }"
                        ></div>
                      </a-tooltip>
                      <a-tooltip :title="`迟到: ${item.late}人`">
                        <div 
                          class="bar bar-late" 
                          :style="{ height: getBarHeight(item.late) }"
                        ></div>
                      </a-tooltip>
                      <a-tooltip :title="`缺勤: ${item.absent}人`">
                        <div 
                          class="bar bar-absent" 
                          :style="{ height: getBarHeight(item.absent) }"
                        ></div>
                      </a-tooltip>
                    </div>
                    <div class="bar-label">{{ item.dateDisplay || item.date_display }}</div>
                    <div class="bar-total">{{ item.present + item.late + item.absent }}</div>
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

        <!-- 考勤方式统计 -->
        <div class="chart-card">
          <div class="chart-header">
            <h3 class="chart-title">
              <PieChartOutlined class="title-icon" />
              考勤方式统计
            </h3>
            <a-tooltip title="显示各种考勤方式的使用次数">
              <QuestionCircleOutlined class="help-icon" />
            </a-tooltip>
          </div>
          <div class="chart-body">
            <div v-if="typeStatsArray.length > 0" class="type-stats">
              <div v-for="(item, index) in typeStatsArray" :key="index" class="type-item">
                <div class="type-info">
                  <span class="type-icon" :style="{ backgroundColor: getTypeColor(item.name) }">
                    <component :is="getTypeIcon(item.name)" />
                  </span>
                  <span class="type-name">{{ getTypeName(item.name) }}</span>
                  <a-tag :color="getTypeTagColor(item.name)" size="small">
                    {{ getTypePercentage(item.count).toFixed(1) }}%
                  </a-tag>
                </div>
                <div class="type-progress">
                  <div class="progress-bar">
                    <a-tooltip :title="`${item.count}次 (${getTypePercentage(item.count).toFixed(1)}%)`">
                      <div 
                        class="progress-fill" 
                        :style="{ 
                          width: getTypePercentage(item.count) + '%',
                          backgroundColor: getTypeColor(item.name)
                        }"
                      ></div>
                    </a-tooltip>
                  </div>
                  <span class="type-count">{{ item.count }} 次</span>
                </div>
              </div>
            </div>
            <div v-else class="empty-chart">
              <PieChartOutlined class="empty-icon" />
              <p>暂无数据</p>
            </div>
          </div>
        </div>
      </div>

      <!-- 出勤率趋势 -->
      <div class="attendance-rate-card">
        <div class="chart-header">
          <h3 class="chart-title">
            <RiseOutlined class="title-icon" />
            出勤率趋势分析
          </h3>
          <a-tooltip title="显示每次考勤任务的出勤率变化">
            <QuestionCircleOutlined class="help-icon" />
          </a-tooltip>
        </div>
        <div class="chart-body">
          <div v-if="dateStats.length > 0" class="rate-chart">
            <div class="rate-line">
              <svg class="rate-svg" viewBox="0 0 100 50" preserveAspectRatio="none">
                <defs>
                  <linearGradient id="rateGradient" x1="0%" y1="0%" x2="0%" y2="100%">
                    <stop offset="0%" style="stop-color:#1890ff;stop-opacity:0.3" />
                    <stop offset="100%" style="stop-color:#1890ff;stop-opacity:0.05" />
                  </linearGradient>
                </defs>
                <path :d="ratePath" fill="url(#rateGradient)" />
                <polyline :points="ratePoints" fill="none" stroke="#1890ff" stroke-width="0.5" />
              </svg>
            </div>
            <div class="rate-labels">
              <span v-for="(item, index) in dateStats" :key="index" class="rate-label">
                {{ item.dateDisplay || item.date_display }}
              </span>
            </div>
          </div>
          <div v-else class="empty-chart">
            <LineChartOutlined class="empty-icon" />
            <p>暂无数据</p>
          </div>
        </div>
      </div>

      <!-- 学生列表 -->
      <div class="students-grid">
        <!-- 全勤学生 -->
        <div class="student-card">
          <div class="student-header">
            <h3 class="student-title">
              <TrophyOutlined class="title-icon" style="color: #52c41a;" />
              全勤学生
            </h3>
            <a-tag color="success">{{ statistics.perfectAttendanceCount || statistics.perfect_attendance_count || 0 }} 人</a-tag>
          </div>
          <div class="student-list">
            <div 
              v-for="student in perfectStudents" 
              :key="student.id" 
              class="student-item student-item-success"
            >
              <div class="student-info">
                <span class="student-name">{{ student.name }}</span>
                <span class="student-code">{{ student.userCode || student.user_code }}</span>
              </div>
              <CheckCircleOutlined class="student-status-icon" />
            </div>
            <div v-if="perfectStudents.length === 0" class="empty-list">
              <SmileOutlined class="empty-icon" />
              <p>暂无全勤学生</p>
            </div>
          </div>
        </div>

        <!-- 预警学生 -->
        <div class="student-card">
          <div class="student-header">
            <h3 class="student-title">
              <WarningOutlined class="title-icon" style="color: #ff4d4f;" />
              预警学生
            </h3>
            <a-tag color="error">{{ statistics.warningCount || statistics.warning_count || 0 }} 人</a-tag>
          </div>
          <div class="student-list">
            <div 
              v-for="student in warningStudents" 
              :key="student.id" 
              class="student-item student-item-warning"
            >
              <div class="student-info">
                <span class="student-name">{{ student.name }}</span>
                <span class="student-code">{{ student.userCode || student.user_code }}</span>
              </div>
              <a-tag color="error">缺勤 {{ student.absentCount || student.absent_count }} 次</a-tag>
            </div>
            <div v-if="warningStudents.length === 0" class="empty-list">
              <SmileOutlined class="empty-icon" />
              <p>暂无预警学生</p>
            </div>
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
import { ref, computed, watch } from 'vue';
import { 
  CheckCircleOutlined, 
  TrophyOutlined, 
  WarningOutlined, 
  PercentageOutlined,
  LineChartOutlined,
  PieChartOutlined,
  BarChartOutlined,
  SmileOutlined,
  QuestionCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  RiseOutlined,
  QrcodeOutlined,
  EnvironmentOutlined,
  UserOutlined,
  EditOutlined
} from '@ant-design/icons-vue';
// import { getCourseAttendanceStatistics } from '@/api/attendanceController';
import { message } from 'ant-design-vue';
import request from '@/request';

interface Props {
  courseId?: number;
}

const props = defineProps<Props>();

// 临时 API 函数
const getCourseAttendanceStatistics = async (courseId: number): Promise<any> => {
  const response = await request.get(`/api/v1/attendances/courses/${courseId}/statistics`);
  return (response as any)?.data || response;
};

// State
const loading = ref(false);
const statistics = ref<any>(null);

// Computed
const dateStats = computed(() => {
  if (!statistics.value) return [];
  return statistics.value.dateStatistics || statistics.value.date_statistics || [];
});

const typeStatsArray = computed(() => {
  if (!statistics.value) return [];
  const typeStats = statistics.value.typeStatistics || statistics.value.type_statistics || {};
  return Object.values(typeStats).filter((item: any) => item.count > 0);
});

const perfectStudents = computed(() => {
  if (!statistics.value) return [];
  return statistics.value.perfectAttendanceStudents || statistics.value.perfect_attendance_students || [];
});

const warningStudents = computed(() => {
  if (!statistics.value) return [];
  return statistics.value.warningStudents || statistics.value.warning_students || [];
});

const maxValue = computed(() => {
  if (dateStats.value.length === 0) return 10;
  const max = Math.max(...dateStats.value.map((item: any) => item.present + item.late + item.absent));
  return Math.ceil(max / 10) * 10 || 10;
});

const totalTypeTasks = computed(() => {
  return typeStatsArray.value.reduce((sum: number, item: any) => sum + item.count, 0);
});

// Methods
const loadStatistics = async () => {
  if (!props.courseId) return;
  
  try {
    loading.value = true;
    const data = await getCourseAttendanceStatistics(props.courseId);
    statistics.value = data;
  } catch (error) {
    console.error('获取统计数据失败:', error);
    message.error('获取统计数据失败');
  } finally {
    loading.value = false;
  }
};

const getBarHeight = (value: number): string => {
  if (maxValue.value === 0) return '0%';
  return `${(value / maxValue.value) * 100}%`;
};

const getTypePercentage = (count: number): number => {
  if (totalTypeTasks.value === 0) return 0;
  return (count / totalTypeTasks.value) * 100;
};

const getTypeName = (type: string): string => {
  const typeNames: Record<string, string> = {
    'qrcode': '二维码签到',
    'gesture': '手势签到',
    'location': '位置签到',
    'face': '人脸签到',
    'manual': '手动签到'
  };
  return typeNames[type] || type;
};

const getTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    'qrcode': '#1890ff',
    'gesture': '#52c41a',
    'location': '#faad14',
    'face': '#722ed1',
    'manual': '#eb2f96'
  };
  return colors[type] || '#1890ff';
};

const getTypeTagColor = (type: string): string => {
  const colors: Record<string, string> = {
    'qrcode': 'blue',
    'gesture': 'green',
    'location': 'orange',
    'face': 'purple',
    'manual': 'magenta'
  };
  return colors[type] || 'blue';
};

const getTypeIcon = (type: string) => {
  const icons: Record<string, any> = {
    'qrcode': QrcodeOutlined,
    'gesture': EditOutlined,
    'location': EnvironmentOutlined,
    'face': UserOutlined,
    'manual': CheckCircleOutlined
  };
  return icons[type] || QrcodeOutlined;
};

// 计算出勤率趋势线路径
const ratePath = computed(() => {
  if (dateStats.value.length === 0) return '';
  
  const points = dateStats.value.map((item: any, index: number) => {
    const total = item.present + item.late + item.absent;
    const rate = total > 0 ? ((item.present + item.late) / total) * 100 : 0;
    const x = (index / (dateStats.value.length - 1)) * 100;
    const y = 50 - (rate / 100) * 50;
    return `${x},${y}`;
  });
  
  return `M 0,50 L ${points.join(' L ')} L 100,50 Z`;
});

const ratePoints = computed(() => {
  if (dateStats.value.length === 0) return '';
  
  return dateStats.value.map((item: any, index: number) => {
    const total = item.present + item.late + item.absent;
    const rate = total > 0 ? ((item.present + item.late) / total) * 100 : 0;
    const x = (index / (dateStats.value.length - 1)) * 100;
    const y = 50 - (rate / 100) * 50;
    return `${x},${y}`;
  }).join(' ');
});

// Watch
watch(() => props.courseId, () => {
  loadStatistics();
}, { immediate: true });

// Expose
defineExpose({
  refresh: loadStatistics
});
</script>

<style scoped lang="scss">
.attendance-dashboard {
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

.dashboard-content {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

// 统计卡片网格
.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
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
  transition: all 0.3s ease;
  border: 1px solid transparent;

  &:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.1);
  }

  .stat-icon {
    width: 56px;
    height: 56px;
    border-radius: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    flex-shrink: 0;
  }

  .stat-content {
    flex: 1;
    min-width: 0;
  }

  .stat-label {
    font-size: 14px;
    color: var(--text-secondary, #8c8c8c);
    margin-bottom: 8px;
  }

  .stat-value {
    font-size: 28px;
    font-weight: 600;
    line-height: 1;
    margin-bottom: 6px;
  }

  .stat-detail {
    font-size: 12px;
    color: var(--text-tertiary, #bfbfbf);
  }
}

.stat-card-blue {
  .stat-icon {
    background: #e6f7ff;
    color: #1890ff;
  }
  .stat-value {
    color: #1890ff;
  }
}

.stat-card-green {
  .stat-icon {
    background: #f6ffed;
    color: #52c41a;
  }
  .stat-value {
    color: #52c41a;
  }
}

.stat-card-red {
  .stat-icon {
    background: #fff1f0;
    color: #ff4d4f;
  }
  .stat-value {
    color: #ff4d4f;
  }
}

.stat-card-purple {
  .stat-icon {
    background: #f9f0ff;
    color: #722ed1;
  }
  .stat-value {
    color: #722ed1;
  }
}

// 图表网格
.charts-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
  gap: 24px;
}

.chart-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.chart-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
}

.chart-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;

  .title-icon {
    font-size: 18px;
    color: #1890ff;
  }
}

.chart-body {
  padding: 24px;
  min-height: 300px;
}

// 折线图（柱状图）
.line-chart {
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

.chart-container {
  display: flex;
  gap: 12px;
  flex: 1;
}

.chart-y-axis {
  display: flex;
  flex-direction: column;
  justify-content: space-between;
  padding: 10px 0;
  
  .y-label {
    font-size: 12px;
    color: var(--text-tertiary, #bfbfbf);
    text-align: right;
    min-width: 30px;
  }
}

.chart-bars {
  flex: 1;
  display: flex;
  align-items: flex-end;
  gap: 8px;
  padding: 10px 0;
  border-bottom: 1px solid #f0f0f0;
  border-left: 1px solid #f0f0f0;
}

.bar-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.bar-stack {
  width: 100%;
  height: 200px;
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
  font-size: 12px;
  color: var(--text-secondary, #8c8c8c);
  text-align: center;
}

// 考勤方式统计
.type-stats {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.type-item {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.type-info {
  display: flex;
  align-items: center;
  gap: 8px;
}

.type-icon {
  width: 12px;
  height: 12px;
  border-radius: 2px;
}

.type-name {
  font-size: 14px;
  font-weight: 500;
}

.type-progress {
  display: flex;
  align-items: center;
  gap: 12px;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: #f0f0f0;
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  border-radius: 4px;
  transition: width 0.3s ease;
}

.type-count {
  font-size: 14px;
  font-weight: 600;
  min-width: 50px;
  text-align: right;
}

// 学生列表
.students-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(350px, 1fr));
  gap: 24px;
}

.student-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
}

.student-header {
  padding: 20px 24px;
  border-bottom: 1px solid #f0f0f0;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.student-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0;
  display: flex;
  align-items: center;
  gap: 8px;

  .title-icon {
    font-size: 18px;
  }
}

.student-list {
  padding: 16px;
  max-height: 400px;
  overflow-y: auto;
}

.student-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-radius: 8px;
  margin-bottom: 8px;
  transition: all 0.2s ease;

  &:hover {
    background: #fafafa;
  }

  &:last-child {
    margin-bottom: 0;
  }
}

.student-item-success {
  border-left: 3px solid #52c41a;
}

.student-item-warning {
  border-left: 3px solid #ff4d4f;
}

.student-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.student-name {
  font-size: 14px;
  font-weight: 500;
}

.student-code {
  font-size: 12px;
  color: var(--text-secondary, #8c8c8c);
}

.student-status-icon {
  font-size: 18px;
  color: #52c41a;
}

.empty-list {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
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

.empty-chart {
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

// 图表卡片大号
.chart-card-large {
  grid-column: span 2;
  
  @media (max-width: 1200px) {
    grid-column: span 1;
  }
}

// 帮助图标
.help-icon {
  font-size: 14px;
  color: var(--text-tertiary, #bfbfbf);
  cursor: help;
  
  &:hover {
    color: var(--primary-color, #1890ff);
  }
}

.chart-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

// 柱状图总数显示
.bar-total {
  font-size: 11px;
  color: var(--text-tertiary, #bfbfbf);
  margin-top: 2px;
}

// 考勤方式图标
.type-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 10px;
  padding: 2px;
}

// 出勤率趋势卡片
.attendance-rate-card {
  background: white;
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  overflow: hidden;
  margin-top: 24px;
}

.rate-chart {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.rate-line {
  width: 100%;
  height: 150px;
  position: relative;
}

.rate-svg {
  width: 100%;
  height: 100%;
}

.rate-labels {
  display: flex;
  justify-content: space-between;
  padding: 0 8px;
}

.rate-label {
  font-size: 12px;
  color: var(--text-secondary, #8c8c8c);
  text-align: center;
  flex: 1;
}

// 图例图标
.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  
  :deep(.anticon) {
    font-size: 12px;
  }
}

// 响应式优化
@media (max-width: 768px) {
  .attendance-dashboard {
    padding: 16px;
  }
  
  .stats-grid {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .charts-grid {
    grid-template-columns: 1fr;
  }
  
  .students-grid {
    grid-template-columns: 1fr;
  }
}
</style>
