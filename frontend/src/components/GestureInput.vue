<template>
  <div class="gesture-input-container">
    <p v-if="hint" class="gesture-hint-text">{{ hint }}</p>
    
    <div 
      class="gesture-box"
      :style="{ width: size + 'px', height: size + 'px' }"
      @mouseleave="endGesture"
      @mouseup="endGesture"
    >
      <!-- Lines -->
      <svg class="gesture-svg">
        <line 
          v-for="(line, idx) in gestureLines" 
          :key="idx"
          :x1="line.start.x" 
          :y1="line.start.y" 
          :x2="line.end.x" 
          :y2="line.end.y"
          stroke="#1890ff" 
          stroke-width="4" 
          stroke-linecap="round" 
        />
        <line 
          v-if="currentLine"
          :x1="currentLine.start.x" 
          :y1="currentLine.start.y" 
          :x2="currentLine.end.x" 
          :y2="currentLine.end.y"
          stroke="#1890ff" 
          stroke-width="4" 
          stroke-linecap="round" 
          opacity="0.5"
        />
      </svg>

      <!-- Points -->
      <div 
        v-for="(point, index) in gesturePoints" 
        :key="index"
        class="gesture-point"
        :class="isPointSelected(index) ? 'point-selected' : ''"
        :style="{
          left: point.x - 30 + 'px',
          top: point.y - 30 + 'px',
        }"
        @mousedown.prevent="startGesture(index)"
        @mouseenter="enterPoint(index)"
      >
        <div class="point-inner" :class="isPointSelected(index) ? 'inner-selected' : ''"></div>
      </div>
    </div>

    <div v-if="showActions" class="gesture-actions">
      <a-button @click="resetGesture">
        <template #icon><ClearOutlined /></template>
        重置
      </a-button>
      <a-button 
        v-if="showCode" 
        type="primary" 
        @click="confirmGesture" 
        :disabled="gesturePath.length < 4"
      >
        <template #icon><KeyOutlined /></template>
        确认使用
      </a-button>
    </div>

    <div v-if="gestureCode && showCode" class="gesture-code-display">
      <a-alert type="success" show-icon>
        <template #message>
          <div class="code-content">
            <span class="code-label">手势码：</span>
            <span class="code-value">{{ gestureCode }}</span>
            <a-button size="small" type="link" @click="copyCode">
              <template #icon><CopyOutlined /></template>
              复制
            </a-button>
          </div>
        </template>
      </a-alert>
      <div class="gesture-status">
        已连接 {{ gesturePath.length }} 个点
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, watch, computed } from 'vue'
import { message } from 'ant-design-vue'
import { ClearOutlined, KeyOutlined, CopyOutlined } from '@ant-design/icons-vue'

interface Point {
  x: number
  y: number
}

interface Props {
  modelValue?: string
  hint?: string
  showCode?: boolean  // 是否显示生成手势码功能（教师端用）
  showActions?: boolean  // 是否显示操作按钮
  size?: number
}

interface GestureData {
  points: number[]
  width: number
  height: number
  duration?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'gestureChange', points: number[]): void
  (e: 'gestureDataChange', data: GestureData): void
}

const props = withDefaults(defineProps<Props>(), {
  hint: '请绘制解锁图案（至少连接4个点）',
  showCode: false,
  showActions: true,
  size: 300
})

const emits = defineEmits<Emits>()

const isDrawing = ref(false)
const gesturePath = ref<number[]>([])
const currentLine = ref<any>(null)
const gestureCode = ref('')

// 计算9个点的位置（3x3网格）
const gesturePoints = computed(() => {
  const points = []
  // 根据size动态计算位置
  const ratio = props.size / 300
  const positions = [50 * ratio, 150 * ratio, 250 * ratio]
  for (let r of positions) {
    for (let c of positions) {
      points.push({ x: c, y: r })
    }
  }
  return points // 0-8
})

// 计算连接线
const gestureLines = computed(() => {
  const lines = []
  for (let i = 0; i < gesturePath.value.length - 1; i++) {
    const startIdx = gesturePath.value[i]
    const endIdx = gesturePath.value[i + 1]
    if (startIdx !== undefined && endIdx !== undefined && gesturePoints.value[startIdx] && gesturePoints.value[endIdx]) {
      lines.push({
        start: gesturePoints.value[startIdx],
        end: gesturePoints.value[endIdx]
      })
    }
  }
  return lines
})

const isPointSelected = (index: number) => gesturePath.value.includes(index)

const startGesture = (index: number) => {
  isDrawing.value = true
  gesturePath.value = [index]
}

const enterPoint = (index: number) => {
  if (!isDrawing.value) return
  if (!gesturePath.value.includes(index)) {
    gesturePath.value.push(index)
  }
}

const endGesture = () => {
  if (isDrawing.value && gesturePath.value.length > 0) {
    isDrawing.value = false
    currentLine.value = null
    emits('gestureChange', gesturePath.value)
    
    // 发送完整的手势数据
    const gestureData: GestureData = {
      points: gesturePath.value,
      width: props.size,
      height: props.size
    }
    emits('gestureDataChange', gestureData)
    
    // 如果不显示手势码生成，自动生成手势码
    if (!props.showCode && gesturePath.value.length >= 4) {
      confirmGesture()
    }
  }
}

const resetGesture = () => {
  gesturePath.value = []
  isDrawing.value = false
  currentLine.value = null
  gestureCode.value = ''
  emits('update:modelValue', '')
  emits('gestureChange', [])
}

const confirmGesture = () => {
  if (gesturePath.value.length < 4) {
    message.warning('手势密码至少连接4个点')
    return
  }
  
  // 将点的索引转换为手势码
  const code = gesturePath.value.join('-')
  gestureCode.value = code
  emits('update:modelValue', code)
  
  if (props.showCode) {
    message.success('手势码已生成')
  }
}


// 复制手势码
const copyCode = async () => {
  try {
    await navigator.clipboard.writeText(gestureCode.value)
    message.success('手势码已复制到剪贴板')
  } catch (error) {
    message.error('复制失败，请手动复制')
  }
}

// 监听外部手势码变化
watch(() => props.modelValue, (newVal) => {
  if (!newVal && gesturePath.value.length > 0) {
    resetGesture()
  } else if (newVal) {
    gestureCode.value = newVal
  }
})
</script>

<style scoped lang="scss">
.gesture-input-container {
  width: 100%;
}

.gesture-hint-text {
  text-align: center;
  color: #8c8c8c;
  font-size: 14px;
  margin-bottom: 16px;
}

.gesture-box {
  position: relative;
  background: white;
  border: 2px solid #d9d9d9;
  border-radius: 8px;
  user-select: none;
  margin: 0 auto;
  
  &:hover {
    border-color: #1890ff;
  }
}

.gesture-svg {
  position: absolute;
  inset: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  z-index: 10;
}

.gesture-point {
  position: absolute;
  width: 60px;
  height: 60px;
  border-radius: 50%;
  border: 2px solid #d9d9d9;
  background: white;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s ease;
  z-index: 20;
  cursor: pointer;
  
  &.point-selected {
    border-color: #1890ff;
    background: #e6f7ff;
  }
}

.point-inner {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: #d9d9d9;
  transition: all 0.2s ease;
  
  &.inner-selected {
    background: #1890ff;
  }
}

.gesture-actions {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
}

.gesture-code-display {
  margin-bottom: 16px;
  
  .code-content {
    display: flex;
    align-items: center;
    gap: 8px;
    
    .code-label {
      font-weight: 600;
    }
    
    .code-value {
      font-family: monospace;
      font-size: 18px;
      color: #1890ff;
      letter-spacing: 2px;
    }
  }
}

.gesture-status {
  margin-top: 12px;
  font-size: 13px;
  color: #8c8c8c;
  text-align: center;
}
</style>
