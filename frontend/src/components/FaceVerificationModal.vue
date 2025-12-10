<template>
  <a-modal
    :open="visible"
    title="人脸验证签到"
    width="700px"
    :footer="null"
    :maskClosable="false"
    @cancel="handleCancel"
  >
    <div class="face-verification-container">
      <!-- 步骤指示器 -->
      <a-steps :current="currentStep" size="small" class="steps-indicator">
        <a-step title="拍照验证" />
        <a-step title="完成验证" />
      </a-steps>

      <!-- 学号信息显示 -->
      <a-alert
        :message="`学号: ${props.studentNumber}`"
        description="系统将使用您预先上传的人脸照片进行验证"
        type="info"
        show-icon
        class="student-info-alert"
      />

      <!-- 步骤1: 拍照验证 -->
      <div v-if="currentStep === 0" class="step-content">
        <div class="camera-section">
          <!-- 预览区域 -->
          <div class="preview-box" :class="{ 'has-image': capturedImage }">
            <img
              v-if="capturedImage"
              :src="capturedImage"
              alt="拍摄的照片"
              class="captured-image"
            />
            <video
              v-else
              ref="videoElement"
              autoplay
              playsinline
              class="camera-video"
            ></video>
            
            <div v-if="!cameraReady && !capturedImage" class="camera-loading">
              <a-spin size="large" />
              <p>正在启动摄像头...</p>
            </div>
          </div>

          <!-- 提示信息 -->
          <a-alert
            v-if="!capturedImage"
            message="拍照提示"
            type="warning"
            show-icon
            class="camera-tips"
          >
            <template #description>
              <ul class="tips-list">
                <li>请确保光线充足，面部清晰可见</li>
                <li>正面对准摄像头，不要遮挡面部</li>
                <li>保持静止，点击拍照按钮</li>
              </ul>
            </template>
          </a-alert>

          <!-- 操作按钮 -->
          <div class="button-group">
            <a-button size="large" @click="handleCancel" :disabled="verifying">
              取消
            </a-button>
            
            <a-button
              v-if="!capturedImage"
              type="primary"
              size="large"
              @click="capturePhoto"
              :disabled="!cameraReady"
            >
              <template #icon><camera-outlined /></template>
              拍照
            </a-button>
            
            <template v-else>
              <a-button size="large" @click="retakePhoto">
                <template #icon><redo-outlined /></template>
                重拍
              </a-button>
              <a-button
                type="primary"
                size="large"
                :loading="verifying"
                @click="handleVerify"
              >
                <template #icon><check-outlined /></template>
                验证
              </a-button>
            </template>
          </div>
        </div>
      </div>

      <!-- 步骤2: 验证结果 -->
      <div v-if="currentStep === 1" class="step-content">
        <div class="result-section">
          <a-result
            :status="verificationResult.success ? 'success' : 'error'"
            :title="verificationResult.title"
            :sub-title="verificationResult.message"
          >
            <template #icon>
              <check-circle-outlined v-if="verificationResult.success" class="success-icon" />
              <close-circle-outlined v-else class="error-icon" />
            </template>
            
            <template #extra>
              <div v-if="verificationResult.similarity > 0" class="similarity-info">
                <p class="similarity-label">相似度</p>
                <a-progress
                  type="circle"
                  :percent="Math.round(verificationResult.similarity * 100)"
                  :status="verificationResult.success ? 'success' : 'exception'"
                  :width="120"
                />
              </div>
              
              <div class="action-buttons">
                <a-button
                  v-if="!verificationResult.success"
                  type="primary"
                  size="large"
                  @click="handleRetry"
                >
                  重新验证
                </a-button>
                <a-button
                  v-if="!verificationResult.success && !verificationResult.hasFaceImage"
                  size="large"
                  @click="handleGoToUpload"
                >
                  去上传人脸照片
                </a-button>
                <a-button
                  v-if="verificationResult.success"
                  type="primary"
                  size="large"
                  @click="handleFinish"
                >
                  完成
                </a-button>
              </div>
            </template>
          </a-result>
        </div>
      </div>
    </div>

    <canvas ref="canvasElement" style="display: none;"></canvas>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, watch, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import {
  UserOutlined,
  CameraOutlined,
  CheckOutlined,
  RedoOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined
} from '@ant-design/icons-vue'
import { attendanceApiFaceVerificationPost } from '@/api/attendanceController'
import { useRouter } from 'vue-router'

interface Props {
  visible: boolean
  attendanceId: number
  studentNumber: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const router = useRouter()

// 响应式数据
const currentStep = ref(0)
const studentNumber = ref('')
const capturedImage = ref('')
const verifying = ref(false)
const cameraReady = ref(false)

const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
let mediaStream: MediaStream | null = null

const verificationResult = ref({
  success: false,
  title: '',
  message: '',
  similarity: 0,
  hasFaceImage: false
})

// 监听弹窗显示状态
watch(() => props.visible, (newVal) => {
  if (newVal) {
    resetState()
  } else {
    closeCamera()
  }
})

// 重置状态
const resetState = () => {
  currentStep.value = 0
  capturedImage.value = ''
  verifying.value = false
  cameraReady.value = false
  verificationResult.value = {
    success: false,
    title: '',
    message: '',
    similarity: 0,
    hasFaceImage: false
  }
  // 自动打开摄像头
  setTimeout(() => {
    openCamera()
  }, 300)
}


// 打开摄像头
const openCamera = async () => {
  try {
    cameraReady.value = false
    mediaStream = await navigator.mediaDevices.getUserMedia({
      video: {
        facingMode: 'user',
        width: { ideal: 1280 },
        height: { ideal: 720 }
      }
    })
    
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
      videoElement.value.onloadedmetadata = () => {
        cameraReady.value = true
      }
    }
  } catch (error) {
    console.error('无法访问摄像头:', error)
    message.error('无法访问摄像头，请检查权限设置')
    currentStep.value = 0
  }
}

// 关闭摄像头
const closeCamera = () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  cameraReady.value = false
}

// 拍照
const capturePhoto = () => {
  if (!videoElement.value || !canvasElement.value) return
  
  const video = videoElement.value
  const canvas = canvasElement.value
  
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    capturedImage.value = canvas.toDataURL('image/jpeg', 0.9)
    closeCamera()
  }
}

// 重拍
const retakePhoto = () => {
  capturedImage.value = ''
  openCamera()
}

// 验证人脸
const handleVerify = async () => {
  if (!capturedImage.value) {
    message.warning('请先拍照')
    return
  }
  
  verifying.value = true
  
  try {
    const response = await attendanceApiFaceVerificationPost({
      studentNumber: props.studentNumber,
      faceImageBase64: capturedImage.value,
      attendanceId: props.attendanceId
    })
    
    if (response.verified) {
      verificationResult.value = {
        success: true,
        title: '验证成功！',
        message: response.message || '人脸验证通过',
        similarity: response.similarity || 0,
        hasFaceImage: response.hasFaceImage || false
      }
      message.success('人脸验证成功！')
      currentStep.value = 1
      // 触发成功事件，让父组件处理签到逻辑
      emit('success')
    } else {
      verificationResult.value = {
        success: false,
        title: '验证失败',
        message: response.message || '人脸验证未通过',
        similarity: response.similarity || 0,
        hasFaceImage: response.hasFaceImage || false
      }
      currentStep.value = 1
    }
  } catch (error: any) {
    console.error('=== 人脸验证失败 ===')
    console.error('完整错误对象:', error)
    console.error('错误响应:', error.response)
    console.error('错误数据:', error.response?.data)
    console.error('状态码:', error.response?.status)
    console.error('请求配置:', error.config)
    
    // 从响应中提取错误信息
    const errorData = error.response?.data || error.data || {}
    const errorMessage = errorData.message || error.message || '人脸验证失败，请重试'
    
    console.error('提取的错误信息:', errorMessage)
    console.error('相似度:', errorData.similarity)
    console.error('是否有人脸照片:', errorData.hasFaceImage || errorData.has_face_image)
    
    verificationResult.value = {
      success: false,
      title: '验证失败',
      message: errorMessage,
      similarity: errorData.similarity || 0,
      hasFaceImage: errorData.hasFaceImage || errorData.has_face_image || false
    }
    
    currentStep.value = 1
  } finally {
    verifying.value = false
  }
}

// 重新验证
const handleRetry = () => {
  currentStep.value = 0
  capturedImage.value = ''
}

// 去上传人脸照片
const handleGoToUpload = () => {
  router.push('/student/face-upload')
  handleCancel()
}

// 完成
const handleFinish = () => {
  handleCancel()
}

// 取消
const handleCancel = () => {
  closeCamera()
  emit('update:visible', false)
}

// 组件卸载时清理
onUnmounted(() => {
  closeCamera()
})
</script>

<style scoped lang="scss">
.face-verification-container {
  padding: 16px 0;
}

.steps-indicator {
  margin-bottom: 24px;
}

.student-info-alert {
  margin-bottom: 24px;
}

.step-content {
  min-height: 400px;
}

// 输入学号步骤
.input-section {
  max-width: 500px;
  margin: 0 auto;
}

.info-alert {
  margin-bottom: 24px;
}

.student-form {
  margin-bottom: 24px;
}

// 拍照步骤
.camera-section {
  .preview-box {
    width: 100%;
    aspect-ratio: 4/3;
    border-radius: 12px;
    overflow: hidden;
    background: var(--background-color-base, #000000);
    border: 2px solid var(--border-color-base, #d9d9d9);
    display: flex;
    align-items: center;
    justify-content: center;
    margin-bottom: 16px;
    position: relative;

    &.has-image {
      border-color: var(--primary-color, #1890ff);
    }
  }

  .camera-video,
  .captured-image {
    width: 100%;
    height: 100%;
    object-fit: cover;
  }

  .camera-loading {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: var(--text-color-inverse, #ffffff);

    p {
      margin-top: 16px;
      font-size: 14px;
    }
  }

  .camera-tips {
    margin-bottom: 16px;
  }

  .tips-list {
    margin: 8px 0 0 0;
    padding-left: 20px;

    li {
      margin-bottom: 4px;
      color: var(--text-color-secondary, #595959);
      font-size: 14px;
    }
  }
}

// 结果步骤
.result-section {
  .success-icon {
    font-size: 72px;
    color: var(--success-color, #52c41a);
  }

  .error-icon {
    font-size: 72px;
    color: var(--error-color, #ff4d4f);
  }

  .similarity-info {
    text-align: center;
    margin-bottom: 24px;

    .similarity-label {
      font-size: 16px;
      font-weight: 500;
      margin-bottom: 16px;
      color: var(--text-color, #262626);
    }
  }

  .action-buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
  }
}

// 按钮组
.button-group {
  display: flex;
  gap: 12px;
  justify-content: center;
  margin-top: 24px;
}

// 响应式
@media (max-width: 768px) {
  .camera-section .preview-box {
    aspect-ratio: 3/4;
  }

  .button-group {
    flex-direction: column;

    button {
      width: 100%;
    }
  }
}
</style>
