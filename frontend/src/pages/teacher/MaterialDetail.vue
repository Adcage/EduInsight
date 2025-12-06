<template>
  <div class="material-detail">
    <a-page-header
      :title="material?.title || '资料详情'"
      @back="handleBack"
    >
      <template #extra>
        <a-space>
          <a-button 
            v-if="canPreview" 
            type="primary" 
            @click="togglePreview"
          >
            <template #icon><EyeOutlined /></template>
            预览
          </a-button>
          <a-button @click="handleDownload">
            <template #icon><DownloadOutlined /></template>
            下载
          </a-button>
          <a-button v-if="canEdit" @click="handleEdit">
            <template #icon><EditOutlined /></template>
            编辑
          </a-button>
          <a-button v-if="canDelete" danger @click="showDeleteConfirm">
            <template #icon><DeleteOutlined /></template>
            删除
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-container">
      <a-spin :spinning="loading">
        <!-- 资料信息卡片 -->
        <a-card :bordered="false" class="info-card">
          <a-descriptions title="资料信息" :column="2" bordered>
            <a-descriptions-item label="文件名">
              {{ material?.fileName }}
            </a-descriptions-item>
            
            <a-descriptions-item label="文件大小">
              {{ formatFileSize(material?.fileSize) }}
            </a-descriptions-item>
            
            <a-descriptions-item label="文件类型">
              <a-tag :color="getFileTypeColor(material?.fileType)">
                {{ getFileTypeText(material?.fileType) }}
              </a-tag>
            </a-descriptions-item>
            
            <a-descriptions-item label="分类">
              {{ material?.category?.name || '未分类' }}
            </a-descriptions-item>
            
            <a-descriptions-item label="上传者">
              {{ material?.uploader?.realName || '未知' }}
            </a-descriptions-item>
            
            <a-descriptions-item label="上传时间">
              {{ formatDateTime(material?.createdAt) }}
            </a-descriptions-item>
            
            <a-descriptions-item label="下载次数">
              <a-statistic
                :value="material?.downloadCount || 0"
                :value-style="{ fontSize: '14px' }"
              >
                <template #prefix>
                  <DownloadOutlined />
                </template>
              </a-statistic>
            </a-descriptions-item>
            
            <a-descriptions-item label="浏览次数">
              <a-statistic
                :value="material?.viewCount || 0"
                :value-style="{ fontSize: '14px' }"
              >
                <template #prefix>
                  <EyeOutlined />
                </template>
              </a-statistic>
            </a-descriptions-item>
            
            <a-descriptions-item label="标签" :span="2">
              <a-space v-if="material?.tags && material.tags.length > 0">
                <a-tag
                  v-for="tag in material.tags"
                  :key="tag.id"
                  color="blue"
                >
                  {{ tag.name }}
                </a-tag>
              </a-space>
              <span v-else class="text-muted">暂无标签</span>
            </a-descriptions-item>
            
            <a-descriptions-item label="描述" :span="2">
              <div class="description-content">
                {{ material?.description || '暂无描述' }}
              </div>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

      </a-spin>
    </div>

    <!-- 预览模态框 -->
    <a-modal
      v-model:open="previewModalVisible"
      :title="`预览 - ${material?.fileName}`"
      width="85%"
      :footer="null"
      :destroyOnClose="true"
      centered
      :bodyStyle="{ height: '70vh', padding: 0, maxHeight: '70vh' }"
      :wrapStyle="{ maxHeight: '90vh' }"
    >
      <FilePreview
        v-if="previewUrl"
        :file-url="previewUrl"
        :file-type="material?.fileType"
        :file-name="material?.fileName"
        @download="handleDownload"
        @back="previewModalVisible = false"
      />
    </a-modal>

    <!-- 编辑资料对话框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑资料"
      width="600px"
      :confirm-loading="editLoading"
      @ok="handleEditSubmit"
      @cancel="handleEditCancel"
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 19 }"
      >
        <a-form-item
          label="资料标题"
          name="title"
          :rules="[{ required: true, message: '请输入资料标题' }]"
        >
          <a-input
            v-model:value="editForm.title"
            placeholder="请输入资料标题"
            :maxlength="100"
          />
        </a-form-item>

        <a-form-item label="资料描述" name="description">
          <a-textarea
            v-model:value="editForm.description"
            placeholder="请输入资料描述"
            :rows="4"
            :maxlength="500"
            show-count
          />
        </a-form-item>

        <a-form-item label="分类" name="categoryId">
          <a-select
            v-model:value="editForm.categoryId"
            placeholder="请选择分类"
            allow-clear
          >
            <a-select-option
              v-for="category in categories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="标签" name="tags">
          <a-select
            v-model:value="editForm.tags"
            mode="tags"
            placeholder="请输入标签（按回车添加）"
            :max-tag-count="5"
          >
          </a-select>
        </a-form-item>

        <a-form-item label="文件信息">
          <a-space direction="vertical" :size="4">
            <div>
              <span class="info-label">文件名：</span>
              <span>{{ material?.fileName }}</span>
            </div>
            <div>
              <span class="info-label">文件类型：</span>
              <a-tag :color="getFileTypeColor(material?.fileType)">
                {{ getFileTypeText(material?.fileType) }}
              </a-tag>
            </div>
            <div>
              <span class="info-label">文件大小：</span>
              <span>{{ formatFileSize(material?.fileSize) }}</span>
            </div>
          </a-space>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message, Modal } from 'ant-design-vue'
import {
  DownloadOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  FileOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import {
  materialApiIntMaterialIdDownloadGet
} from '@/api/materialController'
import { useMaterialStore } from '@/stores/material'
import { useCategoryStore } from '@/stores/category'
import FilePreview from '@/components/materials/preview/FilePreview.vue'

const route = useRoute()
const router = useRouter()

// Stores
const materialStore = useMaterialStore()
const categoryStore = useCategoryStore()

// 状态
const previewModalVisible = ref(false)
const editModalVisible = ref(false)
const editLoading = ref(false)
const editFormRef = ref()
const editForm = ref({
  title: '',
  description: '',
  categoryId: null as number | null,
  tags: [] as string[]
})
const currentUserId = ref<number | null>(null)

// 资料ID
const materialId = computed(() => {
  return Number(route.params.id)
})

// 从store获取状态
const material = computed(() => materialStore.currentMaterial)
const loading = computed(() => materialStore.loading)
const categories = computed(() => categoryStore.flatCategories)

// 预览URL
const previewUrl = computed(() => {
  if (!material.value) return ''
  // 构建预览URL - 使用预览接口（不会触发下载）
  const baseUrl = 'http://localhost:5030'
  return `${baseUrl}/api/v1/materials/${material.value.id}/preview`
})

// 是否可以预览
const canPreview = computed(() => {
  if (!material.value) return false
  // PDF和图片支持预览
  return material.value.fileType === 'pdf' || material.value.fileType === 'image'
})

// 打开预览模态框
const togglePreview = () => {
  previewModalVisible.value = true
}

// 权限判断
const canEdit = computed(() => {
  if (!material.value || !currentUserId.value) return false
  // 只有上传者本人可以编辑
  return material.value.uploaderId === currentUserId.value
})

const canDelete = computed(() => {
  if (!material.value || !currentUserId.value) return false
  // 只有上传者本人可以删除
  return material.value.uploaderId === currentUserId.value
})

// 文件类型颜色映射
const fileTypeColorMap: Record<string, string> = {
  pdf: 'red',
  doc: 'blue',
  ppt: 'orange',
  xls: 'green',
  image: 'purple',
  video: 'cyan',
  archive: 'geekblue',
  text: 'default'
}

// 文件类型文本映射
const fileTypeTextMap: Record<string, string> = {
  pdf: 'PDF',
  doc: 'Word',
  ppt: 'PPT',
  xls: 'Excel',
  text: '文本',
  image: '图片',
  archive: '压缩包',
  video: '视频',
  other: '其他'
}

// 获取文件类型颜色
const getFileTypeColor = (type?: string): string => {
  return fileTypeColorMap[type || ''] || 'default'
}

// 获取文件类型文本
const getFileTypeText = (type?: string): string => {
  return fileTypeTextMap[type || ''] || '其他'
}

// 格式化文件大小
const formatFileSize = (bytes?: number): string => {
  if (!bytes) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

// 格式化日期时间
const formatDateTime = (date?: string): string => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

// 加载资料详情
const loadMaterialDetail = async () => {
  try {
    await materialStore.fetchMaterialDetail(materialId.value)
    
    // 检查是否需要自动打开预览
    if (route.query.preview === 'true') {
      previewModalVisible.value = true
    }
  } catch (error: any) {
    console.error('加载资料详情失败:', error)
    message.error(error.message || '加载资料详情失败')
  }
}

// 下载
const handleDownload = async () => {
  if (!material.value) return
  
  const loadingMsg = message.loading('正在下载...', 0)
  try {
    const response = await materialApiIntMaterialIdDownloadGet({
      materialId: materialId.value
    }, {
      responseType: 'blob'
    })
    
    // 创建下载链接
    const blob = new Blob([response])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', material.value.fileName)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()
    
    // 清理
    setTimeout(() => {
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    }, 100)
    
    loadingMsg()
    message.success('下载成功')
  } catch (error: any) {
    loadingMsg()
    console.error('下载失败:', error)
    message.error(error.message || '下载失败')
  }
}

// 编辑
const handleEdit = () => {
  if (!material.value) return
  
  // 填充编辑表单
  editForm.value = {
    title: material.value.title,
    description: material.value.description || '',
    categoryId: material.value.category?.id || null,
    tags: material.value.tags?.map((tag: any) => tag.name) || []
  }
  
  editModalVisible.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  try {
    // 验证表单
    await editFormRef.value?.validate()
    
    editLoading.value = true
    
    // 调用store更新方法
    await materialStore.updateMaterial(materialId.value, {
      title: editForm.value.title,
      description: editForm.value.description,
      categoryId: editForm.value.categoryId,
      tags: editForm.value.tags
    })
    
    message.success('资料更新成功')
    editModalVisible.value = false
  } catch (error: any) {
    if (error.errorFields) {
      // 表单验证错误
      return
    }
    message.error(error.message || '更新失败')
  } finally {
    editLoading.value = false
  }
}

// 取消编辑
const handleEditCancel = () => {
  editFormRef.value?.resetFields()
  editModalVisible.value = false
}

// 加载分类列表
const loadCategories = async () => {
  try {
    await categoryStore.fetchCategories()
  } catch (error: any) {
    console.error('加载分类失败:', error)
  }
}

// 获取当前用户ID
const loadCurrentUser = () => {
  // 从localStorage或其他地方获取当前用户信息
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      const user = JSON.parse(userStr)
      currentUserId.value = user.id
    } catch (e) {
      console.error('解析用户信息失败:', e)
    }
  }
}

// 删除确认
const showDeleteConfirm = () => {
  Modal.confirm({
    title: '确认删除',
    content: '确定要删除这个资料吗？删除后无法恢复。',
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk: handleDelete
  })
}

// 删除
const handleDelete = async () => {
  try {
    await materialStore.deleteMaterial(materialId.value)
    
    message.success('删除成功')
    router.push('/teacher/materials')
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

// 返回
const handleBack = () => {
  router.back()
}

// 初始化
onMounted(() => {
  loadCurrentUser()
  loadMaterialDetail()
  loadCategories()
})
</script>

<style scoped>
.material-detail .content-container {
  padding: 16px;
}

.material-detail .info-card {
  margin-bottom: 16px;
}

.material-detail .description-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.material-detail .text-muted {
  color: rgba(0, 0, 0, 0.45);
}

.material-detail .preview-modal-content {
  min-height: 400px;
  display: flex;
  justify-content: center;
  align-items: center;
}

.material-detail .pdf-preview-modal,
.material-detail .image-preview-modal {
  width: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.material-detail .image-preview-modal {
  padding: 20px;
  background: #f5f5f5;
  border-radius: 8px;
}

.material-detail .image-preview-modal img {
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.info-label {
  color: rgba(0, 0, 0, 0.65);
  font-weight: 500;
  margin-right: 8px;
}
</style>
