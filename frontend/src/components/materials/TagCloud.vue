<template>
  <div class="tag-cloud">
    <div class="cloud-header">
      <span class="header-title">热门标签</span>
      <a-button v-if="showManage" size="small" type="link" @click="handleManage">
        <SettingOutlined/>
        管理
      </a-button>
    </div>

    <a-spin :spinning="loading">
      <div v-if="tags.length > 0" class="tag-list">
        <a-tag
            v-for="tag in displayTags"
            :key="tag.id"
            :class="{ 'tag-selected': selectedTags.includes(tag.id) }"
            :color="getTagColor(tag.usageCount)"
            class="cloud-tag"
            @click="handleTagClick(tag)"
        >

          {{ tag.name }}
        </a-tag>
      </div>

      <a-empty
          v-else-if="!loading"
          :image="Empty.PRESENTED_IMAGE_SIMPLE"
          description="暂无标签"
      />

      <!-- 展开/收起按钮 -->
      <div v-if="tags.length > defaultShowCount" class="expand-btn">
        <a-button size="small" type="link" @click="toggleExpand">
          {{ expanded ? '收起' : `展开全部 (${tags.length})` }}
          <component :is="expanded ? UpOutlined : DownOutlined"/>
        </a-button>
      </div>
    </a-spin>

    <!-- 标签管理对话框 -->
    <a-modal
        v-model:open="manageModalVisible"
        :footer="null"
        title="标签管理"
        width="800px"
    >
      <div class="tag-manage">
        <div class="manage-actions">
          <a-space>
            <a-input-search
                v-model:value="searchKeyword"
                placeholder="搜索标签..."
                style="width: 300px"
                @search="handleSearch"
            />
            <a-button type="primary" @click="handleAddTag">
              <PlusOutlined/>
              添加标签
            </a-button>
          </a-space>
        </div>

        <a-table
            :columns="columns"
            :data-source="filteredTags"
            :loading="loading"
            :pagination="{ pageSize: 10 }"
            row-key="id"
        >
          <template #bodyCell="{ column, record }">
            <template v-if="column.key === 'name'">
              <a-tag :color="getTagColor(record.usageCount)">
                {{ record.name }}
              </a-tag>
            </template>
            <template v-else-if="column.key === 'actions'">
              <a-popconfirm
                  title="确定删除此标签吗？"
                  @confirm="handleDeleteTag(record.id)"
              >
                <a-button danger size="small" type="link">
                  删除
                </a-button>
              </a-popconfirm>
            </template>
          </template>
        </a-table>
      </div>
    </a-modal>

    <!-- 添加标签对话框 -->
    <a-modal
        v-model:open="addModalVisible"
        :confirm-loading="addLoading"
        title="添加标签"
        @cancel="handleCancelAdd"
        @ok="handleSubmitTag"
    >
      <a-form
          ref="addFormRef"
          :label-col="{ span: 6 }"
          :model="addForm"
          :wrapper-col="{ span: 18 }"
      >
        <a-form-item
            :rules="[
            { required: true, message: '请输入标签名称' },
            { max: 20, message: '标签名称不能超过20个字符' }
          ]"
            label="标签名称"
            name="name"
        >
          <a-input
              v-model:value="addForm.name"
              :maxlength="20"
              placeholder="请输入标签名称"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import {computed, onMounted, ref} from 'vue'
import {Empty, message} from 'ant-design-vue'
import {DownOutlined, PlusOutlined, SettingOutlined, UpOutlined} from '@ant-design/icons-vue'
import {tagApiGet, tagApiIntTagIdDelete, tagApiPost} from '@/api/tagController'

interface Tag {
  id: number
  name: string
  usageCount: number
}

interface Props {
  showManage?: boolean
  defaultShowCount?: number
  modelValue?: number[]
}

interface Emits {
  (e: 'update:modelValue', value: number[]): void

  (e: 'select', tagIds: number[]): void
}

const props = withDefaults(defineProps<Props>(), {
  showManage: false,
  defaultShowCount: 20,
  modelValue: () => []
})

const emit = defineEmits<Emits>()

const loading = ref(false)
const tags = ref<Tag[]>([])
const selectedTags = ref<number[]>(props.modelValue)
const expanded = ref(false)
const manageModalVisible = ref(false)
const addModalVisible = ref(false)
const addLoading = ref(false)
const searchKeyword = ref('')
const addFormRef = ref()
const addForm = ref({
  name: ''
})

// 表格列定义
const columns = [
  {title: '标签名称', dataIndex: 'name', key: 'name'},
  {title: '使用次数', dataIndex: 'usageCount', key: 'usageCount', width: 120},
  {title: '操作', key: 'actions', width: 100}
]

// 显示的标签列表
const displayTags = computed(() => {
  if (expanded.value || tags.value.length <= props.defaultShowCount) {
    return tags.value
  }
  return tags.value.slice(0, props.defaultShowCount)
})

// 过滤后的标签列表（用于管理对话框）
const filteredTags = computed(() => {
  if (!Array.isArray(tags.value)) return []

  if (!searchKeyword.value) {
    return tags.value
  }
  return tags.value.filter(tag =>
      tag.name.toLowerCase().includes(searchKeyword.value.toLowerCase())
  )
})

// 加载标签列表
const loadTags = async () => {
  loading.value = true
  try {
    const response = await tagApiGet()
    const data = (response as any).data?.data || (response as any).data
    // 后端返回的是 { tags: [...] } 格式
    const tagList = data?.tags || []
    tags.value = Array.isArray(tagList)
        ? tagList.sort((a: Tag, b: Tag) => b.usageCount - a.usageCount)
        : []
  } catch (error: any) {
    console.error('加载标签失败:', error)
    message.error(error.message || '加载标签失败')
    tags.value = []
  } finally {
    loading.value = false
  }
}

// 获取标签颜色（根据使用次数）
const getTagColor = (usageCount: number): string => {
  if (usageCount >= 50) return 'red'
  if (usageCount >= 30) return 'orange'
  if (usageCount >= 20) return 'gold'
  if (usageCount >= 10) return 'blue'
  if (usageCount >= 5) return 'cyan'
  return 'default'
}

// 点击标签
const handleTagClick = (tag: Tag) => {
  const index = selectedTags.value.indexOf(tag.id)
  if (index > -1) {
    selectedTags.value.splice(index, 1)
  } else {
    selectedTags.value.push(tag.id)
  }

  emit('update:modelValue', selectedTags.value)
  emit('select', selectedTags.value)
}

// 展开/收起
const toggleExpand = () => {
  expanded.value = !expanded.value
}

// 打开管理对话框
const handleManage = () => {
  manageModalVisible.value = true
}

// 搜索标签
const handleSearch = () => {
  // 搜索逻辑已在 computed 中实现
}

// 添加标签
const handleAddTag = () => {
  addForm.value = {name: ''}
  addModalVisible.value = true
}

// 提交标签
const handleSubmitTag = async () => {
  try {
    await addFormRef.value?.validate()

    addLoading.value = true

    await tagApiPost({name: addForm.value.name})
    message.success('标签创建成功')

    addModalVisible.value = false
    await loadTags()
  } catch (error: any) {
    if (error.errorFields) {
      return
    }
    message.error(error.message || '创建失败')
  } finally {
    addLoading.value = false
  }
}

// 取消添加
const handleCancelAdd = () => {
  addFormRef.value?.resetFields()
  addModalVisible.value = false
}

// 删除标签
const handleDeleteTag = async (tagId: number) => {
  try {
    await tagApiIntTagIdDelete({tagId})
    message.success('标签删除成功')
    await loadTags()
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

onMounted(() => {
  loadTags()
})
</script>

<style scoped>
.tag-cloud {
  background: white;
  border-radius: 4px;
  padding: 16px;
}

.cloud-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-top: 1px solid #f0f0f0;
}

.header-title {
  font-weight: 500;
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
}

.tag-list {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.cloud-tag {
  cursor: pointer;
  transition: all 0.3s;
  margin: 0;
}

.cloud-tag:hover {
  transform: scale(1.05);
  opacity: 0.8;
}

.cloud-tag.tag-selected {
  border: 2px solid #1890ff;
  font-weight: 500;
}

.tag-count {
  margin-left: 4px;
  font-size: 12px;
  opacity: 0.8;
}

.expand-btn {
  margin-top: 12px;
  text-align: center;
}

.tag-manage {
  padding: 16px 0;
}

.manage-actions {
  margin-bottom: 16px;
}
</style>
