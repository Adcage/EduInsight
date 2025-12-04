<template>
  <div class="min-h-screen bg-gray-50 p-6">
    <!-- Header: Course Selection & Info -->
    <div class="bg-white rounded-xl shadow-sm p-6 mb-6">
      <div class="flex justify-between items-start mb-6">
        <div>
          <h1 class="text-2xl font-bold text-gray-900 mb-2">课程考勤</h1>
          <p class="text-gray-500">管理课程考勤任务、查看考勤记录与统计数据</p>
        </div>
        <div class="flex items-center space-x-4">
           <span class="text-gray-600">当前课程：</span>
           <a-select
            v-model:value="currentCourseId"
            class="w-64"
            placeholder="请选择课程"
            size="large"
            @change="handleCourseChange"
          >
            <a-select-option v-for="course in courses" :key="course.id" :value="course.id">
              {{ course.name }}
            </a-select-option>
          </a-select>
        </div>
      </div>

      <!-- Course Card Info -->
      <div v-if="currentCourse" class="bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-100 rounded-xl p-6 flex items-center shadow-sm">
        <div class="w-16 h-16 bg-white rounded-lg flex items-center justify-center text-blue-600 text-3xl mr-6 shadow-sm">
          <BookOutlined />
        </div>
        <div class="flex-1">
          <h3 class="text-xl font-bold text-gray-900 mb-2">{{ currentCourse.name }}</h3>
          <div class="flex flex-wrap gap-6 text-sm text-gray-600">
            <span class="flex items-center"><UserOutlined class="mr-2 text-blue-500" /> 授课教师: 张老师</span>
            <span class="flex items-center"><TeamOutlined class="mr-2 text-blue-500" /> 关联班级: {{ currentCourseClassCount }} 个</span>
            <span class="flex items-center"><ClockCircleOutlined class="mr-2 text-blue-500" /> 考勤次数: {{ currentCourseTaskCount }} 次</span>
          </div>
        </div>
        <div class="pl-6 border-l border-blue-200">
             <div class="text-center">
                 <div class="text-sm text-gray-500 mb-1">平均出勤率</div>
                 <div class="text-2xl font-bold text-blue-600">92%</div>
             </div>
        </div>
      </div>
    </div>

    <!-- Main Content: Tabs -->
    <div class="bg-white rounded-xl shadow-sm min-h-[600px]">
      <a-tabs v-model:activeKey="activeTab" class="px-6 pt-2" size="large">
        <!-- Tab 1: Publish Attendance -->
        <a-tab-pane key="publish" tab="发布考勤">
          <div class="py-6">
            <AttendancePublish 
              v-if="currentCourse"
              :course-id="currentCourse.id"
              :course-name="currentCourse.name"
              :available-classes="currentCourseClasses"
              @success="handleCreateSuccess"
            />
            <div v-else class="flex flex-col items-center justify-center py-20 text-gray-400">
              <BookOutlined class="text-4xl mb-4" />
              <p>请先在上方选择课程</p>
            </div>
          </div>
        </a-tab-pane>

        <!-- Tab 2: Attendance Records -->
        <a-tab-pane key="records" tab="考勤记录">
          <div class="p-4">
             <div class="mb-4 flex justify-between items-center">
                <h3 class="text-lg font-medium">考勤历史</h3>
                <a-input-search placeholder="搜索考勤任务" style="width: 250px" />
             </div>
            <AttendanceList 
              :tasks="currentCourseTasks" 
              @view-detail="handleViewDetail" 
            />
             <div v-if="currentCourseTasks.length === 0" class="text-center py-10 text-gray-400">
                暂无考勤记录
             </div>
          </div>
        </a-tab-pane>

        <!-- Tab 3: Data Dashboard -->
        <a-tab-pane key="dashboard" tab="数据看板">
          <div class="p-8">
             <!-- Placeholder Stats -->
             <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                 <div class="bg-blue-50 p-6 rounded-xl border border-blue-100">
                     <div class="text-gray-500 mb-2">累计签到人次</div>
                     <div class="text-3xl font-bold text-gray-900">1,280</div>
                 </div>
                 <div class="bg-green-50 p-6 rounded-xl border border-green-100">
                     <div class="text-gray-500 mb-2">全勤学生数</div>
                     <div class="text-3xl font-bold text-gray-900">42</div>
                 </div>
                 <div class="bg-red-50 p-6 rounded-xl border border-red-100">
                     <div class="text-gray-500 mb-2">预警学生数</div>
                     <div class="text-3xl font-bold text-gray-900">3</div>
                 </div>
             </div>
             
            <div class="bg-gray-50 rounded-xl p-10 text-center text-gray-500 border border-dashed border-gray-300">
              <BarChartOutlined class="text-4xl mb-4" />
              <p>详细数据图表开发中...</p>
            </div>
          </div>
        </a-tab-pane>
      </a-tabs>
    </div>

    <!-- Detail Modal -->
     <a-modal 
        v-model:open="showDetailModal" 
        title="考勤详情" 
        width="800px" 
        :footer="null"
        destroyOnClose
     >
       <AttendanceDetail v-if="currentTask" :task="currentTask" @back="showDetailModal = false" />
     </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue';
import dayjs from 'dayjs';
import { 
    BookOutlined, 
    UserOutlined, 
    TeamOutlined, 
    ClockCircleOutlined, 
    BarChartOutlined 
} from '@ant-design/icons-vue';
import AttendanceList from './components/AttendanceList.vue';
import AttendancePublish from './components/AttendancePublish.vue';
import AttendanceDetail from './components/AttendanceDetail.vue';
import { MOCK_TASKS } from './mock';
import type { AttendanceTask } from './types';
import { getTeacherCourses, getCourseClasses } from '@/api/courseController';
import type { Course, ClassInfo } from '@/api/courseController';
import { message } from 'ant-design-vue';

// State
const TEACHER_ID = 2; // 固定为张老师的ID
const courses = ref<Course[]>([]);
const tasks = ref<AttendanceTask[]>(MOCK_TASKS);
const currentCourseId = ref<number | undefined>(undefined);
const currentCourseClasses = ref<ClassInfo[]>([]);
const activeTab = ref('publish');
const showDetailModal = ref(false);
const currentTask = ref<AttendanceTask | null>(null);
const loading = ref(false);

// Computed
const currentCourse = computed(() => 
    courses.value.find(c => c.id === currentCourseId.value)
);

const currentCourseTasks = computed(() => 
    tasks.value.filter(t => t.courseId === String(currentCourseId.value))
);

const currentCourseClassCount = computed(() => {
    return currentCourse.value?.classCount || 0;
});

const currentCourseTaskCount = computed(() => currentCourseTasks.value.length);

// Handlers
const handleCourseChange = async () => {
    if (!currentCourseId.value) return;
    
    try {
        loading.value = true;
        const res = await getCourseClasses(currentCourseId.value);
        if (res && res.classes) {
            currentCourseClasses.value = res.classes;
        }
    } catch (error) {
        console.error('获取课程班级失败:', error);
        message.error('获取课程班级信息失败');
    } finally {
        loading.value = false;
    }
};

const handleCreateSuccess = (payload: any) => {
  const task: AttendanceTask = {
    id: `t${Date.now()}`,
    courseId: payload.courseId,
    courseName: payload.courseName,
    className: payload.classes.map((c:any) => c.name).join(', '),
    teacherId: 't001',
    title: `${payload.courseName}考勤`, 
    type: payload.method,
    requireLocation: payload.method === 'location',
    status: 'active',
    totalStudents: payload.students.length > 0 
      ? payload.students.length 
      : payload.classes.reduce((sum:number, c:any) => sum + c.studentCount, 0),
    attendedCount: 0,
    createTime: dayjs().format('YYYY-MM-DD HH:mm:ss'),
    startTime: payload.startTime,
    endTime: payload.endTime
  };
  
  tasks.value.unshift(task);
  activeTab.value = 'records'; // Switch to records tab
};

const handleViewDetail = (task: AttendanceTask) => {
    currentTask.value = task;
    showDetailModal.value = true;
};

// 加载教师课程列表
const loadTeacherCourses = async () => {
    try {
        loading.value = true;
        const res = await getTeacherCourses(TEACHER_ID, {
            includeStats: true,
            status: true // 只获取进行中的课程
        });
        
        if (res && res.courses) {
            courses.value = res.courses;
            
            // 默认选择第一门课程
            if (courses.value.length > 0 && courses.value[0]) {
                currentCourseId.value = courses.value[0].id;
                await handleCourseChange();
            }
        }
    } catch (error) {
        console.error('获取教师课程失败:', error);
        message.error('获取课程列表失败，请刷新页面重试');
    } finally {
        loading.value = false;
    }
};

// Init
onMounted(() => {
    loadTeacherCourses();
});
</script>

<style scoped>
:deep(.ant-tabs-nav) {
    margin-bottom: 0;
}
</style>
