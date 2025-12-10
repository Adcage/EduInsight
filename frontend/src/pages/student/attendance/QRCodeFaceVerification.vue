<template>
  <div class="qr-face-verification-page">
    <div class="page-header">
      <a-button type="text" @click="goBack">
        <template #icon>
          <arrow-left-outlined/>
        </template>
        返回
      </a-button>
      <h1 class="page-title">二维码签到</h1>
    </div>

    <div class="page-content">
      <!-- 步骤指示 -->
      <a-steps :current="currentStep" class="steps-container">
        <a-step title="扫描二维码"/>
        <a-step title="人脸验证"/>
        <a-step title="完成签到"/>
      </a-steps>

      <!-- 步骤1: 扫描二维码 -->
      <div v-if="currentStep === 0" class="step-section">
        <a-card class="scan-card" title="扫描二维码">
          <a-alert
              class="scan-tip"
              description="扫描后将进入人脸验证环节"
              message="请扫描教师展示的二维码"
              show-icon
              type="info"
          />

          <div class="qr-scanner-container">
            <a-button
                block
                size="large"
                type="primary"
                @click="handleScanQRCode"
            >
              <template #icon>
                <scan-outlined/>
              </template>
              开始扫描二维码
            </a-button>
          </div>

          <!-- 或者手动输入 -->
          <a-divider>或</a-divider>

          <a-form layout="vertical">
            <a-form-item label="手动输入考勤ID">
              <a-input-number
                  v-model:value="manualAttendanceId"
                  :min="1"
                  placeholder="请输入考勤ID"
                  style="width: 100%"
              />
            </a-form-item>
            <a-button
                :disabled="!manualAttendanceId"
                block
                @click="handleManualInput"
            >
              确认
            </a-button>
          </a-form>
        </a-card>
      </div>

      <!-- 步骤2: 输入学号 -->
      <div v-if="currentStep === 1" class="step-section">
        <a-card class="verification-card" title="输入学号">
          <a-alert
              class="verification-tip"
              description="验证学号后将进行人脸识别验证"
              message="请输入您的学号"
              show-icon
              type="info"
          />

          <div class="verification-info">
            <p><strong>考勤ID:</strong> {{ attendanceId }}</p>
          </div>

          <a-form layout="vertical">
            <a-form-item label="学号" required>
              <a-input
                  v-model:value="studentNumber"
                  :maxlength="20"
                  placeholder="请输入您的学号"
                  size="large"
                  @pressEnter="openFaceVerification"
              >
                <template #prefix>
                  <user-outlined/>
                </template>
              </a-input>
            </a-form-item>
          </a-form>

          <a-button
              :disabled="!studentNumber.trim()"
              block
              size="large"
              type="primary"
              @click="openFaceVerification"
          >
            <template #icon>
              <camera-outlined/>
            </template>
            下一步 - 人脸验证
          </a-button>
        </a-card>
      </div>

      <!-- 步骤3: 完成 -->
      <div v-if="currentStep === 2" class="step-section">
        <a-result
            status="success"
            sub-title="您已成功完成签到"
            title="签到成功！"
        >
          <template #extra>
            <a-space direction="vertical" style="width: 100%">
              <a-button block size="large" type="primary" @click="goToAttendanceList">
                查看我的签到记录
              </a-button>
              <a-button block size="large" @click="resetAndScanAgain">
                继续扫码签到
              </a-button>
            </a-space>
          </template>
        </a-result>
      </div>
    </div>

    <!-- 人脸验证模态框 -->
    <FaceVerificationModal
        v-model:visible="faceVerificationVisible"
        :attendance-id="attendanceId"
        :student-number="studentNumber"
        @success="handleVerificationSuccess"
    />
  </div>
</template>

<script lang="ts" setup>
import {ref} from 'vue'
import {useRouter} from 'vue-router'
import {message} from 'ant-design-vue'
import {ArrowLeftOutlined, CameraOutlined, ScanOutlined, UserOutlined} from '@ant-design/icons-vue'
import FaceVerificationModal from '@/components/FaceVerificationModal.vue'

const router = useRouter()

// 响应式数据
const currentStep = ref(0)
const attendanceId = ref(0)
const studentNumber = ref('')
const manualAttendanceId = ref<number>()
const faceVerificationVisible = ref(false)

// 返回
const goBack = () => {
  router.back()
}

// 扫描二维码（实际项目中需要集成扫码库）
const handleScanQRCode = () => {
  message.info('请使用手机扫码功能或手动输入考勤ID')
  // 这里应该调用扫码库，例如 html5-qrcode
  // 扫码成功后解析出 attendanceId，然后进入下一步
}

// 手动输入
const handleManualInput = () => {
  if (!manualAttendanceId.value) {
    message.warning('请输入考勤ID')
    return
  }

  attendanceId.value = manualAttendanceId.value
  currentStep.value = 1
  message.success('考勤ID已确认，请输入学号')
}

// 打开人脸验证
const openFaceVerification = () => {
  if (!attendanceId.value) {
    message.error('考勤ID无效')
    return
  }

  if (!studentNumber.value.trim()) {
    message.warning('请输入学号')
    return
  }

  faceVerificationVisible.value = true
}

// 验证成功
const handleVerificationSuccess = () => {
  currentStep.value = 2
}

// 查看签到记录
const goToAttendanceList = () => {
  router.push('/student/attendance')
}

// 重新扫码
const resetAndScanAgain = () => {
  currentStep.value = 0
  attendanceId.value = 0
  manualAttendanceId.value = undefined
}
</script>

<style lang="scss" scoped>
.qr-face-verification-page {
  min-height: 100vh;
  background: var(--background-color, #f5f5f5);
  padding: 16px;
}

.page-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 24px;
  padding: 16px;
  background: var(--component-background, #ffffff);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.page-title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
  color: var(--text-color, #262626);
}

.page-content {
  max-width: 600px;
  margin: 0 auto;
}

.steps-container {
  margin-bottom: 32px;
  padding: 24px;
  background: var(--component-background, #ffffff);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.step-section {
  .scan-card,
  .verification-card {
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
  }

  .scan-tip,
  .verification-tip {
    margin-bottom: 24px;
  }

  .qr-scanner-container {
    margin: 24px 0;
  }

  .verification-info {
    padding: 16px;
    background: var(--background-color-light, #fafafa);
    border-radius: 8px;
    margin-bottom: 24px;

    p {
      margin: 0;
      font-size: 14px;
      color: var(--text-color, #262626);
    }
  }
}

// 响应式
@media (max-width: 768px) {
  .qr-face-verification-page {
    padding: 12px;
  }

  .page-header {
    padding: 12px;
  }

  .page-title {
    font-size: 18px;
  }

  .steps-container {
    padding: 16px;
  }
}
</style>
