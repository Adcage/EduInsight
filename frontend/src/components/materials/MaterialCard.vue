<template>
  <a-card hoverable class="material-card" @click="handleClick">
    <template #cover>
      <div class="file-icon-container">
        <component :is="fileIcon" class="file-icon" />
      </div>
    </template>
    
    <template #actions>
      <a-tooltip title="预览">
        <EyeOutlined key="preview" @click.stop="handlePreview" />
      </a-tooltip>
      <a-tooltip title="下载">
        <DownloadOutlined key="download" @click.stop="handleDownload" />
      </a-tooltip>
      <a-tooltip title="更多">
        <EllipsisOutlined key="more" @click.stop="handleMore" />
      </a-tooltip>
    </template>
    
    <a-card-meta>
      <template #title>
        <a-tooltip :title="material.title">
          <div class="card-title">{{ material.title }}</div>
        </a-tooltip>
      </template>
      <template #description>
        <div class="card-description">
          <p class="description-text">{{ material.description || '暂无描述' }}</p>
          <div class="card-meta">
            <a-space :size="8">
              <a-tag color="blue">{{ fileTypeText }}</a-tag>
              <span class="file-size">{{ formatFileSize(material.fileSize) }}</span>
            </a-space>
          </div>
          <div class="card-footer">
            <a-space :size="16">
              <span>
                <EyeOutlined />
                {{ material.viewCount || 0 }}
              </span>
              <span>
                <DownloadOutlined />
                {{ material.downloadCount || 0 }}
              </span>
            </a-space>
            <span class="upload-time">{{ formatDate(material.createdAt) }}</span>
          </div>
        </div>
      </template>
    </a-card-meta>
  </a-card>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import {
  EyeOutlined,
  DownloadOutlined,
  EllipsisOutlined,
  FilePdfOutlined,
  FileWordOutlined,
  FilePptOutlined,
  FileExcelOutlined,
  FileTextOutlined,
  FileImageOutlined,
  FileZipOutlined,
  FileOutlined
} from '@ant-design/icons-vue'
import { message } from 'ant-design-vue'
import dayjs from 'dayjs'

interface Material {
  id: number
  title: string
  description?: string
  fileName: string
  fileSize: number
  fileType: string
  viewCount?: number
  downloadCount?: number
  createdAt?: string
  [key: string]: any
}

interface Props {
  material: Material
}

const props = defineProps<Props>()

const emit = defineEmits<{
  click: [material: Material]
  preview: [material: Material]
  download: [material: Material]
  more: [material: Material]
}>()

// 文件图标映射
const fileIconMap: Record<string, any> = {
  pdf: FilePdfOutlined,
  doc: FileWordOutlined,
  ppt: FilePptOutlined,
  xls: FileExcelOutlined,
  text: FileTextOutlined,
  image: FileImageOutlined,
  archive: FileZipOutlined,
  other: FileOutlined
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

// 获取文件图标
const fileIcon = computed(() => {
  return fileIconMap[props.material.fileType] || FileOutlined
})

// 获取文件类型文本
const fileTypeText = computed(() => {
  return fileTypeTextMap[props.material.fileType] || '其他'
})

// 格式化文件大小
const formatFileSize = (bytes: number): string => {
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

// 格式化日期
const formatDate = (date?: string): string => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD')
}

// 点击卡片
const handleClick = () => {
  emit('click', props.material)
}

// 预览
const handlePreview = () => {
  emit('preview', props.material)
}

// 下载
const handleDownload = () => {
  emit('download', props.material)
}

// 更多操作
const handleMore = () => {
  emit('more', props.material)
}
</script>

<style scoped>
.material-card {
  height: 100%;
  transition: all 0.3s;
  cursor: pointer;
}

.material-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.file-icon-container {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 160px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px 8px 0 0;
}

.file-icon {
  font-size: 64px;
  color: white;
}

.card-title {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  font-weight: 500;
}

.description-text {
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  margin-bottom: 8px;
  color: rgba(0, 0, 0, 0.65);
  min-height: 40px;
}

.card-meta {
  margin-bottom: 8px;
}

.file-size {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
}

.card-footer {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.upload-time {
  font-size: 12px;
}

:deep(.ant-card-actions li) {
  margin: 8px 0;
}
</style>
