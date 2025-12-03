<template>
  <div class="min-h-screen bg-gray-50 py-8">
    <div class="container mx-auto px-4 max-w-6xl">
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
                    placeholder="请选择课程"
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
                    class="border border-gray-200 rounded-lg p-4 hover:border-blue-500 transition-colors cursor-pointer"
                    :class="{ 'border-2 border-blue-500 bg-blue-50': item.selected }"
                    @click="toggleClassSelection(item)"
                  >
                    <div class="flex items-start">
                      <a-checkbox 
                        :checked="item.selected"
                        @change="() => toggleClassSelection(item)"
                        @click.stop
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
                  <a-input 
                    v-model:value="studentSearch" 
                    placeholder="搜索学生姓名或学号..." 
                    allow-clear
                  >
                    <template #prefix>
                      <SearchOutlined class="text-gray-400" />
                    </template>
                  </a-input>
                </div>
                
                <div class="max-h-60 overflow-y-auto border border-gray-200 rounded-lg">
                  <ul class="divide-y divide-gray-200">
                    <li 
                      v-for="student in filteredStudents" 
                      :key="student.id"
                      class="p-3 hover:bg-gray-50 flex items-center cursor-pointer"
                      @click="toggleStudentSelection(student)"
                    >
                      <a-checkbox 
                        :checked="student.selected"
                        @click.stop="toggleStudentSelection(student)"
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
                    <button class="p-2 rounded-full hover:bg-white transition-colors" @click="prevMonth">
                      <CaretLeftOutlined class="text-gray-600" />
                    </button>
                    <h4 class="font-medium text-gray-900">{{ currentMonthYear }}</h4>
                    <button class="p-2 rounded-full hover:bg-white transition-colors" @click="nextMonth">
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
                      class="calendar-day text-center py-2 text-sm rounded cursor-pointer transition-colors"
                      :class="{
                        'text-gray-400 cursor-not-allowed': day.disabled,
                        'hover:bg-gray-200': !day.disabled && !day.selected,
                        'bg-blue-500 text-white': day.selected
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
                    <a-time-picker 
                      v-model:value="startTime" 
                      format="HH:mm"
                      class="w-full" 
                    />
                  </div>
                  
                  <div>
                    <label class="block text-sm font-medium text-gray-700 mb-2">结束时间</label>
                    <a-time-picker 
                      v-model:value="endTime" 
                      format="HH:mm"
                      class="w-full" 
                    />
                  </div>
                </div>
              </div>
            </div>
          </section>
        </div>
        
        <!-- Right Column - Attendance Method & Preview -->
        <div class="lg:col-span-1">
          <div class="sticky top-6 space-y-6">
            <section class="bg-white rounded-xl shadow-sm p-6">
              <h2 class="text-lg font-medium text-gray-900 mb-6">考勤方式</h2>
              
              <div class="space-y-4">
                <div 
                  v-for="method in attendanceMethods" 
                  :key="method.id"
                  class="attendance-method-card border border-gray-200 rounded-lg p-4 cursor-pointer transition-all"
                  :class="{ 'border-2 border-blue-500 bg-blue-50': method.selected }"
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
            </section>

            <section class="bg-white rounded-xl shadow-sm p-6">
              <h3 class="text-base font-medium text-gray-900 mb-4">考勤详情预览</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-gray-500">课程:</span>
                  <span class="font-medium text-gray-900 text-right ml-4 truncate">{{ selectedCourseLabel }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">班级:</span>
                  <span class="font-medium text-gray-900 text-right ml-4 truncate">{{ selectedClassNames }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">学生:</span>
                  <span class="font-medium text-gray-900 text-right ml-4">{{ selectedStudentsCount }} 人</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">日期:</span>
                  <span class="font-medium text-gray-900 text-right ml-4">{{ formattedSelectedDate }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">时间:</span>
                  <span class="font-medium text-gray-900 text-right ml-4">{{ formattedTimeRange }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-gray-500">方式:</span>
                  <span class="font-medium text-gray-900 text-right ml-4">{{ selectedMethodName }}</span>
                </div>
              </div>
              
              <div class="mt-6 pt-6 border-t border-gray-200 flex flex-col space-y-3">
                <a-button type="primary" size="large" block @click="handlePublish" :loading="publishing">
                  发布考勤
                </a-button>
                <a-button size="large" block @click="$emit('cancel')">
                  取消
                </a-button>
              </div>
            </section>
          </div>
        </div>
      </div>
    </div>
    <!-- Location Selection Modal -->
    <a-modal
      v-model:open="showLocationModal"
      title="选择签到位置与范围"
      :footer="null"
      :maskClosable="false"
      width="800px"
      :bodyStyle="{ padding: '0' }"
      @afterClose="destroyMap"
    >
      <div class="relative h-[500px]">
        <!-- Search Box -->
        <div class="absolute top-4 left-4 z-10 w-72 bg-white rounded shadow p-2">
          <a-input-search
            v-model:value="locationSearchKeyword"
            placeholder="搜索地点..."
            @search="searchLocation"
            allow-clear
          />
          <div v-if="searchResults.length > 0" class="mt-2 max-h-60 overflow-y-auto bg-white border-t">
            <div
              v-for="(item, index) in searchResults"
              :key="index"
              class="p-2 hover:bg-gray-100 cursor-pointer text-sm"
              @click="selectSearchResult(item)"
            >
              <div class="font-medium">{{ item.name }}</div>
              <div class="text-xs text-gray-500">{{ item.address }}</div>
            </div>
          </div>
        </div>

        <!-- Location Button -->
        <div 
          class="absolute top-4 right-4 z-10 bg-white rounded shadow p-2 cursor-pointer hover:bg-gray-50 flex items-center justify-center w-10 h-10" 
          @click="locateCurrentPosition" 
          title="定位当前位置"
        >
          <AimOutlined class="text-xl text-gray-600" />
        </div>

        <!-- Map Container -->
        <div id="amap-container" class="w-full h-full"></div>

        <!-- Radius Control -->
        <div class="absolute bottom-4 left-4 right-4 z-10 bg-white rounded shadow p-4 flex items-center justify-between">
          <div class="flex-1 mr-8">
            <span class="text-sm font-medium text-gray-700 mr-2">签到范围半径:</span>
            <a-slider
              v-model:value="locationRadius"
              :min="100"
              :max="1000"
              :step="50"
              :marks="{ 100: '100m', 500: '500m', 1000: '1000m' }"
              @change="updateCircleRadius"
            />
          </div>
          <div class="flex space-x-3">
            <a-button @click="showLocationModal = false">取消</a-button>
            <a-button type="primary" @click="confirmLocation" :disabled="!selectedLocation">确认位置</a-button>
          </div>
        </div>
      </div>
    </a-modal>

    <!-- Gesture Password Modal -->
    <a-modal
      v-model:open="showGestureModal"
      title="设置手势密码"
      :footer="null"
      :maskClosable="false"
      width="400px"
    >
      <div class="flex flex-col items-center py-4">
        <p class="text-gray-500 mb-4">请绘制解锁图案（至少连接4个点）</p>
        
        <div 
          class="gesture-box relative bg-white select-none" 
          style="width: 300px; height: 300px;"
          @mouseleave="endGesture"
          @mouseup="endGesture"
        >
          <!-- Lines -->
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
            <line 
              v-if="currentLine"
              :x1="currentLine.start.x" 
              :y1="currentLine.start.y" 
              :x2="currentLine.end.x" 
              :y2="currentLine.end.y"
              stroke="#1890ff" 
              stroke-width="4" 
              stroke-linecap="round" 
              opacity="0.5"
            />
          </svg>

          <!-- Points -->
          <div 
            v-for="(point, index) in gesturePoints" 
            :key="index"
            class="absolute rounded-full border-2 flex items-center justify-center transition-colors z-20"
            :class="isPointSelected(index) ? 'border-blue-500 bg-blue-50' : 'border-gray-300 bg-white'"
            :style="{
              width: '60px',
              height: '60px',
              left: point.x - 30 + 'px',
              top: point.y - 30 + 'px',
              cursor: 'pointer'
            }"
            @mousedown.prevent="startGesture(index)"
            @mouseenter="enterPoint(index)"
          >
            <div 
              class="w-4 h-4 rounded-full transition-colors"
              :class="isPointSelected(index) ? 'bg-blue-500' : 'bg-gray-300'"
            ></div>
          </div>
        </div>

        <div class="mt-6 flex space-x-4">
          <a-button @click="resetGesture">重置</a-button>
          <a-button type="primary" @click="confirmGesture" :disabled="gesturePath.length < 4">确认使用</a-button>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import { ref, computed, reactive, nextTick, watch, onUnmounted } from 'vue';
import AMapLoader from '@amap/amap-jsapi-loader';
import dayjs, { type Dayjs } from 'dayjs';
import { message } from 'ant-design-vue';
import { 
  SearchOutlined, 
  CaretDownOutlined, 
  CaretLeftOutlined, 
  CaretRightOutlined,
  FormOutlined,
  EnvironmentOutlined,
  QrcodeOutlined,
  UserOutlined,
  AimOutlined
} from '@ant-design/icons-vue';

// Mock Data Imports
import { MOCK_COURSES, MOCK_CLASSES } from '../mock';

// Configure AMap Security Key
(window as any)._AMapSecurityConfig = {
  securityJsCode: 'aacf0ee3cacbae04e8c60a4169eb6f9c',
};

const emits = defineEmits(['success', 'cancel']);

// --- 1. 考勤范围 Logic ---

// Course Selection
const selectedCourse = ref<string | undefined>(undefined);
const courseOptions = MOCK_COURSES.map(c => ({ value: c.id, label: c.name }));

// Class Selection
const classList = ref(MOCK_CLASSES.map(c => ({
  ...c,
  studentCount: Math.floor(Math.random() * 10) + 30,
  selected: false
})));

const toggleClassSelection = (item: any) => {
  item.selected = !item.selected;
};

const selectedClasses = computed(() => classList.value.filter(c => c.selected));

// Student Selection
const studentSearch = ref('');
const allStudents = ref(Array.from({ length: 20 }).map((_, i) => ({
  id: `s${i}`,
  name: `学生${i + 1}`,
  studentId: `202300${100 + i}`,
  classId: i % 2 === 0 ? 'cl1' : 'cl2',
  selected: true
})));

const filteredStudents = computed(() => {
  const selectedClassIds = selectedClasses.value.map(c => c.id);
  if (selectedClassIds.length === 0) return [];

  let students = allStudents.value.filter(s => selectedClassIds.includes(s.classId));

  if (studentSearch.value) {
    const search = studentSearch.value.toLowerCase();
    students = students.filter(s => 
      s.name.toLowerCase().includes(search) || 
      s.studentId.includes(search)
    );
  }
  return students;
});

const toggleStudentSelection = (student: any) => {
  student.selected = !student.selected;
};

const selectedStudentsCount = computed(() => 
  filteredStudents.value.filter(s => s.selected).length
);

// --- 2. 考勤时间 Logic ---

const currentDate = ref(new Date());
const selectedDate = ref(new Date());

const prevMonth = () => {
  currentDate.value = dayjs(currentDate.value).subtract(1, 'month').toDate();
};

const nextMonth = () => {
  currentDate.value = dayjs(currentDate.value).add(1, 'month').toDate();
};

const selectDate = (date: Date) => {
  selectedDate.value = date;
};

const currentMonthYear = computed(() => dayjs(currentDate.value).format('YYYY年 M月'));

const calendarDays = computed(() => {
  const current = dayjs(currentDate.value);
  const firstDay = current.startOf('month');
  const lastDay = current.endOf('month');
  const startDayOfWeek = firstDay.day();
  const daysInMonth = current.daysInMonth();
  
  const days = [];

  for (let i = 0; i < startDayOfWeek; i++) {
    const d = firstDay.subtract(startDayOfWeek - i, 'day');
    days.push({ date: d.toDate(), text: d.date(), disabled: true, selected: false });
  }

  for (let i = 1; i <= daysInMonth; i++) {
    const d = dayjs(new Date(current.year(), current.month(), i));
    const isSelected = d.isSame(dayjs(selectedDate.value), 'day');
    days.push({ date: d.toDate(), text: i, disabled: false, selected: isSelected });
  }

  const remainingCells = 42 - days.length;
  for (let i = 1; i <= remainingCells; i++) {
    const d = lastDay.add(i, 'day');
    days.push({ date: d.toDate(), text: d.date(), disabled: true, selected: false });
  }

  return days;
});

const formattedSelectedDate = computed(() => dayjs(selectedDate.value).format('YYYY年M月D日'));

const startTime = ref<Dayjs>(dayjs().hour(10).minute(0));
const endTime = ref<Dayjs>(dayjs().hour(12).minute(0));

const formattedTimeRange = computed(() => {
  if (!startTime.value || !endTime.value) return '--';
  return `${startTime.value.format('HH:mm')} - ${endTime.value.format('HH:mm')}`;
});

// --- 3. 考勤方式 Logic ---

const attendanceMethods = ref([
  { 
    id: 'manual', 
    name: '手势签到', 
    description: '学生通过特定手势完成签到',
    icon: FormOutlined,
    bgColor: 'bg-blue-50',
    iconColor: 'text-blue-500',
    selected: false
  },
  { 
    id: 'location', 
    name: '位置签到', 
    description: '限定地理位置范围内签到',
    icon: EnvironmentOutlined,
    bgColor: 'bg-green-50',
    iconColor: 'text-green-500',
    selected: false
  },
  { 
    id: 'qrcode', 
    name: '二维码签到', 
    description: '扫描二维码完成签到',
    icon: QrcodeOutlined,
    bgColor: 'bg-purple-50',
    iconColor: 'text-purple-500',
    selected: true
  },
  { 
    id: 'face', 
    name: '人脸签到', 
    description: '通过人脸识别完成签到',
    icon: UserOutlined,
    bgColor: 'bg-yellow-50',
    iconColor: 'text-yellow-500',
    selected: false
  }
]);

// --- 4. Gesture Password Logic ---

const showGestureModal = ref(false);
const isDrawing = ref(false);
const gesturePath = ref<number[]>([]);
const currentLine = ref<any>(null);

// Initialize 9 points
const gesturePoints = computed(() => {
  const points = [];
  // 3x3 grid in 300x300 box
  // Padding 30px, spacing approx 90px
  // Col: 50, 150, 250
  // Row: 50, 150, 250
  const positions = [50, 150, 250];
  for (let r of positions) {
    for (let c of positions) {
      points.push({ x: c, y: r });
    }
  }
  return points; // 0-8
});

const gestureLines = computed(() => {
  const lines = [];
  for (let i = 0; i < gesturePath.value.length - 1; i++) {
    const startIdx = gesturePath.value[i];
    const endIdx = gesturePath.value[i+1];
    if (startIdx !== undefined && endIdx !== undefined && gesturePoints.value[startIdx] && gesturePoints.value[endIdx]) {
      lines.push({
        start: gesturePoints.value[startIdx],
        end: gesturePoints.value[endIdx]
      });
    }
  }
  return lines;
});

const isPointSelected = (index: number) => gesturePath.value.includes(index);

const startGesture = (index: number) => {
  isDrawing.value = true;
  gesturePath.value = [index];
};

const enterPoint = (index: number) => {
  if (!isDrawing.value) return;
  
  // Prevent selecting the same point immediately again (simple loop prevention)
  // Or standard pattern logic: can revisit if passing through? 
  // Simple version: cannot select already selected point
  if (!gesturePath.value.includes(index)) {
    gesturePath.value.push(index);
  }
};

const endGesture = () => {
  isDrawing.value = false;
  currentLine.value = null;
};

const resetGesture = () => {
  gesturePath.value = [];
  isDrawing.value = false;
  currentLine.value = null;
};

const confirmGesture = () => {
  if (gesturePath.value.length < 4) {
    message.warning('手势密码至少连接4个点');
    return;
  }
  showGestureModal.value = false;
  message.success('手势密码设置成功');
};

// --- 5. Location Selection Logic ---
const showLocationModal = ref(false);
const locationSearchKeyword = ref('');
const searchResults = ref<any[]>([]);
const locationRadius = ref(200);
const selectedLocation = ref<any>(null);

let map: any = null;
let marker: any = null;
let circle: any = null;
let placeSearch: any = null;
let AMapObj: any = null;
let geolocation: any = null;

const initMap = () => {
  AMapLoader.load({
    key: '3f16bb96c7d7b71dca77021b552a416c',
    version: '2.0',
    plugins: ['AMap.AutoComplete', 'AMap.PlaceSearch', 'AMap.Circle', 'AMap.Marker', 'AMap.Geolocation'],
  })
  .then((AMap) => {
    AMapObj = AMap;
    map = new AMap.Map('amap-container', {
      zoom: 15,
      center: [116.397428, 39.90923], // Default Beijing
      resizeEnable: true
    });

    // Click event
    map.on('click', (e: any) => {
      handleMapClick(e.lnglat);
    });

    // Init PlaceSearch
    placeSearch = new AMap.PlaceSearch({
      pageSize: 10,
      pageIndex: 1,
      city: '全国', // city code or name
    });

    // Init Geolocation
    geolocation = new AMap.Geolocation({
      enableHighAccuracy: true,
      timeout: 10000,
      zoomToAccuracy: true,
      position: 'RB'
    });
  })
  .catch((e) => {
    console.error(e);
    message.error('地图加载失败');
  });
};

const locateCurrentPosition = () => {
  if (!geolocation) {
    message.warning('地图组件未就绪');
    return;
  }
  message.loading('正在获取位置...', 0);
  geolocation.getCurrentPosition((status: string, result: any) => {
    message.destroy();
    if (status === 'complete') {
      handleMapClick(result.position);
      message.success('定位成功');
    } else {
      console.error(result);
      message.error('定位失败，请确保已授予位置权限');
    }
  });
};

const handleMapClick = (lnglat: any) => {
  const { lng, lat } = lnglat;
  updateLocationOnMap(lng, lat);
  
  selectedLocation.value = {
    lng,
    lat,
    address: `${lng.toFixed(6)}, ${lat.toFixed(6)}`,
    name: '已选位置'
  };
};

const updateLocationOnMap = (lng: number, lat: number) => {
  if (!AMapObj) return;
  const center = new AMapObj.LngLat(lng, lat);

  if (marker) {
    marker.setPosition(center);
  } else {
    marker = new AMapObj.Marker({
      position: center,
      map: map
    });
  }

  if (circle) {
    circle.setCenter(center);
    circle.setRadius(locationRadius.value);
  } else {
    circle = new AMapObj.Circle({
      center: center,
      radius: locationRadius.value,
      strokeColor: '#3366FF',
      strokeOpacity: 0.2,
      strokeWeight: 1,
      fillColor: '#3366FF',
      fillOpacity: 0.2,
      map: map
    });
  }
  
  map.setCenter(center);
};

const searchLocation = () => {
  if (!placeSearch || !locationSearchKeyword.value) return;
  placeSearch.search(locationSearchKeyword.value, (status: string, result: any) => {
    if (status === 'complete' && result.info === 'OK') {
      searchResults.value = result.poiList.pois;
    } else {
      searchResults.value = [];
      message.info('未找到相关地点');
    }
  });
};

const selectSearchResult = (item: any) => {
  searchResults.value = [];
  locationSearchKeyword.value = item.name;
  const { lng, lat } = item.location;
  updateLocationOnMap(lng, lat);
  selectedLocation.value = {
    lng,
    lat,
    address: item.address,
    name: item.name
  };
};

const updateCircleRadius = () => {
  if (circle) {
    circle.setRadius(locationRadius.value);
  }
};

const confirmLocation = () => {
  if (selectedLocation.value) {
    showLocationModal.value = false;
    message.success(`已选择位置：${selectedLocation.value.name}`);
  }
};

const destroyMap = () => {
  if (map) {
    map.destroy();
    map = null;
    marker = null;
    circle = null;
    placeSearch = null;
    AMapObj = null;
  }
};

watch(showLocationModal, (val) => {
  if (val) {
    nextTick(() => {
      initMap();
    });
  }
});

const selectAttendanceMethod = (method: any) => {
  if (method.id === 'manual') {
    showGestureModal.value = true;
    resetGesture();
  } else if (method.id === 'location') {
    showLocationModal.value = true;
  }
  
  attendanceMethods.value.forEach(m => m.selected = false);
  method.selected = true;
};

const selectedMethodName = computed(() => {
  const selected = attendanceMethods.value.find(m => m.selected);
  return selected ? selected.name : '';
});

// --- Preview & Publish ---

const selectedCourseLabel = computed(() => {
  const c = courseOptions.find(opt => opt.value === selectedCourse.value);
  return c ? c.label : '未选择';
});

const selectedClassNames = computed(() => {
  if (selectedClasses.value.length === 0) return '未选择';
  if (selectedClasses.value.length === 1) return selectedClasses.value[0].name;
  return `${selectedClasses.value[0].name} 等 ${selectedClasses.value.length} 个班级`;
});

const publishing = ref(false);

const handlePublish = () => {
  if (!selectedCourse.value) {
    message.warning('请选择课程');
    return;
  }
  if (selectedClasses.value.length === 0) {
    message.warning('请选择班级');
    return;
  }

  publishing.value = true;
  
  setTimeout(() => {
    publishing.value = false;
    const payload = {
      courseId: selectedCourse.value,
      courseName: selectedCourseLabel.value,
      classes: selectedClasses.value,
      students: filteredStudents.value.filter(s => s.selected),
      date: selectedDate.value,
      startTime: startTime.value?.format('HH:mm'),
      endTime: endTime.value?.format('HH:mm'),
      method: attendanceMethods.value.find(m => m.selected)?.id
    };
    message.success('考勤发布成功！');
    emits('success', payload);
  }, 1000);
};
</script>

<style scoped>
.attendance-method-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
</style>
