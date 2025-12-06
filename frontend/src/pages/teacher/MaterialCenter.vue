<template>
  <div class="material-center">
    <a-page-header
      title="资料中心"
      sub-title="管理和查看所有教学资料"
    >
      <template #extra>
        <a-button type="primary" @click="handleUpload">
          <template #icon><UploadOutlined /></template>
          上传资料
        </a-button>
      </template>
    </a-page-header>

    <div class="content-container">
      <!-- 搜索和筛选区域 -->
      <a-card class="filter-card" :bordered="false">
        <a-space direction="vertical" :size="16" style="width: 100%">
          <!-- 搜索框 -->
          <a-input-search
            v-model:value="searchKeyword"
            placeholder="搜索资料标题、描述..."
            size="large"
            allow-clear
            @search="handleSearch"
          >
            <template #enterButton>
              <a-button type="primary">
                <SearchOutlined />
                搜索
              </a-button>
            </template>
          </a-input-search>

          <!-- 筛选器 -->
          <a-row :gutter="16">
            <a-col :span="6">
              <a-select
                v-model:value="filters.categoryId"
                placeholder="选择分类"
                allow-clear
                style="width: 100%"
                @change="handleFilterChange"
              >
                <a-select-option :value="null">全部分类</a-select-option>
                <a-select-option
                  v-for="category in categories"
                  :key="category.id"
                  :value="category.id"
                >
                  {{ category.name }}
                </a-select-option>
              </a-select>
            </a-col>

            <a-col :span="6">
              <a-select
                v-model:value="filters.fileType"
                placeholder="文件类型"
                allow-clear
                style="width: 100%"
                @change="handleFilterChange"
              >
                <a-select-option :value="null">全部类型</a-select-option>
                <a-select-option value="pdf">PDF</a-select-option>
                <a-select-option value="doc">Word</a-select-option>
                <a-select-option value="ppt">PPT</a-select-option>
                <a-select-option value="xls">Excel</a-select-option>
                <a-select-option value="image">图片</a-select-option>
                <a-select-option value="video">视频</a-select-option>
                <a-select-option value="archive">压缩包</a-select-option>
              </a-select>
            </a-col>

            <a-col :span="6">
              <a-select
                v-model:value="filters.sortBy"
                placeholder="排序方式"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <a-select-option value="created_at">最新上传</a-select-option>
                <a-select-option value="download_count">下载最多</a-select-option>
                <a-select-option value="view_count">浏览最多</a-select-option>
              </a-select>
            </a-col>

            <a-col :span="6">
              <a-select
                v-model:value="filters.order"
                style="width: 100%"
                @change="handleFilterChange"
              >
                <a-select-option value="desc">降序</a-select-option>
                <a-select-option value="asc">升序</a-select-option>
              </a-select>
            </a-col>
          </a-row>
        </a-space>
      </a-card>

      <!-- 资料列表 -->
      <a-card :bordered="false" class="material-list-card">
        <a-spin :spinning="loading">
          <a-empty v-if="materials.length === 0 && !loading" description="暂无资料" />
          
          <a-row v-else :gutter="[16, 16]">
            <a-col
              v-for="material in materials"
              :key="material.id"
              :xs="24"
              :sm="12"
              :md="8"
              :lg="6"
              :xl="6"
            >
              <MaterialCard
                :material="material"
                @click="handleViewDetail"
                @preview="handlePreview"
                @download="handleDownload"
                @more="handleMore"
              />
            </a-col>
          </a-row>

          <!-- 分页 -->
          <div v-if="total > 0" class="pagination-container">
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
        </a-spin>
      </a-card>
    </div>

    <!-- 更多操作菜单 -->
    <a-modal
      v-model:open="moreMenuVisible"
      title="资料操作"
      :footer="null"
      width="400px"
    >
      <a-menu>
        <a-menu-item key="edit" @click="handleEdit">
          <EditOutlined />
          编辑资料
        </a-menu-item>
        <a-menu-item key="share" @click="handleShare">
          <ShareAltOutlined />
          分享资料
        </a-menu-item>
        <a-menu-divider />
        <a-menu-item key="delete" danger @click="handleDelete">
          <DeleteOutlined />
          删除资料
        </a-menu-item>
      </a-menu>
    </a-modal>

    <!-- 编辑资料对话框 -->
    <a-modal
      v-model:open="editModalVisible"
      title="编辑资料"
      width="600px"
      :confirm-loading="editLoading"
      @ok="handleEditSubmit"
      @cancel="handleEditCancel"
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 19 }"
      >
        <a-form-item
          label="资料标题"
          name="title"
          :rules="[{ required: true, message: '请输入资料标题' }]"
        >
          <a-input
            v-model:value="editForm.title"
            placeholder="请输入资料标题"
            :maxlength="100"
          />
        </a-form-item>

        <a-form-item label="资料描述" name="description">
          <a-textarea
            v-model:value="editForm.description"
            placeholder="请输入资料描述"
            :rows="4"
            :maxlength="500"
            show-count
          />
        </a-form-item>

        <a-form-item label="分类" name="categoryId">
          <a-select
            v-model:value="editForm.categoryId"
            placeholder="请选择分类"
            allow-clear
          >
            <a-select-option
              v-for="category in categories"
              :key="category.id"
              :value="category.id"
            >
              {{ category.name }}
            </a-select-option>
          </a-select>
        </a-form-item>

        <a-form-item label="标签" name="tags">
          <a-select
            v-model:value="editForm.tags"
            mode="tags"
            placeholder="请输入标签（按回车添加）"
            :max-tag-count="5"
          >
          </a-select>
        </a-form-item>

        <a-form-item label="文件信息">
          <a-space direction="vertical" :size="4">
            <div>
              <span class="info-label">文件名：</span>
              <span>{{ editForm.fileName }}</span>
            </div>
            <div>
              <span class="info-label">文件类型：</span>
              <a-tag :color="getFileTypeColor(editForm.fileType)">
                {{ getFileTypeText(editForm.fileType) }}
              </a-tag>
            </div>
            <div>
              <span class="info-label">文件大小：</span>
              <span>{{ formatFileSize(editForm.fileSize) }}</span>
            </div>
          </a-space>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import {
  UploadOutlined,
  SearchOutlined,
  EditOutlined,
  ShareAltOutlined,
  DeleteOutlined
} from '@ant-design/icons-vue'
import MaterialCard from '@/components/materials/MaterialCard.vue'
import { 
  materialApiGet, 
  materialApiIntMaterialIdDownloadGet, 
  materialApiIntMaterialIdDelete,
  materialApiIntMaterialIdPut
} from '@/api/materialController'
import { categoryApiGet } from '@/api/categoryController'

const router = useRouter()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const materials = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)
const moreMenuVisible = ref(false)
const currentMaterial = ref<any>(null)
const editModalVisible = ref(false)
const editLoading = ref(false)
const editFormRef = ref()
const editForm = reactive({
  id: 0,
  title: '',
  description: '',
  categoryId: null as number | null,
  tags: [] as string[],
  fileName: '',
  fileType: '',
  fileSize: 0
})

// 筛选条件
const filters = reactive({
  categoryId: null as number | null,
  fileType: null as string | null,
  sortBy: 'created_at',
  order: 'desc'
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

    const response = await materialApiGet(params)
    
    // 直接使用response.data
    const data = (response as any).data?.data || (response as any).data
    console.log('API响应数据:', data)
    // 后端返回的字段是 materials 不是 items
    materials.value = data?.materials || []
    total.value = data?.total || 0
    console.log('资料列表:', materials.value)
  } catch (error: any) {
    message.error(error.message || '加载资料列表失败')
  } finally {
    loading.value = false
  }
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await categoryApiGet()
    const data = (response as any).data?.data || (response as any).data
    categories.value = data || []
  } catch (error: any) {
    console.error('加载分类失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.page = 1
  loadMaterials()
}

// 筛选变化
const handleFilterChange = () => {
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
  try {
    const response = await materialApiIntMaterialIdDownloadGet({
      materialId: material.id
    })
    // 创建下载链接
    const url = window.URL.createObjectURL(new Blob([response.data]))
    const link = document.createElement('a')
    link.href = url
    link.setAttribute('download', material.fileName)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    message.success('下载成功')
  } catch (error: any) {
    message.error(error.message || '下载失败')
  }
}

// 更多操作
const handleMore = (material: any) => {
  currentMaterial.value = material
  moreMenuVisible.value = true
}

// 编辑
const handleEdit = () => {
  if (currentMaterial.value) {
    // 填充编辑表单
    editForm.id = currentMaterial.value.id
    editForm.title = currentMaterial.value.title
    editForm.description = currentMaterial.value.description || ''
    editForm.categoryId = currentMaterial.value.categoryId || null
    editForm.tags = currentMaterial.value.tags?.map((tag: any) => tag.name) || []
    editForm.fileName = currentMaterial.value.fileName
    editForm.fileType = currentMaterial.value.fileType
    editForm.fileSize = currentMaterial.value.fileSize
    
    moreMenuVisible.value = false
    editModalVisible.value = true
  }
}

// 提交编辑
const handleEditSubmit = async () => {
  try {
    // 验证表单
    await editFormRef.value?.validate()
    
    editLoading.value = true
    
    // 调用更新API
    await materialApiIntMaterialIdPut(
      { materialId: editForm.id },
      {
        title: editForm.title,
        description: editForm.description,
        categoryId: editForm.categoryId,
        tags: editForm.tags
      }
    )
    
    message.success('资料更新成功')
    editModalVisible.value = false
    
    // 重新加载列表
    await loadMaterials()
  } catch (error: any) {
    if (error.errorFields) {
      // 表单验证错误
      return
    }
    message.error(error.message || '更新失败')
  } finally {
    editLoading.value = false
  }
}

// 取消编辑
const handleEditCancel = () => {
  editFormRef.value?.resetFields()
  editModalVisible.value = false
}

// 文件类型颜色映射
const fileTypeColorMap: Record<string, string> = {
  pdf: 'red',
  doc: 'blue',
  ppt: 'orange',
  xls: 'green',
  image: 'purple',
  video: 'cyan',
  archive: 'geekblue',
  text: 'default'
}

// 文件类型文本映射
const fileTypeTextMap: Record<string, string> = {
  pdf: 'PDF',
  doc: 'Word',
  ppt: 'PPT',
  xls: 'Excel',
  text: '文本',
  image: '图片',
  archive: '压缩包',
  video: '视频',
  other: '其他'
}

// 获取文件类型颜色
const getFileTypeColor = (type?: string): string => {
  return fileTypeColorMap[type || ''] || 'default'
}

// 获取文件类型文本
const getFileTypeText = (type?: string): string => {
  return fileTypeTextMap[type || ''] || '其他'
}

// 格式化文件大小
const formatFileSize = (bytes?: number): string => {
  if (!bytes) return '0 B'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(2)} ${units[unitIndex]}`
}

// 分享
const handleShare = () => {
  message.info('分享功能开发中...')
  moreMenuVisible.value = false
}

// 删除
const handleDelete = async () => {
  if (!currentMaterial.value) return
  
  try {
    await materialApiIntMaterialIdDelete({
      materialId: currentMaterial.value.id
    })
    
    message.success('删除成功')
    moreMenuVisible.value = false
    loadMaterials()
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

// 初始化
onMounted(() => {
  loadMaterials()
  loadCategories()
})
</script>

<style scoped>
.material-center .content-container {
  padding: 16px;
}

.material-center .filter-card {
  margin-bottom: 16px;
}

.material-center .material-list-card {
  min-height: 400px;
}

.material-center .pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 24px;
  padding-top: 24px;
  border-top: 1px solid #f0f0f0;
}

.info-label {
  color: rgba(0, 0, 0, 0.65);
  font-weight: 500;
  margin-right: 8px;
}
</style>
