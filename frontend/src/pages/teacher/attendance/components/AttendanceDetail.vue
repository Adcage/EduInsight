<template>
  <div class="attendance-detail">
    <div class="header">
      <a-page-header
          :sub-title="task.className"
          :title="task.courseName"
          @back="$emit('back')"
      >
        <template #extra>
          <a-button v-if="task.status === 'active'" danger type="primary" @click="endAttendance">结束考勤</a-button>
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
              <a-statistic :value="task.totalStudents" :value-style="{ color: '#1890ff' }" title="应到人数">
                <template #prefix>
                  <UserOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic :value="presentCount" :value-style="{ color: '#52c41a' }" title="实到人数">
                <template #prefix>
                  <CheckCircleOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic :value="lateCount" :value-style="{ color: '#faad14' }" title="迟到人数">
                <template #prefix>
                  <ClockCircleOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
          <a-col :span="6">
            <a-card :bordered="false" class="stat-card">
              <a-statistic :value="absentCount" :value-style="{ color: '#ff4d4f' }" title="缺勤人数">
                <template #prefix>
                  <CloseCircleOutlined/>
                </template>
              </a-statistic>
            </a-card>
          </a-col>
        </a-row>
      </div>

      <a-row :gutter="24">
        <!-- 左侧：根据类型展示 -->
        <a-col v-if="shouldShowLeftCol" :span="8">

          <!-- 1. 二维码签到 -->
          <a-card v-if="task.type === 'qrcode'" class="info-card" title="扫码签到">
            <template #extra>
              <a-button :loading="qrCodeRefreshing" size="small" type="link" @click="refreshQRCode">
                <ReloadOutlined/>
                刷新
              </a-button>
            </template>
            <div class="card-content-wrapper center">
              <div class="qr-code-box">
                <canvas ref="qrcodeCanvas" class="mx-auto"></canvas>
              </div>
              <p class="hint">请学生扫描二维码签到</p>
              <div class="qr-info mt-4 space-y-2">
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">状态:</span>
                  <span class="font-medium text-green-600">{{ qrCodeStatus }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">有效期:</span>
                  <span class="font-medium">{{ qrCodeValidTime }}</span>
                </div>
                <div class="flex justify-between items-center text-sm">
                  <span class="text-gray-600">刷新倒计时:</span>
                  <span class="font-medium text-blue-600">{{ qrCodeCountdown }}秒</span>
                </div>
              </div>
            </div>
          </a-card>

          <!-- 2. 手势签到 -->
          <a-card v-else-if="task.type === 'gesture'" class="info-card" title="手势签到">
            <div class="card-content-wrapper center">
              <div class="gesture-preview-box relative">
                <svg class="absolute inset-0 w-full h-full pointer-events-none z-10">
                  <line
                      v-for="(line, idx) in gestureLines"
                      :key="idx"
                      :x1="line.start.x"
                      :x2="line.end.x"
                      :y1="line.start.y"
                      :y2="line.end.y"
                      stroke="#1890ff"
                      stroke-linecap="round"
                      stroke-width="4"
                  />
                </svg>
                <div
                    v-for="(point, index) in gesturePoints"
                    :key="index"
                    :class="isPointInPath(index) ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'"
                    :style="{
                    width: '50px',
                    height: '50px',
                    left: point.x - 25 + 'px',
                    top: point.y - 25 + 'px'
                  }"
                    class="absolute rounded-full border-2 flex items-center justify-center z-20"
                >
                  <div
                      :class="isPointInPath(index) ? 'bg-blue-500' : 'bg-gray-300'"
                      class="w-3 h-3 rounded-full"
                  ></div>
                </div>
              </div>
              <p class="hint mt-4">请向学生展示手势图案</p>
            </div>
          </a-card>

          <!-- 3. 位置签到 -->
          <a-card v-else-if="task.type === 'location'" class="info-card" title="位置签到">
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
                  <a-button size="small" type="link" @click="toggleStatus(record)">
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

<script lang="ts" setup>
import {computed, nextTick, onMounted, onUnmounted, ref} from 'vue';
import {message} from 'ant-design-vue';
import AMapLoader from '@amap/amap-jsapi-loader';
import QRCode from 'qrcode';
import {
  CheckCircleOutlined,
  ClockCircleOutlined,
  CloseCircleOutlined,
  ReloadOutlined,
  UserOutlined
} from '@ant-design/icons-vue';
import type {AttendanceRecord, AttendanceTask, CheckInStatus} from '../types';
import {getAttendanceRecords, updateAttendanceRecord} from '@/api/attendanceController';

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

// QR Code related
const qrcodeCanvas = ref<HTMLCanvasElement | null>(null);
const qrCodeData = ref('');
const qrCodeStatus = ref('已生成');
const qrCodeValidTime = ref('5分钟');
const qrCodeCountdown = ref(300);
const qrCodeRefreshing = ref(false);
let qrCodeTimer: number | null = null;

// --- Statistics ---
const presentCount = computed(() => records.value.filter(r => r.status === 'present').length);
const lateCount = computed(() => records.value.filter(r => r.status === 'late').length);
const absentCount = computed(() => records.value.filter(r => r.status === 'absent').length);

const shouldShowLeftCol = computed(() => {
  if (props.task.status !== 'active') return false;
  return ['qrcode', 'gesture', 'location'].includes(props.task.type);
});

// --- Gesture Logic ---
// 从 task 中获取手势数据
const gesturePath = computed(() => {
  const task = props.task as any;

  console.log('Task type:', task.type);
  console.log('Task gesture_pattern:', task.gesture_pattern);
  console.log('Task gesturePattern:', task.gesturePattern);

  // 如果有 gesturePath 字段，直接使用
  if (task.gesturePath && Array.isArray(task.gesturePath)) {
    console.log('Using gesturePath:', task.gesturePath);
    return task.gesturePath;
  }

  // 如果有 gesture_pattern 字段，解析它
  if (task.gesture_pattern || task.gesturePattern) {
    const pattern = task.gesture_pattern || task.gesturePattern;
    console.log('Pattern:', pattern);

    // 如果是字符串，尝试解析为 JSON
    let gestureData = pattern;
    if (typeof pattern === 'string') {
      try {
        gestureData = JSON.parse(pattern);
      } catch (e) {
        console.error('Failed to parse gesture pattern:', e);
        return [0, 1, 2, 5, 8]; // 默认值
      }
    }

    // 如果有 points 数组，将坐标转换为索引
    if (gestureData && gestureData.points && Array.isArray(gestureData.points)) {
      return convertPointsToIndices(gestureData.points);
    }

    // 如果直接是索引数组
    if (Array.isArray(gestureData)) {
      return gestureData;
    }
  }

  // 默认值
  return [0, 1, 2, 5, 8];
});

// 将坐标点转换为 3x3 网格索引
const convertPointsToIndices = (points: Array<{ x: number, y: number }>): number[] => {
  const indices: number[] = [];
  const gridSize = 3;
  const cellWidth = 100; // 假设画布宽度 300，每个格子 100
  const cellHeight = 100;

  points.forEach(point => {
    // 计算点所在的网格位置
    const col = Math.floor(point.x / cellWidth);
    const row = Math.floor(point.y / cellHeight);

    // 转换为索引 (0-8)
    const index = row * gridSize + col;

    // 确保索引在有效范围内
    if (index >= 0 && index < 9 && !indices.includes(index)) {
      indices.push(index);
    }
  });

  return indices;
};

const gesturePoints = computed(() => {
  const points = [];
  // 3x3 grid in approx 250x250 box
  const positions = [40, 125, 210];
  for (let r of positions) {
    for (let c of positions) {
      points.push({x: c, y: r});
    }
  }
  return points;
});

const gestureLines = computed(() => {
  const lines = [];
  const path = gesturePath.value;
  for (let i = 0; i < path.length - 1; i++) {
    const startIdx = path[i];
    const endIdx = path[i + 1];
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

// --- QR Code Logic ---
const generateQRCode = async () => {
  try {
    const timestamp = Date.now();
    const randomStr = Math.random().toString(36).substring(2, 15);

    // 调用后端API，将前端生成的token存储到数据库
    const {generateQRCodeToken} = await import('@/api/attendanceController');
    await generateQRCodeToken({
      attendanceId: Number(props.task.id),
      token: randomStr
    });

    console.log('已将token同步到后端:', randomStr);

    const qrData = {
      type: 'attendance_qrcode',
      timestamp,
      token: randomStr,
      attendanceId: props.task.id
    };

    qrCodeData.value = JSON.stringify(qrData);

    await nextTick();

    if (qrcodeCanvas.value) {
      await QRCode.toCanvas(qrcodeCanvas.value, qrCodeData.value, {
        width: 200,
        margin: 2,
        color: {
          dark: '#000000',
          light: '#FFFFFF'
        }
      });

      qrCodeStatus.value = '已生成';
      startQRCodeCountdown();
    }
  } catch (error) {
    console.error('Failed to generate QR code:', error);
    message.error('二维码生成失败');
  }
};

const startQRCodeCountdown = () => {
  if (qrCodeTimer) {
    clearInterval(qrCodeTimer);
  }

  qrCodeCountdown.value = 300;

  qrCodeTimer = window.setInterval(() => {
    qrCodeCountdown.value--;

    if (qrCodeCountdown.value <= 0) {
      refreshQRCode();
    }
  }, 1000);
};

const refreshQRCode = async () => {
  qrCodeRefreshing.value = true;
  try {
    await generateQRCode();
    message.success('二维码已刷新');
  } finally {
    qrCodeRefreshing.value = false;
  }
};

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
      const response = await getAttendanceRecords(taskId);
      const res = (response as any).data ? (response as any).data : response;
      console.log('Records API response:', res);
      if (res && res.records) {
        // 转换后端数据格式为前端格式
        records.value = res.records.map((record: any) => ({
          id: record.id,
          taskId: String(record.attendance_id),
          studentId: String(record.student_id),
          studentName: record.student_name || '未知学生',
          studentNumber: record.student_code || 'N/A',
          studentCode: record.student_code || 'N/A',
          avatar: record.student_avatar || '',
          status: record.status as CheckInStatus,
          checkInTime: record.check_in_time || '',
          remark: record.remark || ''
        }));
        console.log('Mapped records:', records.value);
      } else {
        // 没有记录
        records.value = [];
        console.log('No records found');
      }
    } else {
      // ID不是数字，清空记录
      records.value = [];
      console.warn('Invalid task ID:', props.task.id);
    }
  } catch (error) {
    console.error('获取考勤记录失败:', error);
    // 失败时清空记录，不使用mock数据
    records.value = [];
    message.error('获取考勤记录失败，请刷新重试');
  }

  if (shouldShowLeftCol.value && props.task.type === 'location') {
    nextTick(() => {
      initMap();
    });
  }

  // 如果是二维码签到，生成二维码
  if (shouldShowLeftCol.value && props.task.type === 'qrcode') {
    nextTick(() => {
      generateQRCode();
    });
  }
});

onUnmounted(() => {
  if (map) {
    map.destroy();
    map = null;
  }

  if (qrCodeTimer) {
    clearInterval(qrCodeTimer);
    qrCodeTimer = null;
  }
});

// --- Table Columns & Helpers ---
const columns = [
  {title: '学号', dataIndex: 'studentNumber', key: 'studentNumber'},
  {title: '姓名', dataIndex: 'studentName', key: 'studentName'},
  {title: '签到时间', dataIndex: 'checkInTime', key: 'checkInTime'},
  {title: '状态', dataIndex: 'status', key: 'status'},
  {title: '操作', key: 'action'},
];

const getRecordStatusColor = (status: CheckInStatus) => {
  switch (status) {
    case 'present':
      return 'success';
    case 'absent':
      return 'error';
    case 'late':
      return 'warning';
    case 'leave':
      return 'processing'; // Changed default 'leave' color
    default:
      return 'default';
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
  const updatedTask = {...props.task, status: 'ended' as const};
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

<style lang="less" scoped>
.attendance-detail {
  background-color: var(--background-color-container);
  min-height: 100%;

  .header {
    margin-bottom: 24px;
    background-color: #fff;
    padding: 16px;
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
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
      canvas {
        width: 200px;
        height: 200px;
      }
    }

    .qr-info {
      width: 100%;
      max-width: 300px;
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
