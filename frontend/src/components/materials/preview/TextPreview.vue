<template>
  <div class="text-preview">
    <a-spin :spinning="loading" tip="加载文本中...">
      <div v-if="error" class="error-container">
        <a-result
            :sub-title="error"
            status="error"
            title="文本加载失败"
        >
          <template #extra>
            <a-button type="primary" @click="reload">
              重新加载
            </a-button>
          </template>
        </a-result>
      </div>

      <div v-else class="text-container">
        <!-- 工具栏 -->
        <div class="text-toolbar">
          <a-space>
            <a-switch
                v-model:checked="enableHighlight"
                checked-children="高亮"
                un-checked-children="纯文本"
                @change="handleHighlightChange"
            />
            <a-select
                v-if="enableHighlight"
                v-model:value="selectedLanguage"
                placeholder="选择语言"
                style="width: 150px"
                @change="handleLanguageChange"
            >
              <a-select-option value="auto">自动检测</a-select-option>
              <a-select-option value="javascript">JavaScript</a-select-option>
              <a-select-option value="typescript">TypeScript</a-select-option>
              <a-select-option value="python">Python</a-select-option>
              <a-select-option value="java">Java</a-select-option>
              <a-select-option value="cpp">C++</a-select-option>
              <a-select-option value="csharp">C#</a-select-option>
              <a-select-option value="html">HTML</a-select-option>
              <a-select-option value="css">CSS</a-select-option>
              <a-select-option value="json">JSON</a-select-option>
              <a-select-option value="xml">XML</a-select-option>
              <a-select-option value="markdown">Markdown</a-select-option>
            </a-select>
            <a-button @click="copyContent">
              <template #icon>
                <CopyOutlined/>
              </template>
              复制
            </a-button>
          </a-space>
        </div>

        <!-- 文本内容 -->
        <div class="text-content">
          <pre v-if="!enableHighlight" class="plain-text">{{ content }}</pre>
          <pre v-else class="highlighted-text" v-html="highlightedContent"></pre>
        </div>
      </div>
    </a-spin>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {CopyOutlined} from '@ant-design/icons-vue'
import hljs from 'highlight.js'
import 'highlight.js/styles/github.css'

interface Props {
  url: string
  language?: string
}

const props = withDefaults(defineProps<Props>(), {
  language: 'auto'
})

const loading = ref(false)
const error = ref('')
const content = ref('')
const enableHighlight = ref(true)
const selectedLanguage = ref(props.language)

// 高亮后的内容
const highlightedContent = computed(() => {
  if (!content.value || !enableHighlight.value) return ''

  try {
    if (selectedLanguage.value === 'auto') {
      const result = hljs.highlightAuto(content.value)
      return result.value
    } else {
      const result = hljs.highlight(content.value, {language: selectedLanguage.value})
      return result.value
    }
  } catch (err) {
    console.error('代码高亮失败:', err)
    return content.value
  }
})

// 加载文本内容
const loadText = async () => {
  loading.value = true
  error.value = ''

  try {
    const response = await fetch(props.url)
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    content.value = await response.text()
    message.success('文本加载成功')
  } catch (err: any) {
    console.error('文本加载失败:', err)
    error.value = err.message || '文本加载失败，请稍后重试'
    message.error('文本加载失败')
  } finally {
    loading.value = false
  }
}

// 复制内容
const copyContent = async () => {
  try {
    await navigator.clipboard.writeText(content.value)
    message.success('复制成功')
  } catch (err) {
    message.error('复制失败')
  }
}

// 切换高亮
const handleHighlightChange = () => {
  // 高亮状态已通过 v-model 更新
}

// 切换语言
const handleLanguageChange = () => {
  // 语言已通过 v-model 更新，computed 会自动重新计算
}

// 重新加载
const reload = () => {
  loadText()
}

// 监听URL变化
watch(() => props.url, () => {
  if (props.url) {
    reload()
  }
})

onMounted(() => {
  if (props.url) {
    loadText()
  }
})
</script>

<style scoped>
.text-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.error-container {
  padding: 40px;
  text-align: center;
}

.text-container {
  display: flex;
  flex-direction: column;
  height: 100%;
}

.text-toolbar {
  padding: 16px;
  background: white;
  border-bottom: 1px solid #e8e8e8;
  flex-shrink: 0;
}

.text-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.plain-text,
.highlighted-text {
  background: white;
  padding: 20px;
  margin: 0;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 14px;
  line-height: 1.6;
  white-space: pre-wrap;
  word-wrap: break-word;
}

.highlighted-text {
  padding: 20px;
}

.highlighted-text :deep(code) {
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
}
</style>
