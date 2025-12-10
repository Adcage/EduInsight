<template>
  <div class="avatar-upload-container">
    <div class="avatar-wrapper" @click="triggerFileInput">
      <!-- Current avatar display -->
      <a-avatar v-if="previewUrl || currentAvatar" :src="previewUrl || currentAvatar" :size="size" class="avatar-image" />
      <!-- Default avatar placeholder -->
      <a-avatar v-else :size="size" class="avatar-placeholder">
        <template #icon>
          <UserOutlined />
        </template>
      </a-avatar>

      <!-- Upload overlay -->
      <div class="upload-overlay">
        <CameraOutlined class="camera-icon" />
        <span class="upload-text">更换头像</span>
      </div>
    </div>

    <!-- Hidden file input -->
    <input ref="fileInputRef" type="file" accept="image/jpeg,image/png,image/gif" class="hidden-input" @change="handleFileSelect" />

    <!-- Preview modal -->
    <a-modal v-model:open="previewModalVisible" title="预览头像" :footer="null" @cancel="handleCancelPreview">
      <div class="preview-content">
        <img v-if="previewUrl" :src="previewUrl" alt="头像预览" class="preview-image" />
        <div class="preview-actions">
          <a-space>
            <a-button @click="handleCancelPreview">取消</a-button>
            <a-button type="primary" :loading="uploading" @click="handleConfirmUpload"> 确认上传 </a-button>
          </a-space>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { UserOutlined, CameraOutlined } from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import { validateAvatarFile, type AvatarValidationResult } from '@/utils/avatarValidation'

interface Props {
  currentAvatar?: string | null
  maxSize?: number // Max file size in bytes, default 2MB
  size?: number | 'small' | 'default' | 'large'
}

const props = withDefaults(defineProps<Props>(), {
  currentAvatar: null,
  maxSize: 2 * 1024 * 1024, // 2MB
  size: 100,
})

const emit = defineEmits<{
  'upload-success': [url: string]
  'upload-error': [error: string]
}>()

// Component state
const fileInputRef = ref<HTMLInputElement | null>(null)
const selectedFile = ref<File | null>(null)
const previewUrl = ref<string | null>(null)
const previewModalVisible = ref(false)
const uploading = ref(false)

/**
 * Trigger file input click
 */
const triggerFileInput = () => {
  fileInputRef.value?.click()
}

/**
 * Handle file selection
 */
const handleFileSelect = (event: Event) => {
  const input = event.target as HTMLInputElement
  const file = input.files?.[0]

  if (!file) return

  // Validate file
  const validation = validateAvatarFile(file, props.maxSize)

  if (!validation.valid) {
    message.error(validation.error || '文件验证失败')
    emit('upload-error', validation.error || '文件验证失败')
    // Reset input
    input.value = ''
    return
  }

  // Store selected file and create preview
  selectedFile.value = file
  previewUrl.value = URL.createObjectURL(file)
  previewModalVisible.value = true

  // Reset input for re-selection
  input.value = ''
}

/**
 * Cancel preview and reset state
 */
const handleCancelPreview = () => {
  if (previewUrl.value) {
    URL.revokeObjectURL(previewUrl.value)
  }
  previewUrl.value = null
  selectedFile.value = null
  previewModalVisible.value = false
}

/**
 * Confirm and upload avatar
 */
const handleConfirmUpload = async () => {
  if (!selectedFile.value) return

  uploading.value = true

  try {
    // Create FormData for upload
    const formData = new FormData()
    formData.append('avatar', selectedFile.value)

    // TODO: Replace with actual API call when backend endpoint is available
    // For now, simulate upload success with the preview URL
    // In production, this would call an API like:
    // const response = await uploadAvatarApi(formData)
    // const newAvatarUrl = response.data.url

    // Simulate API delay
    await new Promise((resolve) => setTimeout(resolve, 500))

    // Use the preview URL as the new avatar (in production, use API response)
    const newAvatarUrl = previewUrl.value!

    message.success('头像上传成功')
    emit('upload-success', newAvatarUrl)

    // Close modal but keep preview URL for display
    previewModalVisible.value = false
    selectedFile.value = null
  } catch (error: any) {
    const errorMessage = error.message || '头像上传失败'
    message.error(errorMessage)
    emit('upload-error', errorMessage)

    // Reset preview on error
    if (previewUrl.value) {
      URL.revokeObjectURL(previewUrl.value)
    }
    previewUrl.value = null
  } finally {
    uploading.value = false
  }
}
</script>

<style scoped>
.avatar-upload-container {
  display: inline-block;
}

.avatar-wrapper {
  position: relative;
  cursor: pointer;
  border-radius: 50%;
  overflow: hidden;
}

.avatar-image,
.avatar-placeholder {
  display: block;
}

.avatar-placeholder {
  background-color: #f0f0f0;
  color: #999;
}

.upload-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
  border-radius: 50%;
}

.avatar-wrapper:hover .upload-overlay {
  opacity: 1;
}

.camera-icon {
  font-size: 24px;
  color: white;
  margin-bottom: 4px;
}

.upload-text {
  font-size: 12px;
  color: white;
}

.hidden-input {
  display: none;
}

.preview-content {
  text-align: center;
}

.preview-image {
  max-width: 100%;
  max-height: 300px;
  border-radius: 8px;
  margin-bottom: 16px;
}

.preview-actions {
  margin-top: 16px;
}
</style>
