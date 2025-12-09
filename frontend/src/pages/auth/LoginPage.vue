<template>
  <div class="login-container">
    <div class="login-card">
      <div class="login-header">
        <h1 class="login-title">教学资源管理系统</h1>
        <p class="login-subtitle">欢迎登录</p>
      </div>

      <a-form
        ref="formRef"
        :model="formState"
        :rules="rules"
        class="login-form"
        @finish="handleLogin"
      >
        <a-form-item name="loginIdentifier" class="form-item">
          <a-input
            v-model:value="formState.loginIdentifier"
            size="large"
            placeholder="邮箱/用户名/工号"
            @keyup.enter="handleEnterKey"
          >
            <template #prefix>
              <UserOutlined class="input-icon" />
            </template>
          </a-input>
        </a-form-item>

        <a-form-item name="password" class="form-item">
          <a-input-password
            v-model:value="formState.password"
            size="large"
            placeholder="密码"
            @keyup.enter="handleEnterKey"
          >
            <template #prefix>
              <LockOutlined class="input-icon" />
            </template>
          </a-input-password>
        </a-form-item>

        <a-form-item class="form-item">
          <a-button
            type="primary"
            html-type="submit"
            size="large"
            :loading="loading"
            :disabled="loading"
            block
            class="login-button"
          >
            {{ loading ? '登录中...' : '登录' }}
          </a-button>
        </a-form-item>
      </a-form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import { UserOutlined, LockOutlined } from '@ant-design/icons-vue'
import type { FormInstance, Rule } from 'ant-design-vue/es/form'
import { useAuth } from '@/composables/useAuth'

// 表单引用
const formRef = ref<FormInstance>()

// 表单状态
const formState = reactive<API.UserLoginModel>({
  loginIdentifier: '',
  password: ''
})

// 使用 useAuth 组合式函数
const { login, loading } = useAuth()

// 表单验证规则
const rules: Record<string, Rule[]> = {
  loginIdentifier: [
    {
      required: true,
      message: '请输入邮箱、用户名或工号',
      trigger: 'blur'
    }
  ],
  password: [
    {
      required: true,
      message: '请输入密码',
      trigger: 'blur'
    },
    {
      min: 6,
      message: '密码至少6个字符',
      trigger: 'blur'
    }
  ]
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
  formRef.value?.validate().then(() => {
    handleLogin()
  }).catch(() => {
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
  animation: fadeIn 0.5s ease-in-out;
}

.login-card {
  width: 100%;
  max-width: 400px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 10px 40px rgba(0, 0, 0, 0.1);
  padding: 40px;
  animation: slideUp 0.6s ease-out;
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.login-title {
  font-size: 24px;
  font-weight: 600;
  color: #1a1a1a;
  margin: 0 0 8px 0;
  animation: fadeInDown 0.8s ease-out;
}

.login-subtitle {
  font-size: 14px;
  color: #666;
  margin: 0;
  animation: fadeInDown 0.9s ease-out;
}

.login-form {
  margin-top: 24px;
}

.form-item {
  margin-bottom: 20px;
  animation: fadeInUp 1s ease-out;
}

.input-icon {
  color: #999;
}

.login-button {
  height: 44px;
  font-size: 16px;
  font-weight: 500;
  margin-top: 8px;
  transition: all 0.3s ease;
}

.login-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(24, 144, 255, 0.3);
}

.login-button:active:not(:disabled) {
  transform: translateY(0);
}

/* 动画定义 */
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

@keyframes slideUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInDown {
  from {
    opacity: 0;
    transform: translateY(-20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 - 移动端 */
@media (max-width: 768px) {
  .login-container {
    padding: 0;
    background: white;
  }

  .login-card {
    max-width: 100%;
    box-shadow: none;
    border-radius: 0;
    padding: 24px;
    min-height: 100vh;
    display: flex;
    flex-direction: column;
    justify-content: center;
    animation: fadeIn 0.5s ease-in-out;
  }

  .login-title {
    font-size: 20px;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .login-card {
    background: #1f1f1f;
  }

  .login-title {
    color: #ffffff;
  }

  .login-subtitle {
    color: #999;
  }

  .login-container {
    background: linear-gradient(135deg, #4a5568 0%, #2d3748 100%);
  }

  @media (max-width: 768px) {
    .login-container {
      background: #1f1f1f;
    }
  }
}
</style>
