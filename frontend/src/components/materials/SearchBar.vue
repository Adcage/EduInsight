<template>
  <div class="search-bar">
    <a-input-search
      v-model:value="searchKeyword"
      placeholder="搜索资料标题、描述、关键词..."
      size="large"
      allow-clear
      @search="handleSearch"
      @change="handleSearchChange"
    >
      <template #enterButton>
        <a-button type="primary">
          <SearchOutlined />
          搜索
        </a-button>
      </template>
    </a-input-search>

    <!-- 搜索建议下拉框 -->
    <div v-if="showSuggestions && suggestions.length > 0" class="search-suggestions">
      <div
        v-for="suggestion in suggestions"
        :key="suggestion.id"
        class="suggestion-item"
        @click="handleSelectSuggestion(suggestion)"
      >
        <FileOutlined class="suggestion-icon" />
        <div class="suggestion-content">
          <div class="suggestion-title">{{ suggestion.title }}</div>
          <div class="suggestion-meta">
            <a-tag :color="getFileTypeColor(suggestion.fileType)" size="small">
              {{ getFileTypeText(suggestion.fileType) }}
            </a-tag>
            <span class="suggestion-size">{{ formatFileSize(suggestion.fileSize) }}</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 搜索历史 -->
    <div v-if="showHistory && searchHistory.length > 0" class="search-history">
      <div class="history-header">
        <span>搜索历史</span>
        <a-button type="link" size="small" @click="clearHistory">
          <DeleteOutlined />
          清空
        </a-button>
      </div>
      <div class="history-items">
        <a-tag
          v-for="(item, index) in searchHistory"
          :key="index"
          closable
          @click="handleHistoryClick(item)"
          @close="removeHistoryItem(index)"
        >
          {{ item }}
        </a-tag>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted } from 'vue'
import { SearchOutlined, FileOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { materialApiGet } from '@/api/materialController'
import { debounce } from 'lodash-es'

interface Material {
  id: number
  title: string
  fileType: string
  fileSize: number
}

interface Props {
  modelValue?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'search', keyword: string): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const searchKeyword = ref(props.modelValue || '')
const suggestions = ref<Material[]>([])
const showSuggestions = ref(false)
const showHistory = ref(false)
const searchHistory = ref<string[]>([])

const HISTORY_KEY = 'material_search_history'
const MAX_HISTORY = 10

// 加载搜索历史
const loadSearchHistory = () => {
  const history = localStorage.getItem(HISTORY_KEY)
  if (history) {
    searchHistory.value = JSON.parse(history)
  }
}

// 保存搜索历史
const saveSearchHistory = (keyword: string) => {
  if (!keyword.trim()) return
  
  // 移除重复项
  const index = searchHistory.value.indexOf(keyword)
  if (index > -1) {
    searchHistory.value.splice(index, 1)
  }
  
  // 添加到开头
  searchHistory.value.unshift(keyword)
  
  // 限制数量
  if (searchHistory.value.length > MAX_HISTORY) {
    searchHistory.value = searchHistory.value.slice(0, MAX_HISTORY)
  }
  
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
}

// 清空搜索历史
const clearHistory = () => {
  searchHistory.value = []
  localStorage.removeItem(HISTORY_KEY)
  showHistory.value = false
}

// 移除单个历史记录
const removeHistoryItem = (index: number) => {
  searchHistory.value.splice(index, 1)
  localStorage.setItem(HISTORY_KEY, JSON.stringify(searchHistory.value))
}

// 点击历史记录
const handleHistoryClick = (keyword: string) => {
  searchKeyword.value = keyword
  showHistory.value = false
  handleSearch()
}

// 获取搜索建议
const fetchSuggestions = debounce(async (keyword: string) => {
  if (!keyword || keyword.length < 2) {
    suggestions.value = []
    showSuggestions.value = false
    return
  }
  
  try {
    const response = await materialApiGet({
      search: keyword,
      page: 1,
      page_size: 5
    })
    
    const data = (response as any).data?.data || (response as any).data
    const materialList = data?.materials || []
    suggestions.value = Array.isArray(materialList) ? materialList : []
    showSuggestions.value = suggestions.value.length > 0
  } catch (error) {
    console.error('获取搜索建议失败:', error)
    suggestions.value = []
    showSuggestions.value = false
  }
}, 300)

// 搜索输入变化
const handleSearchChange = () => {
  emit('update:modelValue', searchKeyword.value)
  
  if (searchKeyword.value.trim()) {
    fetchSuggestions(searchKeyword.value)
    showHistory.value = false
  } else {
    suggestions.value = []
    showSuggestions.value = false
    showHistory.value = searchHistory.value.length > 0
  }
}

// 执行搜索
const handleSearch = () => {
  const keyword = searchKeyword.value.trim()
  if (keyword) {
    saveSearchHistory(keyword)
    emit('search', keyword)
    showSuggestions.value = false
    showHistory.value = false
  }
}

// 选择搜索建议
const handleSelectSuggestion = (suggestion: Material) => {
  searchKeyword.value = suggestion.title
  emit('update:modelValue', suggestion.title)
  showSuggestions.value = false
  handleSearch()
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

const getFileTypeColor = (type: string): string => {
  return fileTypeColorMap[type] || 'default'
}

const getFileTypeText = (type: string): string => {
  return fileTypeTextMap[type] || '其他'
}

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

// 点击外部关闭下拉框
const handleClickOutside = (event: MouseEvent) => {
  const target = event.target as HTMLElement
  if (!target.closest('.search-bar')) {
    showSuggestions.value = false
    showHistory.value = false
  }
}

// 输入框获得焦点
const handleFocus = () => {
  if (!searchKeyword.value && searchHistory.value.length > 0) {
    showHistory.value = true
  }
}

watch(() => props.modelValue, (newValue) => {
  searchKeyword.value = newValue || ''
})

onMounted(() => {
  loadSearchHistory()
  document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
})
</script>

<style scoped>
.search-bar {
  position: relative;
}

.search-suggestions,
.search-history {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin-top: 4px;
  background: white;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  max-height: 400px;
  overflow-y: auto;
}

.suggestion-item {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  cursor: pointer;
  transition: background-color 0.3s;
}

.suggestion-item:hover {
  background-color: #f5f5f5;
}

.suggestion-icon {
  font-size: 20px;
  color: #1890ff;
  margin-right: 12px;
}

.suggestion-content {
  flex: 1;
  min-width: 0;
}

.suggestion-title {
  font-weight: 500;
  margin-bottom: 4px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.suggestion-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.suggestion-size {
  color: rgba(0, 0, 0, 0.45);
}

.search-history {
  padding: 12px 16px;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  font-weight: 500;
  color: rgba(0, 0, 0, 0.85);
}

.history-items {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.history-items :deep(.ant-tag) {
  cursor: pointer;
  margin: 0;
}

.history-items :deep(.ant-tag:hover) {
  opacity: 0.8;
}
</style>
