# Stores 使用说明

本目录包含使用 Pinia 实现的状态管理 stores。

## 已实现的 Stores

### 1. Material Store (`material.ts`)

资料管理相关的状态管理。

**功能特性：**
- ✅ 资料列表获取（支持分页、筛选、排序）
- ✅ 资料详情获取（带缓存）
- ✅ 资料上传
- ✅ 资料更新
- ✅ 资料删除
- ✅ 资料搜索
- ✅ 5分钟缓存策略

**使用示例：**

```typescript
import { useMaterialStore } from '@/stores/material'

// 在组件中使用
const materialStore = useMaterialStore()

// 获取资料列表
await materialStore.fetchMaterials({
  page: 1,
  perPage: 20,
  courseId: 1,
  categoryId: 2,
  fileType: 'pdf',
  keyword: '搜索关键词'
})

// 获取资料详情（自动缓存）
await materialStore.fetchMaterialDetail(materialId)

// 强制刷新（跳过缓存）
await materialStore.fetchMaterialDetail(materialId, true)

// 上传资料
const formData = new FormData()
formData.append('file', file)
formData.append('title', '资料标题')
await materialStore.uploadMaterial(formData)

// 更新资料
await materialStore.updateMaterial(materialId, {
  title: '新标题',
  description: '新描述',
  categoryId: 3,
  tags: ['标签1', '标签2']
})

// 删除资料
await materialStore.deleteMaterial(materialId)

// 搜索资料
await materialStore.searchMaterials('关键词', { page: 1, perPage: 20 })

// 访问状态
console.log(materialStore.materials) // 资料列表
console.log(materialStore.currentMaterial) // 当前资料
console.log(materialStore.total) // 总数
console.log(materialStore.loading) // 加载状态
console.log(materialStore.filters) // 当前过滤器

// 计算属性
console.log(materialStore.hasMore) // 是否还有更多
console.log(materialStore.isEmpty) // 是否为空

// 工具方法
materialStore.resetFilters() // 重置过滤器
materialStore.clearCache() // 清除所有缓存
materialStore.clearExpiredCache() // 清除过期缓存
```

### 2. Category Store (`category.ts`)

分类管理相关的状态管理。

**功能特性：**
- ✅ 分类列表获取（树形结构）
- ✅ 分类创建
- ✅ 分类更新
- ✅ 分类删除
- ✅ 分类路径获取（面包屑）
- ✅ 10分钟缓存策略

**使用示例：**

```typescript
import { useCategoryStore } from '@/stores/category'

const categoryStore = useCategoryStore()

// 获取分类树
await categoryStore.fetchCategories()

// 强制刷新
await categoryStore.fetchCategories(true)

// 创建分类
await categoryStore.createCategory({
  name: '新分类',
  parentId: 1, // 可选，父分类ID
  description: '分类描述',
  sortOrder: 1
})

// 更新分类
await categoryStore.updateCategory(categoryId, {
  name: '更新后的名称',
  description: '更新后的描述'
})

// 删除分类
await categoryStore.deleteCategory(categoryId)

// 根据ID获取分类
const category = categoryStore.getCategoryById(categoryId)

// 获取分类路径（面包屑导航）
const path = categoryStore.getCategoryPath(categoryId)
// 返回: [{ id: 1, name: '根分类' }, { id: 2, name: '子分类' }]

// 访问状态
console.log(categoryStore.categoryTree) // 树形结构
console.log(categoryStore.flatCategories) // 扁平化列表
console.log(categoryStore.categoryMap) // Map映射
console.log(categoryStore.loading) // 加载状态

// 清除缓存
categoryStore.clearCache()
```

### 3. Course Store (`course.ts`)

课程管理相关的状态管理（待完善）。

**注意：** 该 store 目前使用模拟数据，需要在实现课程 API 后进行完善。

**使用示例：**

```typescript
import { useCourseStore } from '@/stores/course'

const courseStore = useCourseStore()

// 获取课程列表
await courseStore.fetchCourses()

// 获取课程详情
await courseStore.fetchCourseDetail(courseId)

// 访问状态
console.log(courseStore.courses) // 课程列表
console.log(courseStore.activeCourses) // 进行中的课程
console.log(courseStore.courseMap) // Map映射
console.log(courseStore.loading) // 加载状态

// 根据ID获取课程
const course = courseStore.getCourseById(courseId)
```

## 缓存策略

### Material Store
- **缓存时长：** 5分钟
- **缓存内容：** 资料详情
- **缓存键：** 资料ID
- **清理策略：** 手动清理 + 过期清理

### Category Store
- **缓存时长：** 10分钟
- **缓存内容：** 整个分类树
- **清理策略：** 手动清理 + 时间戳检查

### Course Store
- **缓存时长：** 10分钟
- **缓存内容：** 课程列表
- **清理策略：** 手动清理 + 时间戳检查

## 最佳实践

### 1. 在组件中使用

```vue
<script setup lang="ts">
import { onMounted } from 'vue'
import { useMaterialStore } from '@/stores/material'

const materialStore = useMaterialStore()

onMounted(async () => {
  // 组件挂载时加载数据
  await materialStore.fetchMaterials()
})
</script>
```

### 2. 响应式数据访问

```typescript
import { computed } from 'vue'
import { useMaterialStore } from '@/stores/material'

const materialStore = useMaterialStore()

// 使用 computed 访问 store 数据
const materials = computed(() => materialStore.materials)
const loading = computed(() => materialStore.loading)
```

### 3. 错误处理

```typescript
try {
  await materialStore.fetchMaterials()
} catch (error) {
  console.error('加载失败:', error)
  message.error('加载资料列表失败')
}
```

### 4. 缓存管理

```typescript
// 定期清理过期缓存（可在 App.vue 中设置）
setInterval(() => {
  materialStore.clearExpiredCache()
}, 60000) // 每分钟清理一次

// 用户登出时清除所有缓存
const handleLogout = () => {
  materialStore.clearCache()
  categoryStore.clearCache()
  courseStore.clearCache()
}
```

## 待完善功能

### Course Store
- [ ] 实现课程 API 接口
- [ ] 完善课程 CRUD 操作
- [ ] 添加课程详情缓存

### Material Store
- [ ] 添加批量操作支持
- [ ] 实现资料统计功能
- [ ] 优化大列表性能

### Category Store
- [ ] 添加拖拽排序支持
- [ ] 实现分类统计（资料数量）

## 注意事项

1. **权限控制：** Store 中不包含权限验证逻辑，权限验证应在组件层面或 API 层面处理
2. **错误处理：** Store 方法会抛出错误，调用时需要使用 try-catch 处理
3. **缓存刷新：** 修改数据后会自动更新缓存，但某些情况下可能需要手动刷新
4. **并发请求：** Store 不处理并发请求去重，如需要请在组件层面处理
