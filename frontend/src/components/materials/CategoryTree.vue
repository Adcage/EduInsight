<template>
  <div class="category-tree">
    <div class="tree-header">
      <span class="header-title">资料分类</span>
      <a-button v-if="showManage" type="link" size="small" @click="handleManage">
        <SettingOutlined />
        管理
      </a-button>
    </div>

    <a-spin :spinning="loading">
      <a-tree
        v-model:selectedKeys="selectedKeys"
        v-model:expandedKeys="expandedKeys"
        :tree-data="treeData"
        :field-names="{ title: 'name', key: 'id', children: 'children' }"
        :show-line="true"
        @select="handleSelect"
      >
        <template #title="{ name, id }">
          <div class="tree-node-title">
            <span class="node-name">{{ name }}</span>
            <span v-if="showCount" class="node-count">
              ({{ getCategoryCount(id) }})
            </span>
          </div>
        </template>
      </a-tree>

      <!-- 空状态 -->
      <a-empty
        v-if="!loading && treeData.length === 0"
        description="暂无分类"
        :image="Empty.PRESENTED_IMAGE_SIMPLE"
      />
    </a-spin>

    <!-- 分类管理对话框 -->
    <a-modal
      v-model:open="manageModalVisible"
      title="分类管理"
      width="800px"
      :footer="null"
    >
      <div class="category-manage">
        <div class="manage-actions">
          <a-button type="primary" @click="handleAddCategory">
            <PlusOutlined />
            添加分类
          </a-button>
        </div>

        <a-table
          :columns="columns"
          :data-source="categories"
          :pagination="false"
          :loading="loading"
          row-key="id"
          :indent-size="30"
          :expanded-row-keys="tableExpandedKeys"
          @expand="handleTableExpand"
          :custom-row="customTableRow"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button type="link" size="small" @click.stop="handleEditCategory(record)">
                  编辑
                </a-button>
                <a-button type="link" danger size="small" @click.stop="confirmDeleteCategory(record)">
                  删除
                </a-button>
              </a-space>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>

    <!-- 添加/编辑分类对话框 -->
    <a-modal
      v-model:open="editModalVisible"
      :title="editingCategory ? '编辑分类' : '添加分类'"
      :confirm-loading="editLoading"
      @ok="handleSubmitCategory"
      @cancel="handleCancelEdit"
    >
      <a-form
        ref="editFormRef"
        :model="editForm"
        :label-col="{ span: 6 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item
          label="分类名称"
          name="name"
          :rules="[{ required: true, message: '请输入分类名称' }]"
        >
          <a-input v-model:value="editForm.name" placeholder="请输入分类名称" />
        </a-form-item>

        <a-form-item label="父分类" name="parentId">
          <a-tree-select
            v-model:value="editForm.parentId"
            :tree-data="parentOptions"
            :field-names="{ label: 'name', value: 'id', children: 'children' }"
            placeholder="选择父分类（不选则为顶级分类）"
            allow-clear
            tree-default-expand-all
          />
        </a-form-item>

        <a-form-item label="分类描述" name="description">
          <a-textarea
            v-model:value="editForm.description"
            placeholder="请输入分类描述"
            :rows="3"
          />
        </a-form-item>

        <a-form-item label="排序序号" name="sortOrder">
          <a-input-number
            v-model:value="editForm.sortOrder"
            :min="0"
            placeholder="数字越小越靠前"
            style="width: 100%"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue'
import { message, Empty, Modal } from 'ant-design-vue'
import {
  SettingOutlined,
  PlusOutlined
} from '@ant-design/icons-vue'
import {
  categoryApiGet,
  categoryApiPost,
  categoryApiIntCategoryIdPut,
  categoryApiIntCategoryIdDelete
} from '@/api/categoryController'
import { materialApiGet } from '@/api/materialController'

interface Category {
  id: number
  name: string
  description?: string
  parentId?: number | null
  sortOrder: number
  children?: Category[]
  level?: number
}

interface Props {
  showManage?: boolean
  showCount?: boolean
  modelValue?: number | null
}

interface Emits {
  (e: 'update:modelValue', value: number | null): void
  (e: 'select', categoryId: number | null): void
}

const props = withDefaults(defineProps<Props>(), {
  showManage: false,
  showCount: true
})

const emit = defineEmits<Emits>()

const loading = ref(false)
const categories = ref<Category[]>([])
const selectedKeys = ref<number[]>([])
const expandedKeys = ref<number[]>([])  // 用于左侧树形控件
const tableExpandedKeys = ref<number[]>([])  // 用于管理对话框中的表格
const categoryCounts = ref<Record<number, number>>({})
const manageModalVisible = ref(false)
const editModalVisible = ref(false)
const editLoading = ref(false)
const editingCategory = ref<Category | null>(null)
const editFormRef = ref()
const editForm = ref({
  name: '',
  description: '',
  parentId: null as number | null,
  sortOrder: 0
})

// 表格列定义
const columns = [
  { title: '分类名称', dataIndex: 'name', key: 'name' },
  { title: '描述', dataIndex: 'description', key: 'description' },
  { title: '排序', dataIndex: 'sortOrder', key: 'sortOrder', width: 80 },
  { title: '操作', key: 'actions', width: 150 }
]

// 树形数据
const treeData = computed(() => {
  return categories.value
})

// 父分类选项（排除当前编辑的分类及其子分类）
const parentOptions = computed(() => {
  if (!Array.isArray(categories.value)) return []
  
  if (!editingCategory.value) {
    return categories.value
  }
  
  // 递归过滤掉当前分类及其子分类
  const filterCategory = (items: Category[]): Category[] => {
    if (!Array.isArray(items)) return []
    
    return items
      .filter(item => item.id !== editingCategory.value?.id)
      .map(item => ({
        ...item,
        children: item.children && Array.isArray(item.children) ? filterCategory(item.children) : []
      }))
  }
  
  return filterCategory(categories.value)
})

// 将平铺分类列表转换为树形结构
const buildCategoryTree = (flatList: Category[]): Category[] => {
  if (!Array.isArray(flatList)) return []
  
  const map = new Map<number, Category>()
  const roots: Category[] = []
  
  // 首先创建所有节点的副本并建立映射
  flatList.forEach(item => {
    map.set(item.id, { ...item, children: [] })
  })
  
  // 然后构建树形结构
  map.forEach(item => {
    // 使用 parent_id 或 parentId（兼容两种命名）
    const parentId = (item as any).parent_id ?? item.parentId
    
    if (parentId) {
      const parent = map.get(parentId)
      if (parent) {
        if (!parent.children) parent.children = []
        parent.children.push(item)
      } else {
        // 如果找不到父节点，作为根节点
        roots.push(item)
      }
    } else {
      // 没有父节点的作为根节点
      roots.push(item)
    }
  })
  
  return roots
}

// 加载分类列表
const loadCategories = async () => {
  loading.value = true
  try {
    const response = await categoryApiGet()
    const data = (response as any).data?.data || (response as any).data
    // 后端返回的是 { categories: [...] } 格式
    const categoryList = data?.categories || data
    // 确保 categoryList 是数组
    const flatList = Array.isArray(categoryList) ? categoryList : []
    
    console.log('📋 原始分类数据（平铺）:', flatList)
    console.log('📋 第一个分类的parentId:', flatList[0]?.parentId)
    
    // 将平铺列表转换为树形结构
    categories.value = buildCategoryTree(flatList)
    
    console.log('🌳 转换后的树形数据:', categories.value)
    console.log('🌳 根节点数量:', categories.value.length)
    if (categories.value.length > 0 && categories.value[0]?.children) {
      console.log('🌳 第一个根节点的子节点数量:', categories.value[0]?.children?.length)
    }
    
    // 加载分类统计
    if (props.showCount) {
      await loadCategoryCounts()
    }
  } catch (error: any) {
    console.error('加载分类失败:', error)
    message.error(error.message || '加载分类失败')
    categories.value = []
  } finally {
    loading.value = false
  }
}

// 获取所有分类ID
const getAllCategoryIds = (items: Category[]): number[] => {
  if (!Array.isArray(items)) return []
  
  const ids: number[] = []
  items.forEach(item => {
    ids.push(item.id)
    if (item.children && Array.isArray(item.children) && item.children.length > 0) {
      ids.push(...getAllCategoryIds(item.children))
    }
  })
  return ids
}

// 加载分类统计
const loadCategoryCounts = async () => {
  try {
    // 获取所有资料 - 使用 perPage 而非 page_size
    const response = await materialApiGet({ page: 1, perPage: 1000 })
    const data = (response as any).data?.data || (response as any).data
    const materialList = data?.materials || []
    const materials = Array.isArray(materialList) ? materialList : []
    
    // 统计每个分类的资料数量
    const counts: Record<number, number> = {}
    materials.forEach((material: any) => {
      if (material.categoryId) {
        counts[material.categoryId] = (counts[material.categoryId] || 0) + 1
      }
    })
    
    categoryCounts.value = counts
    console.log('分类统计加载完成:', counts)
  } catch (error) {
    console.error('加载分类统计失败:', error)
    categoryCounts.value = {}
  }
}

// 递归查找分类
const findCategoryById = (categories: Category[], id: number): Category | null => {
  for (const category of categories) {
    if (category.id === id) {
      return category
    }
    if (category.children && category.children.length > 0) {
      const found = findCategoryById(category.children, id)
      if (found) return found
    }
  }
  return null
}

// 获取分类资料数量（包含子分类）
const getCategoryCount = (categoryId: number): number => {
  // 获取当前分类自己的资料数量
  let count = categoryCounts.value[categoryId] || 0
  
  // 查找当前分类
  const category = findCategoryById(categories.value, categoryId)
  
  // 递归累加所有子分类的资料数量
  if (category && category.children && category.children.length > 0) {
    category.children.forEach(child => {
      count += getCategoryCount(child.id)
    })
  }
  
  return count
}

// 选择分类
const handleSelect = (selectedKeys: number[]) => {
  const categoryId = selectedKeys.length > 0 ? selectedKeys[0] : null
  emit('update:modelValue', categoryId)
  emit('select', categoryId)
  console.log('分类选择:', categoryId)
}

// 处理表格行展开/折叠
const handleExpand = (expanded: boolean, record: Category) => {
  const key = record.id
  if (expanded) {
    // 展开：添加到expandedKeys
    if (!expandedKeys.value.includes(key)) {
      expandedKeys.value.push(key)
    }
  } else {
    // 折叠：从expandedKeys移除
    const index = expandedKeys.value.indexOf(key)
    if (index > -1) {
      expandedKeys.value.splice(index, 1)
    }
  }
}

// 自定义行属性，实现点击行展开/折叠
const customRow = (record: Category) => {
  return {
    onClick: (event: Event) => {
      // 检查是否有子分类
      if (record.children && record.children.length > 0) {
        const isExpanded = expandedKeys.value.includes(record.id)
        handleExpand(!isExpanded, record)
      }
    }
  }
}

// 处理表格行展开/折叠（管理对话框中的表格）
const handleTableExpand = (expanded: boolean, record: Category) => {
  const key = record.id
  if (expanded) {
    // 展开：添加到tableExpandedKeys
    if (!tableExpandedKeys.value.includes(key)) {
      tableExpandedKeys.value.push(key)
    }
  } else {
    // 折叠：从tableExpandedKeys移除
    const index = tableExpandedKeys.value.indexOf(key)
    if (index > -1) {
      tableExpandedKeys.value.splice(index, 1)
    }
  }
}

// 自定义表格行属性，实现点击行展开/折叠（管理对话框中的表格）
const customTableRow = (record: Category) => {
  return {
    onClick: (event: Event) => {
      // 检查是否有子分类
      if (record.children && record.children.length > 0) {
        const isExpanded = tableExpandedKeys.value.includes(record.id)
        handleTableExpand(!isExpanded, record)
      }
    }
  }
}

// 打开管理对话框
const handleManage = () => {
  manageModalVisible.value = true
}

// 添加分类
const handleAddCategory = () => {
  editingCategory.value = null
  editForm.value = {
    name: '',
    description: '',
    parentId: null,
    sortOrder: 0
  }
  editModalVisible.value = true
}

// 编辑分类
const handleEditCategory = (category: Category) => {
  editingCategory.value = category
  editForm.value = {
    name: category.name,
    description: category.description || '',
    parentId: category.parentId || null,
    sortOrder: category.sortOrder
  }
  editModalVisible.value = true
}

// 提交分类
const handleSubmitCategory = async () => {
  try {
    await editFormRef.value?.validate()
    
    editLoading.value = true
    
    if (editingCategory.value) {
      // 更新分类
      await categoryApiIntCategoryIdPut(
        { categoryId: editingCategory.value.id },
        editForm.value
      )
      message.success('分类更新成功')
    } else {
      // 创建分类
      await categoryApiPost(editForm.value)
      message.success('分类创建成功')
    }
    
    editModalVisible.value = false
    await loadCategories()
  } catch (error: any) {
    if (error.errorFields) {
      return
    }
    message.error(error.message || '操作失败')
  } finally {
    editLoading.value = false
  }
}

// 取消编辑
const handleCancelEdit = () => {
  editFormRef.value?.resetFields()
  editModalVisible.value = false
}

// 确认删除分类（检查是否有子分类）
const confirmDeleteCategory = (category: Category) => {
  const hasChildren = category.children && category.children.length > 0
  
  if (hasChildren) {
    // 有子分类，询问是否级联删除
    Modal.confirm({
      title: '删除分类确认',
      content: `分类"${category.name}"包含 ${category.children!.length} 个子分类，是否同时删除所有子分类？`,
      okText: '删除全部',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await handleDeleteCategoryWithChildren(category)
      }
    })
  } else {
    // 没有子分类，直接确认删除
    Modal.confirm({
      title: '删除分类确认', 
      content: `确定删除分类"${category.name}"吗？`,
      okText: '确定',
      okType: 'danger',
      cancelText: '取消',
      onOk: async () => {
        await handleDeleteCategory(category.id)
      }
    })
  }
}

// 递归删除分类及其所有子分类
const handleDeleteCategoryWithChildren = async (category: Category) => {
  try {
    // 先递归删除所有子分类
    if (category.children && category.children.length > 0) {
      for (const child of category.children) {
        await handleDeleteCategoryWithChildren(child)
      }
    }
    
    // 最后删除自己
    await categoryApiIntCategoryIdDelete({ categoryId: category.id })
    message.success(`分类"${category.name}"删除成功`)
    await loadCategories()
  } catch (error: any) {
    message.error(error.message || `删除分类"${category.name}"失败`)
    throw error
  }
}

// 删除单个分类
const handleDeleteCategory = async (categoryId: number) => {
  try {
    await categoryApiIntCategoryIdDelete({ categoryId })
    message.success('分类删除成功')
    await loadCategories()
  } catch (error: any) {
    message.error(error.message || '删除失败')
    throw error
  }
}

watch(() => props.modelValue, (newValue) => {
  selectedKeys.value = newValue ? [newValue] : []
})

onMounted(() => {
  loadCategories()
  if (props.modelValue) {
    selectedKeys.value = [props.modelValue]
  }
})
</script>

<style scoped>
.category-tree {
  background: white;
  border-radius: 4px;
  padding: 16px;
}

.tree-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f0f0f0;
}

.header-title {
  font-weight: 500;
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
}

.tree-node-title {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
}

.node-name {
  flex: 1;
}

.node-count {
  color: rgba(0, 0, 0, 0.45);
  font-size: 12px;
  margin-left: 8px;
}

.category-manage {
  padding: 16px 0;
}

.manage-actions {
  margin-bottom: 16px;
}
</style>
