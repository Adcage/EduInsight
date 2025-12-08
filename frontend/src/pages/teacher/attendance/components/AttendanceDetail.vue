<template>
  <div class="attendance-detail">
    <div class="header">
      <a-page-header
        :title="task.courseName"
        :sub-title="task.className"
        @back="$emit('back')"
      >
        <template #extra>
          <a-button v-if="task.status === 'active'" type="primary" danger @click="endAttendance">结束考勤</a-button>
          <a-tag :color="task.status === 'active' ? 'green' : 'default'">
            {{ task.status === 'active' ? '进行中' : '已结束' }}
          </a-tag>
        </template>
      </a-page-header>
    </div>

    <div class="content">
      <!-- 统计数据概览 -->
      <div class="stats-overview mb-6">
        <a-row :gutter="16">
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic title="应到人数" :value="task.totalStudents" :value-style="{ color: '#1890ff' }">
                <template #prefix><UserOutlined /></template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic title="实到人数" :value="presentCount" :value-style="{ color: '#52c41a' }">
                <template #prefix><CheckCircleOutlined /></template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic title="迟到人数" :value="lateCount" :value-style="{ color: '#faad14' }">
                <template #prefix><ClockCircleOutlined /></template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic title="缺勤人数" :value="absentCount" :value-style="{ color: '#ff4d4f' }">
                <template #prefix><CloseCircleOutlined /></template>
              </a-statistic>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <a-row :gutter="24">
        <!-- 左侧：根据类型展示 -->
        <a-col :span="8" v-if="shouldShowLeftCol">
          
          <!-- 1. 二维码签到 -->
          <a-card v-if="task.type === 'qrcode'" title="扫码签到" class="info-card">
            <div class="card-content-wrapper center">
              <div class="qr-code-box">
                <!-- 模拟二维码，实际可用 a-qrcode 或 qrcode.vue -->
                <img src="https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=EduInsightAttendance" alt="CheckIn QR" />
              </div>
              <p class="hint">请学生扫描二维码签到</p>
              <p class="code-text">签到码: {{ task.qrCode || '----' }}</p>
            </div>
          </a-card>

          <!-- 2. 手势签到 -->
          <a-card v-else-if="task.type === 'manual'" title="手势签到" class="info-card">
            <div class="card-content-wrapper center">
              <div class="gesture-preview-box relative">
                <svg class="absolute inset-0 w-full h-full pointer-events-none z-10">
                  <line 
                    v-for="(line, idx) in gestureLines" 
                    :key="idx"
                    :x1="line.start.x" 
                    :y1="line.start.y" 
                    :x2="line.end.x" 
                    :y2="line.end.y"
                    stroke="#1890ff" 
                    stroke-width="4" 
                    stroke-linecap="round" 
                  />
                </svg>
                <div 
                  v-for="(point, index) in gesturePoints" 
                  :key="index"
                  class="absolute rounded-full border-2 flex items-center justify-center z-20"
                  :class="isPointInPath(index) ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'"
                  :style="{
                    width: '50px',
                    height: '50px',
                    left: point.x - 25 + 'px',
                    top: point.y - 25 + 'px'
                  }"
                >
                  <div 
                    class="w-3 h-3 rounded-full"
                    :class="isPointInPath(index) ? 'bg-blue-500' : 'bg-gray-300'"
                  ></div>
                </div>
              </div>
              <p class="hint mt-4">请向学生展示手势图案</p>
            </div>
          </a-card>

          <!-- 3. 位置签到 -->
          <a-card v-else-if="task.type === 'location'" title="位置签到" class="info-card">
            <div class="card-content-wrapper">
              <div id="detail-map-container" class="map-box"></div>
              <div class="location-info mt-4">
                <p><strong>中心点:</strong> {{ task.location || '未知位置' }}</p>
                <p><strong>范围半径:</strong> {{ (task as any).radius || 200 }} 米</p>
              </div>
            </div>
          </a-card>

        </a-col>
        
        <!-- 右侧：学生列表 -->
        <a-col :span="shouldShowLeftCol ? 16 : 24">
          <a-card title="签到名单">
            <a-table 
              :columns="columns" 
              :data-source="records" 
              :pagination="{ pageSize: 10 }"
              size="small"
            >
              <template #bodyCell="{ column, record }">
                <template v-if="column.key === 'status'">
                  <a-tag :color="getRecordStatusColor(record.status)">
                    {{ getRecordStatusText(record.status) }}
                  </a-tag>
                </template>
                <template v-else-if="column.key === 'action'">
                  <a-button type="link" size="small" @click="toggleStatus(record)">
                    {{ record.status === 'present' ? '标记缺勤' : '标记已到' }}
                  </a-button>
                </template>
              </template>
            </a-table>
          </a-card>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick, onUnmounted, watch } from 'vue';
import { message } from 'ant-design-vue';
import AMapLoader from '@amap/amap-jsapi-loader';
import {
  UserOutlined,
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue';
import type { AttendanceTask, AttendanceRecord, CheckInStatus } from '../types';
import { MOCK_RECORDS } from '../mock';
import { getAttendanceRecords, updateAttendanceRecord } from '@/api/attendanceController';

// Ensure Security Config
(window as any)._AMapSecurityConfig = {
  securityJsCode: 'aacf0ee3cacbae04e8c60a4169eb6f9c',
};

interface Props {
  task: AttendanceTask;
}

interface Emits {
  (e: 'back'): void;
  (e: 'update:task', task: AttendanceTask): void;
}

const props = defineProps<Props>();
const emits = defineEmits<Emits>();

const records = ref<AttendanceRecord[]>([]);
let map: any = null;

// --- Statistics ---
const presentCount = computed(() => records.value.filter(r => r.status === 'present').length);
const lateCount = computed(() => records.value.filter(r => r.status === 'late').length);
const absentCount = computed(() => records.value.filter(r => r.status === 'absent').length);

const shouldShowLeftCol = computed(() => {
  if (props.task.status !== 'active') return false;
  return ['qrcode', 'manual', 'location'].includes(props.task.type);
});

// --- Gesture Logic ---
// Mock gesture path if not in task
const gesturePath = computed(() => (props.task as any).gesturePath || [0, 1, 2, 5, 8]); 

const gesturePoints = computed(() => {
  const points = [];
  // 3x3 grid in approx 250x250 box
  const positions = [40, 125, 210];
  for (let r of positions) {
    for (let c of positions) {
      points.push({ x: c, y: r });
    }
  }
  return points;
});

const gestureLines = computed(() => {
  const lines = [];
  const path = gesturePath.value;
  for (let i = 0; i < path.length - 1; i++) {
    const startIdx = path[i];
    const endIdx = path[i+1];
    if (gesturePoints.value[startIdx] && gesturePoints.value[endIdx]) {
      lines.push({
        start: gesturePoints.value[startIdx],
        end: gesturePoints.value[endIdx]
      });
    }
  }
  return lines;
});

const isPointInPath = (index: number) => gesturePath.value.includes(index);

// --- Map Logic ---
const initMap = () => {
  if (props.task.type !== 'location') return;

  AMapLoader.load({
    key: '3f16bb96c7d7b71dca77021b552a416c',
    version: '2.0',
    plugins: ['AMap.Circle', 'AMap.Marker'],
  })
  .then((AMap) => {
    // Mock location if missing (Beijing)
    const center = (props.task as any).longitude && (props.task as any).latitude 
      ? [(props.task as any).longitude, (props.task as any).latitude]
      : [116.397428, 39.90923];

    map = new AMap.Map('detail-map-container', {
      zoom: 16,
      center: center,
      resizeEnable: true,
      dragEnable: false, // Read only-ish
      zoomEnable: true
    });

    new AMap.Marker({
      position: center,
      map: map
    });

    new AMap.Circle({
      center: center,
      radius: (props.task as any).radius || 200,
      strokeColor: '#3366FF',
      strokeOpacity: 0.2,
      strokeWeight: 1,
      fillColor: '#3366FF',
      fillOpacity: 0.2,
      map: map
    });
  })
  .catch((e) => {
    console.error(e);
  });
};

onMounted(async () => {
  // 从API获取考勤记录
  console.log('AttendanceDetail mounted, task:', props.task);
  try {
    const taskId = Number(props.task.id);
    console.log('Task ID:', taskId);
    if (!isNaN(taskId)) {
      const res = await getAttendanceRecords(taskId);
      console.log('Records API response:', res);
      if (res && res.records) {
        // 转换后端数据格式为前端格式
        records.value = res.records.map((record: any) => ({
          id: record.id,
          taskId: String(record.attendance_id),
          studentId: String(record.student_id),
          studentName: record.student_name || '未知学生',
          studentNumber: record.student_code || '',
          studentCode: record.student_code || '',
          studentAvatar: record.student_avatar || '',
          status: record.status,
          checkInTime: record.check_in_time || '',
          remark: record.remark || ''
        }));
        console.log('Mapped records:', records.value);
      }
    } else {
      // 如果ID不是数字，使用mock数据（兼容旧数据）
      records.value = MOCK_RECORDS.filter(r => r.taskId === props.task.id || props.task.id !== 't1');
      if (records.value.length === 0) {
        records.value = MOCK_RECORDS;
      }
    }
  } catch (error) {
    console.error('获取考勤记录失败:', error);
    // 失败时使用mock数据
    records.value = MOCK_RECORDS.filter(r => r.taskId === props.task.id || props.task.id !== 't1');
    if (records.value.length === 0) {
      records.value = MOCK_RECORDS;
    }
  }

  if (shouldShowLeftCol.value && props.task.type === 'location') {
    nextTick(() => {
      initMap();
    });
  }
});

onUnmounted(() => {
  if (map) {
    map.destroy();
    map = null;
  }
});

// --- Table Columns & Helpers ---
const columns = [
  { title: '学号', dataIndex: 'studentNumber', key: 'studentNumber' },
  { title: '姓名', dataIndex: 'studentName', key: 'studentName' },
  { title: '签到时间', dataIndex: 'checkInTime', key: 'checkInTime' },
  { title: '状态', dataIndex: 'status', key: 'status' },
  { title: '操作', key: 'action' },
];

const getRecordStatusColor = (status: CheckInStatus) => {
  switch (status) {
    case 'present': return 'success';
    case 'absent': return 'error';
    case 'late': return 'warning';
    case 'leave': return 'processing'; // Changed default 'leave' color
    default: return 'default';
  }
};

const getRecordStatusText = (status: CheckInStatus) => {
  const map: Record<string, string> = {
    present: '已到',
    absent: '缺勤',
    late: '迟到',
    leave: '请假'
  };
  return map[status] || status;
};

const endAttendance = () => {
  message.success('考勤已结束');
  const updatedTask = { ...props.task, status: 'ended' as const };
  emits('update:task', updatedTask);
};

const toggleStatus = async (record: AttendanceRecord) => {
  const newStatus = record.status === 'present' ? 'absent' : 'present';
  
  try {
    const taskId = Number(props.task.id);
    const recordId = Number(record.id);
    
    if (isNaN(taskId) || isNaN(recordId)) {
      message.error('无效的任务或记录ID');
      return;
    }
    
    // 调用API更新状态
    await updateAttendanceRecord(taskId, recordId, {
      status: newStatus,
      remark: record.remark
    });
    
    // 更新本地状态
    record.status = newStatus;
    message.success(`已标记 ${record.studentName} 为 ${getRecordStatusText(newStatus)}`);
  } catch (error) {
    console.error('更新考勤记录失败:', error);
    message.error('更新失败，请稍后重试');
  }
};
</script>

<style scoped lang="less">
.attendance-detail {
  background-color: var(--background-color-container);
  min-height: 100%;
  
  .header {
    margin-bottom: 24px;
    background-color: #fff;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.05);
  }

  .content {
    // .ant-card {
    //   height: 100%;
    // }
  }

  .info-card {
    min-height: 400px;
    
    .card-content-wrapper {
      &.center {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
      }
      min-height: 280px;
    }
    
    .qr-code-box {
      img {
        width: 200px;
        height: 200px;
      }
    }

    .gesture-preview-box {
      width: 250px;
      height: 250px;
      background: #fafafa;
      border-radius: 8px;
      margin-bottom: 16px;
    }

    .map-box {
      width: 100%;
      height: 300px;
      border-radius: 8px;
      overflow: hidden;
    }

    .hint {
      margin-top: 12px;
      color: #666;
    }
    
    .code-text {
      font-size: 20px;
      font-weight: bold;
      color: #1890ff;
      margin-top: 8px;
      letter-spacing: 2px;
    }

    .stats {
      margin-top: 24px;
      border-top: 1px solid #f0f0f0;
      padding-top: 16px;
    }
  }
}
</style>
