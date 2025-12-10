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
            <template #icon>
              <EyeOutlined/>
            </template>
            预览
          </a-button>
          <a-button @click="handleDownload">
            <template #icon>
              <DownloadOutlined/>
            </template>
            下载
          </a-button>
          <a-button v-if="canEdit" @click="handleEdit">
            <template #icon>
              <EditOutlined/>
            </template>
            编辑
          </a-button>
          <a-button v-if="canDelete" danger @click="showDeleteConfirm">
            <template #icon>
              <DeleteOutlined/>
            </template>
            删除
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-container">
      <a-spin :spinning="loading">
        <!-- 资料信息卡片 -->
        <a-card :bordered="false" class="info-card">
          <a-descriptions :column="2" bordered title="资料信息">
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
              <span v-if="material?.categoryName">
                {{ material.categoryName }}
                <a-tag v-if="material?.autoClassified" color="purple" size="small" style="margin-left: 4px">
                  <RobotOutlined/> 智能分类
                </a-tag>
              </span>
              <span v-else class="text-muted">未分类</span>
            </a-descriptions-item>

            <a-descriptions-item label="上传者">
              {{ material?.uploaderName || '未知' }}
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
                  <DownloadOutlined/>
                </template>
              </a-statistic>
            </a-descriptions-item>

            <a-descriptions-item label="浏览次数">
              <a-statistic
                  :value="material?.viewCount || 0"
                  :value-style="{ fontSize: '14px' }"
              >
                <template #prefix>
                  <EyeOutlined/>
                </template>
              </a-statistic>
            </a-descriptions-item>

            <a-descriptions-item :span="2" label="标签">
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

            <a-descriptions-item :span="2" label="描述">
              <div class="description-content">
                {{ material?.description || '暂无描述' }}
              </div>
            </a-descriptions-item>
          </a-descriptions>
        </a-card>

        <!-- 智能分析卡片 -->
        <a-card :bordered="false" class="info-card" style="margin-top: 16px">
          <template #title>
            <div style="display: flex; align-items: center; gap: 8px">
              <RobotOutlined/>
              <span>智能分析</span>
            </div>
          </template>
          <template #extra>
            <a-button
                :loading="keywordsLoading"
                size="small"
                type="link"
                @click="loadKeywords"
            >
              <template #icon>
                <ReloadOutlined/>
              </template>
              刷新
            </a-button>
          </template>

          <a-row :gutter="16">
            <!-- 关键词 -->
            <a-col :span="24">
              <div class="analysis-section">
                <div class="section-label">提取的关键词</div>
                <div v-if="keywordsLoading" class="loading-keywords">
                  <a-spin size="small"/>
                  <span>正在提取关键词...</span>
                </div>
                <div v-else-if="keywords.length > 0" class="keywords-display">
                  <a-tag
                      v-for="(kw, index) in keywords"
                      :key="index"
                      :color="getKeywordColor(kw.weight)"
                      class="keyword-tag"
                  >
                    {{ kw.keyword }}
                    <span class="weight-text">({{ Math.round(kw.weight * 100) }}%)</span>
                  </a-tag>
                </div>
                <div v-else class="no-keywords">
                  <span class="text-muted">暂无关键词，点击刷新进行提取</span>
                </div>
              </div>
            </a-col>
          </a-row>
        </a-card>

      </a-spin>
    </div>

    <!-- 预览模态框 -->
    <a-modal
        v-model:open="previewModalVisible"
        :bodyStyle="{ height: '70vh', padding: 0, maxHeight: '70vh' }"
        :destroyOnClose="true"
        :footer="null"
        :title="`预览 - ${material?.fileName}`"
        :wrapStyle="{ maxHeight: '90vh' }"
        centered
        width="85%"
    >
      <FilePreview
          v-if="previewUrl"
          :file-name="material?.fileName"
          :file-type="material?.fileType"
          :file-url="previewUrl"
          @back="previewModalVisible = false"
          @download="handleDownload"
      />
    </a-modal>

    <!-- 编辑资料对话框 -->
    <a-modal
        v-model:open="editModalVisible"
        :confirm-loading="editLoading"
        title="编辑资料"
        width="600px"
        @cancel="handleEditCancel"
        @ok="handleEditSubmit"
    >
      <a-form
          ref="editFormRef"
          :label-col="{ span: 5 }"
          :model="editForm"
          :wrapper-col="{ span: 19 }"
      >
        <a-form-item
            :rules="[{ required: true, message: '请输入资料标题' }]"
            label="资料标题"
            name="title"
        >
          <a-input
              v-model:value="editForm.title"
              :maxlength="100"
              placeholder="请输入资料标题"
          />
        </a-form-item>

        <a-form-item label="资料描述" name="description">
          <a-textarea
              v-model:value="editForm.description"
              :maxlength="500"
              :rows="4"
              placeholder="请输入资料描述"
              show-count
          />
        </a-form-item>

        <a-form-item label="分类" name="categoryId">
          <a-select
              v-model:value="editForm.categoryId"
              allow-clear
              placeholder="请选择分类"
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
              :max-tag-count="5"
              mode="tags"
              placeholder="请输入标签（按回车添加）"
          >
          </a-select>
        </a-form-item>

        <a-form-item label="文件信息">
          <a-space :size="4" direction="vertical">
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

<script lang="ts" setup>
import {computed, onBeforeUnmount, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {message, Modal} from 'ant-design-vue'
import {
  DeleteOutlined,
  DownloadOutlined,
  EditOutlined,
  EyeOutlined,
  ReloadOutlined,
  RobotOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import {materialApiIntMaterialIdDownloadGet, materialApiIntMaterialIdPreviewGet} from '@/api/materialController.ts'
import {materialApiIntMaterialIdKeywordsGet} from '@/api/classificationController.ts'
import {useMaterialStore} from '@/stores/material.ts'
import {useCategoryStore} from '@/stores/category.ts'
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

// 预览URL状态
const previewUrl = ref('')
const previewLoading = ref(false)

// 关键词状态
const keywords = ref<API.KeywordResponseModel[]>([])
const keywordsLoading = ref(false)

// 资料ID
const materialId = computed(() => {
  return Number(route.params.id)
})

// 从store获取状态
const material = computed(() => materialStore.currentMaterial)
const loading = computed(() => materialStore.loading)
const categories = computed(() => categoryStore.flatCategories)

// 是否可以预览
const canPreview = computed(() => {
  if (!material.value) return false
  // PDF和图片支持预览
  return material.value.fileType === 'pdf' || material.value.fileType === 'image'
})

// 打开预览模态框
const togglePreview = async () => {
  if (!material.value) return
  
  previewLoading.value = true
  try {
    // 通过API获取文件blob数据
    const response = await materialApiIntMaterialIdPreviewGet({
      materialId: materialId.value
    }, {
      responseType: 'blob'
    })
    
    console.log('预览响应:', response)
    console.log('响应头:', response.headers)
    console.log('响应数据类型:', response.data instanceof Blob, response.data)
    
    // 从响应中提取blob数据
    let blob: Blob
    if (response.data instanceof Blob) {
      blob = response.data
    } else {
      // 获取Content-Type
      const contentType = response.headers?.['content-type'] || getContentTypeByFileType(material.value.fileType)
      blob = new Blob([response.data], { type: contentType })
    }
    
    console.log('创建的blob:', blob, 'type:', blob.type, 'size:', blob.size)
    
    // 创建本地blob URL
    // 清理旧的URL
    if (previewUrl.value) {
      window.URL.revokeObjectURL(previewUrl.value)
    }
    previewUrl.value = window.URL.createObjectURL(blob)
    
    console.log('创建的blob URL:', previewUrl.value)
    
    // 打开预览模态框
    previewModalVisible.value = true
  } catch (error: any) {
    console.error('获取预览失败:', error)
    message.error(error.message || '获取预览失败')
  } finally {
    previewLoading.value = false
  }
}

// 根据文件类型获取Content-Type
const getContentTypeByFileType = (fileType: string): string => {
  const typeMap: Record<string, string> = {
    'pdf': 'application/pdf',
    'image': 'image/jpeg',
    'jpg': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'png': 'image/png',
    'gif': 'image/gif',
    'doc': 'application/msword',
    'docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  }
  return typeMap[fileType.toLowerCase()] || 'application/octet-stream'
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

    // 自动加载关键词
    loadKeywords()
  } catch (error: any) {
    console.error('加载资料详情失败:', error)
    message.error(error.message || '加载资料详情失败')
  }
}

// 加载关键词
const loadKeywords = async () => {
  if (!materialId.value) return

  keywordsLoading.value = true
  try {
    const response = await materialApiIntMaterialIdKeywordsGet({
      materialId: materialId.value,
      topN: 10
    })

    console.log('响应数据:', response)

    if (response.data.code === 200 && response.data.data) {
      keywords.value = response.data.data
    } else {
      keywords.value = []
    }
  } catch (error: any) {
    console.error('加载关键词失败:', error)
    keywords.value = []
  } finally {
    keywordsLoading.value = false
  }
}

// 获取关键词颜色
const getKeywordColor = (weight: number): string => {
  if (weight > 0.3) return 'blue'
  if (weight > 0.15) return 'cyan'
  return 'default'
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

    // 从axios响应中提取blob数据
    // response.data 才是实际的blob数据
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
    
    // 尝试从响应头获取文件名
    let fileName = material.value.fileName
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (fileNameMatch && fileNameMatch[1]) {
        fileName = fileNameMatch[1].replace(/['"]/g, '')
        // 处理URL编码的文件名
        try {
          fileName = decodeURIComponent(fileName)
        } catch (e) {
          // 如果解码失败,使用原始文件名
        }
      }
    }

    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
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
    categoryId: material.value.categoryId || null,
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

// 清理
onBeforeUnmount(() => {
  // 清理blob URL
  if (previewUrl.value) {
    window.URL.revokeObjectURL(previewUrl.value)
  }
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

.analysis-section {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.section-label {
  font-weight: 500;
  margin-bottom: 12px;
  color: rgba(0, 0, 0, 0.85);
}

.loading-keywords {
  display: flex;
  align-items: center;
  gap: 8px;
  color: rgba(0, 0, 0, 0.45);
}

.keywords-display {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.weight-text {
  font-size: 10px;
  opacity: 0.7;
}

.no-keywords {
  padding: 8px 0;
}
</style>
