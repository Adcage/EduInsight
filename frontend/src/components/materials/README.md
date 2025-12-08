# 资料中心组件库

资料中心的可复用组件集合，提供完整的资料管理功能。

## 组件列表

### 1. SearchBar - 搜索栏组件

智能搜索组件，支持搜索建议和历史记录。

**功能特性：**

- 实时搜索建议（防抖处理）
- 搜索历史记录（本地存储）
- 点击建议快速搜索
- 清空历史记录

**使用示例：**

```vue
<template>
  <SearchBar v-model="searchKeyword" @search="handleSearch" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import SearchBar from '@/components/materials/SearchBar.vue'

const searchKeyword = ref('')

const handleSearch = (keyword: string) => {
  console.log('搜索关键词:', keyword)
  // 执行搜索逻辑
}
</script>
```

**Props：**

- `modelValue?: string` - 搜索关键词（v-model）

**Events：**

- `update:modelValue` - 搜索关键词变化
- `search` - 执行搜索

---

### 2. CategoryTree - 分类树组件

树形结构展示和管理资料分类。

**功能特性：**

- 树形结构展示
- 显示资料数量统计
- 分类选择
- 分类管理（添加/编辑/删除）
- 父分类选择
- 排序设置

**使用示例：**

```vue
<template>
  <CategoryTree v-model="selectedCategoryId" :show-manage="true" :show-count="true" @select="handleCategorySelect" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import CategoryTree from '@/components/materials/CategoryTree.vue'

const selectedCategoryId = ref<number | null>(null)

const handleCategorySelect = (categoryId: number | null) => {
  console.log('选中分类:', categoryId)
  // 执行筛选逻辑
}
</script>
```

**Props：**

- `modelValue?: number | null` - 选中的分类ID（v-model）
- `showManage?: boolean` - 是否显示管理按钮（默认：false）
- `showCount?: boolean` - 是否显示资料数量（默认：true）

**Events：**

- `update:modelValue` - 选中分类变化
- `select` - 选择分类

---

### 3. TagCloud - 标签云组件

展示和管理热门标签。

**功能特性：**

- 标签云展示（按使用次数排序）
- 根据使用次数显示不同颜色
- 标签选择/取消选择
- 展开/收起功能
- 标签管理（添加/删除）
- 标签搜索

**使用示例：**

```vue
<template>
  <TagCloud v-model="selectedTagIds" :show-manage="true" :default-show-count="20" @select="handleTagSelect" />
</template>

<script setup lang="ts">
import { ref } from 'vue'
import TagCloud from '@/components/materials/TagCloud.vue'

const selectedTagIds = ref<number[]>([])

const handleTagSelect = (tagIds: number[]) => {
  console.log('选中标签:', tagIds)
  // 执行筛选逻辑
}
</script>
```

**Props：**

- `modelValue?: number[]` - 选中的标签ID列表（v-model）
- `showManage?: boolean` - 是否显示管理按钮（默认：false）
- `defaultShowCount?: number` - 默认显示的标签数量（默认：20）

**Events：**

- `update:modelValue` - 选中标签变化
- `select` - 选择标签

---

### 4. AdvancedFilter - 高级筛选组件

多维度筛选组件，支持多种筛选条件。

**功能特性：**

- 基础筛选（分类、文件类型、排序）
- 高级筛选（课程、上传者、文件大小、时间范围）
- 展开/收起高级筛选
- 当前筛选条件可视化
- 单个条件移除
- 清空全部筛选
- URL 状态同步

**使用示例：**

```vue
<template>
  <AdvancedFilter v-model="filters" @change="handleFilterChange" />
</template>

<script setup lang="ts">
import { reactive } from 'vue'
import AdvancedFilter from '@/components/materials/AdvancedFilter.vue'

const filters = reactive({
  categoryId: null,
  fileType: null,
  sortBy: 'created_at',
  order: 'desc',
  courseId: null,
  uploaderId: null,
  fileSizeRange: null,
  dateRange: null,
})

const handleFilterChange = (newFilters: any) => {
  console.log('筛选条件变化:', newFilters)
  // 执行筛选逻辑
}
</script>
```

**Props：**

- `modelValue?: Partial<FilterValues>` - 筛选条件（v-model）

**Events：**

- `update:modelValue` - 筛选条件变化
- `change` - 应用筛选

**FilterValues 类型：**

```typescript
interface FilterValues {
  categoryId: number | null // 分类ID
  fileType: string | null // 文件类型
  sortBy: string // 排序字段
  order: string // 排序方向
  courseId: number | null // 课程ID
  uploaderId: number | null // 上传者ID
  fileSizeRange: string | null // 文件大小范围
  dateRange: [Dayjs, Dayjs] | null // 时间范围
}
```

---

### 5. MaterialCard - 资料卡片组件

展示单个资料的卡片组件。

**功能特性：**

- 文件图标展示
- 资料信息展示
- 统计信息（浏览、下载次数）
- 操作按钮（预览、下载、更多）

**使用示例：**

```vue
<template>
  <MaterialCard :material="material" @click="handleViewDetail" @preview="handlePreview" @download="handleDownload" @more="handleMore" />
</template>

<script setup lang="ts">
import MaterialCard from '@/components/materials/MaterialCard.vue'

const material = {
  id: 1,
  title: '示例资料',
  description: '这是一个示例资料',
  fileName: 'example.pdf',
  fileSize: 1024000,
  fileType: 'pdf',
  viewCount: 100,
  downloadCount: 50,
  createdAt: '2024-12-08',
}

const handleViewDetail = (material: any) => {
  console.log('查看详情:', material)
}

const handlePreview = (material: any) => {
  console.log('预览:', material)
}

const handleDownload = (material: any) => {
  console.log('下载:', material)
}

const handleMore = (material: any) => {
  console.log('更多操作:', material)
}
</script>
```

**Props：**

- `material: Material` - 资料对象

**Events：**

- `click` - 点击卡片
- `preview` - 预览
- `download` - 下载
- `more` - 更多操作

---

## 完整示例

查看 `MaterialCenterEnhanced.vue` 了解如何组合使用这些组件。

```vue
<template>
  <div class="material-center">
    <a-row :gutter="16">
      <!-- 左侧：分类和标签 -->
      <a-col :span="6">
        <CategoryTree v-model="filters.categoryId" :show-manage="true" @select="handleCategorySelect" />
        <TagCloud v-model="selectedTags" :show-manage="true" @select="handleTagSelect" />
      </a-col>

      <!-- 右侧：搜索、筛选和列表 -->
      <a-col :span="18">
        <SearchBar v-model="searchKeyword" @search="handleSearch" />
        <AdvancedFilter v-model="filters" @change="handleFilterChange" />
        <a-row :gutter="[16, 16]">
          <a-col v-for="material in materials" :key="material.id" :span="6">
            <MaterialCard :material="material" @click="handleViewDetail" />
          </a-col>
        </a-row>
      </a-col>
    </a-row>
  </div>
</template>
```

## 技术特性

- **TypeScript** - 完整的类型定义
- **响应式设计** - 支持多种屏幕尺寸
- **性能优化** - 防抖、节流、懒加载
- **状态管理** - 本地存储、URL 同步
- **用户体验** - 加载状态、错误处理、友好提示

## 依赖

- Vue 3
- Ant Design Vue
- Vue Router
- Lodash-es (防抖)
- Dayjs (日期处理)

## 注意事项

1. 所有组件都需要在有 API 支持的环境下使用
2. 确保已正确配置 API 接口
3. 某些功能需要用户登录权限
4. 建议在使用前查看各组件的 Props 和 Events 定义
