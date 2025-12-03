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
      <a-row :gutter="24">
        <!-- 左侧：二维码/考勤码 -->
        <a-col :span="8" v-if="task.status === 'active'">
          <a-card title="扫码签到" class="qr-card">
            <div class="qr-code-placeholder">
              <!-- 这里应该是真实的二维码组件 -->
              <div class="mock-qr">QR Code</div>
              <p class="hint">请学生扫描二维码签到</p>
            </div>
            <div class="stats">
              <a-statistic title="已签到" :value="task.attendedCount" :suffix="` / ${task.totalStudents}`" />
            </div>
          </a-card>
        </a-col>
        
        <!-- 右侧：学生列表 -->
        <a-col :span="task.status === 'active' ? 16 : 24">
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
import { ref, onMounted } from 'vue';
import { message } from 'ant-design-vue';
import type { AttendanceTask, AttendanceRecord, CheckInStatus } from '../types';
import { MOCK_RECORDS } from '../mock';

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

onMounted(() => {
  // Mock fetching records
  records.value = MOCK_RECORDS.filter(r => r.taskId === props.task.id || props.task.id !== 't1'); // simple mock logic
  // If it's a new task with no mock records, generate empty ones or just use mock
  if (records.value.length === 0) {
    records.value = MOCK_RECORDS; // Fallback for demo
  }
});

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

const toggleStatus = (record: AttendanceRecord) => {
  const newStatus = record.status === 'present' ? 'absent' : 'present';
  record.status = newStatus;
  message.success(`已标记 ${record.studentName} 为 ${getRecordStatusText(newStatus)}`);
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
  }

  .qr-card {
    text-align: center;
    
    .qr-code-placeholder {
      margin: 20px 0;
      
      .mock-qr {
        width: 200px;
        height: 200px;
        background-color: #f0f0f0;
        margin: 0 auto;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 24px;
        color: #999;
        border: 1px dashed #ccc;
      }
      
      .hint {
        margin-top: 12px;
        color: var(--text-color-secondary);
      }
    }
    
    .stats {
      margin-top: 24px;
      border-top: 1px solid var(--border-color-split);
      padding-top: 16px;
    }
  }
}
</style>
