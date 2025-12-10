<template>
  <div class="student-material-detail">
    <a-page-header :title="material?.title || '资料详情'" @back="handleBack">
      <template #extra>
        <a-space>
          <a-button v-if="canPreview" type="primary" @click="togglePreview">
            <template #icon><EyeOutlined /></template>
            预览
          </a-button>
          <a-button @click="handleDownload">
            <template #icon><DownloadOutlined /></template>
            下载
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-container">
      <!-- 骨架屏加载状态 - Requirements 1.1 -->
      <div v-if="loading" class="skeleton-container">
        <a-card :bordered="false" class="info-card">
          <a-skeleton active :paragraph="{ rows: 8 }" />
        </a-card>
        <a-card :bordered="false" class="info-card" style="margin-top: 16px">
          <a-skeleton active :paragraph="{ rows: 4 }" />
        </a-card>
      </div>

      <template v-else>
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
              <span v-if="material?.category?.name">
                {{ material.category.name }}
              </span>
              <span v-else class="text-muted">未分类</span>
            </a-descriptions-item>

            <a-descriptions-item label="上传者">
              {{ material?.uploader?.realName || '未知' }}
            </a-descriptions-item>

            <a-descriptions-item label="上传时间">
              {{ formatDateTime(material?.createdAt) }}
            </a-descriptions-item>

            <a-descriptions-item label="下载次数">
              <a-statistic :value="material?.downloadCount || 0" :value-style="{ fontSize: '14px' }">
                <template #prefix>
                  <DownloadOutlined />
                </template>
              </a-statistic>
            </a-descriptions-item>

            <a-descriptions-item label="浏览次数">
              <a-statistic :value="material?.viewCount || 0" :value-style="{ fontSize: '14px' }">
                <template #prefix>
                  <EyeOutlined />
                </template>
              </a-statistic>
            </a-descriptions-item>

            <a-descriptions-item label="标签" :span="2">
              <a-space v-if="material?.tags && material.tags.length > 0">
                <a-tag v-for="tag in material.tags" :key="tag.id" color="blue">
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

        <!-- 相关资料卡片 -->
        <a-card :bordered="false" class="info-card" style="margin-top: 16px">
          <template #title>
            <div style="display: flex; align-items: center; gap: 8px">
              <AppstoreOutlined />
              <span>相关资料</span>
            </div>
          </template>

          <!-- 相关资料骨架屏 -->
          <div v-if="relatedLoading" class="related-skeleton">
            <a-row :gutter="[16, 16]">
              <a-col v-for="n in 4" :key="n" :xs="24" :sm="12" :md="8" :lg="6">
                <a-card class="skeleton-card">
                  <a-skeleton :loading="true" active :paragraph="{ rows: 2 }" />
                </a-card>
              </a-col>
            </a-row>
          </div>
          <a-empty v-else-if="relatedMaterials.length === 0" description="暂无相关资料" />
          <a-row v-else :gutter="[16, 16]">
            <a-col v-for="relatedMaterial in relatedMaterials" :key="relatedMaterial.id" :xs="24" :sm="12" :md="8" :lg="6">
              <MaterialCard
                :material="relatedMaterial"
                @click="handleViewRelated"
                @preview="handlePreviewRelated"
                @download="handleDownloadRelated"
              />
            </a-col>
          </a-row>
        </a-card>
      </template>
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
  </div>
</template>

<script setup lang="ts">
/**
 * 学生端资料详情页面
 * 功能：展示资料详细信息，提供预览和下载功能，显示相关资料
 * Requirements: 4.1, 4.2, 4.3
 */
import { ref, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { DownloadOutlined, EyeOutlined, AppstoreOutlined } from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import { materialApiIntMaterialIdDownloadGet, materialApiGet } from '@/api/materialController'
import { useMaterialStore } from '@/stores/material'
import FilePreview from '@/components/materials/preview/FilePreview.vue'
import MaterialCard from '@/components/materials/MaterialCard.vue'

const route = useRoute()
const router = useRouter()

// Stores
const materialStore = useMaterialStore()

// 状态
const previewModalVisible = ref(false)
const relatedMaterials = ref<any[]>([])
const relatedLoading = ref(false)

// 资料ID
const materialId = computed(() => {
  return Number(route.params.id)
})

// 从store获取状态
const material = computed(() => materialStore.currentMaterial)
const loading = computed(() => materialStore.loading)

// 预览URL
const previewUrl = computed(() => {
  if (!material.value) return ''
  const baseUrl = 'http://localhost:5030'
  return `${baseUrl}/api/v1/materials/${material.value.id}/preview`
})

// 是否可以预览
const canPreview = computed(() => {
  if (!material.value) return false
  return material.value.fileType === 'pdf' || material.value.fileType === 'image'
})

// 打开预览模态框
const togglePreview = () => {
  previewModalVisible.value = true
}

// 文件类型颜色映射
const fileTypeColorMap: Record<string, string> = {
  pdf: 'red',
  doc: 'blue',
  ppt: 'orange',
  xls: 'green',
  image: 'purple',
  video: 'cyan',
  archive: 'geekblue',
  text: 'default',
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
  other: '其他',
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

    // 加载相关资料
    loadRelatedMaterials()
  } catch (error: any) {
    console.error('加载资料详情失败:', error)
    message.error(error.message || '加载资料详情失败')
  }
}

// 加载相关资料（基于相同分类或标签）
const loadRelatedMaterials = async () => {
  if (!material.value) return

  relatedLoading.value = true
  try {
    const params: any = {
      page: 1,
      page_size: 4,
    }

    // 优先按分类查询
    if (material.value.categoryId) {
      params.category_id = material.value.categoryId
    } else if (material.value.tags && material.value.tags.length > 0) {
      // 如果没有分类，按标签查询
      params.tag_ids = material.value.tags.map((t: any) => t.id).join(',')
    }

    const response = await materialApiGet(params)
    const data = (response as any).data?.data || (response as any).data

    // 过滤掉当前资料
    relatedMaterials.value = (data?.materials || []).filter((m: any) => m.id !== materialId.value).slice(0, 4)
  } catch (error: any) {
    console.error('加载相关资料失败:', error)
    relatedMaterials.value = []
  } finally {
    relatedLoading.value = false
  }
}

// 下载
const handleDownload = async () => {
  if (!material.value) return

  const loadingMsg = message.loading('正在下载...', 0)
  try {
    const response = await materialApiIntMaterialIdDownloadGet({
      materialId: materialId.value,
    })

    // 创建下载链接
    const blob = new Blob([response.data])
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

// 查看相关资料详情
const handleViewRelated = (relatedMaterial: any) => {
  router.push(`/student/materials/${relatedMaterial.id}`)
}

// 预览相关资料
const handlePreviewRelated = (relatedMaterial: any) => {
  router.push(`/student/materials/${relatedMaterial.id}?preview=true`)
}

// 下载相关资料
const handleDownloadRelated = async (relatedMaterial: any) => {
  if (!relatedMaterial) return

  const loadingMsg = message.loading('正在下载...', 0)
  try {
    const response = await materialApiIntMaterialIdDownloadGet({
      materialId: relatedMaterial.id,
    })

    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', relatedMaterial.fileName)
    link.style.display = 'none'
    document.body.appendChild(link)
    link.click()

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

// 返回
const handleBack = () => {
  router.push('/student/materials')
}

// 初始化
onMounted(() => {
  loadMaterialDetail()
})
</script>

<style scoped>
.student-material-detail .content-container {
  padding: 16px;
}

.student-material-detail .info-card {
  margin-bottom: 16px;
}

.student-material-detail .description-content {
  white-space: pre-wrap;
  word-break: break-word;
}

.student-material-detail .text-muted {
  color: rgba(0, 0, 0, 0.45);
}

/* 骨架屏加载样式 - Requirements 1.1 */
.skeleton-container {
  padding: 0;
}

.skeleton-card {
  height: 120px;
  border-radius: 8px;
}

.related-skeleton {
  padding: 8px 0;
}
</style>
