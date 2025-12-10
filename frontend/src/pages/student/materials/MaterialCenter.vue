<template>
  <div class="student-material-center">
    <a-page-header title="资料中心" sub-title="浏览和下载学习资料" />

    <div class="content-container">
      <a-row :gutter="16">
        <!-- 左侧：标签云和分类树 -->
        <a-col :xs="24" :sm="24" :md="4" :lg="4">
          <!-- 标签云 -->
          <TagCloud v-model="selectedTags" :show-manage="false" :default-show-count="15" @select="handleTagSelect" />

          <!-- 分类树 -->
          <div class="category-tree-wrapper" style="margin-top: 16px">
            <CategoryTree v-model="filters.categoryId" :show-manage="false" :show-count="true" @select="handleCategorySelect" />
          </div>
        </a-col>

        <!-- 右侧：搜索、筛选和资料列表 -->
        <a-col :xs="24" :sm="24" :md="20" :lg="20">
          <!-- 搜索栏 -->
          <SearchBar v-model="searchKeyword" @search="handleSearch" />

          <!-- 高级筛选 -->
          <div style="margin-top: 16px">
            <AdvancedFilter :model-value="filters" @update:model-value="handleFilterUpdate" @change="handleFilterChange" />
          </div>

          <!-- 资料列表 -->
          <a-card :bordered="false" class="material-list-card">
            <!-- 骨架屏加载状态 - Requirements 1.1 -->
            <div v-if="loading" class="skeleton-container">
              <a-row :gutter="[16, 16]">
                <a-col v-for="n in pagination.pageSize" :key="n" :xs="24" :sm="12" :md="12" :lg="8" :xl="6">
                  <a-card class="skeleton-card">
                    <a-skeleton :loading="true" active :paragraph="{ rows: 3 }">
                      <template #avatar>
                        <a-skeleton-avatar :size="48" shape="square" />
                      </template>
                    </a-skeleton>
                  </a-card>
                </a-col>
              </a-row>
            </div>

            <!-- 空状态展示 - Requirements 2.4 -->
            <div v-else-if="materials.length === 0" class="empty-state">
              <a-empty :description="emptyStateDescription">
                <template #image>
                  <FolderOpenOutlined class="empty-icon" />
                </template>
                <div class="empty-suggestions">
                  <p v-if="hasActiveFilters" class="suggestion-text">当前筛选条件下没有找到资料，您可以：</p>
                  <p v-else class="suggestion-text">暂时没有可用的学习资料，您可以：</p>
                  <div class="suggestion-actions">
                    <a-button v-if="hasActiveFilters" type="link" @click="clearAllFilters"> <ClearOutlined /> 清除所有筛选条件 </a-button>
                    <a-button v-if="searchKeyword" type="link" @click="clearSearch"> <SearchOutlined /> 清除搜索关键词 </a-button>
                    <a-button type="link" @click="loadMaterials"> <ReloadOutlined /> 刷新列表 </a-button>
                  </div>
                  <div v-if="searchKeyword" class="search-suggestions">
                    <p class="suggestion-title">搜索建议：</p>
                    <ul>
                      <li>检查关键词是否有拼写错误</li>
                      <li>尝试使用更简短或更通用的关键词</li>
                      <li>尝试搜索资料标题或描述中的关键词</li>
                    </ul>
                  </div>
                </div>
              </a-empty>
            </div>

            <!-- 资料列表 -->
            <a-row v-else :gutter="[16, 16]">
              <a-col v-for="material in materials" :key="material.id" :xs="24" :sm="12" :md="12" :lg="8" :xl="6">
                <MaterialCard :material="material" @click="handleViewDetail" @preview="handlePreview" @download="handleDownload" @more="handleMore" />
              </a-col>
            </a-row>

            <!-- 分页 -->
            <div v-if="total > 0 && !loading" class="pagination-container">
              <a-pagination
                v-model:current="pagination.page"
                v-model:page-size="pagination.pageSize"
                :total="total"
                :show-total="(total: number) => `共 ${total} 条`"
                :show-size-changer="true"
                :page-size-options="['12', '24', '36', '48']"
                @change="handlePageChange"
                @show-size-change="handlePageSizeChange"
              />
            </div>
          </a-card>
        </a-col>
      </a-row>
    </div>

    <!-- 预览弹窗 -->
    <a-modal
      v-model:open="previewModalVisible"
      :title="previewMaterial?.title || '文件预览'"
      :width="900"
      :footer="null"
      :destroy-on-close="true"
      class="preview-modal"
    >
      <div class="preview-container">
        <FilePreview
          v-if="previewMaterial && previewUrl"
          :file-url="previewUrl"
          :file-type="previewMaterial.fileType"
          :file-name="previewMaterial.fileName"
          @download="handleDownload(previewMaterial)"
          @back="previewModalVisible = false"
        />
        <div v-else-if="!isPreviewSupported(previewMaterial?.fileType)" class="unsupported-preview">
          <a-result status="info" title="该文件类型暂不支持在线预览" :sub-title="`文件类型: ${previewMaterial?.fileType || '未知'}，建议下载后查看`">
            <template #extra>
              <a-space>
                <a-button type="primary" @click="handleDownload(previewMaterial)"> 下载文件 </a-button>
                <a-button @click="previewModalVisible = false"> 关闭 </a-button>
              </a-space>
            </template>
          </a-result>
        </div>
      </div>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
/**
 * 学生端资料中心页面
 * 功能：资料列表展示、分类筛选、搜索、下载、预览
 * Requirements: 1.1, 1.5
 */
import { ref, reactive, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import { FolderOpenOutlined, ClearOutlined, SearchOutlined, ReloadOutlined } from '@ant-design/icons-vue'
import SearchBar from '@/components/materials/SearchBar.vue'
import CategoryTree from '@/components/materials/CategoryTree.vue'
import TagCloud from '@/components/materials/TagCloud.vue'
import AdvancedFilter from '@/components/materials/AdvancedFilter.vue'
import MaterialCard from '@/components/materials/MaterialCard.vue'
import FilePreview from '@/components/materials/preview/FilePreview.vue'
import { materialApiGet, materialApiIntMaterialIdDownloadGet, materialApiIntMaterialIdPreviewGet } from '@/api/materialController'

const router = useRouter()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const materials = ref<any[]>([])
const total = ref(0)
const selectedTags = ref<number[]>([])

// 预览相关状态
const previewModalVisible = ref(false)
const previewMaterial = ref<any>(null)
const previewUrl = ref<string>('')

// 筛选条件
const filters = reactive({
  categoryId: null as number | null,
  fileType: null as string | null,
  sortBy: 'created_at',
  order: 'desc',
  courseId: null as number | null,
  uploaderId: null as number | null,
  fileSizeRange: null as string | null,
  dateRange: null as any,
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 12,
})

// 支持预览的文件类型
const previewSupportedTypes = ['pdf', 'image', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']

// 是否有激活的筛选条件
const hasActiveFilters = computed(() => {
  return (
    filters.categoryId !== null ||
    filters.fileType !== null ||
    filters.courseId !== null ||
    filters.dateRange !== null ||
    selectedTags.value.length > 0 ||
    searchKeyword.value !== ''
  )
})

// 空状态描述文本
const emptyStateDescription = computed(() => {
  if (searchKeyword.value) {
    return `未找到与 "${searchKeyword.value}" 相关的资料`
  }
  if (hasActiveFilters.value) {
    return '当前筛选条件下没有找到资料'
  }
  return '暂无可用的学习资料'
})

// 清除所有筛选条件
const clearAllFilters = () => {
  filters.categoryId = null
  filters.fileType = null
  filters.courseId = null
  filters.dateRange = null
  selectedTags.value = []
  searchKeyword.value = ''
  pagination.page = 1
  loadMaterials()
}

// 清除搜索关键词
const clearSearch = () => {
  searchKeyword.value = ''
  pagination.page = 1
  loadMaterials()
}

// 判断文件类型是否支持预览
const isPreviewSupported = (fileType?: string): boolean => {
  if (!fileType) return false
  return previewSupportedTypes.includes(fileType.toLowerCase())
}

// 加载资料列表
const loadMaterials = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      sort_by: filters.sortBy,
      order: filters.order,
    }

    if (searchKeyword.value) {
      params.search = searchKeyword.value
    }
    if (filters.categoryId) {
      params.category_id = filters.categoryId
    }
    if (filters.fileType) {
      params.file_type = filters.fileType
    }
    if (filters.courseId) {
      params.course_id = filters.courseId
    }
    // 添加标签筛选
    if (selectedTags.value && selectedTags.value.length > 0) {
      params.tag_ids = selectedTags.value.join(',')
    }
    // 添加日期范围筛选
    if (filters.dateRange && filters.dateRange.length === 2) {
      params.start_date = filters.dateRange[0].format('YYYY-MM-DD')
      params.end_date = filters.dateRange[1].format('YYYY-MM-DD')
    }

    console.log('加载资料，参数:', params)

    const response = await materialApiGet(params)
    const data = (response as any).data?.data || (response as any).data
    materials.value = data?.materials || []
    total.value = data?.total || 0

    console.log('加载完成，资料数量:', materials.value.length, '总数:', total.value)
  } catch (error: any) {
    console.error('加载资料失败:', error)
    message.error(error.message || '加载资料列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = (keyword: string) => {
  console.log('搜索关键词:', keyword)
  searchKeyword.value = keyword
  pagination.page = 1
  loadMaterials()
}

// 分类选择
const handleCategorySelect = (categoryId: number | null) => {
  console.log('选择分类:', categoryId)
  filters.categoryId = categoryId
  pagination.page = 1
  loadMaterials()
}

// 标签选择
const handleTagSelect = (tagIds: number[]) => {
  console.log('选择标签:', tagIds)
  selectedTags.value = tagIds
  pagination.page = 1
  loadMaterials()
}

// 筛选条件更新（从子组件）
const handleFilterUpdate = (newFilters: any) => {
  console.log('收到筛选更新:', newFilters)
  Object.keys(newFilters).forEach((key) => {
    ;(filters as any)[key] = newFilters[key]
  })
  console.log('更新后的筛选条件:', filters)
}

// 筛选变化
const handleFilterChange = () => {
  console.log('筛选条件变化:', filters)
  pagination.page = 1
  loadMaterials()
}

// 分页变化
const handlePageChange = (page: number, pageSize: number) => {
  pagination.page = page
  pagination.pageSize = pageSize
  loadMaterials()
}

// 页面大小变化
const handlePageSizeChange = (current: number, size: number) => {
  pagination.page = 1
  pagination.pageSize = size
  loadMaterials()
}

// 查看详情
const handleViewDetail = (material: any) => {
  router.push(`/student/materials/${material.id}`)
}

// 预览
const handlePreview = async (material: any) => {
  previewMaterial.value = material

  // 检查是否支持预览
  if (!isPreviewSupported(material.fileType)) {
    previewModalVisible.value = true
    previewUrl.value = ''
    return
  }

  try {
    // 获取预览URL
    const response = await materialApiIntMaterialIdPreviewGet({
      materialId: material.id,
    })

    // 创建blob URL用于预览
    const blob = new Blob([response.data], { type: getContentType(material.fileType) })
    previewUrl.value = window.URL.createObjectURL(blob)
    previewModalVisible.value = true
  } catch (error: any) {
    console.error('获取预览失败:', error)
    message.error(error.message || '获取预览失败')
  }
}

// 获取文件MIME类型
const getContentType = (fileType: string): string => {
  const typeMap: Record<string, string> = {
    pdf: 'application/pdf',
    image: 'image/*',
    jpg: 'image/jpeg',
    jpeg: 'image/jpeg',
    png: 'image/png',
    gif: 'image/gif',
    bmp: 'image/bmp',
    webp: 'image/webp',
    svg: 'image/svg+xml',
  }
  return typeMap[fileType.toLowerCase()] || 'application/octet-stream'
}

// 下载
const handleDownload = async (material: any) => {
  if (!material) return

  try {
    const response = await materialApiIntMaterialIdDownloadGet({
      materialId: material.id,
    })

    const blob = new Blob([response.data])
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', material.fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    message.success('下载成功')
  } catch (error: any) {
    console.error('下载失败:', error)
    message.error(error.message || '下载失败')
  }
}

// 更多操作（学生端暂不实现）
const handleMore = (material: any) => {
  // 学生端暂无更多操作
}

// 初始化
onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.student-material-center {
  min-height: 100vh;
  padding: 0;
  margin: 0;
}

.content-container {
  padding: 0 16px 16px 16px;
}

.category-tree-wrapper {
  overflow-y: auto;
  overflow-x: hidden;
}

.material-list-card {
  margin-top: 16px;
  min-height: 400px;
}

.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.preview-modal :deep(.ant-modal-body) {
  padding: 0;
  height: 70vh;
  overflow: hidden;
}

.preview-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.unsupported-preview {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: 40px;
}

/* 空状态样式 - Requirements 2.4 */
.empty-state {
  padding: 40px 20px;
  text-align: center;
}

.empty-icon {
  font-size: 64px;
  color: #d9d9d9;
}

.empty-suggestions {
  margin-top: 16px;
}

.suggestion-text {
  color: #666;
  margin-bottom: 12px;
}

.suggestion-actions {
  display: flex;
  justify-content: center;
  gap: 8px;
  flex-wrap: wrap;
  margin-bottom: 16px;
}

.search-suggestions {
  text-align: left;
  max-width: 300px;
  margin: 16px auto 0;
  padding: 12px 16px;
  background: #fafafa;
  border-radius: 4px;
}

.suggestion-title {
  font-weight: 500;
  color: #333;
  margin-bottom: 8px;
}

.search-suggestions ul {
  margin: 0;
  padding-left: 20px;
  color: #666;
}

.search-suggestions li {
  margin-bottom: 4px;
  font-size: 13px;
}

/* 骨架屏加载样式 - Requirements 1.1 */
.skeleton-container {
  padding: 8px 0;
}

.skeleton-card {
  height: 180px;
  border-radius: 8px;
}

.skeleton-card :deep(.ant-skeleton) {
  padding: 16px;
}

.skeleton-card :deep(.ant-skeleton-content) {
  padding-top: 8px;
}
</style>
