<!-- 代码已包含 CSS：使用 TailwindCSS , 安装 TailwindCSS 后方可看到布局样式效果 -->

<template>
  <div class="min-h-screen bg-gray-50 flex flex-col">
    <!-- Navigation Bar -->
    <div class="fixed top-0 left-0 w-full bg-white shadow-sm z-10 flex items-center justify-between px-4 py-3">
      <a-button type="text" @click="goBack">
        <LeftOutlined />
      </a-button>
      <span class="text-lg font-semibold">学生签到</span>
      <a-button type="text">
        <QuestionCircleOutlined />
      </a-button>
    </div>

    <!-- Main Content -->
    <div class="pt-16 pb-20 px-4 flex-1">
      <!-- Step 1: Student ID Input -->
      <div v-if="currentStep === 1" class="space-y-6">
        <!-- 调试信息卡片 -->
        <div class="bg-blue-50 rounded-xl p-4 shadow-sm border border-blue-200">
          <h3 class="text-sm font-bold mb-2 text-blue-800">调试信息</h3>
          <div class="text-xs text-blue-700 space-y-1">
            <p><strong>考勤ID:</strong> {{ attendanceId || '未获取' }}</p>
            <p><strong>二维码Token长度:</strong> {{ qrCodeToken ? qrCodeToken.length : 0 }}</p>
            <p class="break-all"><strong>二维码Token:</strong> {{ qrCodeToken || '未获取' }}</p>
            <p><strong>后端API:</strong> {{ apiBaseUrl }}</p>
            <p><strong>网络状态:</strong> <span :class="isOnline ? 'text-green-600' : 'text-red-600'">{{ isOnline ? '在线' : '离线' }}</span></p>
          </div>
        </div>
        
        <!-- 错误信息卡片 -->
        <div v-if="lastError" class="bg-red-50 rounded-xl p-4 shadow-sm border border-red-200">
          <h3 class="text-sm font-bold mb-2 text-red-800">错误详情</h3>
          <div class="text-xs text-red-700 space-y-1">
            <p><strong>错误信息:</strong> {{ lastError.message }}</p>
            <p v-if="lastError.status"><strong>状态码:</strong> {{ lastError.status }}</p>
            <p v-if="lastError.url"><strong>请求地址:</strong> {{ lastError.url }}</p>
            <div v-if="lastError.detail" class="mt-2 p-2 bg-red-100 rounded text-xs overflow-auto max-h-32">
              <pre>{{ lastError.detail }}</pre>
            </div>
          </div>
        </div>
        
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="text-xl font-bold mb-2">请输入学号</h2>
          <p class="text-gray-500 mb-6">验证学号后将进行人脸识别验证</p>
          
          <a-input 
            v-model:value="studentId"
            size="large"
            placeholder="请输入您的学号"
            class="mb-6"
          >
            <template #prefix>
              <UserOutlined />
            </template>
          </a-input>
          
          <a-button 
            type="primary" 
            size="large" 
            block 
            @click="handleNextStep"
            :loading="validating"
            :disabled="!studentId.trim()"
          >
            下一步 - 人脸验证
          </a-button>
        </div>
        
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h3 class="font-bold mb-3">签到说明</h3>
          <ul class="space-y-2 text-gray-600">
            <li class="flex items-start">
              <CheckCircleOutlined class="text-green-500 mt-1 mr-2" />
              <span>请输入您的学号进行身份验证</span>
            </li>
            <li class="flex items-start">
              <CheckCircleOutlined class="text-green-500 mt-1 mr-2" />
              <span>点击下一步后将进行人脸识别验证</span>
            </li>
            <li class="flex items-start">
              <CheckCircleOutlined class="text-green-500 mt-1 mr-2" />
              <span>请确保您已上传人脸照片</span>
            </li>
          </ul>
        </div>
      </div>

      <!-- Step 2: Face Recognition (暂时隐藏，第二阶段实现) -->
      <div v-else-if="currentStep === 2 && false" class="space-y-6">
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h2 class="text-xl font-bold mb-2">人脸识别验证</h2>
          <p class="text-gray-500 mb-6">请将面部对准摄像头完成身份验证</p>
          
          <div class="relative bg-gray-100 rounded-lg overflow-hidden mb-6" style="height: 240px;">
            <div v-if="!cameraActive" class="absolute inset-0 flex items-center justify-center">
              <CameraOutlined class="text-4xl text-gray-400" />
            </div>
            <video 
              v-show="cameraActive" 
              ref="videoRef"
              autoplay 
              playsinline
              class="w-full h-full object-cover"
            ></video>
            
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="border-2 border-dashed border-white rounded-full w-48 h-48"></div>
            </div>
          </div>
          
          <div class="flex space-x-3">
            <a-button 
              size="large" 
              block 
              @click="toggleCamera"
            >
              {{ cameraActive ? '关闭摄像头' : '开启摄像头' }}
            </a-button>
            <a-button 
              type="primary" 
              size="large" 
              block 
              @click="captureAndVerify"
              :loading="verifying"
            >
              确认签到
            </a-button>
          </div>
        </div>
        
        <div class="bg-blue-50 border border-blue-100 rounded-xl p-4">
          <InfoCircleOutlined class="text-blue-500 mr-2" />
          <span class="text-blue-700">请确保您处于安静、光线良好的环境中，避免他人干扰识别过程</span>
        </div>
      </div>

      <!-- Step 3: Check-in Success -->
      <div v-else-if="currentStep === 3" class="space-y-6">
        <div class="bg-white rounded-xl p-8 shadow-sm text-center">
          <CheckCircleOutlined class="text-6xl text-green-500 mb-4" />
          <h2 class="text-2xl font-bold mb-2">签到成功！</h2>
          <p class="text-gray-500 mb-6">您已完成今日课程签到</p>
          
          <div class="bg-gray-50 rounded-lg p-4 mb-6 text-left">
            <div class="flex justify-between py-2 border-b">
              <span class="text-gray-500">签到时间</span>
              <span class="font-medium">{{ successTime }}</span>
            </div>
            <div class="flex justify-between py-2 border-b">
              <span class="text-gray-500">签到状态</span>
              <span class="font-medium" :style="{ color: statusColor }">{{ statusText }}</span>
            </div>
            <div class="flex justify-between py-2">
              <span class="text-gray-500">签到方式</span>
              <span class="font-medium">二维码签到</span>
            </div>
          </div>
          
          <a-button 
            type="primary" 
            size="large" 
            block 
            @click="finishProcess"
          >
            完成
          </a-button>
        </div>
        
        <div class="bg-white rounded-xl p-6 shadow-sm">
          <h3 class="font-bold mb-3">签到统计</h3>
          <div class="flex justify-between text-center">
            <div>
              <div class="text-2xl font-bold text-green-500">24</div>
              <div class="text-gray-500">本月签到</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-blue-500">100%</div>
              <div class="text-gray-500">出勤率</div>
            </div>
            <div>
              <div class="text-2xl font-bold text-orange-500">0</div>
              <div class="text-gray-500">缺勤次数</div>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 人脸验证模态框 -->
    <FaceVerificationModal
      v-model:visible="faceVerificationVisible"
      :attendance-id="attendanceId"
      :student-number="studentId"
      @success="handleFaceVerificationSuccess"
    />

    <!-- Tab Bar -->
    <div class="fixed bottom-0 left-0 w-full bg-white border-t flex justify-around py-2">
      <div class="flex flex-col items-center w-1/3">
        <HomeOutlined class="text-xl" />
        <span class="text-xs mt-1">首页</span>
      </div>
      <div class="flex flex-col items-center w-1/3 text-blue-500">
        <CheckSquareOutlined class="text-xl" />
        <span class="text-xs mt-1">签到</span>
      </div>
      <div class="flex flex-col items-center w-1/3">
        <UserOutlined class="text-xl" />
        <span class="text-xs mt-1">我的</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onBeforeUnmount, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { 
  LeftOutlined, 
  QuestionCircleOutlined, 
  UserOutlined, 
  CheckCircleOutlined,
  CameraOutlined,
  InfoCircleOutlined,
  HomeOutlined,
  CheckSquareOutlined
} from '@ant-design/icons-vue';
import { message } from 'ant-design-vue';
import { verifyQRCodeAndCheckIn, type AttendanceRecord } from '@/api/attendanceController';
import FaceVerificationModal from '@/components/FaceVerificationModal.vue';

const route = useRoute();
const router = useRouter();

// 从 URL 获取考勤信息
const attendanceId = ref<number>(Number(route.query.attendanceId) || 0);
const qrCodeToken = ref<string>((route.query.token as string) || '');

// 调试：打印接收到的参数
console.log('=== AttendanceMobile 接收到的参数 ===');
console.log('route.query:', route.query);
console.log('attendanceId:', attendanceId.value);
console.log('qrCodeToken:', qrCodeToken.value);
console.log('qrCodeToken长度:', qrCodeToken.value.length);

// 网络状态检测
const isOnline = ref(navigator.onLine);

// 获取实际的API地址
const getApiBaseUrl = () => {
  const hostname = window.location.hostname;
  if (hostname === 'localhost' || hostname === '127.0.0.1') {
    return 'http://localhost:5030';
  } else {
    return `http://${hostname}:5030`;
  }
};

const apiBaseUrl = ref(getApiBaseUrl());

// 监听网络状态变化
window.addEventListener('online', () => {
  isOnline.value = true;
  message.success('网络已连接');
});

window.addEventListener('offline', () => {
  isOnline.value = false;
  message.error('网络已断开');
});

// State variables
const currentStep = ref<1 | 2 | 3>(1);
const studentId = ref('');
const validating = ref(false);
const verifying = ref(false);
const cameraActive = ref(false);
const videoRef = ref<HTMLVideoElement | null>(null);
let stream: MediaStream | null = null;

// 错误信息
const lastError = ref<{
  message: string;
  status?: number;
  url?: string;
  detail?: string;
} | null>(null);

// 签到结果数据
const checkInRecord = ref<AttendanceRecord | null>(null);

// 检查是否有考勤信息
const hasAttendanceInfo = computed(() => {
  return attendanceId.value > 0 && qrCodeToken.value.length > 0;
});

// 格式化签到时间
const successTime = computed(() => {
  if (!checkInRecord.value?.checkInTime && !checkInRecord.value?.check_in_time) {
    return new Date().toLocaleString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    });
  }
  
  const timeStr = checkInRecord.value.checkInTime || checkInRecord.value.check_in_time;
  return new Date(timeStr!).toLocaleString('zh-CN', {
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  });
});

// 签到状态文本
const statusText = computed(() => {
  if (!checkInRecord.value) return '正常';
  
  const status = checkInRecord.value.status;
  switch (status) {
    case 'present':
      return '正常';
    case 'late':
      return '迟到';
    case 'absent':
      return '缺勤';
    case 'leave':
      return '请假';
    default:
      return '未知';
  }
});

// 签到状态颜色
const statusColor = computed(() => {
  if (!checkInRecord.value) return 'green';
  
  const status = checkInRecord.value.status;
  switch (status) {
    case 'present':
      return 'green';
    case 'late':
      return 'orange';
    case 'absent':
      return 'red';
    case 'leave':
      return 'blue';
    default:
      return 'gray';
  }
});

// Navigation functions
const goBack = () => {
  if (currentStep.value > 1) {
    currentStep.value--;
  } else {
    // 实际项目中应返回上一页
    console.log('返回上一页');
  }
};

// 人脸验证模态框显示状态
const faceVerificationVisible = ref(false);

// 点击下一步，打开人脸验证模态框
const handleNextStep = () => {
  if (!studentId.value.trim()) {
    message.error('请输入学号');
    return;
  }

  // 检查是否有考勤信息
  if (!hasAttendanceInfo.value) {
    message.error('缺少考勤信息，请重新扫描二维码');
    return;
  }

  // 检查网络状态
  if (!isOnline.value) {
    message.error('网络已断开，请检查网络连接');
    return;
  }
  
  // 打开人脸验证模态框
  faceVerificationVisible.value = true;
};

// 人脸验证成功回调
const handleFaceVerificationSuccess = () => {
  // 人脸验证成功后，调用二维码签到接口完成签到
  validateStudentId();
};

// Student ID validation and check-in
const validateStudentId = async () => {
  if (!studentId.value.trim()) {
    message.error('请输入学号');
    return;
  }

  // 检查是否有考勤信息
  if (!hasAttendanceInfo.value) {
    message.error('缺少考勤信息，请重新扫描二维码');
    return;
  }

  // 检查网络状态
  if (!isOnline.value) {
    message.error('网络已断开，请检查网络连接');
    return;
  }
  
  // 清除之前的错误
  lastError.value = null;
  
  validating.value = true;
  
  try {
    console.log('=== 开始签到 ===');
    console.log('请求参数:', {
      attendanceId: attendanceId.value,
      qrCodeToken: qrCodeToken.value,
      studentNumber: studentId.value
    });
    
    // 调用后端API验证二维码并签到
    const result = await verifyQRCodeAndCheckIn({
      attendanceId: attendanceId.value,
      qrCodeToken: qrCodeToken.value,
      studentNumber: studentId.value  // 传递学号
    });
    
    // 保存签到记录
    checkInRecord.value = result.data;
    
    // 签到成功，跳转到成功页面
    currentStep.value = 3;
    message.success('签到成功！');
    
  } catch (error: any) {
    console.error('签到失败 - 完整错误信息:', error);
    console.error('错误响应:', error.response);
    console.error('错误数据:', error.response?.data);
    console.error('错误状态码:', error.response?.status);
    console.error('请求配置:', error.config);
    
    // 构建详细错误信息
    let errorMsg = '签到失败';
    let errorDetail = '';
    
    if (error.response) {
      // 服务器返回了错误响应
      const status = error.response.status;
      const data = error.response.data;
      
      errorMsg = data?.message || `服务器错误 (${status})`;
      errorDetail = `状态码: ${status}\n请求地址: ${error.config?.url}\n响应数据: ${JSON.stringify(data, null, 2)}`;
      
      // 保存错误信息到界面
      lastError.value = {
        message: errorMsg,
        status: status,
        url: error.config?.url,
        detail: errorDetail
      };
      
      console.log('服务器错误响应:', errorDetail);
    } else if (error.request) {
      // 请求已发送但没有收到响应
      errorMsg = '网络连接失败';
      errorDetail = `请求地址: ${error.config?.url}\n请求方法: ${error.config?.method}\n请求数据: ${JSON.stringify(error.config?.data, null, 2)}\n\n可能原因:\n1. 后端服务未启动\n2. 后端地址不正确\n3. 网络防火墙阻止\n4. CORS 跨域问题`;
      
      console.log('网络连接错误:', errorDetail);
    } else {
      // 设置请求时发生了错误
      errorMsg = error.message || '未知错误';
      errorDetail = `错误信息: ${error.message}\n错误堆栈: ${error.stack}`;
      
      console.log('请求配置错误:', errorDetail);
    }
    
    // 显示错误信息
    if (errorMsg.includes('过期')) {
      message.error('二维码已过期，请重新扫描');
    } else if (errorMsg.includes('不存在')) {
      message.error('学号不存在，请重新输入');
    } else if (errorMsg.includes('不在') || errorMsg.includes('范围')) {
      message.error('您不在本次考勤范围内，请联系教师');
    } else if (errorMsg.includes('已经签到') || errorMsg.includes('重复')) {
      message.error('您已经签到过了');
    } else if (errorMsg.includes('网络') || errorMsg.includes('连接')) {
      // 网络错误，显示详细信息
      message.error({
        content: errorMsg,
        duration: 5
      });
      // 在控制台显示详细信息
      console.error('=== 网络错误详情 ===')
      console.error(errorDetail);
      console.error('===================');
    } else {
      message.error({
        content: errorMsg + ' - 请查看控制台获取详细信息',
        duration: 5
      });
      console.error('=== 错误详情 ===')
      console.error(errorDetail);
      console.error('================');
    }
  } finally {
    validating.value = false;
  }
};

// Camera control
const toggleCamera = async () => {
  if (cameraActive.value) {
    stopCamera();
  } else {
    await startCamera();
  }
};

const startCamera = async () => {
  try {
    stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'user' } 
    });
    
    if (videoRef.value) {
      videoRef.value.srcObject = stream;
    }
    
    cameraActive.value = true;
  } catch (err) {
    message.error('无法访问摄像头，请检查权限设置');
    console.error('Camera error:', err);
  }
};

const stopCamera = () => {
  if (stream) {
    stream.getTracks().forEach(track => track.stop());
    stream = null;
  }
  
  if (videoRef.value) {
    videoRef.value.srcObject = null;
  }
  
  cameraActive.value = false;
};

// Face verification
const captureAndVerify = async () => {
  if (!cameraActive.value) {
    message.warning('请先开启摄像头');
    return;
  }

  verifying.value = true;
  
  // Simulate face recognition process
  await new Promise(resolve => setTimeout(resolve, 2000));
  
  // Mock verification result
  const isSuccess = Math.random() > 0.2; // 80% success rate
  
  if (isSuccess) {
    stopCamera();
    currentStep.value = 3;
    message.success('人脸识别成功，签到完成！');
  } else {
    message.error('人脸识别失败，请调整角度后重试');
  }
  
  verifying.value = false;
};

// Finish process
const finishProcess = () => {
  // In real app, this would navigate to another page
  message.info('签到流程已完成');
  currentStep.value = 1;
  studentId.value = '';
};

// Lifecycle hooks
onMounted(() => {
  // 检查是否有考勤信息
  if (!hasAttendanceInfo.value) {
    message.warning('缺少考勤信息，请先扫描二维码');
    // 可以选择跳转到扫描页面
    // router.push({ name: 'QRCodeScanner' });
  }
  
  // Initialize with step 1
  currentStep.value = 1;
});

onBeforeUnmount(() => {
  // Clean up camera when component is destroyed
  stopCamera();
});
</script>

<style scoped>
:deep(.ant-input-affix-wrapper) {
  border-radius: 12px;
  padding: 12px 16px;
}

:deep(.ant-btn) {
  border-radius: 12px !important;
}

:deep(.ant-btn-primary) {
  background-color: #1677ff;
  border-color: #1677ff;
}
</style>

