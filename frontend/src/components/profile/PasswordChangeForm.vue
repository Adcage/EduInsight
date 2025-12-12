<template>
  <a-modal :confirm-loading="loading" :open="visible" title="修改密码" @cancel="handleCancel" @ok="handleSubmit">
    <a-form ref="formRef" :model="formState" :rules="rules" autocomplete="off" layout="vertical">
      <a-form-item label="当前密码" name="currentPassword">
        <a-input-password v-model:value="formState.currentPassword" allow-clear placeholder="请输入当前密码"/>
      </a-form-item>

      <a-form-item label="新密码" name="newPassword">
        <a-input-password v-model:value="formState.newPassword" allow-clear placeholder="请输入新密码（至少6位）"
                          @input="updatePasswordStrength"/>
        <!-- Password strength indicator -->
        <div v-if="formState.newPassword" class="password-strength">
          <span class="strength-label">密码强度：</span>
          <a-progress
              :percent="passwordStrength.percent"
              :show-info="false"
              :status="passwordStrength.status"
              :stroke-color="passwordStrength.color"
              size="small"
          />
          <span :style="{ color: passwordStrength.color }" class="strength-text">
            {{ passwordStrength.text }}
          </span>
        </div>
      </a-form-item>

      <a-form-item label="确认新密码" name="confirmPassword">
        <a-input-password v-model:value="formState.confirmPassword" allow-clear placeholder="请再次输入新密码"/>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script lang="ts" setup>
import {reactive, ref, watch} from 'vue'
import type {FormInstance, Rule} from 'ant-design-vue/es/form'
import {message} from 'ant-design-vue'
import {authApiChangePasswordPost} from '@/api/authController'
import {calculatePasswordStrength, type PasswordStrengthResult, validatePasswordMatch} from '@/utils/passwordValidation'

interface Props {
  visible: boolean
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  success: []
}>()

// Form state
const formRef = ref<FormInstance>()
const loading = ref(false)

const formState = reactive({
  currentPassword: '',
  newPassword: '',
  confirmPassword: '',
})

// Password strength state
const passwordStrength = ref<PasswordStrengthResult>({
  score: 0,
  percent: 0,
  text: '',
  color: '#d9d9d9',
  status: 'normal',
})

/**
 * Update password strength indicator
 */
const updatePasswordStrength = () => {
  passwordStrength.value = calculatePasswordStrength(formState.newPassword)
}

/**
 * Custom validator for confirm password
 */
const validateConfirmPassword = async (_rule: Rule, value: string) => {
  const result = validatePasswordMatch(formState.newPassword, value)
  if (!result.valid) {
    return Promise.reject(result.error)
  }
  return Promise.resolve()
}

// Form validation rules
const rules: Record<string, Rule[]> = {
  currentPassword: [{required: true, message: '请输入当前密码', trigger: 'blur'}],
  newPassword: [
    {required: true, message: '请输入新密码', trigger: 'blur'},
    {min: 6, message: '密码长度不能少于6位', trigger: 'blur'},
  ],
  confirmPassword: [
    {required: true, message: '请确认新密码', trigger: 'blur'},
    {validator: validateConfirmPassword, trigger: 'blur'},
  ],
}

/**
 * Reset form state
 */
const resetForm = () => {
  formState.currentPassword = ''
  formState.newPassword = ''
  formState.confirmPassword = ''
  passwordStrength.value = {
    score: 0,
    percent: 0,
    text: '',
    color: '#d9d9d9',
    status: 'normal',
  }
  formRef.value?.resetFields()
}

/**
 * Handle cancel
 */
const handleCancel = () => {
  resetForm()
  emit('update:visible', false)
}

/**
 * Handle form submission
 */
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    loading.value = true

    await authApiChangePasswordPost({
      oldPassword: formState.currentPassword,
      newPassword: formState.newPassword,
      confirmPassword: formState.confirmPassword,
    })

    message.success('密码修改成功')
    resetForm()
    emit('success')
    emit('update:visible', false)
  } catch (error: any) {
    if (error.errorFields) {
      // Form validation error
      return
    }
    // API error
    message.error(error.message || '密码修改失败')
  } finally {
    loading.value = false
  }
}

// Reset form when modal closes
watch(
    () => props.visible,
    (newVal) => {
      if (!newVal) {
        resetForm()
      }
    },
)
</script>

<style scoped>
.password-strength {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 8px;
}

.strength-label {
  font-size: 12px;
  color: #666;
  white-space: nowrap;
}

.strength-text {
  font-size: 12px;
  font-weight: 500;
  white-space: nowrap;
}

:deep(.ant-progress) {
  flex: 1;
  max-width: 120px;
}
</style>
