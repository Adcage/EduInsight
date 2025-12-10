<template>
  <div class="barrage-wall" ref="wallRef">
    <!-- 控制栏 -->
    <div class="barrage-controls">
      <a-space>
        <a-select v-model:value="speed" size="small" style="width: 100px" @change="handleSpeedChange">
          <a-select-option :value="1">慢速</a-select-option>
          <a-select-option :value="2">正常</a-select-option>
          <a-select-option :value="3">快速</a-select-option>
        </a-select>

        <a-checkbox v-model:checked="showAnswerOnly"> 只显示答案弹幕 </a-checkbox>

        <a-button size="small" danger @click="clearBarrages">
          <template #icon><DeleteOutlined /></template>
          清空
        </a-button>

        <a-badge :count="props.totalCount" :overflow-count="999" show-zero>
          <span style="color: #fff; margin-left: 8px">弹幕总数</span>
        </a-badge>
      </a-space>
    </div>

    <!-- 弹幕容器 -->
    <div class="barrage-container" :style="{ height: height + 'px' }">
      <div
        v-for="barrage in displayBarrages"
        :key="barrage.id"
        :class="['barrage-item', getBarrageClass(barrage)]"
        :style="getBarrageStyle(barrage)"
      >
        {{ barrage.user_name }}：{{ barrage.content }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { DeleteOutlined } from '@ant-design/icons-vue'

// Props
interface Props {
  courseId: number
  height?: number
  autoScroll?: boolean
  showAnswerOnlyProp?: boolean
  maxBarrages?: number
  totalCount?: number
}

const props = withDefaults(defineProps<Props>(), {
  height: 500,
  autoScroll: true,
  showAnswerOnlyProp: false,
  maxBarrages: 50,
  totalCount: 0,
})



// 数据
const wallRef = ref<HTMLElement>()
const barrages = ref<any[]>([])
const speed = ref(2) // 1=慢, 2=正常, 3=快
const showAnswerOnly = ref(props.showAnswerOnlyProp)

// 轨道系统
const TRACK_HEIGHT = 50 // 每条轨道的高度
const tracks = ref<number[]>([]) // 记录每条轨道最后一条弹幕的结束时间

// 定时器管理
const pendingTimers = ref<number[]>([]) // 记录所有待执行的定时器

// 计算显示的弹幕
const displayBarrages = computed(() => {
  if (showAnswerOnly.value) {
    return barrages.value.filter((b) => b.question_id !== null)
  }
  return barrages.value
})

// 获取可用轨道
const getAvailableTrack = () => {
  const now = Date.now()
  const maxTracks = Math.floor(props.height / TRACK_HEIGHT)
  
  // 初始化轨道
  if (tracks.value.length === 0) {
    tracks.value = new Array(maxTracks).fill(0)
  }
  
  // 找到最早可用的轨道
  for (let i = 0; i < tracks.value.length; i++) {
    if (tracks.value[i] <= now) {
      return i
    }
  }
  
  // 如果所有轨道都被占用，返回最早结束的轨道
  let minTrack = 0
  let minTime = tracks.value[0]
  for (let i = 1; i < tracks.value.length; i++) {
    if (tracks.value[i] < minTime) {
      minTime = tracks.value[i]
      minTrack = i
    }
  }
  return minTrack
}

// 添加弹幕
const addBarrage = (barrage: any) => {
  // 限制弹幕数量
  if (barrages.value.length >= props.maxBarrages) {
    barrages.value.shift() // 移除最旧的弹幕
  }

  // 获取可用轨道
  const trackIndex = getAvailableTrack()
  const duration = getAnimationDuration()
  
  // 添加动画属性和移除定时器ID
  const removeTimerId = setTimeout(() => {
    removeBarrage(newBarrage.id)
  }, duration * 1000)
  
  const newBarrage = {
    ...barrage,
    top: trackIndex * TRACK_HEIGHT + 10, // 使用轨道位置
    animationDuration: duration,
    timestamp: Date.now(),
    removeTimerId, // 保存移除定时器ID
  }

  barrages.value.push(newBarrage)
  
  // 更新轨道占用时间（弹幕完全通过需要的时间）
  tracks.value[trackIndex] = Date.now() + duration * 1000
}

// 批量添加弹幕
const addBarrages = (newBarrages: any[]) => {
  // 清除之前的定时器
  clearPendingTimers()
  
  newBarrages.forEach((barrage, index) => {
    // 延迟添加，避免同时出现
    // 增加间隔到800ms，让弹幕更自然地依次出现
    const timerId = setTimeout(() => {
      addBarrage(barrage)
      // 从待执行列表中移除
      const timerIndex = pendingTimers.value.indexOf(timerId)
      if (timerIndex > -1) {
        pendingTimers.value.splice(timerIndex, 1)
      }
    }, index * 800)
    
    // 记录定时器ID
    pendingTimers.value.push(timerId)
  })
}

// 清除所有待执行的定时器
const clearPendingTimers = () => {
  pendingTimers.value.forEach(timerId => clearTimeout(timerId))
  pendingTimers.value = []
}

// 移除弹幕
const removeBarrage = (id: number) => {
  const index = barrages.value.findIndex((b) => b.id === id)
  if (index > -1) {
    barrages.value.splice(index, 1)
  }
}

// 清空弹幕
const clearBarrages = () => {
  clearPendingTimers() // 清除待执行的定时器
  barrages.value = []
}

// 速度变化
const handleSpeedChange = () => {
  // 重新计算所有弹幕的动画时长
  barrages.value.forEach((barrage) => {
    barrage.animationDuration = getAnimationDuration()
  })
}

// 获取动画时长
const getAnimationDuration = () => {
  const baseSpeed = 15 // 基础速度（秒）- 增加到15秒让弹幕更慢
  return baseSpeed / speed.value
}

// 获取弹幕样式
const getBarrageStyle = (barrage: any) => {
  return {
    top: `${barrage.top}px`,
    animationDuration: `${barrage.animationDuration}s`,
  }
}

// 获取弹幕类名
const getBarrageClass = (barrage: any) => {
  return barrage.question_id ? 'barrage-answer' : 'barrage-free'
}



// 监听showAnswerOnlyProp变化
watch(
  () => props.showAnswerOnlyProp,
  (newVal) => {
    showAnswerOnly.value = newVal
  }
)

// 暴露方法给父组件
defineExpose({
  addBarrage,
  addBarrages,
  clearBarrages,
  removeBarrage,
})
</script>

<style scoped lang="scss">
.barrage-wall {
  position: relative;
  background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
}

.barrage-controls {
  position: absolute;
  top: 10px;
  right: 10px;
  z-index: 10;
  background: rgba(0, 0, 0, 0.8);
  padding: 8px 12px;
  border-radius: 6px;
  backdrop-filter: blur(10px);
}

.barrage-container {
  position: relative;
  width: 100%;
  overflow: hidden;
}

.barrage-item {
  position: absolute;
  right: 0;
  white-space: nowrap;
  font-size: 18px;
  font-weight: 600;
  padding: 6px 16px;
  border-radius: 20px;
  animation: barrage-move linear;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
}

// 答案弹幕（绿色）
.barrage-answer {
  background: linear-gradient(135deg, #52c41a 0%, #73d13d 100%);
  color: #fff;
  border: 2px solid #95de64;
  box-shadow: 0 2px 8px rgba(82, 196, 26, 0.4);

  &:hover {
    box-shadow: 0 4px 16px rgba(82, 196, 26, 0.6);
  }
}

// 自由弹幕（蓝色）
.barrage-free {
  background: linear-gradient(135deg, #1890ff 0%, #40a9ff 100%);
  color: #fff;
  border: 2px solid #69c0ff;
  box-shadow: 0 2px 8px rgba(24, 144, 255, 0.4);

  &:hover {
    box-shadow: 0 4px 16px rgba(24, 144, 255, 0.6);
  }
}



// 弹幕移动动画
@keyframes barrage-move {
  from {
    transform: translateX(0);
  }
  to {
    transform: translateX(calc(-100% - 100vw));
  }
}
</style>
