<template>
  <div class="face-upload-container">
    <div class="face-upload-card">
      <div class="card-header">
        <camera-outlined class="header-icon" />
        <h2 class="header-title">上传人脸照片</h2>
        <p class="header-subtitle">用于人脸识别签到，请确保照片清晰且正面</p>
      </div>

      <div class="card-body">
        <!-- 预览区域 -->
        <div class="preview-section">
          <div class="preview-box" :class="{ 'has-image': previewUrl }">
            <img v-if="previewUrl" :src="previewUrl" alt="人脸预览" class="preview-image" />
            <div v-else class="preview-placeholder">
              <user-outlined class="placeholder-icon" />
              <p class="placeholder-text">暂无照片</p>
            </div>
          </div>

          <!-- 拍照/上传按钮 -->
          <div class="action-buttons">
            <a-button 
              type="primary" 
              size="large" 
              @click="openCamera"
              :loading="cameraLoading"
              class="action-btn"
            >
              <template #icon><camera-outlined /></template>
              拍照上传
            </a-button>
            
            <a-button 
              size="large" 
              @click="selectFile"
              class="action-btn"
            >
              <template #icon><upload-outlined /></template>
              选择文件
            </a-button>
            
            <input 
              ref="fileInput" 
              type="file" 
              accept="image/*" 
              @change="handleFileSelect"
              style="display: none"
            />
          </div>
        </div>

        <!-- 提示信息 -->
        <div class="tips-section">
          <a-alert
            message="拍照提示"
            type="info"
            show-icon
          >
            <template #description>
              <ul class="tips-list">
                <li>请确保光线充足，面部清晰可见</li>
                <li>正面拍摄，不要遮挡面部</li>
                <li>建议使用纯色背景</li>
                <li>照片大小不超过5MB</li>
              </ul>
            </template>
          </a-alert>
        </div>

        <!-- 上传按钮 -->
        <div class="submit-section">
          <a-button 
            type="primary" 
            size="large" 
            block
            :disabled="!previewUrl"
            :loading="uploading"
            @click="handleUpload"
            class="submit-btn"
          >
            <template #icon><check-outlined /></template>
            确认上传
          </a-button>
        </div>
      </div>
    </div>

    <!-- 相机模态框 -->
    <a-modal
      v-model:open="cameraModalVisible"
      title="拍照上传"
      width="800px"
      :footer="null"
      @cancel="closeCamera"
    >
      <div class="camera-container">
        <video 
          ref="videoElement" 
          autoplay 
          playsinline
          class="camera-video"
        ></video>
        <canvas ref="canvasElement" style="display: none;"></canvas>
        
        <div class="camera-controls">
          <a-button 
            type="primary" 
            size="large"
            @click="capturePhoto"
            class="capture-btn"
          >
            <template #icon><camera-outlined /></template>
            拍照
          </a-button>
          <a-button 
            size="large"
            @click="closeCamera"
          >
            取消
          </a-button>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onUnmounted } from 'vue'
import { message } from 'ant-design-vue'
import { 
  CameraOutlined, 
  UploadOutlined, 
  UserOutlined,
  CheckOutlined 
} from '@ant-design/icons-vue'
import { userApiUploadFaceImage } from '@/api/userController'

// 响应式数据
const previewUrl = ref<string>('')
const uploading = ref(false)
const cameraLoading = ref(false)
const cameraModalVisible = ref(false)
const fileInput = ref<HTMLInputElement | null>(null)
const videoElement = ref<HTMLVideoElement | null>(null)
const canvasElement = ref<HTMLCanvasElement | null>(null)
let mediaStream: MediaStream | null = null

// 选择文件
const selectFile = () => {
  fileInput.value?.click()
}

// 处理文件选择
const handleFileSelect = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    message.error('请选择图片文件')
    return
  }
  
  // 验证文件大小（5MB）
  const maxSize = 5 * 1024 * 1024
  if (file.size > maxSize) {
    message.error('图片大小不能超过5MB')
    return
  }
  
  // 读取文件并预览
  const reader = new FileReader()
  reader.onload = (e) => {
    previewUrl.value = e.target?.result as string
  }
  reader.readAsDataURL(file)
}

// 打开相机
const openCamera = async () => {
  cameraLoading.value = true
  cameraModalVisible.value = true
  
  try {
    // 请求摄像头权限
    mediaStream = await navigator.mediaDevices.getUserMedia({ 
      video: { 
        facingMode: 'user',
        width: { ideal: 1280 },
        height: { ideal: 720 }
      } 
    })
    
    if (videoElement.value) {
      videoElement.value.srcObject = mediaStream
    }
  } catch (error) {
    console.error('无法访问摄像头:', error)
    message.error('无法访问摄像头，请检查权限设置')
    cameraModalVisible.value = false
  } finally {
    cameraLoading.value = false
  }
}

// 关闭相机
const closeCamera = () => {
  if (mediaStream) {
    mediaStream.getTracks().forEach(track => track.stop())
    mediaStream = null
  }
  cameraModalVisible.value = false
}

// 拍照
const capturePhoto = () => {
  if (!videoElement.value || !canvasElement.value) return
  
  const video = videoElement.value
  const canvas = canvasElement.value
  
  // 设置canvas尺寸与视频一致
  canvas.width = video.videoWidth
  canvas.height = video.videoHeight
  
  // 绘制当前视频帧到canvas
  const ctx = canvas.getContext('2d')
  if (ctx) {
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height)
    
    // 转换为base64
    previewUrl.value = canvas.toDataURL('image/jpeg', 0.9)
    
    message.success('拍照成功')
    closeCamera()
  }
}

// 上传照片
const handleUpload = async () => {
  if (!previewUrl.value) {
    message.warning('请先选择或拍摄照片')
    return
  }
  
  uploading.value = true
  
  try {
    const response = await userApiUploadFaceImage({
      faceImageBase64: previewUrl.value
    })
    
    if (response) {
      message.success('人脸照片上传成功！')
    }
  } catch (error: any) {
    console.error('上传失败:', error)
    message.error(error.message || '上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

// 组件卸载时清理资源
onUnmounted(() => {
  closeCamera()
})
</script>

<style scoped lang="scss">
.face-upload-container {
  min-height: 100vh;
  background: linear-gradient(135deg, var(--primary-color-light, #e6f4ff) 0%, var(--background-color, #f5f5f5) 100%);
  padding: 24px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.face-upload-card {
  width: 100%;
  max-width: 600px;
  background: var(--component-background, #ffffff);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  overflow: hidden;
}

.card-header {
  background: linear-gradient(135deg, var(--primary-color, #1890ff) 0%, var(--primary-color-hover, #40a9ff) 100%);
  color: var(--text-color-inverse, #ffffff);
  padding: 32px 24px;
  text-align: center;
}

.header-icon {
  font-size: 48px;
  margin-bottom: 16px;
  display: block;
}

.header-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
  color: var(--text-color-inverse, #ffffff);
}

.header-subtitle {
  font-size: 14px;
  margin: 0;
  opacity: 0.9;
  color: var(--text-color-inverse, #ffffff);
}

.card-body {
  padding: 32px 24px;
}

.preview-section {
  margin-bottom: 24px;
}

.preview-box {
  width: 100%;
  aspect-ratio: 4/3;
  border-radius: 12px;
  overflow: hidden;
  background: var(--background-color-light, #fafafa);
  border: 2px dashed var(--border-color-base, #d9d9d9);
  display: flex;
  align-items: center;
  justify-content: center;
  margin-bottom: 16px;
  transition: all 0.3s ease;

  &.has-image {
    border-color: var(--primary-color, #1890ff);
    border-style: solid;
  }
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  text-align: center;
  color: var(--text-color-secondary, #8c8c8c);
}

.placeholder-icon {
  font-size: 64px;
  margin-bottom: 8px;
  display: block;
}

.placeholder-text {
  margin: 0;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 12px;
}

.action-btn {
  flex: 1;
  height: 48px;
  font-size: 16px;
  border-radius: 8px;
}

.tips-section {
  margin-bottom: 24px;
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

.submit-section {
  margin-top: 24px;
}

.submit-btn {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  border-radius: 8px;
}

// 相机模态框样式
.camera-container {
  text-align: center;
}

.camera-video {
  width: 100%;
  max-height: 500px;
  border-radius: 8px;
  background: var(--background-color-base, #000000);
  margin-bottom: 16px;
}

.camera-controls {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.capture-btn {
  min-width: 120px;
  height: 40px;
}

// 响应式设计
@media (max-width: 768px) {
  .face-upload-container {
    padding: 16px;
  }

  .card-header {
    padding: 24px 16px;
  }

  .header-icon {
    font-size: 36px;
  }

  .header-title {
    font-size: 20px;
  }

  .card-body {
    padding: 24px 16px;
  }

  .action-buttons {
    flex-direction: column;
  }

  .action-btn {
    width: 100%;
  }
}
</style>
