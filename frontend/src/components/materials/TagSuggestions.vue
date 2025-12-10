<template>
  <div class="tag-suggestions">
    <a-card
        :bordered="false"
        :loading="loading"
        class="suggestions-card"
        size="small"
    >
      <template #title>
        <div class="card-title">
          <TagsOutlined/>
          <span>智能标签推荐</span>
        </div>
      </template>

      <template #extra>
        <a-button
            v-if="!loading"
            size="small"
            type="link"
            @click="handleRefresh"
        >
          <template #icon>
            <ReloadOutlined/>
          </template>
          刷新
        </a-button>
      </template>

      <!-- 加载中 -->
      <div v-if="loading" class="loading-state">
        <a-spin size="small"/>
        <span>正在获取推荐...</span>
      </div>

      <!-- 推荐结果 -->
      <div v-else-if="suggestions.length > 0" class="suggestions-content">
        <div class="suggestions-list">
          <div
              v-for="(suggestion, index) in suggestions"
              :key="index"
              :class="{
              'is-selected': isSelected(suggestion.tagName),
              'is-existing': suggestion.isExisting
            }"
              class="suggestion-item"
              @click="handleToggle(suggestion)"
          >
            <a-tag
                :color="isSelected(suggestion.tagName) ? 'blue' : (suggestion.isExisting ? 'green' : 'default')"
                class="suggestion-tag"
            >
              <template #icon>
                <CheckCircleFilled v-if="isSelected(suggestion.tagName)"/>
                <TagOutlined v-else-if="suggestion.isExisting"/>
                <PlusOutlined v-else/>
              </template>
              {{ suggestion.tagName }}
            </a-tag>
            <span class="relevance-indicator">
              <a-progress
                  :percent="Math.round(suggestion.relevance * 100)"
                  :show-info="false"
                  :stroke-color="getRelevanceColor(suggestion.relevance)"
                  size="small"
                  style="width: 40px"
              />
            </span>
          </div>
        </div>

        <div class="legend">
          <span class="legend-item">
            <a-tag color="green" size="small"><TagOutlined/> 现有</a-tag>
          </span>
          <span class="legend-item">
            <a-tag size="small"><PlusOutlined/> 新建</a-tag>
          </span>
        </div>
      </div>

      <!-- 无推荐 -->
      <div v-else class="empty-state">
        <a-empty
            :image="Empty.PRESENTED_IMAGE_SIMPLE"
            description="暂无标签推荐"
        />
      </div>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {Empty, message} from 'ant-design-vue'
import {CheckCircleFilled, PlusOutlined, ReloadOutlined, TagOutlined, TagsOutlined} from '@ant-design/icons-vue'
import {materialApiIntMaterialIdSuggestTagsPost} from '@/api/classificationController'

// Props
const props = defineProps<{
  materialId: number
  selectedTags?: string[]
  autoLoad?: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'select', tag: API.TagSuggestionResponseModel): void
  (e: 'deselect', tagName: string): void
  (e: 'update:selectedTags', tags: string[]): void
}>()

// 状态
const loading = ref(false)
const suggestions = ref<API.TagSuggestionResponseModel[]>([])

// 计算已选中的标签
const selectedTagsSet = computed(() => new Set(props.selectedTags || []))

// 判断标签是否已选中
const isSelected = (tagName: string): boolean => {
  return selectedTagsSet.value.has(tagName)
}

// 加载推荐 - 必须在 watch 之前定义
const loadSuggestions = async () => {
  if (!props.materialId) return

  loading.value = true
  try {
    const response: any = await materialApiIntMaterialIdSuggestTagsPost({materialId: props.materialId})

    // 处理 axios 响应结构: response.data 是后端返回的 { code, message, data }
    const responseData = response.data || response

    if (responseData.code === 200 && responseData.data) {
      suggestions.value = responseData.data
    } else {
      suggestions.value = []
    }
  } catch (error: any) {
    console.error('获取标签推荐失败:', error)
    suggestions.value = []
  } finally {
    loading.value = false
  }
}

// 监听 materialId 变化
watch(() => props.materialId, (newId) => {
  if (newId && props.autoLoad) {
    loadSuggestions()
  }
}, {immediate: true})

// 刷新推荐
const handleRefresh = () => {
  loadSuggestions()
}

// 切换标签选中状态
const handleToggle = (suggestion: API.TagSuggestionResponseModel) => {
  const tagName = suggestion.tagName

  if (isSelected(tagName)) {
    // 取消选中
    emit('deselect', tagName)
    const newTags = (props.selectedTags || []).filter(t => t !== tagName)
    emit('update:selectedTags', newTags)
  } else {
    // 选中
    emit('select', suggestion)
    const newTags = [...(props.selectedTags || []), tagName]
    emit('update:selectedTags', newTags)
    message.success(`已添加标签: ${tagName}`)
  }
}

// 获取相关度颜色
const getRelevanceColor = (relevance: number): string => {
  if (relevance > 0.7) return '#52c41a'
  if (relevance > 0.4) return '#1890ff'
  return '#d9d9d9'
}

// 暴露方法
defineExpose({
  refresh: loadSuggestions,
  suggestions
})
</script>

<style scoped>
.tag-suggestions {
  margin-bottom: 16px;
}

.suggestions-card {
  border-radius: 8px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  font-size: 14px;
}

.loading-state {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 16px 0;
  color: rgba(0, 0, 0, 0.45);
}

.suggestions-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.suggestion-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 8px 12px;
  background: #fafafa;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.suggestion-item:hover {
  background: #f0f0f0;
}

.suggestion-item.is-selected {
  background: #e6f7ff;
  border: 1px solid #91d5ff;
}

.suggestion-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
}

.relevance-indicator {
  display: flex;
  align-items: center;
}

.legend {
  display: flex;
  gap: 12px;
  padding-top: 8px;
  border-top: 1px solid #f0f0f0;
  font-size: 12px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 4px;
  color: rgba(0, 0, 0, 0.45);
}

.empty-state {
  padding: 16px 0;
}
</style>
