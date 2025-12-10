<template>
  <div class="material-center-enhanced">
    <a-page-header
        sub-title="管理和查看所有教学资料"
        title="资料中心"
    >
      <template #extra>
        <a-button type="primary" @click="handleUpload">
          <template #icon>
            <UploadOutlined/>
          </template>
          上传资料
        </a-button>
      </template>
    </a-page-header>

    <div class="content-container">
      <a-row :gutter="16">
        <!-- 左侧：标签云和分类树 -->
        <a-col :lg="4" :md="4" :sm="24" :xs="24">
          <!-- 标签云 -->
          <TagCloud
              v-model="selectedTags"
              :default-show-count="15"
              :show-manage="true"
              @select="handleTagSelect"
          />

          <!-- 分类树 -->
          <div class="category-tree-wrapper" style="margin-top: 16px">
            <CategoryTree
                v-model="filters.categoryId"
                :show-count="true"
                :show-manage="true"
                @select="handleCategorySelect"
            />
          </div>
        </a-col>

        <!-- 右侧：搜索、筛选和资料列表 -->
        <a-col :lg="20" :md="20" :sm="24" :xs="24">
          <!-- 搜索栏 -->
          <SearchBar
              v-model="searchKeyword"
              @search="handleSearch"
          />

          <!-- 高级筛选 -->
          <div style="margin-top: 16px">
            <AdvancedFilter
                :model-value="filters"
                @change="handleFilterChange"
                @update:model-value="handleFilterUpdate"
            />
          </div>

          <!-- 资料列表 -->
          <a-card :bordered="false" class="material-list-card">
            <a-spin :spinning="loading">
              <a-empty v-if="materials.length === 0 && !loading" description="暂无资料"/>

              <a-row v-else :gutter="[16, 16]">
                <a-col
                    v-for="material in materials"
                    :key="material.id"
                    :lg="8"
                    :md="12"
                    :sm="12"
                    :xl="6"
                    :xs="24"
                >
                  <MaterialCard
                      :material="material"
                      @click="handleViewDetail"
                      @download="handleDownload"
                      @more="handleMore"
                      @preview="handlePreview"
                  />
                </a-col>
              </a-row>

              <!-- 分页 -->
              <div v-if="total > 0" class="pagination-container">
                <a-pagination
                    v-model:current="pagination.page"
                    v-model:page-size="pagination.pageSize"
                    :page-size-options="['12', '24', '36', '48']"
                    :show-size-changer="true"
                    :show-total="(total: number) => `共 ${total} 条`"
                    :total="total"
                    @change="handlePageChange"
                    @show-size-change="handlePageSizeChange"
                />
              </div>
            </a-spin>
          </a-card>
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {message} from 'ant-design-vue'
import {UploadOutlined} from '@ant-design/icons-vue'
import SearchBar from '@/components/materials/SearchBar.vue'
import CategoryTree from '@/components/materials/CategoryTree.vue'
import TagCloud from '@/components/materials/TagCloud.vue'
import AdvancedFilter from '@/components/materials/AdvancedFilter.vue'
import MaterialCard from '@/components/materials/MaterialCard.vue'
import {materialApiGet, materialApiIntMaterialIdDownloadGet} from '@/api/materialController.ts'

const router = useRouter()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const materials = ref<any[]>([])
const total = ref(0)
const selectedTags = ref<number[]>([])

// 筛选条件
const filters = reactive({
  categoryId: null as number | null,
  fileType: null as string | null,
  sortBy: 'created_at',
  order: 'desc',
  courseId: null as number | null,
  uploaderId: null as number | null,
  fileSizeRange: null as string | null,
  dateRange: null as any
})

// 分页
const pagination = reactive({
  page: 1,
  pageSize: 12
})

// 加载资料列表
const loadMaterials = async () => {
  loading.value = true
  try {
    const params: any = {
      page: pagination.page,
      page_size: pagination.pageSize,
      sort_by: filters.sortBy,
      order: filters.order
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
    if (filters.uploaderId) {
      params.uploader_id = filters.uploaderId
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
  // 手动更新 reactive 对象的每个属性
  Object.keys(newFilters).forEach(key => {
    (filters as any)[key] = newFilters[key]
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

// 上传资料
const handleUpload = () => {
  router.push('/teacher/materials/upload')
}

// 查看详情
const handleViewDetail = (material: any) => {
  router.push(`/teacher/materials/${material.id}`)
}

// 预览
const handlePreview = (material: any) => {
  router.push(`/teacher/materials/${material.id}?preview=true`)
}

// 下载
const handleDownload = async (material: any) => {
  const loadingMsg = message.loading('正在下载...', 0)
  try {
    const response = await materialApiIntMaterialIdDownloadGet({
      materialId: material.id
    }, {
      responseType: 'blob'
    })
    
    // 从axios响应中提取blob数据
    const blob = response.data instanceof Blob ? response.data : new Blob([response.data])
    
    // 尝试从响应头获取文件名
    let fileName = material.fileName
    const contentDisposition = response.headers?.['content-disposition']
    if (contentDisposition) {
      const fileNameMatch = contentDisposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/)
      if (fileNameMatch && fileNameMatch[1]) {
        fileName = fileNameMatch[1].replace(/['"]/g, '')
        try {
          fileName = decodeURIComponent(fileName)
        } catch (e) {
          // 如果解码失败,使用原始文件名
        }
      }
    }
    
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)

    loadingMsg()
    message.success('下载成功')
  } catch (error: any) {
    loadingMsg()
    console.error('下载失败:', error)
    message.error(error.message || '下载失败')
  }
}

// 更多操作
const handleMore = (material: any) => {
  // TODO: 实现更多操作
}

// 初始化
onMounted(() => {
  loadMaterials()
})
</script>

<style scoped>
.material-center-enhanced {
  min-height: 100vh;
  padding: 0;
  margin: 0;
}

.content-container {
  padding: 0 16px 16px 16px;
}

.category-tree-wrapper {
  /* max-height: 500px; */
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
</style>
