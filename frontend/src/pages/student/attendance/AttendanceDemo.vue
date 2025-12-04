<template>
  <div class="attendance-demo">
    <div class="demo-header" v-if="currentView !== 'create'">
      <h2>课堂考勤演示</h2>
      <div v-if="currentView === 'list'">
        <a-button type="primary" @click="currentView = 'create'">发起考勤</a-button>
      </div>
    </div>

    <div class="demo-content" :class="{ 'no-bg': currentView === 'create' }">
      <AttendanceList 
        v-if="currentView === 'list'" 
        :tasks="tasks" 
        @view-detail="handleViewDetail"
      />
      
      <AttendancePublish 
        v-else-if="currentView === 'create'" 
        @success="handleCreateSuccess"
        @cancel="currentView = 'list'"
      />
      
      <AttendanceDetail 
        v-else-if="currentView === 'detail' && currentTask"
        :task="currentTask"
        @back="currentView = 'list'"
        @update:task="handleTaskUpdate"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import dayjs from 'dayjs';
import AttendanceList from './components/AttendanceList.vue';
import AttendancePublish from './components/AttendancePublish.vue';
import AttendanceDetail from './components/AttendanceDetail.vue';
import { MOCK_TASKS } from './mock';
import type { AttendanceTask, AttendanceType } from './types';

type ViewState = 'list' | 'create' | 'detail';

interface CreateTaskPayload {
  courseId: string;
  courseName: string;
  classes: Array<{ name: string; studentCount: number }>;
  students: Array<any>;
  date: Date;
  startTime: string;
  endTime: string;
  method: string;
}

const currentView = ref<ViewState>('list');
const tasks = ref<AttendanceTask[]>(MOCK_TASKS);
const currentTask = ref<AttendanceTask | null>(null);

const handleViewDetail = (task: AttendanceTask) => {
  currentTask.value = task;
  currentView.value = 'detail';
};

const handleCreateSuccess = (payload: CreateTaskPayload) => {
  const task: AttendanceTask = {
    id: `t${Date.now()}`,
    courseId: payload.courseId,
    courseName: payload.courseName,
    className: payload.classes.map(c => c.name).join(', '),
    teacherId: 't001', // Mock ID
    title: `${payload.courseName}考勤`,
    type: payload.method as AttendanceType,
    requireLocation: payload.method === 'location',
    status: 'active',
    // If specific students selected, use that count, else sum of class counts
    totalStudents: payload.students.length > 0 
      ? payload.students.length 
      : payload.classes.reduce((sum, c) => sum + c.studentCount, 0),
    attendedCount: 0,
    createTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
    startTime: payload.startTime,
    endTime: payload.endTime
  };
  
  tasks.value.unshift(task);
  currentView.value = 'list';
};

const handleTaskUpdate = (updatedTask: AttendanceTask) => {
  const index = tasks.value.findIndex(t => t.id === updatedTask.id);
  if (index !== -1) {
    tasks.value[index] = updatedTask;
  }
  currentTask.value = updatedTask;
};
</script>

<style scoped lang="less">
.attendance-demo {
  padding: 24px;
  background-color: var(--background-color-base, #f5f7fa);
  min-height: 100vh;

  .demo-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    
    h2 {
      margin: 0;
      font-size: 24px;
      font-weight: 600;
      color: var(--text-color, #333);
    }
  }

  .demo-content {
    background: var(--background-color-container, #fff);
    border-radius: 8px;
    box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
    
    &.no-bg {
      background: transparent;
      box-shadow: none;
    }
  }
}
</style>
