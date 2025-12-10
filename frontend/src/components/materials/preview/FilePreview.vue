<template>
  <div class="file-preview">
    <a-spin :spinning="loading" tip="正在加载...">
      <!-- PDF预览 -->
      <PdfPreview v-if="fileType === 'pdf'" :url="fileUrl"/>

      <!-- 图片预览 -->
      <ImagePreview v-else-if="isImage" :alt="fileName" :url="fileUrl"/>

      <!-- Word文档预览 -->
      <DocxPreview v-else-if="isDocx" :url="fileUrl"/>

      <!-- 文本文件预览 -->
      <TextPreview v-else-if="isText" :language="textLanguage" :url="fileUrl"/>

      <!-- 不支持预览的文件类型 -->
      <div v-else class="no-preview">
        <a-result
            :sub-title="`文件类型: ${fileType || '未知'}`"
            status="info"
            title="该文件类型暂不支持在线预览"
        >
          <template #icon>
            <FileOutlined style="color: #1890ff"/>
          </template>
          <template #extra>
            <a-space>
              <a-button type="primary" @click="handleDownload">
                <template #icon>
                  <DownloadOutlined/>
                </template>
                下载查看
              </a-button>
              <a-button @click="handleBack">
                返回
              </a-button>
            </a-space>
          </template>
        </a-result>
      </div>
    </a-spin>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {DownloadOutlined, FileOutlined} from '@ant-design/icons-vue'
import PdfPreview from './PdfPreview.vue'
import ImagePreview from './ImagePreview.vue'
import DocxPreview from './DocxPreview.vue'
import TextPreview from './TextPreview.vue'

interface Props {
  fileUrl: string
  fileType?: string
  fileName?: string
}

const props = defineProps<Props>()
const emit = defineEmits<{
  download: []
  back: []
}>()
const loading = ref(false)

// 图片类型
const imageTypes = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg', 'image']

// 文本类型
const textTypes = ['txt', 'md', 'json', 'xml', 'csv', 'log', 'js', 'ts', 'jsx', 'tsx', 'vue', 'css', 'scss', 'less', 'html', 'py', 'java', 'cpp', 'c', 'h', 'cs', 'go', 'rs', 'php', 'rb', 'sh', 'yaml', 'yml', 'text']

// Word文档类型
const docxTypes = ['doc', 'docx', 'word']

// 判断是否为图片
const isImage = computed(() => {
  if (!props.fileType) return false
  const type = props.fileType.toLowerCase()
  // 支持 'image' 或具体的图片格式
  return imageTypes.includes(type)
})

// 判断是否为文本
const isText = computed(() => {
  if (!props.fileType) return false
  return textTypes.includes(props.fileType.toLowerCase())
})

// 判断是否为Word文档
const isDocx = computed(() => {
  if (!props.fileType) return false
  return docxTypes.includes(props.fileType.toLowerCase())
})

// 文本语言
const textLanguage = computed(() => {
  if (!props.fileType) return 'auto'

  const typeMap: Record<string, string> = {
    'js': 'javascript',
    'ts': 'typescript',
    'jsx': 'javascript',
    'tsx': 'typescript',
    'vue': 'html',
    'py': 'python',
    'java': 'java',
    'cpp': 'cpp',
    'c': 'cpp',
    'cs': 'csharp',
    'html': 'html',
    'css': 'css',
    'scss': 'scss',
    'less': 'less',
    'json': 'json',
    'xml': 'xml',
    'md': 'markdown',
    'yaml': 'yaml',
    'yml': 'yaml',
    'sh': 'bash',
    'go': 'go',
    'rs': 'rust',
    'php': 'php',
    'rb': 'ruby'
  }

  return typeMap[props.fileType.toLowerCase()] || 'auto'
})

// 下载文件
const handleDownload = () => {
  emit('download')
}

// 返回
const handleBack = () => {
  emit('back')
}

onMounted(() => {
  // 调试信息
  console.log('FilePreview mounted:', {
    fileUrl: props.fileUrl,
    fileType: props.fileType,
    fileName: props.fileName,
    isImage: isImage.value,
    isText: isText.value,
    isDocx: isDocx.value
  })
})
</script>

<style scoped>
.file-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
  overflow: auto;
  min-height: 0;
  min-width: 0;
}

.no-preview {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 40px;
  background: white;
  overflow: auto;
}
</style>
