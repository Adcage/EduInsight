<template>
  <div class="profile-page">
    <a-page-header title="个人资料" sub-title="查看和管理您的账户信息" />

    <div class="content-container">
      <!-- 骨架屏加载状态 - Requirements 1.1 -->
      <a-card v-if="loading" class="profile-card">
        <div class="avatar-section">
          <a-skeleton-avatar :size="120" shape="circle" />
          <div class="user-basic-info">
            <a-skeleton :loading="true" active :paragraph="{ rows: 1, width: '150px' }" :title="{ width: '200px' }" />
          </div>
        </div>
        <a-divider />
        <a-skeleton :loading="true" active :paragraph="{ rows: 6 }" />
        <a-divider />
        <a-skeleton :loading="true" active :paragraph="{ rows: 1 }" />
      </a-card>

      <a-card v-else class="profile-card">
        <!-- Avatar Section -->
        <div class="avatar-section">
          <AvatarUpload
            :current-avatar="userInfo?.avatar"
            :size="120"
            @upload-success="handleAvatarUploadSuccess"
            @upload-error="handleAvatarUploadError"
          />
          <div class="user-basic-info">
            <h2 class="username">{{ userInfo?.realName || userInfo?.username }}</h2>
            <a-tag :color="roleTagColor">{{ formatRoleDisplay(userInfo?.role || '') }}</a-tag>
          </div>
        </div>

        <a-divider />

        <!-- Profile Info Section -->
        <div class="profile-info-section">
          <div class="section-header">
            <h3>基本信息</h3>
            <a-button v-if="!isEditing" type="primary" ghost @click="startEditing">
              <template #icon><EditOutlined /></template>
              编辑
            </a-button>
            <a-space v-else>
              <a-button @click="cancelEditing">取消</a-button>
              <a-button type="primary" :loading="saving" @click="saveProfile">保存</a-button>
            </a-space>
          </div>

          <!-- Display Mode -->
          <a-descriptions v-if="!isEditing" :column="2" bordered>
            <a-descriptions-item label="用户名">{{ userInfo?.username }}</a-descriptions-item>
            <a-descriptions-item label="工号/学号">{{ userInfo?.userCode }}</a-descriptions-item>
            <a-descriptions-item label="真实姓名">{{ userInfo?.realName }}</a-descriptions-item>
            <a-descriptions-item label="角色">{{ formatRoleDisplay(userInfo?.role || '') }}</a-descriptions-item>
            <a-descriptions-item label="邮箱">{{ userInfo?.email }}</a-descriptions-item>
            <a-descriptions-item label="手机号">{{ userInfo?.phone || '未设置' }}</a-descriptions-item>
            <a-descriptions-item label="注册时间">{{ formatDateTime(userInfo?.createdAt) }}</a-descriptions-item>
            <a-descriptions-item label="最后登录">{{ formatDateTime(userInfo?.lastLoginTime) || '从未登录' }}</a-descriptions-item>
          </a-descriptions>

          <!-- Edit Mode -->
          <a-form v-else ref="editFormRef" :model="editForm" :rules="editFormRules" layout="vertical" class="edit-form">
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="用户名">
                  <a-input :value="userInfo?.username" disabled />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="工号/学号">
                  <a-input :value="userInfo?.userCode" disabled />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="真实姓名" name="realName">
                  <a-input v-model:value="editForm.realName" placeholder="请输入真实姓名" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="角色">
                  <a-input :value="formatRoleDisplay(userInfo?.role || '')" disabled />
                </a-form-item>
              </a-col>
            </a-row>
            <a-row :gutter="24">
              <a-col :span="12">
                <a-form-item label="邮箱" name="email">
                  <a-input v-model:value="editForm.email" placeholder="请输入邮箱地址" />
                </a-form-item>
              </a-col>
              <a-col :span="12">
                <a-form-item label="手机号" name="phone">
                  <a-input v-model:value="editForm.phone" placeholder="请输入手机号码" />
                </a-form-item>
              </a-col>
            </a-row>
          </a-form>
        </div>

        <a-divider />

        <!-- Security Section -->
        <div class="security-section">
          <div class="section-header">
            <h3>账户安全</h3>
          </div>
          <a-button type="default" @click="showPasswordModal">
            <template #icon><LockOutlined /></template>
            修改密码
          </a-button>
        </div>
      </a-card>
    </div>

    <!-- Password Change Modal -->
    <PasswordChangeForm v-model:visible="passwordModalVisible" @success="handlePasswordChangeSuccess" />
  </div>
</template>

<script setup lang="ts">
/**
 * 个人资料页面
 * 功能：展示和管理用户个人信息，支持编辑、修改密码、上传头像
 * Requirements: 5.1, 5.2, 5.3, 5.4, 6.1, 6.2, 6.3, 6.4, 6.5, 7.1
 */
import { ref, reactive, computed, onMounted } from 'vue'
import { EditOutlined, LockOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import type { FormInstance, Rule } from 'ant-design-vue/es/form'
import dayjs from 'dayjs'
import AvatarUpload from '@/components/profile/AvatarUpload.vue'
import PasswordChangeForm from '@/components/profile/PasswordChangeForm.vue'
import { useAuthStore } from '@/stores/auth'
import { userApiIntUserIdPut } from '@/api/userController'
import { validateEmail, validatePhone, formatRoleDisplay } from '@/utils/profileValidation'

// Store
const authStore = useAuthStore()

// State
const loading = ref(false)
const saving = ref(false)
const isEditing = ref(false)
const passwordModalVisible = ref(false)
const editFormRef = ref<FormInstance>()

// User info from store
const userInfo = computed(() => authStore.user)

// Edit form state
const editForm = reactive({
  realName: '',
  email: '',
  phone: '',
})

// Original values for cancel restoration
const originalValues = ref({
  realName: '',
  email: '',
  phone: '',
})

// Role tag color
const roleTagColor = computed(() => {
  const role = userInfo.value?.role?.toLowerCase()
  switch (role) {
    case 'admin':
      return 'red'
    case 'teacher':
      return 'blue'
    case 'student':
      return 'green'
    default:
      return 'default'
  }
})

// Form validation rules
const editFormRules: Record<string, Rule[]> = {
  realName: [{ required: true, message: '请输入真实姓名', trigger: 'blur' }],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    {
      validator: async (_rule: Rule, value: string) => {
        const result = validateEmail(value)
        if (!result.valid) {
          return Promise.reject(result.error)
        }
        return Promise.resolve()
      },
      trigger: 'blur',
    },
  ],
  phone: [
    {
      validator: async (_rule: Rule, value: string) => {
        const result = validatePhone(value)
        if (!result.valid) {
          return Promise.reject(result.error)
        }
        return Promise.resolve()
      },
      trigger: 'blur',
    },
  ],
}

/**
 * Format date time for display
 */
const formatDateTime = (dateStr: string | null | undefined): string => {
  if (!dateStr) return ''
  return dayjs(dateStr).format('YYYY-MM-DD HH:mm:ss')
}

/**
 * Load user info
 */
const loadUserInfo = async () => {
  loading.value = true
  try {
    await authStore.fetchCurrentUser()
  } catch (error: any) {
    message.error(error.message || '获取用户信息失败')
  } finally {
    loading.value = false
  }
}

/**
 * Start editing mode
 */
const startEditing = () => {
  // Store original values for cancel restoration
  originalValues.value = {
    realName: userInfo.value?.realName || '',
    email: userInfo.value?.email || '',
    phone: userInfo.value?.phone || '',
  }
  // Initialize edit form with current values
  editForm.realName = userInfo.value?.realName || ''
  editForm.email = userInfo.value?.email || ''
  editForm.phone = userInfo.value?.phone || ''
  isEditing.value = true
}

/**
 * Cancel editing and restore original values
 */
const cancelEditing = () => {
  // Restore original values
  editForm.realName = originalValues.value.realName
  editForm.email = originalValues.value.email
  editForm.phone = originalValues.value.phone
  isEditing.value = false
  editFormRef.value?.resetFields()
}

/**
 * Save profile changes
 */
const saveProfile = async () => {
  try {
    await editFormRef.value?.validate()

    if (!userInfo.value?.id) {
      message.error('用户信息不完整')
      return
    }

    saving.value = true

    await userApiIntUserIdPut(
      { userId: userInfo.value.id },
      {
        realName: editForm.realName,
        email: editForm.email,
        phone: editForm.phone || null,
      },
    )

    // Refresh user info
    await authStore.fetchCurrentUser()

    message.success('个人信息更新成功')
    isEditing.value = false
  } catch (error: any) {
    if (error.errorFields) {
      // Form validation error
      return
    }
    message.error(error.message || '更新失败')
  } finally {
    saving.value = false
  }
}

/**
 * Show password change modal
 */
const showPasswordModal = () => {
  passwordModalVisible.value = true
}

/**
 * Handle password change success
 */
const handlePasswordChangeSuccess = () => {
  message.success('密码修改成功，请使用新密码重新登录')
}

/**
 * Handle avatar upload success
 */
const handleAvatarUploadSuccess = async (url: string) => {
  if (!userInfo.value?.id) return

  try {
    await userApiIntUserIdPut({ userId: userInfo.value.id }, { avatar: url })
    await authStore.fetchCurrentUser()
    message.success('头像更新成功')
  } catch (error: any) {
    message.error(error.message || '头像更新失败')
  }
}

/**
 * Handle avatar upload error
 */
const handleAvatarUploadError = (error: string) => {
  message.error(error)
}

// Load user info on mount
onMounted(() => {
  loadUserInfo()
})
</script>

<style scoped>
.profile-page {
  min-height: 100vh;
  padding: 0;
  margin: 0;
  background-color: #f5f5f5;
}

.content-container {
  padding: 16px 24px;
  max-width: 900px;
  margin: 0 auto;
}

.profile-card {
  border-radius: 8px;
}

.avatar-section {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 16px 0;
}

.user-basic-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.username {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
}

.profile-info-section {
  padding: 8px 0;
}

.edit-form {
  max-width: 100%;
}

.security-section {
  padding: 8px 0;
}

:deep(.ant-descriptions-item-label) {
  width: 120px;
  font-weight: 500;
}
</style>
