<template>
  <div class="category-tree">
    <div class="tree-header">
      <span class="header-title">资料分类</span>
      <a-button v-if="showManage" size="small" type="link" @click="handleManage">
        <SettingOutlined/>
        管理
      </a-button>
    </div>

    <a-spin :spinning="loading">
      <a-tree
          v-model:expandedKeys="expandedKeys"
          v-model:selectedKeys="selectedKeys"
          :field-names="{ title: 'name', key: 'id', children: 'children' }"
          :show-line="true"
          :tree-data="treeData"
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
          :image="Empty.PRESENTED_IMAGE_SIMPLE"
          description="暂无分类"
      />
    </a-spin>

    <!-- 分类管理对话框 -->
    <a-modal
        v-model:open="manageModalVisible"
        :footer="null"
        title="分类管理"
        width="800px"
    >
      <div class="category-manage">
        <div class="manage-actions">
          <a-button type="primary" @click="handleAddCategory">
            <PlusOutlined/>
            添加分类
          </a-button>
        </div>

        <a-table
            :columns="columns"
            :custom-row="customTableRow"
            :data-source="categories"
            :expanded-row-keys="tableExpandedKeys"
            :indent-size="30"
            :loading="loading"
            :pagination="false"
            row-key="id"
            @expand="handleTableExpand"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'actions'">
              <a-space>
                <a-button size="small" type="link" @click.stop="handleEditCategory(record)">
                  编辑
                </a-button>
                <a-button danger size="small" type="link" @click.stop="confirmDeleteCategory(record)">
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
        :confirm-loading="editLoading"
        :title="editingCategory ? '编辑分类' : '添加分类'"
        @cancel="handleCancelEdit"
        @ok="handleSubmitCategory"
    >
      <a-form
          ref="editFormRef"
          :label-col="{ span: 6 }"
          :model="editForm"
          :wrapper-col="{ span: 18 }"
      >
        <a-form-item
            :rules="[{ required: true, message: '请输入分类名称' }]"
            label="分类名称"
            name="name"
        >
          <a-input v-model:value="editForm.name" placeholder="请输入分类名称"/>
        </a-form-item>

        <a-form-item label="父分类" name="parentId">
          <a-tree-select
              v-model:value="editForm.parentId"
              :field-names="{ label: 'name', value: 'id', children: 'children' }"
              :tree-data="parentOptions"
              allow-clear
              placeholder="选择父分类（不选则为顶级分类）"
              tree-default-expand-all
          />
        </a-form-item>

        <a-form-item label="分类描述" name="description">
          <a-textarea
              v-model:value="editForm.description"
              :rows="3"
              placeholder="请输入分类描述"
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

<script lang="ts" setup>
import {computed, onMounted, ref, watch} from 'vue'
import {Empty, message, Modal} from 'ant-design-vue'
import {PlusOutlined, SettingOutlined} from '@ant-design/icons-vue'
import {
  categoryApiGet,
  categoryApiIntCategoryIdDelete,
  categoryApiIntCategoryIdPut,
  categoryApiPost
} from '@/api/categoryController'
import {materialApiGet} from '@/api/materialController'

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
  {title: '分类名称', dataIndex: 'name', key: 'name'},
  {title: '描述', dataIndex: 'description', key: 'description'},
  {title: '排序', dataIndex: 'sortOrder', key: 'sortOrder', width: 80},
  {title: '操作', key: 'actions', width: 150}
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
    map.set(item.id, {...item, children: []})
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


    // 将平铺列表转换为树形结构
    categories.value = buildCategoryTree(flatList)

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
    const response = await materialApiGet({page: 1, perPage: 1000})
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
          {categoryId: editingCategory.value.id},
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
    await categoryApiIntCategoryIdDelete({categoryId: category.id})
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
    await categoryApiIntCategoryIdDelete({categoryId})
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
