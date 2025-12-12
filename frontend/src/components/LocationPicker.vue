<template>
  <div class="location-picker-container">
    <div class="location-display">
      <div v-if="locationLoading" class="location-loading">
        <a-spin/>
        <span>正在获取位置...</span>
      </div>

      <div v-else-if="locationError" class="location-error">
        <a-alert :message="locationError" show-icon type="error"/>
        <a-button style="margin-top: 12px" type="primary" @click="getCurrentLocation">
          <template #icon>
            <ReloadOutlined/>
          </template>
          重新获取
        </a-button>
      </div>

      <div v-else-if="currentLocation" class="location-info">
        <div class="location-item">
          <EnvironmentOutlined class="location-icon"/>
          <div class="location-details">
            <div class="location-coords">
              <span class="coord-label">纬度：</span>
              <span class="coord-value">{{ currentLocation.latitude.toFixed(6) }}</span>
              <span class="coord-label" style="margin-left: 16px">经度：</span>
              <span class="coord-value">{{ currentLocation.longitude.toFixed(6) }}</span>
            </div>
            <div v-if="currentLocation.address" class="location-address">
              {{ currentLocation.address }}
            </div>
          </div>
        </div>

        <div v-if="showRange" class="location-range">
          <div class="range-label">签到范围（米）：</div>
          <a-slider
              v-model:value="rangeValue"
              :marks="{ 10: '10m', 100: '100m', 200: '200m', 500: '500m' }"
              :max="500"
              :min="10"
              :step="10"
              @change="handleRangeChange"
          />
          <div class="range-value">{{ rangeValue }} 米</div>
        </div>
      </div>

      <div v-else class="location-empty">
        <EnvironmentOutlined style="font-size: 48px; color: #bfbfbf; margin-bottom: 16px"/>
        <p>{{ placeholder }}</p>
        <div class="location-buttons">
          <a-button type="primary" @click="getCurrentLocation">
            <template #icon>
              <AimOutlined/>
            </template>
            获取当前位置
          </a-button>
          <a-button @click="useMockLocation">
            <template #icon>
              <EnvironmentOutlined/>
            </template>
            使用模拟位置
          </a-button>
        </div>
      </div>
    </div>

    <div v-if="showMap && currentLocation" class="location-map">
      <div class="map-placeholder">
        <EnvironmentOutlined style="font-size: 64px; color: #1890ff"/>
        <p>地图显示区域</p>
        <p class="map-hint">（可集成高德地图或百度地图）</p>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {AimOutlined, EnvironmentOutlined, ReloadOutlined} from '@ant-design/icons-vue'

interface Location {
  latitude: number
  longitude: number
  address?: string
}

interface Props {
  modelValue?: Location | null
  placeholder?: string
  showMap?: boolean
  showRange?: boolean
  defaultRange?: number
  autoGet?: boolean  // 是否自动获取位置
}

interface Emits {
  (e: 'update:modelValue', value: Location | null): void

  (e: 'rangeChange', value: number): void
}

const props = withDefaults(defineProps<Props>(), {
  placeholder: '点击按钮获取当前位置',
  showMap: false,
  showRange: false,
  defaultRange: 100,
  autoGet: false
})

const emits = defineEmits<Emits>()

const locationLoading = ref(false)
const locationError = ref('')
const currentLocation = ref<Location | null>(null)
const rangeValue = ref(props.defaultRange)

onMounted(() => {
  if (props.autoGet) {
    getCurrentLocation()
  }

  // 如果有初始值，设置当前位置
  if (props.modelValue) {
    currentLocation.value = props.modelValue
  }
})

// 获取当前位置
const getCurrentLocation = () => {
  console.log('[LocationPicker] 开始获取位置...')

  if (!navigator.geolocation) {
    const errorMsg = '您的浏览器不支持地理定位'
    console.error('[LocationPicker]', errorMsg)
    locationError.value = errorMsg
    message.error(errorMsg)
    return
  }

  locationLoading.value = true
  locationError.value = ''

  console.log('[LocationPicker] 调用 navigator.geolocation.getCurrentPosition...')

  navigator.geolocation.getCurrentPosition(
      (position) => {
        console.log('[LocationPicker] 位置获取成功:', position.coords)
        const location: Location = {
          latitude: position.coords.latitude,
          longitude: position.coords.longitude
        }

        currentLocation.value = location
        locationLoading.value = false
        emits('update:modelValue', location)
        message.success(`位置获取成功！纬度: ${location.latitude.toFixed(6)}, 经度: ${location.longitude.toFixed(6)}`)

        // 可以调用逆地理编码API获取地址
        // getAddressFromCoords(location.latitude, location.longitude)
      },
      (error) => {
        console.error('[LocationPicker] 位置获取失败:', error)
        locationLoading.value = false
        let errorMsg = ''

        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMsg = '位置权限被拒绝。请在浏览器地址栏左侧点击锁图标，允许位置访问权限。'
            console.error('[LocationPicker] PERMISSION_DENIED')
            break
          case error.POSITION_UNAVAILABLE:
            errorMsg = '位置信息不可用。请确保设备GPS已开启，或尝试使用模拟位置。'
            console.error('[LocationPicker] POSITION_UNAVAILABLE')
            break
          case error.TIMEOUT:
            errorMsg = '获取位置超时（10秒）。请检查网络连接或GPS信号。'
            console.error('[LocationPicker] TIMEOUT')
            break
          default:
            errorMsg = `获取位置失败（错误代码: ${error.code}）。${error.message || ''}`
            console.error('[LocationPicker] UNKNOWN ERROR:', error.code, error.message)
        }

        locationError.value = errorMsg
        message.error(errorMsg)
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 0
      }
  )

  console.log('[LocationPicker] getCurrentPosition 已调用，等待回调...')
}

// 使用模拟位置（用于测试）
const useMockLocation = () => {
  console.log('[LocationPicker] 使用模拟位置')
  // 使用北京天安门的坐标作为模拟位置
  const mockLocation: Location = {
    latitude: 39.9042,
    longitude: 116.4074,
    address: '北京市东城区天安门广场（模拟位置）'
  }

  currentLocation.value = mockLocation
  emits('update:modelValue', mockLocation)
  message.success('已使用模拟位置（北京天安门）')
}

// 处理范围变化
const handleRangeChange = (value: number) => {
  emits('rangeChange', value)
}

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal) {
    currentLocation.value = newVal
  }
})

watch(() => props.defaultRange, (newVal) => {
  rangeValue.value = newVal
})
</script>

<style lang="scss" scoped>
.location-picker-container {
  width: 100%;
}

.location-display {
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  padding: 20px;
  background: #fafafa;
  min-height: 200px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.location-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #666;
}

.location-error {
  width: 100%;
  text-align: center;
}

.location-info {
  width: 100%;
}

.location-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  background: white;
  border-radius: 8px;
  margin-bottom: 16px;
}

.location-icon {
  font-size: 24px;
  color: #1890ff;
  flex-shrink: 0;
  margin-top: 4px;
}

.location-details {
  flex: 1;
}

.location-coords {
  font-size: 14px;
  margin-bottom: 8px;

  .coord-label {
    color: #8c8c8c;
  }

  .coord-value {
    font-family: monospace;
    font-weight: 600;
    color: #262626;
  }
}

.location-address {
  font-size: 13px;
  color: #595959;
  line-height: 1.5;
}

.location-range {
  padding: 16px;
  background: white;
  border-radius: 8px;

  .range-label {
    font-size: 14px;
    font-weight: 600;
    color: #262626;
    margin-bottom: 16px;
  }

  .range-value {
    text-align: center;
    font-size: 16px;
    font-weight: 600;
    color: #1890ff;
    margin-top: 8px;
  }
}

.location-empty {
  text-align: center;
  color: #8c8c8c;

  p {
    margin: 0 0 16px 0;
  }
}

.location-buttons {
  display: flex;
  gap: 12px;
  justify-content: center;
}

.location-map {
  margin-top: 16px;
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  height: 300px;
  overflow: hidden;
}

.map-placeholder {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: #f5f5f5;
  color: #8c8c8c;

  p {
    margin: 8px 0;
  }

  .map-hint {
    font-size: 12px;
    color: #bfbfbf;
  }
}
</style>
