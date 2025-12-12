<template>
  <div class="advanced-filter">
    <a-card :bordered="false" class="filter-card">
      <a-form :model="filters" class="filter-form" layout="inline">
        <a-row :gutter="[12, 12]" align="middle" style="width: 100%">
          <!-- 分类筛选 -->
          <a-col :md="6" :sm="12" :xs="24">
            <a-form-item label="分类">
              <a-tree-select
                  :field-names="{ label: 'name', value: 'id', children: 'children' }"
                  :tree-data="categories"
                  :value="filters.categoryId"
                  allow-clear
                  placeholder="选择分类"
                  style="min-width: 140px"
                  tree-default-expand-all
                  @change="(value: any) => handleFilterChange(updateFilter('categoryId', value))"
              />
            </a-form-item>
          </a-col>

          <!-- 文件类型筛选 -->
          <a-col :md="6" :sm="12" :xs="24">
            <a-form-item label="文件类型">
              <a-select
                  :value="filters.fileType"
                  allow-clear
                  placeholder="全部类型"
                  style="min-width: 140px"
                  @change="(value: any) => handleFilterChange(updateFilter('fileType', value))"
              >
                <a-select-option :value="null">全部类型</a-select-option>
                <a-select-option value="pdf">
                  <FilePdfOutlined/>
                  PDF
                </a-select-option>
                <a-select-option value="doc">
                  <FileWordOutlined/>
                  Word
                </a-select-option>
                <a-select-option value="ppt">
                  <FilePptOutlined/>
                  PPT
                </a-select-option>
                <a-select-option value="xls">
                  <FileExcelOutlined/>
                  Excel
                </a-select-option>
                <a-select-option value="image">
                  <FileImageOutlined/>
                  图片
                </a-select-option>
                <a-select-option value="video">
                  <PlayCircleOutlined/>
                  视频
                </a-select-option>
                <a-select-option value="archive">
                  <FileZipOutlined/>
                  压缩包
                </a-select-option>
                <a-select-option value="text">
                  <FileTextOutlined/>
                  文本
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <!-- 排序方式 -->
          <a-col :md="6" :sm="12" :xs="24">
            <a-form-item label="排序">
              <a-select
                  :value="filters.sortBy"
                  style="min-width: 130px"
                  @change="(value: any) => handleFilterChange(updateFilter('sortBy', value))"
              >
                <a-select-option value="created_at">
                  <ClockCircleOutlined/>
                  最新上传
                </a-select-option>
                <a-select-option value="download_count">
                  <DownloadOutlined/>
                  下载最多
                </a-select-option>
                <a-select-option value="view_count">
                  <EyeOutlined/>
                  浏览最多
                </a-select-option>
                <a-select-option value="file_size">
                  <FileOutlined/>
                  文件大小
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>

          <!-- 排序方向 -->
          <a-col :md="6" :sm="12" :xs="24">
            <a-form-item label="顺序">
              <a-select
                  :value="filters.order"
                  style="min-width: 110px"
                  @change="(value: any) => handleFilterChange(updateFilter('order', value))"
              >
                <a-select-option value="desc">
                  <ArrowDownOutlined/>
                  降序
                </a-select-option>
                <a-select-option value="asc">
                  <ArrowUpOutlined/>
                  升序
                </a-select-option>
              </a-select>
            </a-form-item>
          </a-col>


          <!-- 操作按钮 -->
          <a-col :md="12" :sm="12" :xs="24">
            <a-form-item style="margin-bottom: 0">
              <a-space :size="12">
                <a-button size="middle" type="primary" @click="handleApply">
                  <FilterOutlined/>
                  筛选
                </a-button>
                <a-button size="middle" @click="handleReset">
                  <ReloadOutlined/>
                  重置
                </a-button>
                <a-button size="middle" type="link" @click="toggleAdvanced">
                  {{ showAdvanced ? '收起' : '更多筛选' }}
                  <component :is="showAdvanced ? UpOutlined : DownOutlined"/>
                </a-button>
              </a-space>
            </a-form-item>
          </a-col>


          <!-- 高级筛选选项 -->
          <template v-if="showAdvanced">
            <!-- 占位符，强制换行 -->
            <a-col :span="24" style="height: 0; padding: 0"></a-col>

            <!-- 课程筛选 -->
            <a-col :md="6" :sm="12" :xs="24">
              <a-form-item label="课程">
                <a-select
                    :filter-option="filterCourseOption"
                    :value="filters.courseId"
                    allow-clear
                    placeholder="选择课程"
                    show-search
                    style="min-width: 140px"
                    @change="(value: any) => handleFilterChange(updateFilter('courseId', value))"
                >
                  <a-select-option :value="null">全部课程</a-select-option>
                  <a-select-option
                      v-for="course in courses"
                      :key="course.id"
                      :value="course.id"
                  >
                    {{ course.name }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <!-- 上传者筛选 -->
            <a-col :md="6" :sm="12" :xs="24">
              <a-form-item label="上传者">
                <a-select
                    :filter-option="filterUserOption"
                    :value="filters.uploaderId"
                    allow-clear
                    placeholder="选择上传者"
                    show-search
                    style="min-width: 140px"
                    @change="(value: any) => handleFilterChange(updateFilter('uploaderId', value))"
                >
                  <a-select-option :value="null">全部上传者</a-select-option>
                  <a-select-option
                      v-for="user in users"
                      :key="user.id"
                      :value="user.id"
                  >
                    {{ user.realName || user.username }}
                  </a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <!-- 文件大小范围 -->
            <a-col :md="6" :sm="12" :xs="24">
              <a-form-item label="文件大小">
                <a-select
                    :value="filters.fileSizeRange"
                    allow-clear
                    placeholder="选择大小范围"
                    style="min-width: 140px"
                    @change="(value: any) => handleFilterChange(updateFilter('fileSizeRange', value))"
                >
                  <a-select-option :value="null">不限</a-select-option>
                  <a-select-option value="0-1">小于 1MB</a-select-option>
                  <a-select-option value="1-10">1MB - 10MB</a-select-option>
                  <a-select-option value="10-50">10MB - 50MB</a-select-option>
                  <a-select-option value="50-100">50MB - 100MB</a-select-option>
                  <a-select-option value="100+">大于 100MB</a-select-option>
                </a-select>
              </a-form-item>
            </a-col>

            <!-- 上传时间范围 -->
            <a-col :md="6" :sm="12" :xs="24">
              <a-form-item label="上传时间">
                <a-range-picker
                    :value="filters.dateRange"
                    style="max-width: 170px"
                    @change="(value: any) => handleFilterChange(updateFilter('dateRange', value))"
                />
              </a-form-item>
            </a-col>
          </template>
        </a-row>
      </a-form>

      <!-- 当前筛选条件标签 -->
      <div v-if="activeFilters.length > 0" class="active-filters">
        <span class="filter-label">当前筛选：</span>
        <a-tag
            v-for="filter in activeFilters"
            :key="filter.key"
            closable
            @close="removeFilter(filter.key)"
        >
          {{ filter.label }}: {{ filter.value }}
        </a-tag>
        <a-button size="small" type="link" @click="clearAllFilters">
          清空全部
        </a-button>
      </div>
    </a-card>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {
  ArrowDownOutlined,
  ArrowUpOutlined,
  ClockCircleOutlined,
  DownloadOutlined,
  DownOutlined,
  EyeOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  FileOutlined,
  FilePdfOutlined,
  FilePptOutlined,
  FileTextOutlined,
  FileWordOutlined,
  FileZipOutlined,
  FilterOutlined,
  PlayCircleOutlined,
  ReloadOutlined,
  UpOutlined
} from '@ant-design/icons-vue'
import {categoryApiGet} from '@/api/categoryController'
import type {Dayjs} from 'dayjs'

interface FilterValues {
  categoryId: number | null
  fileType: string | null
  sortBy: string
  order: string
  courseId: number | null
  uploaderId: number | null
  fileSizeRange: string | null
  dateRange: [Dayjs, Dayjs] | null
}

interface Props {
  modelValue?: Partial<FilterValues>
}

interface Emits {
  (e: 'update:modelValue', value: Partial<FilterValues>): void

  (e: 'change', value: Partial<FilterValues>): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const route = useRoute()
const router = useRouter()

const showAdvanced = ref(false)
const categories = ref<any[]>([])
const courses = ref<any[]>([])
const users = ref<any[]>([])

// 获取当前筛选条件
const filters = computed(() => props.modelValue || {
  categoryId: null,
  fileType: null,
  sortBy: 'created_at',
  order: 'desc',
  courseId: null,
  uploaderId: null,
  fileSizeRange: null,
  dateRange: null
})

// 更新筛选条件的辅助函数，返回新的筛选条件
const updateFilter = (key: string, value: any): Partial<FilterValues> => {
  const newFilters = {...filters.value, [key]: value}
  console.log(`更新筛选 ${key}:`, value, '新筛选条件:', newFilters)
  emit('update:modelValue', newFilters)
  return newFilters
}

// 文件类型映射
const fileTypeMap: Record<string, string> = {
  pdf: 'PDF',
  doc: 'Word',
  ppt: 'PPT',
  xls: 'Excel',
  image: '图片',
  video: '视频',
  archive: '压缩包',
  text: '文本'
}

// 排序方式映射
const sortByMap: Record<string, string> = {
  created_at: '最新上传',
  download_count: '下载最多',
  view_count: '浏览最多',
  file_size: '文件大小'
}

// 当前激活的筛选条件
const activeFilters = computed(() => {
  const result: Array<{ key: string; label: string; value: string }> = []
  const currentFilters = filters.value

  if (currentFilters.categoryId) {
    const category = findCategory(categories.value, currentFilters.categoryId)
    if (category) {
      result.push({
        key: 'categoryId',
        label: '分类',
        value: category.name
      })
    }
  }

  if (currentFilters.fileType) {
    result.push({
      key: 'fileType',
      label: '文件类型',
      value: fileTypeMap[currentFilters.fileType] || currentFilters.fileType
    })
  }

  if (currentFilters.courseId) {
    const course = courses.value.find(c => c.id === currentFilters.courseId)
    if (course) {
      result.push({
        key: 'courseId',
        label: '课程',
        value: course.name
      })
    }
  }

  if (currentFilters.uploaderId) {
    const user = users.value.find(u => u.id === currentFilters.uploaderId)
    if (user) {
      result.push({
        key: 'uploaderId',
        label: '上传者',
        value: user.realName || user.username
      })
    }
  }

  if (currentFilters.fileSizeRange) {
    result.push({
      key: 'fileSizeRange',
      label: '文件大小',
      value: currentFilters.fileSizeRange
    })
  }

  if (currentFilters.dateRange) {
    result.push({
      key: 'dateRange',
      label: '上传时间',
      value: `${currentFilters.dateRange[0].format('YYYY-MM-DD')} ~ ${currentFilters.dateRange[1].format('YYYY-MM-DD')}`
    })
  }

  return result
})

// 递归查找分类
const findCategory = (items: any[], id: number): any => {
  if (!Array.isArray(items)) return null

  for (const item of items) {
    if (item.id === id) return item
    if (item.children && Array.isArray(item.children)) {
      const found = findCategory(item.children, id)
      if (found) return found
    }
  }
  return null
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await categoryApiGet()
    const data = (response as any).data?.data || (response as any).data
    // 后端返回的是 { categories: [...] } 格式
    const categoryList = data?.categories || data
    categories.value = Array.isArray(categoryList) ? categoryList : []
    console.log('AdvancedFilter 加载分类成功，数量:', categories.value.length)
  } catch (error) {
    console.error('加载分类失败:', error)
    categories.value = []
  }
}

// 课程筛选
const filterCourseOption = (input: string, option: any) => {
  return option.children[0].children.toLowerCase().includes(input.toLowerCase())
}

// 用户筛选
const filterUserOption = (input: string, option: any) => {
  return option.children[0].children.toLowerCase().includes(input.toLowerCase())
}

// 筛选变化（实时触发）
const handleFilterChange = (newFilters?: Partial<FilterValues>) => {
  const currentFilters = newFilters || filters.value
  console.log('AdvancedFilter 筛选变化:', currentFilters)
  // 只发送 change 事件，update:modelValue 已经在 updateFilter 中发送过了
  emit('change', currentFilters)

  // 同步到 URL
  syncFiltersToUrl()
}

// 应用筛选（手动触发）
const handleApply = () => {
  const currentFilters = filters.value
  emit('update:modelValue', currentFilters)
  emit('change', currentFilters)
  syncFiltersToUrl()
}

// 重置筛选
const handleReset = () => {
  const resetFilters = {
    categoryId: null,
    fileType: null,
    sortBy: 'created_at',
    order: 'desc',
    courseId: null,
    uploaderId: null,
    fileSizeRange: null,
    dateRange: null
  }

  emit('update:modelValue', resetFilters)
  emit('change', resetFilters)

  // 清除 URL 参数
  router.push({query: {}})
}

// 移除单个筛选条件
const removeFilter = (key: string) => {
  const currentFilters = {...filters.value}
  ;(currentFilters as any)[key] = null
  emit('update:modelValue', currentFilters)
  emit('change', currentFilters)
}

// 清空所有筛选
const clearAllFilters = () => {
  handleReset()
}

// 切换高级筛选
const toggleAdvanced = () => {
  showAdvanced.value = !showAdvanced.value
}

// 同步筛选条件到 URL
const syncFiltersToUrl = () => {
  const currentFilters = filters.value
  const query: Record<string, any> = {}

  if (currentFilters.categoryId) query.categoryId = currentFilters.categoryId
  if (currentFilters.fileType) query.fileType = currentFilters.fileType
  if (currentFilters.sortBy !== 'created_at') query.sortBy = currentFilters.sortBy
  if (currentFilters.order !== 'desc') query.order = currentFilters.order
  if (currentFilters.courseId) query.courseId = currentFilters.courseId
  if (currentFilters.uploaderId) query.uploaderId = currentFilters.uploaderId
  if (currentFilters.fileSizeRange) query.fileSizeRange = currentFilters.fileSizeRange
  if (currentFilters.dateRange) {
    query.startDate = currentFilters.dateRange[0].format('YYYY-MM-DD')
    query.endDate = currentFilters.dateRange[1].format('YYYY-MM-DD')
  }

  router.push({query})
}

// 从 URL 加载筛选条件
const loadFiltersFromUrl = () => {
  const query = route.query
  const urlFilters: Partial<FilterValues> = {}

  if (query.categoryId) urlFilters.categoryId = Number(query.categoryId)
  if (query.fileType) urlFilters.fileType = query.fileType as string
  if (query.sortBy) urlFilters.sortBy = query.sortBy as string
  if (query.order) urlFilters.order = query.order as string
  if (query.courseId) urlFilters.courseId = Number(query.courseId)
  if (query.uploaderId) urlFilters.uploaderId = Number(query.uploaderId)
  if (query.fileSizeRange) urlFilters.fileSizeRange = query.fileSizeRange as string

  // 如果有高级筛选条件，自动展开
  if (query.courseId || query.uploaderId || query.fileSizeRange || query.startDate) {
    showAdvanced.value = true
  }

  // 通知父组件更新
  if (Object.keys(urlFilters).length > 0) {
    emit('update:modelValue', {...filters.value, ...urlFilters})
  }
}

onMounted(() => {
  loadCategories()
  loadFiltersFromUrl()
})
</script>

<style scoped>
.advanced-filter {
  margin-bottom: 16px;
}

.filter-card {
  background: #fafafa;
  border-radius: 8px;
}

.filter-form {
  padding: 8px 0;
}

.filter-actions {
  padding-top: 4px;
}

.active-filters {
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #e8e8e8;
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 8px;
}

.filter-label {
  font-weight: 500;
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  margin-right: 4px;
}

:deep(.ant-form-item) {
  margin-bottom: 0;
}

:deep(.ant-form-item-label) {
  padding-right: 8px;
}

:deep(.ant-form-item-label > label) {
  font-size: 13px;
  color: rgba(0, 0, 0, 0.65);
  font-weight: 500;
}

:deep(.ant-select-selector),
:deep(.ant-picker) {
  border-radius: 6px !important;
}

:deep(.ant-tag) {
  border-radius: 4px;
  font-size: 12px;
}
</style>
