<template>
  <div class="map-location-picker">
    <div class="map-wrapper">
      <!-- 搜索框 - 浮动在左上角 -->
      <div v-if="editable" class="absolute top-4 left-4 z-10 w-72 bg-white rounded shadow p-2">
        <a-input-search
            v-model:value="searchKeyword"
            allow-clear
            placeholder="搜索地点..."
            @search="handleSearch"
        />
        <div v-if="searchResults.length > 0" class="mt-2 max-h-60 overflow-y-auto bg-white border-t">
          <div
              v-for="(item, index) in searchResults"
              :key="index"
              class="p-2 hover:bg-gray-100 cursor-pointer text-sm"
              @click="selectSearchResult(item)"
          >
            <div class="font-medium">{{ item.name }}</div>
            <div class="text-xs text-gray-500">{{ item.address }}</div>
          </div>
        </div>
      </div>

      <!-- 定位按钮 - 浮动在右上角 -->
      <div
          :class="{ 'opacity-50 cursor-not-allowed': locating }"
          class="absolute top-4 right-4 z-10 bg-white rounded shadow p-2 cursor-pointer hover:bg-gray-50 flex items-center justify-center w-10 h-10"
          title="定位当前位置"
          @click="locateCurrentPosition"
      >
        <AimOutlined class="text-xl text-gray-600"/>
      </div>

      <!-- 地图容器 -->
      <div
          ref="mapContainer"
          :class="{ 'readonly': !editable }"
          class="map-container"
      ></div>

      <!-- 底部半径控制 -->
      <div v-if="showRadius" class="absolute bottom-4 left-4 right-4 z-10 bg-white rounded shadow p-4">
        <div class="flex items-center">
          <span class="text-sm font-medium text-gray-700 mr-4 whitespace-nowrap">签到范围半径:</span>
          <a-slider
              v-model:value="radiusValue"
              :marks="{ 100: '100m', 500: '500m', 1000: '1000m' }"
              :max="1000"
              :min="100"
              :step="50"
              class="flex-1"
              @change="handleRadiusChange"
          />
          <span class="text-sm font-medium text-blue-600 ml-4 whitespace-nowrap">{{ radiusValue }}米</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, onUnmounted, ref, watch} from 'vue'
import {message} from 'ant-design-vue'
import {AimOutlined} from '@ant-design/icons-vue'
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
const searchResults = ref<any[]>([])
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
          resizeEnable: true  // 启用地图自适应（与教师端保持一致）
        })

        // 初始化地点搜索
        placeSearch = new AMap.PlaceSearch({
          city: '全国',
        })

        // 初始化定位 - 高精度配置（优化版）
        geolocation = new AMap.Geolocation({
          enableHighAccuracy: true,    // 启用高精度定位（使用GPS）
          timeout: 30000,               // 超时时间30秒（给GPS更多时间）
          maximumAge: 0,                // 不使用缓存位置，每次都重新定位
          convert: true,                // 自动转换为高德坐标系
          needAddress: false,           // 不需要逆地理编码（加快定位速度）
          extensions: 'all',            // 返回更多信息
          GeoLocationFirst: true,       // 优先使用浏览器原生定位（GPS）
          noIpLocate: 3,                // 禁用IP定位（只用GPS/WiFi精确定位）
          noGeoLocation: 0,             // 允许使用浏览器定位
          useNative: true,              // 使用浏览器原生定位API
          zoomToAccuracy: true,         // 定位成功后调整地图视野
          buttonPosition: 'RB'          // 定位按钮位置（右下角）
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

  if (!map) {
    console.error('[MapLocationPicker] map对象未初始化')
    message.warning('地图未加载完成，请稍后再试')
    return
  }

  if (!AMapObj) {
    console.error('[MapLocationPicker] AMapObj未初始化')
    message.warning('地图组件未就绪，请稍后再试')
    return
  }

  // 每次定位都重新初始化geolocation对象（解决同一任务中多次定位失败的问题）
  console.log('[MapLocationPicker] 重新初始化geolocation对象')
  geolocation = new AMapObj.Geolocation({
    enableHighAccuracy: true,    // 启用高精度定位（使用GPS）
    timeout: 30000,               // 超时时间30秒（给GPS更多时间）
    maximumAge: 0,                // 不使用缓存位置，每次都重新定位
    convert: true,                // 自动转换为高德坐标系
    needAddress: false,           // 不需要逆地理编码（加快定位速度）
    extensions: 'all',            // 返回更多信息
    GeoLocationFirst: true,       // 优先使用浏览器原生定位（GPS）
    noIpLocate: 3,                // 禁用IP定位（只用GPS/WiFi精确定位）
    noGeoLocation: 0,             // 允许使用浏览器定位
    useNative: true,              // 使用浏览器原生定位API
    zoomToAccuracy: true,         // 定位成功后调整地图视野
    buttonPosition: 'RB'          // 定位按钮位置（右下角）
  })

  locating.value = true
  message.loading({
    content: '正在高精度定位中，请稍候...',
    duration: 0,
    key: 'locating'
  })

  console.log('[MapLocationPicker] 调用 geolocation.getCurrentPosition')

  geolocation.getCurrentPosition((status: string, result: any) => {
    console.log('[MapLocationPicker] 定位回调 - status:', status, 'result:', result)
    message.destroy()
    locating.value = false

    if (status === 'complete') {
      console.log('[MapLocationPicker] ========== 定位成功 ==========')
      console.log('[MapLocationPicker] 经度:', result.position.lng)
      console.log('[MapLocationPicker] 纬度:', result.position.lat)
      console.log('[MapLocationPicker] 定位精度:', result.accuracy, '米')
      console.log('[MapLocationPicker] 定位类型:', result.location_type)
      console.log('[MapLocationPicker] 完整结果:', result)
      console.log('[MapLocationPicker] ================================')

      handleMapClick(result.position)

      // 根据精度给出提示
      const accuracy = result.accuracy ? Math.round(result.accuracy) : null
      if (accuracy !== null) {
        if (accuracy <= 20) {
          message.success(`定位成功！精度优秀 (±${accuracy}米)`, 3)
        } else if (accuracy <= 50) {
          message.success(`定位成功！精度良好 (±${accuracy}米)`, 3)
        } else if (accuracy <= 100) {
          message.warning(`定位成功，精度一般 (±${accuracy}米)`, 3)
        } else {
          message.warning(`定位成功，但精度较低 (±${accuracy}米)，建议移至室外或窗边`, 4)
        }
      } else {
        message.success('定位成功')
      }
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
      searchResults.value = result.poiList.pois
    } else {
      searchResults.value = []
      message.info('未找到相关地点')
    }
  })
}

const selectSearchResult = (item: any) => {
  const location = item.location
  handleMapClick(location)
  searchResults.value = []
  searchKeyword.value = ''
  message.success(`已定位到：${item.name}`)
}

const handleMapClick = (lnglat: any) => {
  const {lng, lat} = lnglat
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

// 监听目标位置变化 - 重新初始化地图（模拟教师端行为，提升定位精度）
watch(() => props.targetLocation, (newVal, oldVal) => {
  // 当目标位置变化时（打开新的签到任务），重新初始化地图
  if (newVal && newVal !== oldVal) {
    console.log('[MapLocationPicker] 目标位置变化，重新初始化地图以提升定位精度')

    // 销毁旧地图
    if (map) {
      map.destroy()
      map = null
      marker = null
      targetMarker = null
      circle = null
    }

    // 重新初始化地图
    initMap()
  }
})

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

<style lang="scss" scoped>
.map-location-picker {
  width: 100%;
}

.map-wrapper {
  position: relative;
  width: 100%;
  height: v-bind(height);
}

.map-container {
  width: 100%;
  height: 100%;
  border-radius: 8px;
  overflow: hidden;

  &.readonly {
    cursor: default;
  }
}
</style>
