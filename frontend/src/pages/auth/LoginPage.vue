<template>
  <div class="login-container">
    <!-- 背景装饰圆圈 -->
    <div class="bg-circles">
      <div class="circle circle-1"></div>
      <div class="circle circle-2"></div>
      <div class="circle circle-3"></div>
    </div>

    <!-- 动态装饰元素 -->
    <div class="decorative-elements">
      <div class="floating-card card-1">
        <FileTextOutlined class="card-icon" />
        <span class="card-text">资料管理</span>
      </div>
      <div class="floating-card card-2">
        <TeamOutlined class="card-icon" />
        <span class="card-text">协作共享</span>
      </div>
      <div class="floating-card card-3">
        <CloudUploadOutlined class="card-icon" />
        <span class="card-text">云端存储</span>
      </div>
      <div class="floating-card card-4">
        <SafetyOutlined class="card-icon" />
        <span class="card-text">安全可靠</span>
      </div>
    </div>

    <!-- 主卡片 -->
    <div class="main-card">
      <!-- 左侧展示区域 -->
      <div class="login-left">
        <div class="brand-section">
          <div class="logo-wrapper">
            <div class="logo-circle">
              <img src="@/assets/logo-origin.png" alt="Logo" class="logo-image" />
            </div>
          </div>
          <h1 class="brand-title">教学资源管理系统</h1>
          <p class="brand-subtitle">智能化教学资源管理平台</p>
        </div>
      </div>

      <!-- 右侧登录区域 -->
      <div class="login-right">
        <div class="login-content">
          <div class="login-header">
            <h2 class="login-title">欢迎回来</h2>
            <p class="login-subtitle">请登录您的账户</p>
          </div>

          <a-form ref="formRef" :model="formState" :rules="rules" class="login-form" @finish="handleLogin">
            <a-form-item name="loginIdentifier" class="form-item">
              <a-input v-model:value="formState.loginIdentifier" size="large" placeholder="邮箱/用户名/工号" @keyup.enter="handleEnterKey">
                <template #prefix>
                  <UserOutlined class="input-icon" />
                </template>
              </a-input>
            </a-form-item>

            <a-form-item name="password" class="form-item">
              <a-input-password v-model:value="formState.password" size="large" placeholder="密码" @keyup.enter="handleEnterKey">
                <template #prefix>
                  <LockOutlined class="input-icon" />
                </template>
              </a-input-password>
            </a-form-item>

            <a-form-item class="form-item">
              <a-button type="primary" html-type="submit" size="large" :loading="loading" :disabled="loading" block class="login-button">
                {{ loading ? '登录中...' : '登录' }}
              </a-button>
            </a-form-item>
          </a-form>

          <div class="login-footer">
            <span class="footer-text">首次使用？请联系管理员开通账号</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { UserOutlined, LockOutlined, FileTextOutlined, TeamOutlined, CloudUploadOutlined, SafetyOutlined } from '@ant-design/icons-vue'
import type { FormInstance, Rule } from 'ant-design-vue/es/form'
import { useAuth } from '@/composables/useAuth'

// 表单引用
const formRef = ref<FormInstance>()

// 表单状态
const formState = reactive<API.UserLoginModel>({
  loginIdentifier: '',
  password: '',
})

// 使用 useAuth 组合式函数
const { login, loading } = useAuth()

// 表单验证规则
const rules: Record<string, Rule[]> = {
  loginIdentifier: [
    {
      required: true,
      message: '请输入邮箱、用户名或工号',
      trigger: 'blur',
    },
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur',
    },
    {
      min: 6,
      message: '密码至少6个字符',
      trigger: 'blur',
    },
  ],
}

/**
 * 处理登录表单提交
 */
const handleLogin = async () => {
  try {
    await login(formState)
  } catch (error) {
    // 错误已在 useAuth 中处理
    console.error('Login failed:', error)
  }
}

/**
 * 处理 Enter 键提交
 */
const handleEnterKey = () => {
  formRef.value
    ?.validate()
    .then(() => {
      handleLogin()
    })
    .catch(() => {
      // 验证失败，不执行提交
    })
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  position: relative;
  overflow: hidden;
  animation: fadeIn 0.6s ease-in-out;
}

/* ========== 主卡片 ========== */
.main-card {
  width: 90%;
  max-width: 1100px;
  min-height: 600px;
  background: white;
  border-radius: 24px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  display: flex;
  overflow: hidden;
  position: relative;
  z-index: 10;
  animation: slideUp 0.8s ease-out;
}

/* ========== 左侧展示区域 ========== */
.login-left {
  flex: 1;
  background: linear-gradient(135deg, #1890ff 0%, #096dd9 100%);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  position: relative;
}

.brand-section {
  position: relative;
  z-index: 2;
  text-align: center;
  animation: fadeInLeft 0.8s ease-out;
}

.logo-wrapper {
  margin-bottom: 32px;
}

.logo-circle {
  width: 260px;
  height: 260px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  margin: 0 auto;
  animation: pulse 3s ease-in-out infinite;
  box-shadow: 0 12px 48px rgba(0, 0, 0, 0.25), 0 0 0 8px rgba(255, 255, 255, 0.1);
  border: 3px solid rgba(255, 255, 255, 0.3);
}

.logo-icon {
  font-size: 56px;
  color: white;
}

.logo-image {
  width: 240px;
  height: 240px;
  object-fit: contain;
}

.brand-title {
  font-size: 32px;
  font-weight: 700;
  color: white;
  margin: 0 0 16px 0;
  letter-spacing: 1px;
}

.brand-subtitle {
  font-size: 16px;
  color: rgba(255, 255, 255, 0.95);
  margin: 0;
  font-weight: 300;
}

/* 动态装饰卡片 - 在背景层 */
.decorative-elements {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  pointer-events: none;
  z-index: 1;
}

.floating-card {
  position: absolute;
  background: rgba(255, 255, 255, 0.15);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 12px;
  padding: 14px 22px;
  display: flex;
  align-items: center;
  gap: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.15);
}

.card-icon {
  font-size: 22px;
  color: white;
}

.card-text {
  color: white;
  font-size: 14px;
  font-weight: 500;
  white-space: nowrap;
}

.card-1 {
  top: 15%;
  left: 10%;
  animation: float 6s ease-in-out infinite;
}

.card-2 {
  top: 25%;
  right: 15%;
  animation: float 7s ease-in-out infinite 1s;
}

.card-3 {
  bottom: 30%;
  left: 15%;
  animation: float 8s ease-in-out infinite 2s;
}

.card-4 {
  bottom: 15%;
  right: 10%;
  animation: float 7s ease-in-out infinite 1.5s;
}

/* 背景装饰圆圈 */
.bg-circles {
  position: fixed;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  overflow: hidden;
  z-index: 0;
}

.circle {
  position: absolute;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.05);
  animation: rotate 20s linear infinite;
}

.circle-1 {
  width: 400px;
  height: 400px;
  top: -150px;
  left: -150px;
}

.circle-2 {
  width: 500px;
  height: 500px;
  bottom: -200px;
  right: -200px;
  animation-duration: 25s;
  animation-direction: reverse;
}

.circle-3 {
  width: 300px;
  height: 300px;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  animation-duration: 30s;
}

/* ========== 右侧登录区域 ========== */
.login-right {
  flex: 0 0 450px;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 50px;
}

.login-content {
  width: 100%;
  max-width: 360px;
}

.login-header {
  margin-bottom: 40px;
}

.login-title {
  font-size: 28px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
}

.login-form {
  margin-top: 32px;
}

.form-item {
  margin-bottom: 24px;
}

.input-icon {
  color: #999;
}

.login-button {
  height: 48px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 6px 20px rgba(24, 144, 255, 0.4);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

.login-footer {
  margin-top: 24px;
  text-align: center;
}

.footer-text {
  font-size: 13px;
  color: #999;
}

/* ========== 动画定义 ========== */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes fadeInLeft {
  from {
    opacity: 0;
    transform: translateX(-30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes fadeInRight {
  from {
    opacity: 0;
    transform: translateX(30px);
  }
  to {
    opacity: 1;
    transform: translateX(0);
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(40px) scale(0.95);
  }
  to {
    opacity: 1;
    transform: translateY(0) scale(1);
  }
}

@keyframes pulse {
  0%,
  100% {
    transform: scale(1);
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  }
  50% {
    transform: scale(1.05);
    box-shadow: 0 12px 48px rgba(0, 0, 0, 0.15);
  }
}

@keyframes float {
  0%,
  100% {
    transform: translateY(0) translateX(0);
  }
  25% {
    transform: translateY(-20px) translateX(10px);
  }
  50% {
    transform: translateY(-10px) translateX(-10px);
  }
  75% {
    transform: translateY(-15px) translateX(5px);
  }
}

@keyframes rotate {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* ========== 响应式设计 ========== */
@media (max-width: 1024px) {
  .main-card {
    width: 95%;
    max-width: 900px;
  }

  .login-left {
    padding: 40px 30px;
  }

  .login-right {
    flex: 0 0 380px;
    padding: 50px 40px;
  }
}

@media (max-width: 768px) {
  .login-container {
    padding: 20px;
  }

  .main-card {
    width: 100%;
    flex-direction: column;
    min-height: auto;
    border-radius: 16px;
  }

  .login-left {
    flex: 0 0 auto;
    padding: 40px 24px;
  }

  .logo-circle {
    width: 80px;
    height: 80px;
  }

  .logo-icon {
    font-size: 40px;
  }

  .brand-title {
    font-size: 24px;
  }

  .brand-subtitle {
    font-size: 14px;
  }

  .floating-card {
    display: none;
  }

  .login-right {
    flex: 1;
    padding: 40px 24px;
  }

  .login-content {
    max-width: 100%;
  }

  .login-title {
    font-size: 24px;
  }
}

/* ========== 暗色主题适配 ========== */
@media (prefers-color-scheme: dark) {
  .login-container {
    background: linear-gradient(135deg, #177ddc 0%, #0958d9 100%);
  }

  .main-card {
    background: #1f1f1f;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
  }

  .login-right {
    background: #1f1f1f;
  }

  .login-title {
    color: #ffffff;
  }

  .login-subtitle {
    color: #8c8c8c;
  }

  .footer-text {
    color: #595959;
  }

  .login-left {
    background: linear-gradient(135deg, #177ddc 0%, #0958d9 100%);
  }
}
</style>
