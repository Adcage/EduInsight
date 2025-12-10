<template>
  <div class="docx-preview">
    <a-spin :spinning="loading" tip="加载文档中...">
      <div v-if="error" class="error-container">
        <a-result
            :sub-title="error"
            status="error"
            title="文档加载失败"
        >
          <template #extra>
            <a-button type="primary" @click="reload">
              重新加载
            </a-button>
          </template>
        </a-result>
      </div>

      <div v-else ref="docxContainer" class="docx-container"></div>
    </a-spin>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {renderAsync} from 'docx-preview'

interface Props {
  url: string
}

const props = defineProps<Props>()

const loading = ref(false)
const error = ref('')
const docxContainer = ref<HTMLDivElement>()

// 加载并渲染Word文档
const loadDocx = async () => {
  if (!docxContainer.value) return

  loading.value = true
  error.value = ''

  try {
    // 获取文件
    const response = await fetch(props.url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const arrayBuffer = await response.arrayBuffer()

    // 清空容器
    docxContainer.value.innerHTML = ''

    // 渲染文档
    await renderAsync(arrayBuffer, docxContainer.value, undefined, {
      className: 'docx-wrapper',
      inWrapper: true,
      ignoreWidth: false,
      ignoreHeight: false,
      ignoreFonts: false,
      breakPages: true,
      ignoreLastRenderedPageBreak: true,
      experimental: false,
      trimXmlDeclaration: true,
      useBase64URL: false,
      renderChanges: false,
      renderHeaders: true,
      renderFooters: true,
      renderFootnotes: true,
      renderEndnotes: true
    })

    message.success('文档加载成功')
  } catch (err: any) {
    console.error('Word文档加载失败:', err)
    error.value = err.message || 'Word文档加载失败，请稍后重试'
    message.error('文档加载失败')
  } finally {
    loading.value = false
  }
}

// 重新加载
const reload = () => {
  loadDocx()
}

// 监听URL变化
watch(() => props.url, () => {
  if (props.url) {
    reload()
  }
})

onMounted(() => {
  if (props.url) {
    loadDocx()
  }
})
</script>

<style scoped>
.docx-preview {
  width: 100%;
  height: 100%;
  overflow: auto;
  background: #f5f5f5;
}

.error-container {
  padding: 40px;
  text-align: center;
}

.docx-container {
  padding: 20px;
  min-height: 100%;
}

.docx-container :deep(.docx-wrapper) {
  background: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  padding: 40px;
  margin: 0 auto;
  max-width: 21cm;
}

.docx-container :deep(.docx-wrapper section.docx) {
  margin-bottom: 20px;
}
</style>
