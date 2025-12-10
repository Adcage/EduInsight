<template>
  <div class="my-materials">
    <a-page-header
        sub-title="管理我上传的教学资料"
        title="我的资料"
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
      <!-- 统计信息 -->
      <a-row :gutter="16" class="stats-row">
        <a-col :md="6" :sm="12" :xs="24">
          <a-statistic
              :value="total"
              :value-style="{ color: '#1890ff' }"
              title="资料总数"
          >
            <template #prefix>
              <FileOutlined/>
            </template>
          </a-statistic>
        </a-col>
        <a-col :md="6" :sm="12" :xs="24">
          <a-statistic
              :value="totalDownloads"
              :value-style="{ color: '#52c41a' }"
              title="总下载次数"
          >
            <template #prefix>
              <DownloadOutlined/>
            </template>
          </a-statistic>
        </a-col>
        <a-col :md="6" :sm="12" :xs="24">
          <a-statistic
              :value="totalViews"
              :value-style="{ color: '#faad14' }"
              title="总浏览次数"
          >
            <template #prefix>
              <EyeOutlined/>
            </template>
          </a-statistic>
        </a-col>
        <a-col :md="6" :sm="12" :xs="24">
          <a-statistic
              :value="formatTotalSize(totalSize)"
              :value-style="{ color: '#eb2f96' }"
              title="总文件大小"
          >
            <template #prefix>
              <DatabaseOutlined/>
            </template>
          </a-statistic>
        </a-col>
      </a-row>

      <!-- 搜索和筛选区域 -->
      <a-card :bordered="false" class="filter-card">
        <a-space :size="16" direction="vertical" style="width: 100%">
          <!-- 搜索框 -->
          <a-input-search
              v-model:value="searchKeyword"
              allow-clear
              placeholder="搜索资料标题、描述..."
              size="large"
              @search="handleSearch"
          >
            <template #enterButton>
              <a-button type="primary">
                <SearchOutlined/>
                搜索
              </a-button>
            </template>
          </a-input-search>

          <!-- 筛选器 -->
          <a-row :gutter="16">
            <a-col :span="6">
              <a-select
                  v-model:value="filters.categoryId"
                  allow-clear
                  placeholder="选择分类"
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
                  allow-clear
                  placeholder="文件类型"
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

      <!-- 资料列表 - 表格视图 -->
      <a-card :bordered="false" class="material-list-card">
        <a-spin :spinning="loading">
          <a-table
              :columns="columns"
              :data-source="materials"
              :loading="loading"
              :pagination="pagination"
              :scroll="{ x: 1200 }"
              @change="handleTableChange"
          >
            <!-- 文件名列 -->
            <template #bodyCell="{ column, record }">
              <template v-if="column.key === 'fileName'">
                <a-space :size="8">
                  <component :is="getFileIcon(record.fileType)"/>
                  <a-tooltip :title="record.fileName">
                    <span class="file-name">{{ record.fileName }}</span>
                  </a-tooltip>
                </a-space>
              </template>

              <!-- 文件类型列 -->
              <template v-else-if="column.key === 'fileType'">
                <a-tag :color="getFileTypeColor(record.fileType)">
                  {{ getFileTypeText(record.fileType) }}
                </a-tag>
              </template>

              <!-- 文件大小列 -->
              <template v-else-if="column.key === 'fileSize'">
                {{ formatFileSize(record.fileSize) }}
              </template>

              <!-- 统计列 -->
              <template v-else-if="column.key === 'statistics'">
                <a-space :size="16">
                  <a-tooltip title="浏览次数">
                    <span>
                      <EyeOutlined/>
                      {{ record.viewCount || 0 }}
                    </span>
                  </a-tooltip>
                  <a-tooltip title="下载次数">
                    <span>
                      <DownloadOutlined/>
                      {{ record.downloadCount || 0 }}
                    </span>
                  </a-tooltip>
                </a-space>
              </template>

              <!-- 上传时间列 -->
              <template v-else-if="column.key === 'createdAt'">
                {{ formatDateTime(record.createdAt) }}
              </template>

              <!-- 操作列 -->
              <template v-else-if="column.key === 'action'">
                <a-space :size="8">
                  <a-button
                      size="small"
                      type="link"
                      @click="handleView(record)"
                  >
                    查看
                  </a-button>
                  <a-button
                      size="small"
                      type="link"
                      @click="handleEdit(record)"
                  >
                    编辑
                  </a-button>
                  <a-button
                      danger
                      size="small"
                      type="link"
                      @click="showDeleteConfirm(record)"
                  >
                    删除
                  </a-button>
                </a-space>
              </template>
            </template>
          </a-table>
        </a-spin>
      </a-card>
    </div>

    <!-- 编辑资料对话框 -->
    <a-modal
        v-model:open="editModalVisible"
        :confirm-loading="editLoading"
        title="编辑资料"
        width="600px"
        @cancel="handleEditCancel"
        @ok="handleEditSubmit"
    >
      <a-form
          ref="editFormRef"
          :label-col="{ span: 5 }"
          :model="editForm"
          :wrapper-col="{ span: 19 }"
      >
        <a-form-item
            :rules="[{ required: true, message: '请输入资料标题' }]"
            label="资料标题"
            name="title"
        >
          <a-input
              v-model:value="editForm.title"
              :maxlength="100"
              placeholder="请输入资料标题"
          />
        </a-form-item>

        <a-form-item label="资料描述" name="description">
          <a-textarea
              v-model:value="editForm.description"
              :maxlength="500"
              :rows="4"
              placeholder="请输入资料描述"
              show-count
          />
        </a-form-item>

        <a-form-item label="分类" name="categoryId">
          <a-select
              v-model:value="editForm.categoryId"
              allow-clear
              placeholder="请选择分类"
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
              :max-tag-count="5"
              mode="tags"
              placeholder="请输入标签（按回车添加）"
          >
          </a-select>
        </a-form-item>

        <a-form-item label="文件信息">
          <a-space :size="4" direction="vertical">
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

<script lang="ts" setup>
import {onMounted, reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import {message, Modal} from 'ant-design-vue'
import {
  DatabaseOutlined,
  DownloadOutlined,
  EyeOutlined,
  FileExcelOutlined,
  FileImageOutlined,
  FileOutlined,
  FilePdfOutlined,
  FilePptOutlined,
  FileTextOutlined,
  FileWordOutlined,
  FileZipOutlined,
  SearchOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'
import dayjs from 'dayjs'
import {materialApiGet, materialApiIntMaterialIdDelete, materialApiIntMaterialIdPut} from '@/api/materialController.ts'
import {categoryApiGet} from '@/api/categoryController.ts'

const router = useRouter()

// 状态
const loading = ref(false)
const searchKeyword = ref('')
const materials = ref<any[]>([])
const categories = ref<any[]>([])
const total = ref(0)
const totalDownloads = ref(0)
const totalViews = ref(0)
const totalSize = ref(0)
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
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  pageSizeOptions: ['10', '20', '50', '100'],
  showTotal: (total: number) => `共 ${total} 条`
})

// 表格列定义
const columns = [
  {
    title: '文件名',
    dataIndex: 'fileName',
    key: 'fileName',
    width: 200,
    ellipsis: true
  },
  {
    title: '文件类型',
    dataIndex: 'fileType',
    key: 'fileType',
    width: 100
  },
  {
    title: '文件大小',
    dataIndex: 'fileSize',
    key: 'fileSize',
    width: 100
  },
  {
    title: '分类',
    dataIndex: 'category',
    key: 'category',
    width: 100,
    customRender: ({text}: any) => text?.name || '未分类'
  },
  {
    title: '统计',
    dataIndex: 'statistics',
    key: 'statistics',
    width: 150
  },
  {
    title: '上传时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 150
  },
  {
    title: '操作',
    dataIndex: 'action',
    key: 'action',
    width: 150,
    fixed: 'right'
  }
]

// 文件图标映射
const fileIconMap: Record<string, any> = {
  pdf: FilePdfOutlined,
  doc: FileWordOutlined,
  ppt: FilePptOutlined,
  xls: FileExcelOutlined,
  text: FileTextOutlined,
  image: FileImageOutlined,
  archive: FileZipOutlined,
  other: FileOutlined
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

// 获取文件图标
const getFileIcon = (type?: string): any => {
  return fileIconMap[type || ''] || FileOutlined
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

// 格式化总大小
const formatTotalSize = (bytes: number): string => {
  return formatFileSize(bytes)
}

// 格式化日期时间
const formatDateTime = (date?: string): string => {
  if (!date) return ''
  return dayjs(date).format('YYYY-MM-DD HH:mm')
}

// 加载资料列表
const loadMaterials = async () => {
  loading.value = true
  try {
    // 从 localStorage 获取当前用户信息
    const userInfo = localStorage.getItem('user')  // 注意：登录时存储的键是'user'而不是'userInfo'
    let currentUserId = null
    if (userInfo) {
      try {
        const user = JSON.parse(userInfo)
        currentUserId = user.id
        console.log('当前用户ID:', currentUserId, '用户信息:', user)
      } catch (e) {
        console.error('解析用户信息失败:', e)
      }
    } else {
      console.warn('未找到用户信息')
    }

    const params: any = {
      page: pagination.current,
      perPage: pagination.pageSize,
      sort_by: filters.sortBy,
      order: filters.order
    }

    // 添加当前用户ID筛选,只显示当前用户上传的资料
    if (currentUserId) {
      params.uploader_id = currentUserId
      console.log('添加uploader_id筛选:', currentUserId)
    }

    console.log('请求参数:', params)

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
    materials.value = data?.materials || []
    total.value = data?.total || 0
    pagination.total = total.value

    // 计算统计信息
    calculateStatistics()
  } catch (error: any) {
    message.error(error.message || '加载资料列表失败')
  } finally {
    loading.value = false
  }
}

// 计算统计信息
const calculateStatistics = () => {
  totalDownloads.value = materials.value.reduce((sum, m) => sum + (m.downloadCount || 0), 0)
  totalViews.value = materials.value.reduce((sum, m) => sum + (m.viewCount || 0), 0)
  totalSize.value = materials.value.reduce((sum, m) => sum + (m.fileSize || 0), 0)
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await categoryApiGet()
    const data = (response as any).data?.data || (response as any).data
    // 后端返回的数据结构是 {categories: [...]}
    categories.value = data?.categories || data || []
  } catch (error: any) {
    console.error('加载分类失败:', error)
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  loadMaterials()
}

// 筛选变化
const handleFilterChange = () => {
  pagination.current = 1
  loadMaterials()
}

// 表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  loadMaterials()
}

// 上传资料
const handleUpload = () => {
  router.push('/teacher/materials/upload')
}

// 查看详情
const handleView = (material: any) => {
  router.push(`/teacher/materials/${material.id}`)
}

// 编辑
const handleEdit = (material: any) => {
  // 填充编辑表单
  editForm.id = material.id
  editForm.title = material.title
  editForm.description = material.description || ''
  editForm.categoryId = material.categoryId || null
  editForm.tags = material.tags?.map((tag: any) => tag.name) || []
  editForm.fileName = material.fileName
  editForm.fileType = material.fileType
  editForm.fileSize = material.fileSize

  editModalVisible.value = true
}

// 提交编辑
const handleEditSubmit = async () => {
  try {
    // 验证表单
    await editFormRef.value?.validate()

    editLoading.value = true

    // 调用更新API
    await materialApiIntMaterialIdPut(
        {materialId: editForm.id},
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

// 删除确认
const showDeleteConfirm = (material: any) => {
  Modal.confirm({
    title: '确认删除',
    content: `确定要删除资料"${material.title}"吗？删除后无法恢复。`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    onOk: () => handleDelete(material)
  })
}

// 删除
const handleDelete = async (material: any) => {
  try {
    await materialApiIntMaterialIdDelete({
      materialId: material.id
    })

    message.success('删除成功')
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
.my-materials .content-container {
  padding: 16px;
}

.my-materials .stats-row {
  margin-bottom: 24px;
}

.my-materials .filter-card {
  margin-bottom: 16px;
}

.my-materials .material-list-card {
  min-height: 400px;
}

.file-name {
  max-width: 200px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  display: inline-block;
}

.info-label {
  color: rgba(0, 0, 0, 0.65);
  font-weight: 500;
  margin-right: 8px;
}
</style>
