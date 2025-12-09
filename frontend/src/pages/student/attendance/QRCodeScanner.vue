<!-- 二维码扫描页面 -->
<template>
  <div class="qr-scanner-page">
    <!-- 顶部导航栏 -->
    <div class="scanner-header">
      <a-button type="text" @click="goBack" class="back-btn">
        <LeftOutlined />
      </a-button>
      <span class="header-title">扫描签到二维码</span>
      <div class="placeholder"></div>
    </div>

    <!-- 扫描区域 -->
    <div class="scanner-container">
      <div id="qr-reader" class="qr-reader"></div>
      
      <!-- 扫描框遮罩 -->
      <div class="scanner-overlay">
        <div class="scanner-frame">
          <div class="corner corner-tl"></div>
          <div class="corner corner-tr"></div>
          <div class="corner corner-bl"></div>
          <div class="corner corner-br"></div>
        </div>
      </div>

      <!-- 提示信息 -->
      <div class="scanner-tips">
        <p class="tip-text">{{ scanStatusText }}</p>
        <p class="tip-subtext">{{ scanSubText }}</p>
        <div class="scan-stats" v-if="scanAttempts > 0">
          <span class="stats-item">扫描次数: {{ scanAttempts }}</span>
          <span class="stats-item" v-if="lastScanTime">上次扫描: {{ lastScanTime }}</span>
        </div>
      </div>
      
      <!-- 扫描状态指示器 -->
      <div class="scan-indicator" :class="scanIndicatorClass">
        <div class="indicator-dot"></div>
        <span>{{ scanIndicatorText }}</span>
      </div>
    </div>

    <!-- 底部操作区 -->
    <div class="scanner-footer">
      <a-button 
        type="primary" 
        size="large" 
        @click="toggleFlash"
        v-if="flashAvailable"
        class="flash-btn"
      >
        <BulbOutlined />
        {{ flashOn ? '关闭闪光灯' : '开启闪光灯' }}
      </a-button>
      
      <div class="help-text">
        <InfoCircleOutlined />
        <span>扫描教师展示的考勤二维码即可签到</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onBeforeUnmount } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { LeftOutlined, BulbOutlined, InfoCircleOutlined } from '@ant-design/icons-vue'

// 动态导入 html5-qrcode（需要先安装：npm install html5-qrcode）
// @ts-ignore
import { Html5Qrcode } from 'html5-qrcode'

interface CameraDevice {
  id: string
  label: string
}

const router = useRouter()

// 状态变量
const flashOn = ref(false)
const flashAvailable = ref(false)
const scanStatus = ref<'idle' | 'scanning' | 'detected' | 'success' | 'error'>('idle')
const scanAttempts = ref(0)
const lastScanTime = ref('')
const scanStatusText = ref('请将二维码放入框内')
const scanSubText = ref('保持适当距离，确保光线充足')
let html5QrCode: Html5Qrcode | null = null
let currentStream: MediaStream | null = null
let scanDebounce: NodeJS.Timeout | null = null

/**
 * 扫描成功回调
 */
const onScanSuccess = (decodedText: string) => {
  // 防抖处理，避免重复扫描
  if (scanDebounce) {
    clearTimeout(scanDebounce)
  }
  
  scanDebounce = setTimeout(() => {
    try {
      console.log('扫描到二维码:', decodedText)
      
      // 更新状态
      scanStatus.value = 'detected'
      scanAttempts.value++
      lastScanTime.value = new Date().toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit', second: '2-digit' })
      scanStatusText.value = '✓ 检测到二维码'
      scanSubText.value = '正在解析数据...'
      
      // 解析二维码数据
      const qrData = JSON.parse(decodedText)
      
      console.log('解析后的数据:', qrData)
      
      // 验证二维码类型
      if (qrData.type !== 'attendance_qrcode') {
        scanStatus.value = 'error'
        scanStatusText.value = '✗ 二维码类型错误'
        scanSubText.value = '这不是考勤二维码，请扫描正确的二维码'
        message.error('这不是考勤二维码，请扫描正确的二维码')
        
        // 3秒后恢复扫描状态
        setTimeout(() => {
          scanStatus.value = 'scanning'
          scanStatusText.value = '请将二维码放入框内'
          scanSubText.value = '保持适当距离，确保光线充足'
        }, 3000)
        return
      }
      
      // 验证必要字段
      if (!qrData.attendanceId && !qrData.attendance_id) {
        scanStatus.value = 'error'
        scanStatusText.value = '✗ 数据不完整'
        scanSubText.value = '二维码缺少考勤ID'
        message.error('二维码数据不完整')
        
        setTimeout(() => {
          scanStatus.value = 'scanning'
          scanStatusText.value = '请将二维码放入框内'
          scanSubText.value = '保持适当距离，确保光线充足'
        }, 3000)
        return
      }
      
      if (!qrData.token) {
        scanStatus.value = 'error'
        scanStatusText.value = '✗ 数据不完整'
        scanSubText.value = '二维码缺少验证令牌'
        message.error('二维码数据不完整')
        
        setTimeout(() => {
          scanStatus.value = 'scanning'
          scanStatusText.value = '请将二维码放入框内'
          scanSubText.value = '保持适当距离，确保光线充足'
        }, 3000)
        return
      }
      
      // 扫描成功
      scanStatus.value = 'success'
      scanStatusText.value = '✓ 识别成功！'
      scanSubText.value = '正在跳转到签到页面...'
      
      // 停止扫描
      stopScanner()
      
      // 跳转到签到页面，携带考勤信息
      const attendanceId = qrData.attendanceId || qrData.attendance_id
      const token = qrData.token
      
      console.log('=== 准备跳转 ===')
      console.log('attendanceId:', attendanceId)
      console.log('token:', token)
      console.log('token长度:', token.length)
      
      router.push({
        name: 'AttendanceMobile',
        query: {
          attendanceId: attendanceId,
          token: token  // Vue Router会自动进行URL编码
        }
      })
      
      message.success('二维码识别成功，正在跳转...')
      
    } catch (error) {
      console.error('二维码解析错误:', error)
      scanStatus.value = 'error'
      scanStatusText.value = '✗ 解析失败'
      scanSubText.value = '二维码格式错误，请扫描正确的考勤二维码'
      message.error('二维码格式错误，请扫描正确的考勤二维码')
      
      // 3秒后恢复扫描状态
      setTimeout(() => {
        scanStatus.value = 'scanning'
        scanStatusText.value = '请将二维码放入框内'
        scanSubText.value = '保持适当距离，确保光线充足'
      }, 3000)
    }
  }, 300) // 300ms 防抖
}

/**
 * 扫描错误回调
 */
const onScanError = (errorMessage: string) => {
  // 扫描过程中的错误通常可以忽略（如未检测到二维码）
  if (!errorMessage.includes('NotFoundException')) {
    console.warn('扫描警告:', errorMessage)
  }
  
  // 更新扫描状态
  if (scanStatus.value === 'idle') {
    scanStatus.value = 'scanning'
    scanStatusText.value = '正在扫描...'
    scanSubText.value = '请将二维码对准扫描框'
  }
}

/**
 * 启动扫描器
 */
const startScanner = async () => {
  try {
    html5QrCode = new Html5Qrcode('qr-reader')
    
    // 获取相机列表
    const devices = await Html5Qrcode.getCameras()
    
    if (devices && devices.length > 0) {
      // 优先使用后置摄像头
      const backCamera = devices.find((device: CameraDevice) => 
        device.label.toLowerCase().includes('back') || 
        device.label.toLowerCase().includes('rear')
      )
      
      const cameraId = backCamera ? backCamera.id : devices[0].id
      
      // 启动相机扫描
      await html5QrCode.start(
        cameraId,
        {
          fps: 10,    // 每秒扫描10帧
          qrbox: { width: 250, height: 250 }, // 扫描框大小
          aspectRatio: 1.0
        },
        onScanSuccess,
        onScanError
      )
      
      // 检查是否支持闪光灯
      checkFlashSupport()
      
      scanStatus.value = 'scanning'
      scanStatusText.value = '相机已就绪'
      scanSubText.value = '请将二维码放入框内扫描'
      message.success('相机已启动，请扫描二维码')
    } else {
      message.error('未检测到可用的相机设备')
    }
  } catch (error) {
    console.error('相机启动失败:', error)
    message.error('无法启动相机，请检查相机权限设置')
  }
}

/**
 * 停止扫描器
 */
const stopScanner = async () => {
  try {
    if (html5QrCode) {
      await html5QrCode.stop()
      html5QrCode.clear()
    }
  } catch (error) {
    console.error('停止扫描器失败:', error)
  }
}

/**
 * 检查闪光灯支持
 */
const checkFlashSupport = async () => {
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ 
      video: { facingMode: 'environment' } 
    })
    currentStream = stream
    
    const tracks = stream.getVideoTracks()
    if (tracks.length === 0) return
    
    const track = tracks[0]
    const capabilities = track.getCapabilities() as any
    
    if (capabilities.torch) {
      flashAvailable.value = true
    }
  } catch (error) {
    console.warn('闪光灯不可用:', error)
  }
}

/**
 * 切换闪光灯
 */
const toggleFlash = async () => {
  try {
    if (!currentStream) return
    
    const tracks = currentStream.getVideoTracks()
    if (tracks.length === 0) return
    
    const track = tracks[0]
    await track.applyConstraints({
      advanced: [{ torch: !flashOn.value } as any]
    })
    
    flashOn.value = !flashOn.value
    message.success(flashOn.value ? '闪光灯已开启' : '闪光灯已关闭')
  } catch (error) {
    console.error('切换闪光灯失败:', error)
    message.error('闪光灯操作失败')
  }
}

/**
 * 返回上一页
 */
const goBack = () => {
  stopScanner()
  router.back()
}

// 生命周期钩子
onMounted(() => {
  startScanner()
})

onBeforeUnmount(() => {
  stopScanner()
  
  // 清理防抖定时器
  if (scanDebounce) {
    clearTimeout(scanDebounce)
  }
  
  // 清理媒体流
  if (currentStream) {
    currentStream.getTracks().forEach(track => track.stop())
  }
})

// 计算属性：扫描指示器类名
const scanIndicatorClass = computed(() => {
  return `indicator-${scanStatus.value}`
})

// 计算属性：扫描指示器文本
const scanIndicatorText = computed(() => {
  switch (scanStatus.value) {
    case 'idle':
      return '准备中...'
    case 'scanning':
      return '扫描中'
    case 'detected':
      return '已检测'
    case 'success':
      return '成功'
    case 'error':
      return '错误'
    default:
      return '扫描中'
  }
})
</script>

<style scoped>
.qr-scanner-page {
  width: 100%;
  height: 100vh;
  background: #000;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

/* 顶部导航栏 */
.scanner-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  background: rgba(0, 0, 0, 0.8);
  color: #fff;
  z-index: 10;
}

.back-btn {
  color: #fff !important;
  font-size: 20px;
}

.header-title {
  font-size: 16px;
  font-weight: 500;
}

.placeholder {
  width: 32px;
}

/* 扫描容器 */
.scanner-container {
  flex: 1;
  position: relative;
  overflow: hidden;
}

.qr-reader {
  width: 100%;
  height: 100%;
}

/* 隐藏 html5-qrcode 默认的按钮 */
:deep(#qr-reader__dashboard_section_csr) {
  display: none !important;
}

:deep(#qr-reader__header_message) {
  display: none !important;
}

/* 扫描框遮罩 */
.scanner-overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  display: flex;
  align-items: center;
  justify-content: center;
}

.scanner-frame {
  position: relative;
  width: 250px;
  height: 250px;
  box-shadow: 0 0 0 9999px rgba(0, 0, 0, 0.6);
}

/* 扫描框四角 */
.corner {
  position: absolute;
  width: 30px;
  height: 30px;
  border: 3px solid var(--primary-color, #1677ff);
}

.corner-tl {
  top: -3px;
  left: -3px;
  border-right: none;
  border-bottom: none;
}

.corner-tr {
  top: -3px;
  right: -3px;
  border-left: none;
  border-bottom: none;
}

.corner-bl {
  bottom: -3px;
  left: -3px;
  border-right: none;
  border-top: none;
}

.corner-br {
  bottom: -3px;
  right: -3px;
  border-left: none;
  border-top: none;
}

/* 提示信息 */
.scanner-tips {
  position: absolute;
  bottom: 120px;
  left: 0;
  right: 0;
  text-align: center;
  color: #fff;
  z-index: 5;
}

.tip-text {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
}

.tip-subtext {
  font-size: 14px;
  opacity: 0.8;
}

.scan-stats {
  margin-top: 12px;
  display: flex;
  gap: 16px;
  justify-content: center;
  font-size: 12px;
  opacity: 0.7;
}

.stats-item {
  background: rgba(255, 255, 255, 0.1);
  padding: 4px 12px;
  border-radius: 12px;
}

/* 扫描状态指示器 */
.scan-indicator {
  position: absolute;
  top: 80px;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border-radius: 20px;
  background: rgba(0, 0, 0, 0.7);
  color: #fff;
  font-size: 14px;
  z-index: 5;
  transition: all 0.3s ease;
}

.indicator-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  animation: pulse 2s infinite;
}

.indicator-idle .indicator-dot {
  background: #999;
}

.indicator-scanning .indicator-dot {
  background: #1677ff;
}

.indicator-detected .indicator-dot {
  background: #faad14;
}

.indicator-success .indicator-dot {
  background: #52c41a;
}

.indicator-error .indicator-dot {
  background: #ff4d4f;
}

@keyframes pulse {
  0%, 100% {
    opacity: 1;
    transform: scale(1);
  }
  50% {
    opacity: 0.5;
    transform: scale(1.2);
  }
}

/* 底部操作区 */
.scanner-footer {
  padding: 20px 16px;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
  z-index: 10;
}

.flash-btn {
  width: 100%;
  max-width: 300px;
  height: 48px;
  border-radius: 24px;
  font-size: 16px;
}

.help-text {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(255, 255, 255, 0.7);
  font-size: 14px;
}

/* 响应式调整 */
@media (max-width: 375px) {
  .scanner-frame {
    width: 220px;
    height: 220px;
  }
}

@media (min-width: 768px) {
  .scanner-frame {
    width: 300px;
    height: 300px;
  }
}
</style>
