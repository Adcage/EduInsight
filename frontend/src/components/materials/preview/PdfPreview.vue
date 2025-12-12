<template>
  <div class="pdf-preview">
    <a-spin :spinning="loading" tip="加载PDF中...">
      <div v-if="error" class="error-container">
        <a-result
            :sub-title="error"
            status="error"
            title="PDF加载失败"
        >
          <template #extra>
            <a-button type="primary" @click="reload">
              重新加载
            </a-button>
          </template>
        </a-result>
      </div>

      <div v-else class="pdf-container">
        <!-- 工具栏 -->
        <div class="pdf-toolbar">
          <a-space>
            <a-button-group>
              <a-button :disabled="currentPage <= 1" @click="prevPage">
                <template #icon>
                  <LeftOutlined/>
                </template>
                上一页
              </a-button>
              <a-button disabled>
                {{ currentPage }} / {{ totalPages }}
              </a-button>
              <a-button :disabled="currentPage >= totalPages" @click="nextPage">
                下一页
                <template #icon>
                  <RightOutlined/>
                </template>
              </a-button>
            </a-button-group>

            <a-divider type="vertical"/>

            <a-button-group>
              <a-button :disabled="scale <= 0.5" @click="zoomOut">
                <template #icon>
                  <ZoomOutOutlined/>
                </template>
              </a-button>
              <a-button disabled>
                {{ Math.round(scale * 100) }}%
              </a-button>
              <a-button :disabled="scale >= 3" @click="zoomIn">
                <template #icon>
                  <ZoomInOutlined/>
                </template>
              </a-button>
            </a-button-group>

            <a-button @click="resetZoom">
              <template #icon>
                <ReloadOutlined/>
              </template>
              重置
            </a-button>

            <a-button @click="rotate">
              <template #icon>
                <RotateRightOutlined/>
              </template>
              旋转
            </a-button>
          </a-space>
        </div>

        <!-- PDF画布 -->
        <div ref="containerRef" class="pdf-canvas-container">
          <canvas
              ref="canvasRef"
              :style="{
              transform: `rotate(${rotation}deg)`,
              transformOrigin: 'center center'
            }"
          ></canvas>
        </div>
      </div>
    </a-spin>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {
  LeftOutlined,
  ReloadOutlined,
  RightOutlined,
  RotateRightOutlined,
  ZoomInOutlined,
  ZoomOutOutlined
} from '@ant-design/icons-vue'
import * as pdfjsLib from 'pdfjs-dist'

// 配置 PDF.js worker
pdfjsLib.GlobalWorkerOptions.workerSrc = `//cdnjs.cloudflare.com/ajax/libs/pdf.js/${pdfjsLib.version}/pdf.worker.min.js`

interface Props {
  url: string
}

const props = defineProps<Props>()

const loading = ref(false)
const error = ref('')
const canvasRef = ref<HTMLCanvasElement>()
const containerRef = ref<HTMLDivElement>()
const currentPage = ref(1)
const totalPages = ref(0)
const scale = ref(1.5)
const rotation = ref(0)

let pdfDoc: any = null
let pageRendering = false
let pageNumPending: number | null = null

// 加载PDF文档
const loadPdf = async () => {
  loading.value = true
  error.value = ''

  try {
    // 配置PDF.js加载选项
    const loadingTask = pdfjsLib.getDocument({
      url: props.url,
      withCredentials: true // 携带cookies用于认证
    })
    
    pdfDoc = await loadingTask.promise
    totalPages.value = pdfDoc.numPages

    // 渲染第一页
    await renderPage(1)
  } catch (err: any) {
    console.error('PDF加载失败:', err)
    error.value = err.message || 'PDF加载失败,请稍后重试'
    message.error('PDF加载失败')
  } finally {
    loading.value = false
  }
}

// 渲染指定页面
const renderPage = async (num: number) => {
  if (!pdfDoc || !canvasRef.value) return

  pageRendering = true

  try {
    const page = await pdfDoc.getPage(num)
    const viewport = page.getViewport({scale: scale.value})

    const canvas = canvasRef.value
    const context = canvas.getContext('2d')

    if (!context) return

    canvas.height = viewport.height
    canvas.width = viewport.width

    const renderContext = {
      canvasContext: context,
      viewport: viewport
    }

    await page.render(renderContext).promise

    pageRendering = false

    // 如果有待渲染的页面，渲染它
    if (pageNumPending !== null) {
      const pending = pageNumPending
      pageNumPending = null
      await renderPage(pending)
    }
  } catch (err: any) {
    console.error('页面渲染失败:', err)
    message.error('页面渲染失败')
    pageRendering = false
  }
}

// 队列渲染页面
const queueRenderPage = (num: number) => {
  if (pageRendering) {
    pageNumPending = num
  } else {
    renderPage(num)
  }
}

// 上一页
const prevPage = () => {
  if (currentPage.value <= 1) return
  currentPage.value--
  queueRenderPage(currentPage.value)
}

// 下一页
const nextPage = () => {
  if (currentPage.value >= totalPages.value) return
  currentPage.value++
  queueRenderPage(currentPage.value)
}

// 放大
const zoomIn = () => {
  if (scale.value >= 3) return
  scale.value += 0.25
  queueRenderPage(currentPage.value)
}

// 缩小
const zoomOut = () => {
  if (scale.value <= 0.5) return
  scale.value -= 0.25
  queueRenderPage(currentPage.value)
}

// 重置缩放
const resetZoom = () => {
  scale.value = 1.5
  rotation.value = 0
  queueRenderPage(currentPage.value)
}

// 旋转
const rotate = () => {
  rotation.value = (rotation.value + 90) % 360
}

// 重新加载
const reload = () => {
  currentPage.value = 1
  scale.value = 1.5
  rotation.value = 0
  loadPdf()
}

// 监听URL变化
watch(() => props.url, () => {
  if (props.url) {
    reload()
  }
})

onMounted(() => {
  if (props.url) {
    loadPdf()
  }
})
</script>

<style scoped>
.pdf-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
}

.error-container {
  padding: 40px;
  text-align: center;
}

.pdf-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.pdf-toolbar {
  padding: 16px;
  background: #fafafa;
  border-bottom: 1px solid #e8e8e8;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.pdf-canvas-container {
  flex: 1;
  overflow: auto;
  padding: 20px;
  background: #f5f5f5;
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.pdf-canvas-container canvas {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  background: white;
  transition: transform 0.3s ease;
}
</style>
