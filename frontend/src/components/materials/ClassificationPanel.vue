<template>
  <div class="classification-panel">
    <a-card
        :bordered="false"
        :loading="loading"
        class="classification-card"
    >
      <template #title>
        <div class="card-title">
          <RobotOutlined/>
          <span>智能分类分析</span>
        </div>
      </template>

      <template #extra>
        <a-button
            v-if="!loading && !classificationResult"
            size="small"
            type="primary"
            @click="handleAnalyze"
        >
          <template #icon>
            <ThunderboltOutlined/>
          </template>
          开始分析
        </a-button>
        <a-button
            v-if="classificationResult"
            size="small"
            @click="handleAnalyze"
        >
          <template #icon>
            <ReloadOutlined/>
          </template>
          重新分析
        </a-button>
      </template>

      <!-- 分析中状态 -->
      <div v-if="loading" class="analyzing-state">
        <a-spin tip="正在分析文档内容..."/>
      </div>

      <!-- 分析结果 -->
      <div v-else-if="classificationResult" class="result-content">
        <!-- 分类建议 -->
        <div class="result-section">
          <div class="section-title">分类建议</div>
          <div v-if="classificationResult.suggestedCategoryName" class="category-suggestion">
            <div class="suggestion-row">
              <span class="label">推荐分类：</span>
              <a-tag class="category-tag" color="blue">
                {{ classificationResult.suggestedCategoryName }}
              </a-tag>
            </div>
            <div class="suggestion-row">
              <span class="label">置信度：</span>
              <a-progress
                  :percent="Math.round(classificationResult.confidence * 100)"
                  :status="getConfidenceStatus(classificationResult.confidence)"
                  :stroke-color="getConfidenceColor(classificationResult.confidence)"
                  size="small"
                  style="width: 150px"
              />
              <span class="confidence-text">
                {{ getConfidenceText(classificationResult.confidence) }}
              </span>
            </div>

            <!-- 操作按钮 -->
            <div v-if="classificationResult.logId" class="action-buttons">
              <a-space>
                <a-button
                    v-if="classificationResult.shouldAutoApply || classificationResult.needsConfirmation"
                    :loading="acceptLoading"
                    size="small"
                    type="primary"
                    @click="handleAccept"
                >
                  <template #icon>
                    <CheckOutlined/>
                  </template>
                  {{ classificationResult.shouldAutoApply ? '确认应用' : '接受建议' }}
                </a-button>
                <a-button
                    :loading="rejectLoading"
                    size="small"
                    @click="handleReject"
                >
                  <template #icon>
                    <CloseOutlined/>
                  </template>
                  拒绝
                </a-button>
              </a-space>
            </div>
          </div>
          <div v-else class="no-suggestion">
            <a-alert
                message="置信度较低，建议手动选择分类"
                show-icon
                type="info"
            />
          </div>
        </div>

        <!-- 关键词 -->
        <div v-if="classificationResult.keywords?.length" class="result-section">
          <div class="section-title">提取的关键词</div>
          <div class="keywords-container">
            <a-tag
                v-for="(kw, index) in classificationResult.keywords"
                :key="index"
                :color="getKeywordColor(kw.weight)"
                class="keyword-tag"
            >
              {{ kw.keyword }}
              <span class="weight-badge">{{ Math.round(kw.weight * 100) }}%</span>
            </a-tag>
          </div>
        </div>

        <!-- 错误信息 -->
        <div v-if="classificationResult.error" class="error-section">
          <a-alert
              :message="classificationResult.error"
              show-icon
              type="warning"
          />
        </div>
      </div>

      <!-- 初始状态 -->
      <div v-else class="initial-state">
        <a-empty description="点击「开始分析」进行智能分类">
          <template #image>
            <RobotOutlined style="font-size: 48px; color: #bfbfbf"/>
          </template>
        </a-empty>
      </div>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import {ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {CheckOutlined, CloseOutlined, ReloadOutlined, RobotOutlined, ThunderboltOutlined} from '@ant-design/icons-vue'
import {
  materialApiClassificationLogsIntLogIdAcceptPost,
  materialApiClassificationLogsIntLogIdRejectPost,
  materialApiIntMaterialIdClassifyPost
} from '@/api/classificationController'

// Props
const props = defineProps<{
  materialId: number
  autoAnalyze?: boolean
}>()

// Emits
const emit = defineEmits<{
  (e: 'classified', result: API.ClassifyMaterialResponseModel): void
  (e: 'accepted', categoryId: number): void
  (e: 'rejected'): void
}>()

// 状态
const loading = ref(false)
const acceptLoading = ref(false)
const rejectLoading = ref(false)
const classificationResult = ref<API.ClassifyMaterialResponseModel | null>(null)

// 开始分析 - 必须在 watch 之前定义
const handleAnalyze = async () => {
  if (!props.materialId) return

  loading.value = true
  classificationResult.value = null

  try {
    const response: any = await materialApiIntMaterialIdClassifyPost({materialId: props.materialId})

    // 处理 axios 响应结构: response.data 是后端返回的 { code, message, data }
    const responseData = response.data || response

    if (responseData.code === 200 && responseData.data) {
      classificationResult.value = responseData.data
      emit('classified', responseData.data)

      if (responseData.data.shouldAutoApply) {
        message.success('已自动应用高置信度分类')
      }
    } else {
      message.error(responseData.message || '分析失败')
    }
  } catch (error: any) {
    console.error('分类分析失败:', error)
    message.error(error.message || '分类分析失败')
  } finally {
    loading.value = false
  }
}

// 监听 materialId 变化
watch(() => props.materialId, (newId) => {
  if (newId && props.autoAnalyze) {
    handleAnalyze()
  }
}, {immediate: true})

// 接受分类建议
const handleAccept = async () => {
  if (!classificationResult.value?.logId) return

  acceptLoading.value = true
  try {
    const response: any = await materialApiClassificationLogsIntLogIdAcceptPost({
      logId: classificationResult.value.logId
    })

    const responseData = response.data || response

    if (responseData.code === 200) {
      message.success('已接受分类建议')
      if (classificationResult.value.suggestedCategoryId) {
        emit('accepted', classificationResult.value.suggestedCategoryId)
      }
    } else {
      message.error(responseData.message || '操作失败')
    }
  } catch (error: any) {
    console.error('接受分类失败:', error)
    message.error(error.message || '操作失败')
  } finally {
    acceptLoading.value = false
  }
}

// 拒绝分类建议
const handleReject = async () => {
  if (!classificationResult.value?.logId) return

  rejectLoading.value = true
  try {
    const response: any = await materialApiClassificationLogsIntLogIdRejectPost({
      logId: classificationResult.value.logId
    })

    const responseData = response.data || response

    if (responseData.code === 200) {
      message.info('已拒绝分类建议')
      emit('rejected')
    } else {
      message.error(responseData.message || '操作失败')
    }
  } catch (error: any) {
    console.error('拒绝分类失败:', error)
    message.error(error.message || '操作失败')
  } finally {
    rejectLoading.value = false
  }
}

// 获取置信度状态
const getConfidenceStatus = (confidence: number): 'success' | 'normal' | 'exception' => {
  if (confidence >= 0.5) return 'success'  // 50%以上为高置信度
  if (confidence >= 0.3) return 'normal'   // 30%-50%为中等置信度
  return 'exception'
}

// 获取置信度颜色
const getConfidenceColor = (confidence: number): string => {
  if (confidence >= 0.5) return '#52c41a'  // 50%以上为绿色（高置信度）
  if (confidence >= 0.3) return '#faad14'  // 30%-50%为橙色（中等置信度）
  return '#ff4d4f'
}

// 获取置信度文本
const getConfidenceText = (confidence: number): string => {
  if (confidence >= 0.5) return '高'  // 50%以上为高置信度
  if (confidence >= 0.3) return '中'  // 30%-50%为中等置信度
  return '低'
}

// 获取关键词颜色
const getKeywordColor = (weight: number): string => {
  if (weight > 0.3) return 'blue'
  if (weight > 0.15) return 'cyan'
  return 'default'
}

// 暴露方法供父组件调用
defineExpose({
  analyze: handleAnalyze,
  result: classificationResult
})
</script>

<style scoped>
.classification-panel {
  margin-bottom: 16px;
}

.classification-card {
  border-radius: 8px;
}

.card-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
}

.analyzing-state {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
}

.result-content {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.result-section {
  padding: 12px;
  background: #fafafa;
  border-radius: 6px;
}

.section-title {
  font-weight: 500;
  margin-bottom: 12px;
  color: rgba(0, 0, 0, 0.85);
}

.category-suggestion {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.suggestion-row {
  display: flex;
  align-items: center;
  gap: 8px;
}

.suggestion-row .label {
  color: rgba(0, 0, 0, 0.65);
  min-width: 70px;
}

.category-tag {
  font-size: 14px;
  padding: 4px 12px;
}

.confidence-text {
  margin-left: 8px;
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
}

.action-buttons {
  margin-top: 8px;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.no-suggestion {
  padding: 8px 0;
}

.keywords-container {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.keyword-tag {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  padding: 4px 8px;
}

.weight-badge {
  font-size: 10px;
  opacity: 0.7;
}

.error-section {
  margin-top: 8px;
}

.initial-state {
  padding: 24px 0;
}
</style>
