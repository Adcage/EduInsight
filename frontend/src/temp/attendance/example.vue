<!-- 代码已包含 CSS：使用 TailwindCSS , 安装 TailwindCSS 后方可看到布局样式效果 -->

<template>
  <div class="bg-gray-50 min-h-screen flex flex-col">
    <!-- Header -->
    <header class="bg-white shadow-sm py-4 px-6 flex items-center justify-between">
      <div class="flex items-center space-x-4">
        <button class="p-2 rounded-full hover:bg-gray-100 transition-colors">
          <ArrowLeftOutlined class="text-lg text-gray-600" />
        </button>
        <h1 class="text-xl font-semibold text-gray-900">发布考勤任务</h1>
      </div>
      <button class="p-2 rounded-full hover:bg-gray-100 transition-colors">
        <QuestionCircleOutlined class="text-lg text-gray-600" />
      </button>
    </header>

    <!-- Main Content -->
    <main class="flex-grow container mx-auto px-4 py-8 max-w-6xl">
      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Left Column - Attendance Range & Time -->
        <div class="lg:col-span-2 space-y-8">
          <!-- Attendance Range Section -->
          <section class="bg-white rounded-xl shadow-sm p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-6">考勤范围</h2>
            
            <div class="step-indicator space-y-8">
              <!-- Step 1: Course Selection -->
              <div class="active pb-6 border-b border-gray-100">
                <div class="flex items-center mb-4">
                  <span class="text-base font-medium text-gray-700">选择课程</span>
                </div>
                <div class="relative">
                  <a-select 
                    v-model:value="selectedCourse" 
                    class="w-full"
                    :options="courseOptions"
                  >
                    <template #suffixIcon>
                      <CaretDownOutlined />
                    </template>
                  </a-select>
                </div>
              </div>
              
              <!-- Step 2: Class Selection -->
              <div class="active pb-6 border-b border-gray-100">
                <div class="flex items-center mb-4">
                  <span class="text-base font-medium text-gray-700">选择班级</span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div 
                    v-for="item in classList" 
                    :key="item.id"
                    class="border border-gray-200 rounded-lg p-4 hover:border-primary transition-colors cursor-pointer"
                    :class="{ 'border-2 border-primary bg-indigo-50': item.selected }"
                    @click="toggleClassSelection(item)"
                  >
                    <div class="flex items-start">
                      <Checkbox 
                        :checked="item.selected"
                        @change="toggleClassSelection(item)"
                      />
                      <div class="ml-3">
                        <h3 class="font-medium text-gray-900">{{ item.name }}</h3>
                        <p class="text-sm text-gray-500 mt-1">共 {{ item.studentCount }} 人</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Step 3: Student Selection -->
              <div class="pb-2">
                <div class="flex items-center mb-4">
                  <span class="text-base font-medium text-gray-700">选择学生 (可选)</span>
                </div>
                
                <div class="mb-4 relative">
                  <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                    <SearchOutlined class="text-gray-400" />
                  </div>
                  <a-input 
                    v-model:value="studentSearch" 
                    placeholder="搜索学生姓名或学号..." 
                    class="pl-10"
                  />
                </div>
                
                <div class="max-h-60 overflow-y-auto border border-gray-200 rounded-lg">
                  <ul class="divide-y divide-gray-200">
                    <li 
                      v-for="student in filteredStudents" 
                      :key="student.id"
                      class="p-3 hover:bg-gray-50 flex items-center"
                    >
                      <Checkbox 
                        :checked="student.selected"
                        @change="toggleStudentSelection(student)"
                      />
                      <div class="flex-1 min-w-0 ml-3">
                        <p class="text-sm font-medium text-gray-900 truncate">{{ student.name }}</p>
                        <p class="text-xs text-gray-500 truncate">{{ student.studentId }}</p>
                      </div>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </section>
          
          <!-- Attendance Time Section -->
          <section class="bg-white rounded-xl shadow-sm p-6">
            <h2 class="text-lg font-medium text-gray-900 mb-6">考勤时间</h2>
            
            <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
              <!-- Date Picker -->
              <div>
                <h3 class="text-base font-medium text-gray-700 mb-4">选择日期</h3>
                <div class="bg-gray-50 rounded-lg p-4">
                  <div class="flex justify-between items-center mb-4">
                    <button class="p-2 rounded-full hover:bg-white" @click="prevMonth">
                      <CaretLeftOutlined class="text-gray-600" />
                    </button>
                    <h4 class="font-medium text-gray-900">{{ currentMonthYear }}</h4>
                    <button class="p-2 rounded-full hover:bg-white" @click="nextMonth">
                      <CaretRightOutlined class="text-gray-600" />
                    </button>
                  </div>
                  
                  <div class="grid grid-cols-7 gap-1 mb-2">
                    <div class="text-center text-xs font-medium text-gray-500 py-2">日</div>
                    <div class="text-center text-xs font-medium text-gray-500 py-2">一</div>
                    <div class="text-center text-xs font-medium text-gray-500 py-2">二</div>
                    <div class="text-center text-xs font-medium text-gray-500 py-2">三</div>
                    <div class="text-center text-xs font-medium text-gray-500 py-2">四</div>
                    <div class="text-center text-xs font-medium text-gray-500 py-2">五</div>
                    <div class="text-center text-xs font-medium text-gray-500 py-2">六</div>
                  </div>
                  
                  <div class="grid grid-cols-7 gap-1">
                    <div 
                      v-for="(day, index) in calendarDays" 
                      :key="index"
                      class="calendar-day text-center py-2 text-sm rounded cursor-pointer"
                      :class="{
                        'disabled text-gray-400': day.disabled,
                        'hover:bg-gray-200': !day.disabled && !day.selected,
                        'selected bg-primary text-white': day.selected
                      }"
                      @click="!day.disabled && selectDate(day.date)"
                    >
                      {{ day.text }}
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- Time Selection -->
              <div>
                <h3 class="text-base font-medium text-gray-700 mb-4">选择时间</h3>
                
                <div class="space-y-6">
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">开始时间</label>
                    <div class="flex space-x-3">
                      <a-select 
                        v-model:value="startTime" 
                        class="flex-1"
                        :options="timeOptions"
                      />
                    </div>
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">结束时间</label>
                    <div class="flex space-x-3">
                      <a-select 
                        v-model:value="endTime" 
                        class="flex-1"
                        :options="timeOptions"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
        
        <!-- Right Column - Attendance Method -->
        <div class="lg:col-span-1">
          <section class="bg-white rounded-xl shadow-sm p-6 sticky top-6">
            <h2 class="text-lg font-medium text-gray-900 mb-6">考勤方式</h2>
            
            <div class="space-y-4">
              <div 
                v-for="method in attendanceMethods" 
                :key="method.id"
                class="attendance-method-card border border-gray-200 rounded-lg p-4 cursor-pointer"
                :class="{ 'border-2 border-primary bg-indigo-50 selected': method.selected }"
                @click="selectAttendanceMethod(method)"
              >
                <div class="flex items-center">
                  <div class="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center mr-4" :class="method.bgColor">
                    <component :is="method.icon" :class="method.iconColor" class="text-lg" />
                  </div>
                  <div>
                    <h3 class="font-medium text-gray-900">{{ method.name }}</h3>
                    <p class="text-sm text-gray-500">{{ method.description }}</p>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="mt-8 pt-6 border-t border-gray-200">
              <h3 class="text-base font-medium text-gray-900 mb-4">考勤详情预览</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-500">课程:</span>
                  <span class="font-medium text-gray-900">{{ selectedCourseLabel }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">班级:</span>
                  <span class="font-medium text-gray-900">{{ selectedClassNames }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">学生:</span>
                  <span class="font-medium text-gray-900">已选择 {{ selectedStudents.length }} 名学生</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">日期:</span>
                  <span class="font-medium text-gray-900">{{ formattedSelectedDate }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">时间:</span>
                  <span class="font-medium text-gray-900">{{ startTime }} - {{ endTime }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">方式:</span>
                  <span class="font-medium text-gray-900">{{ selectedMethodName }}</span>
                </div>
              </div>
            </div>
          </section>
        </div>
      </div>
    </main>
    
    <!-- Footer Actions -->
    <footer class="bg-white border-t border-gray-200 py-4 px-6">
      <div class="container mx-auto max-w-6xl flex justify-end space-x-4">
        <button class="px-6 py-3 border border-gray-300 rounded-button text-gray-700 font-medium hover:bg-gray-50 transition-colors whitespace-nowrap">
          预览考勤
        </button>
        <button class="px-6 py-3 bg-primary rounded-button text-white font-medium hover:bg-indigo-700 transition-colors whitespace-nowrap">
          发布考勤
        </button>
      </div>
    </footer>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed } from 'vue';
import { 
  ArrowLeftOutlined, 
  QuestionCircleOutlined, 
  SearchOutlined, 
  CaretDownOutlined, 
  CaretLeftOutlined, 
  CaretRightOutlined,
  PaperClipOutlined,
  EnvironmentOutlined,
  QrcodeOutlined,
  UserOutlined
} from '@ant-design/icons-vue';
import { Checkbox } from 'ant-design-vue';

// Course selection
const selectedCourse = ref('MAT101');
const courseOptions = [
  { value: 'MAT101', label: '高等数学 (MAT101)' },
  { value: 'PHY102', label: '大学物理 (PHY102)' },
  { value: 'CS101', label: '计算机科学导论 (CS101)' },
  { value: 'ENG103', label: '英语写作 (ENG103)' }
];

// Class selection
const classList = ref([
  { id: 1, name: '计算机科学与技术 2023 级 1 班', studentCount: 45, selected: false },
  { id: 2, name: '软件工程 2023 级 2 班', studentCount: 38, selected: true },
  { id: 3, name: '信息安全 2023 级 3 班', studentCount: 42, selected: false },
  { id: 4, name: '网络工程 2023 级 4 班', studentCount: 39, selected: false }
]);

const toggleClassSelection = (item: any) => {
  item.selected = !item.selected;
};

// Student selection
const studentSearch = ref('');
const studentList = ref([
  { id: 1, name: '林晓峰', studentId: '2023001001', selected: false },
  { id: 2, name: '陈雨桐', studentId: '2023001002', selected: true },
  { id: 3, name: '黄志伟', studentId: '2023001003', selected: false },
  { id: 4, name: '吴雅琳', studentId: '2023001004', selected: true },
  { id: 5, name: '郑浩然', studentId: '2023001005', selected: false },
  { id: 6, name: '周慧敏', studentId: '2023001006', selected: false },
  { id: 7, name: '徐天宇', studentId: '2023001007', selected: true },
  { id: 8, name: '孙佳怡', studentId: '2023001008', selected: false }
]);

const filteredStudents = computed(() => {
  if (!studentSearch.value) return studentList.value;
  const search = studentSearch.value.toLowerCase();
  return studentList.value.filter(
    student => 
      student.name.toLowerCase().includes(search) || 
      student.studentId.includes(search)
  );
});

const toggleStudentSelection = (student: any) => {
  student.selected = !student.selected;
};

const selectedStudents = computed(() => 
  studentList.value.filter(s => s.selected)
);

// Date selection
const currentDate = ref(new Date());
const selectedDate = ref(new Date(2023, 11, 15)); // Default to Dec 15, 2023

const prevMonth = () => {
  currentDate.value.setMonth(currentDate.value.getMonth() - 1);
  currentDate.value = new Date(currentDate.value);
};

const nextMonth = () => {
  currentDate.value.setMonth(currentDate.value.getMonth() + 1);
  currentDate.value = new Date(currentDate.value);
};

const selectDate = (date: Date) => {
  selectedDate.value = date;
};

const currentMonthYear = computed(() => {
  return `${currentDate.value.getFullYear()}年 ${currentDate.value.getMonth() + 1}月`;
});

const calendarDays = computed(() => {
  const year = currentDate.value.getFullYear();
  const month = currentDate.value.getMonth();
  
  // First day of the month
  const firstDay = new Date(year, month, 1);
  // Last day of the month
  const lastDay = new Date(year, month + 1, 0);
  // Days from previous month to show
  const prevMonthDays = firstDay.getDay();
  // Days from next month to show
  const nextMonthDays = 6 - lastDay.getDay();
  
  const days = [];
  
  // Previous month days
  for (let i = prevMonthDays - 1; i >= 0; i--) {
    const date = new Date(year, month, -i);
    days.push({
      date,
      text: date.getDate(),
      disabled: true,
      selected: false
    });
  }
  
  // Current month days
  for (let i = 1; i <= lastDay.getDate(); i++) {
    const date = new Date(year, month, i);
    const isSelected = date.toDateString() === selectedDate.value.toDateString();
    days.push({
      date,
      text: i,
      disabled: false,
      selected: isSelected
    });
  }
  
  // Next month days
  for (let i = 1; i <= nextMonthDays; i++) {
    const date = new Date(year, month + 1, i);
    days.push({
      date,
      text: i,
      disabled: true,
      selected: false
    });
  }
  
  return days;
});

const formattedSelectedDate = computed(() => {
  const date = selectedDate.value;
  return `${date.getFullYear()}年 ${date.getMonth() + 1}月 ${date.getDate()}日`;
});

// Time selection
const startTime = ref('10:00');
const endTime = ref('14:00');

const timeOptions = [
  { value: '08:00', label: '08:00' },
  { value: '09:00', label: '09:00' },
  { value: '10:00', label: '10:00' },
  { value: '11:00', label: '11:00' },
  { value: '12:00', label: '12:00' },
  { value: '13:00', label: '13:00' },
  { value: '14:00', label: '14:00' },
  { value: '15:00', label: '15:00' },
  { value: '16:00', label: '16:00' },
  { value: '17:00', label: '17:00' }
];

// Attendance methods
const attendanceMethods = ref([
  { 
    id: 1, 
    name: '手势签到', 
    description: '学生通过特定手势完成签到',
    icon: PaperClipOutlined,
    bgColor: 'bg-blue-50',
    iconColor: 'text-primary',
    selected: false
  },
  { 
    id: 2, 
    name: '位置签到', 
    description: '限定地理位置范围内签到',
    icon: EnvironmentOutlined,
    bgColor: 'bg-green-50',
    iconColor: 'text-green-500',
    selected: false
  },
  { 
    id: 3, 
    name: '二维码签到', 
    description: '扫描二维码完成签到',
    icon: QrcodeOutlined,
    bgColor: 'bg-purple-50',
    iconColor: 'text-purple-500',
    selected: true
  },
  { 
    id: 4, 
    name: '人脸签到', 
    description: '通过人脸识别完成签到',
    icon: UserOutlined,
    bgColor: 'bg-yellow-50',
    iconColor: 'text-yellow-500',
    selected: false
  }
]);

const selectAttendanceMethod = (method: any) => {
  attendanceMethods.value.forEach(m => m.selected = false);
  method.selected = true;
};

const selectedMethodName = computed(() => {
  const selected = attendanceMethods.value.find(m => m.selected);
  return selected ? selected.name : '';
});

// Computed properties for preview
const selectedCourseLabel = computed(() => {
  const course = courseOptions.find(c => c.value === selectedCourse.value);
  return course ? course.label : '';
});

const selectedClassNames = computed(() => {
  const selected = classList.value.filter(c => c.selected);
  if (selected.length === 0) return '未选择班级';
  if (selected.length === 1) return selected[0].name;
  return `${selected[0].name} 等 ${selected.length} 个班级`;
});
</script>

<style scoped>
body {
  font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
}

.font-logo {
  font-family: 'Pacifico', cursive;
}

input[type=number]::-webkit-inner-spin-button,
input[type=number]::-webkit-outer-spin-button {
  -webkit-appearance: none;
  margin: 0;
}

.step-indicator {
  counter-reset: step;
}

.step-indicator > div::before {
  counter-increment: step;
  content: counter(step);
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background-color: #E5E7EB;
  color: #6B7280;
  font-weight: bold;
  margin-right: 12px;
}

.step-indicator > div.active::before {
  background-color: #4F46E5;
  color: white;
}

.attendance-method-card {
  transition: all 0.2s ease;
}

.attendance-method-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}

.calendar-day {
  transition: all 0.15s ease;
}

.calendar-day:hover:not(.disabled) {
  background-color: #E0E7FF;
  cursor: pointer;
}

.calendar-day.selected {
  background-color: #4F46E5;
  color: white;
}
</style>

