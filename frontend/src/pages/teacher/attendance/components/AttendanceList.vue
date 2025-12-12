<template>
  <div class="attendance-list">
    <a-table
        :columns="columns"
        :data-source="tasks"
        :pagination="{ pageSize: 10 }"
        row-key="id"
    >
      <template #bodyCell="{ column, record }">
        <template v-if="column.key === 'status'">
          <a-tag :color="getStatusColor(record.status)">
            {{ getStatusText(record.status) }}
          </a-tag>
        </template>
        <template v-else-if="column.key === 'progress'">
          <a-progress
              :percent="Math.round((record.attendedCount / record.totalStudents) * 100)"
              :status="record.status === 'active' ? 'active' : 'normal'"
              size="small"
          />
        </template>
        <template v-else-if="column.key === 'action'">
          <a-button type="link" @click="viewDetail(record)">详情</a-button>
        </template>
      </template>
    </a-table>
  </div>
</template>

<script lang="ts" setup>
import type {AttendanceTask} from '../types';

interface Props {
  tasks: AttendanceTask[];
}

interface Emits {
  (e: 'view-detail', task: AttendanceTask): void;
}

const props = defineProps<Props>();
const emits = defineEmits<Emits>();

const columns = [
  {
    title: '任务名称',
    dataIndex: 'title',
    key: 'title',
  },
  {
    title: '课程名称',
    dataIndex: 'courseName',
    key: 'courseName',
  },
  {
    title: '班级',
    dataIndex: 'className',
    key: 'className',
  },
  {
    title: '创建时间',
    dataIndex: 'createTime',
    key: 'createTime',
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '考勤进度',
    key: 'progress',
    width: 200,
  },
  {
    title: '操作',
    key: 'action',
    width: 100,
  },
];

const getStatusColor = (status: string) => {
  switch (status) {
    case 'active':
      return 'processing';
    case 'ended':
      return 'default';
    case 'pending':
      return 'warning';
    default:
      return 'default';
  }
};

const getStatusText = (status: string) => {
  switch (status) {
    case 'active':
      return '进行中';
    case 'ended':
      return '已结束';
    case 'pending':
      return '未开始';
    default:
      return status;
  }
};

const viewDetail = (task: AttendanceTask) => {
  emits('view-detail', task);
};
</script>

<style lang="less" scoped>
.attendance-list {
  background-color: var(--background-color-container);
  padding: 24px;
  border-radius: 8px;
}
</style>
