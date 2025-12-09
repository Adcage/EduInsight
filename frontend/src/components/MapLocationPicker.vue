<template>
  <div class="map-location-picker">
    <!-- 控制栏 -->
    <div class="map-controls">
      <a-space>
        <a-button @click="locateCurrentPosition" :loading="locating">
          <template #icon><AimOutlined /></template>
          定位当前位置
        </a-button>
        <a-input-search
          v-if="editable"
          v-model:value="searchKeyword"
          placeholder="搜索地点"
          style="width: 300px"
          @search="handleSearch"
        >
          <template #enterButton>
            <SearchOutlined />
          </template>
        </a-input-search>
      </a-space>
    </div>

    <!-- 位置信息 - 仅教师端显示经纬度 -->
    <div class="map-info" v-if="selectedLocation && editable">
      <a-descriptions :column="2" size="small" bordered>
        <a-descriptions-item label="经度">
          {{ typeof selectedLocation.lng === 'number' ? selectedLocation.lng.toFixed(6) : '--' }}
        </a-descriptions-item>
        <a-descriptions-item label="纬度">
          {{ typeof selectedLocation.lat === 'number' ? selectedLocation.lat.toFixed(6) : '--' }}
        </a-descriptions-item>
        <a-descriptions-item label="地址" :span="2">
          {{ selectedLocation.address || '未知地址' }}
        </a-descriptions-item>
      </a-descriptions>
    </div>

    <div 
      ref="mapContainer" 
      class="map-container"
      :class="{ 'readonly': !editable }"
    ></div>

    <div class="map-footer" v-if="editable && showRadius">
      <div class="radius-control">
        <label>签到范围：</label>
        <a-slider
          v-model:value="radiusValue"
          :min="10"
          :max="500"
          :step="10"
          :marks="{ 10: '10m', 100: '100m', 200: '200m', 500: '500m' }"
          style="flex: 1; margin: 0 16px"
          @change="handleRadiusChange"
        />
        <span class="radius-value">{{ radiusValue }}米</span>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import { AimOutlined, SearchOutlined } from '@ant-design/icons-vue'
import AMapLoader from '@amap/amap-jsapi-loader'

interface LocationData {
  lng: number
  lat: number
  address?: string
  name?: string
}

interface Props {
  modelValue?: LocationData | null
  targetLocation?: LocationData | null  // 目标位置（学生端显示签到目标点）
  editable?: boolean  // 是否可编辑（教师端true，学生端false）
  showRadius?: boolean  // 是否显示半径控制
  defaultRadius?: number
  height?: string
  useBrowserFallback?: boolean  // 是否使用浏览器降级定位（默认false，只用高德）
}

interface Emits {
  (e: 'update:modelValue', value: LocationData | null): void
  (e: 'radiusChange', value: number): void
}

const props = withDefaults(defineProps<Props>(), {
  editable: true,
  showRadius: true,
  defaultRadius: 100,
  height: '400px',
  useBrowserFallback: false
})

const emits = defineEmits<Emits>()

const mapContainer = ref<HTMLDivElement>()
const searchKeyword = ref('')
const locating = ref(false)
const selectedLocation = ref<LocationData | null>(null)
const radiusValue = ref(props.defaultRadius)

let map: any = null
let marker: any = null  // 当前位置标记（蓝色）
let targetMarker: any = null  // 目标位置标记（红色）
let circle: any = null
let geolocation: any = null
let AMapObj: any = null
let placeSearch: any = null

onMounted(() => {
  initMap()
  
  // 如果有初始值，设置位置
  if (props.modelValue) {
    selectedLocation.value = props.modelValue
  }
})

onUnmounted(() => {
  if (map) {
    map.destroy()
  }
})

const initMap = () => {
  AMapLoader.load({
    key: '3f16bb96c7d7b71dca77021b552a416c',
    version: '2.0',
    plugins: ['AMap.AutoComplete', 'AMap.PlaceSearch', 'AMap.Circle', 'AMap.Marker', 'AMap.Geolocation'],
  })
  .then((AMap) => {
    AMapObj = AMap
    
    if (!mapContainer.value) return

    map = new AMap.Map(mapContainer.value, {
      zoom: 15,
      center: [116.397428, 39.90923], // 默认北京
      viewMode: '3D',
    })

    // 初始化地点搜索
    placeSearch = new AMap.PlaceSearch({
      city: '全国',
    })

    // 初始化定位 - 与教师端保持一致的高精度配置
    geolocation = new AMap.Geolocation({
      enableHighAccuracy: true,     // 启用高精度定位
      timeout: 15000,               // 超时时间15秒
      maximumAge: 0,                // 不使用缓存位置
      convert: true,                // 自动转换为高德坐标
      noIpLocate: 0,                // 优先使用精确定位，IP定位作为备选
      noGeoLocation: 0,             // 优先使用浏览器定位
      GeoLocationFirst: true,       // 优先使用浏览器定位而非IP定位
      useNative: true,              // 优先使用浏览器原生定位
      showButton: false,            // 不显示定位按钮（我们自己控制）
      showMarker: false,            // 不显示定位标记（我们自己控制）
      showCircle: false,            // 不显示精度圆圈（我们自己控制）
      panToLocation: false,         // 不自动移动地图（我们自己控制）
      zoomToAccuracy: false         // 不自动调整缩放（我们自己控制）
    })

    // 如果可编辑，添加点击事件
    if (props.editable) {
      map.on('click', (e: any) => {
        handleMapClick(e.lnglat)
      })
    }

    // 如果有目标位置（学生端），显示目标位置标记
    if (props.targetLocation) {
      showTargetLocation(props.targetLocation)
      map.setCenter([props.targetLocation.lng, props.targetLocation.lat])
    }
    
    // 如果有初始位置，显示在地图上
    if (selectedLocation.value) {
      updateLocationOnMap(selectedLocation.value.lng, selectedLocation.value.lat)
      if (!props.targetLocation) {
        map.setCenter([selectedLocation.value.lng, selectedLocation.value.lat])
      }
    }
  })
  .catch((e) => {
    console.error('地图加载失败:', e)
    message.error('地图加载失败，请刷新页面重试')
  })
}

// 显示目标位置标记（红色）
const showTargetLocation = (location: LocationData) => {
  if (!AMapObj || !map) return
  
  const center = new AMapObj.LngLat(location.lng, location.lat)
  
  // 创建或更新目标位置标记（红色）
  if (targetMarker) {
    targetMarker.setPosition(center)
  } else {
    targetMarker = new AMapObj.Marker({
      position: center,
      map: map,
      icon: new AMapObj.Icon({
        size: new AMapObj.Size(25, 34),
        image: '//a.amap.com/jsapi_demos/static/demo-center/icons/poi-marker-red.png',
        imageSize: new AMapObj.Size(25, 34)
      }),
      title: location.name || '签到位置',
      label: {
        content: location.name || '签到位置',
        offset: new AMapObj.Pixel(0, -34),
        direction: 'top'
      }
    })
  }
  
  // 显示签到范围圆圈
  if (props.showRadius || props.defaultRadius) {
    if (circle) {
      circle.setCenter(center)
      circle.setRadius(radiusValue.value)
    } else {
      circle = new AMapObj.Circle({
        center: center,
        radius: radiusValue.value,
        strokeColor: '#ff4d4f',
        strokeWeight: 2,
        fillColor: '#ff4d4f',
        fillOpacity: 0.1,
        map: map
      })
    }
  }
}

const locateCurrentPosition = () => {
  console.log('[MapLocationPicker] 开始定位...')
  
  if (!geolocation) {
    console.error('[MapLocationPicker] geolocation对象未初始化')
    message.warning('地图组件未就绪，请稍后再试')
    return
  }
  
  if (!map) {
    console.error('[MapLocationPicker] map对象未初始化')
    message.warning('地图未加载完成，请稍后再试')
    return
  }
  
  locating.value = true
  message.loading('正在获取位置...', 0)
  
  console.log('[MapLocationPicker] 调用 geolocation.getCurrentPosition')
  
  geolocation.getCurrentPosition((status: string, result: any) => {
    console.log('[MapLocationPicker] 定位回调 - status:', status, 'result:', result)
    message.destroy()
    locating.value = false
    
    if (status === 'complete') {
      console.log('[MapLocationPicker] 定位成功，位置:', result.position)
      handleMapClick(result.position)
      message.success('定位成功')
    } else {
      console.error('[MapLocationPicker] 定位失败 - info:', result.info, 'message:', result.message)
      
      // 根据不同的错误类型给出不同的提示
      let errorMsg = '定位失败'
      let errorDetail = ''
      
      if (result.message && result.message.includes('timeout')) {
        errorMsg = '定位超时'
        errorDetail = '网络较慢或GPS信号弱，请尝试：\n1. 检查网络连接\n2. 移动到窗边或室外\n3. 使用搜索功能选择位置'
      } else if (result.message && result.message.includes('permission')) {
        errorMsg = '定位权限被拒绝'
        errorDetail = '请在浏览器设置中允许位置访问'
      } else if (result.message && result.message.includes('ipLocation failed')) {
        errorMsg = '定位服务暂时不可用'
        errorDetail = '建议使用搜索功能选择位置'
      } else if (result.info === 'FAILED') {
        errorMsg = '定位服务失败'
        errorDetail = '请检查网络连接或使用搜索功能'
      }
      
      message.error({
        content: errorMsg,
        duration: 5
      })
      
      // 在控制台输出详细信息
      if (errorDetail) {
        console.warn('[MapLocationPicker] 定位失败详情:', errorDetail)
      }
      
      // 只在启用降级时才使用浏览器原生定位
      if (props.useBrowserFallback) {
        tryBrowserGeolocation()
      }
    }
  })
}

// 降级方案：使用浏览器原生定位（高精度配置）
const tryBrowserGeolocation = () => {
  console.log('[MapLocationPicker] 尝试使用浏览器原生定位...')
  
  if (!navigator.geolocation) {
    console.error('[MapLocationPicker] 浏览器不支持地理定位')
    return
  }
  
  message.loading('尝试使用浏览器高精度定位...', 0)
  
  navigator.geolocation.getCurrentPosition(
    (position) => {
      message.destroy()
      console.log('[MapLocationPicker] 浏览器定位成功:', position.coords)
      console.log('[MapLocationPicker] 定位精度:', position.coords.accuracy, '米')
      
      const location = {
        lng: position.coords.longitude,
        lat: position.coords.latitude
      }
      
      handleMapClick(location)
      
      // 显示定位精度信息
      const accuracy = Math.round(position.coords.accuracy)
      message.success(`定位成功（精度: ±${accuracy}米）`)
    },
    (error) => {
      message.destroy()
      console.error('[MapLocationPicker] 浏览器定位也失败:', error)
      
      let errorMsg = '所有定位方式均失败'
      switch (error.code) {
        case error.PERMISSION_DENIED:
          errorMsg = '位置权限被拒绝，请在浏览器设置中允许位置访问'
          break
        case error.POSITION_UNAVAILABLE:
          errorMsg = '位置信息不可用，请检查设备GPS设置'
          break
        case error.TIMEOUT:
          errorMsg = '定位超时，请检查网络连接'
          break
      }
      
      message.error(errorMsg)
    },
    {
      enableHighAccuracy: true,   // 启用高精度定位（使用GPS）
      timeout: 15000,             // 增加超时时间到15秒
      maximumAge: 0               // 不使用缓存位置，每次都重新获取
    }
  )
}

const handleSearch = () => {
  if (!searchKeyword.value.trim()) {
    message.warning('请输入搜索关键词')
    return
  }

  if (!placeSearch) {
    message.warning('搜索功能未就绪')
    return
  }

  placeSearch.search(searchKeyword.value, (status: string, result: any) => {
    if (status === 'complete' && result.poiList && result.poiList.pois.length > 0) {
      const poi = result.poiList.pois[0]
      const location = poi.location
      handleMapClick(location)
      message.success(`已定位到：${poi.name}`)
    } else {
      message.error('未找到相关地点')
    }
  })
}

const handleMapClick = (lnglat: any) => {
  const { lng, lat } = lnglat
  updateLocationOnMap(lng, lat)
  
  selectedLocation.value = {
    lng,
    lat,
    address: `${lng.toFixed(6)}, ${lat.toFixed(6)}`,
    name: '已选位置'
  }
  
  emits('update:modelValue', selectedLocation.value)
  
  // 逆地理编码获取地址
  if (AMapObj) {
    const geocoder = new AMapObj.Geocoder()
    geocoder.getAddress([lng, lat], (status: string, result: any) => {
      if (status === 'complete' && result.info === 'OK') {
        if (selectedLocation.value) {
          selectedLocation.value.address = result.regeocode.formattedAddress
          emits('update:modelValue', selectedLocation.value)
        }
      }
    })
  }
}

const updateLocationOnMap = (lng: number, lat: number) => {
  if (!AMapObj || !map) return
  
  const center = new AMapObj.LngLat(lng, lat)

  if (marker) {
    marker.setPosition(center)
  } else {
    marker = new AMapObj.Marker({
      position: center,
      map: map
    })
  }

  if (props.showRadius) {
    if (circle) {
      circle.setCenter(center)
      circle.setRadius(radiusValue.value)
    } else {
      circle = new AMapObj.Circle({
        center: center,
        radius: radiusValue.value,
        strokeColor: '#1890ff',
        strokeWeight: 2,
        fillColor: '#1890ff',
        fillOpacity: 0.2,
        map: map
      })
    }
  }

  map.setCenter(center)
}

const handleRadiusChange = (value: number) => {
  if (circle) {
    circle.setRadius(value)
  }
  emits('radiusChange', value)
}

// 监听外部位置变化
watch(() => props.modelValue, (newVal) => {
  if (newVal && map) {
    selectedLocation.value = newVal
    updateLocationOnMap(newVal.lng, newVal.lat)
    map.setCenter([newVal.lng, newVal.lat])
  }
})

// 监听半径变化
watch(() => props.defaultRadius, (newVal) => {
  radiusValue.value = newVal
  if (circle) {
    circle.setRadius(newVal)
  }
})
</script>

<style scoped lang="scss">
.map-location-picker {
  width: 100%;
}

.map-controls {
  margin-bottom: 16px;
}

.map-info {
  margin-bottom: 16px;
}

.map-container {
  width: 100%;
  height: v-bind(height);
  border: 1px solid #d9d9d9;
  border-radius: 8px;
  overflow: hidden;
  
  &.readonly {
    cursor: default;
  }
}

.map-footer {
  margin-top: 16px;
}

.radius-control {
  display: flex;
  align-items: center;
  padding: 12px 16px;
  background: #f5f5f5;
  border-radius: 8px;
  
  label {
    font-weight: 600;
    color: #262626;
    white-space: nowrap;
  }
  
  .radius-value {
    font-weight: 600;
    color: #1890ff;
    white-space: nowrap;
    min-width: 60px;
    text-align: right;
  }
}
</style>
