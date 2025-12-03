---
trigger: model_decision
description: 开发前端Vue页面时的代码规范
---

# 前端开发代码规范

## 目录
- [1. 概述](#1-概述)
- [2. 项目结构规范](#2-项目结构规范)
- [3. 命名规范](#3-命名规范)
- [4. Vue组件开发规范](#4-vue组件开发规范)
- [5. TypeScript开发规范](#5-typescript开发规范)
- [6. Ant Design Vue组件规范](#6-ant-design-vue组件规范)
- [7. 样式开发规范](#7-样式开发规范)
- [8. API接口规范](#8-api接口规范)
- [9. 状态管理规范](#9-状态管理规范)
- [10. 错误处理规范](#10-错误处理规范)
- [11. Git提交规范](#11-git提交规范)
- [12. 代码审查规范](#12-代码审查规范)
- [13. 性能规范](#13-性能规范)
- [14. Ant Design Vue快速参考](#14-ant-design-vue快速参考)
- [15. 主题样式编写规范](#15-主题样式编写规范)

---

## 1. 概述

### 1.1 规范目的
本规范旨在统一前端开发团队的代码风格，提高代码质量和可维护性，确保项目的长期稳定发展。

### 1.2 适用范围
- Vue 3 + TypeScript 项目
- 使用 Ant Design Vue 组件库
- 使用 Pinia 状态管理
- 使用 Vue Router 路由管理

### 1.3 规范原则
- **一致性**：团队成员编写的代码风格保持一致
- **可读性**：代码易于理解和维护
- **可扩展性**：便于功能扩展和重构
- **性能优先**：考虑代码执行效率和用户体验

---

## 2. 项目结构规范

### 2.1 目录结构
```
src/
├── access/              # 权限控制
│   ├── access.ts        # 权限判断逻辑
│   ├── router_access.ts # 路由权限拦截
│   └── index.ts         # 导出文件
├── api/                 # API接口定义
│   ├── typings.d.ts     # 类型定义
│   ├── authController.ts
│   └── index.ts
├── assets/              # 静态资源
│   ├── styles/          # 全局样式
│   │   ├── variables.scss
│   │   ├── mixins.scss
│   │   ├── themes/
│   │   └── index.scss
│   └── images/
├── components/          # 公共组件
├── composables/         # 组合式函数
├── layouts/             # 布局组件
├── pages/               # 页面组件
├── router/              # 路由配置
├── stores/              # 状态管理
├── utils/               # 工具函数
├── types/               # 类型定义
├── App.vue
├── main.ts
└── env.d.ts
```

### 2.2 目录命名规范
- 所有目录名使用**小写字母**
- 多个单词使用**下划线**连接
- 避免使用缩写，使用完整的英文单词

---

## 3. 命名规范

### 3.1 文件命名
#### Vue组件文件
```
# 页面组件：功能名 + Page
LoginPage.vue
UserManagePage.vue
DashboardPage.vue

# 布局组件：功能名 + Layout  
BasicLayout.vue
AdminLayout.vue

# 业务组件：功能描述
UserTable.vue
CompetitionForm.vue

# 全局组件：Global + 功能名
GlobalHeader.vue
GlobalFooter.vue
```

#### TypeScript文件
```
# 使用 camelCase
userController.ts
authController.ts
useAuth.ts
request.ts
```

#### 样式文件
```
# 使用 kebab-case
variables.scss
mixins.scss
theme-light.scss
```

### 3.2 变量命名
```typescript
// 常量：SCREAMING_SNAKE_CASE
const API_BASE_URL = 'https://api.example.com'
const MAX_RETRY_COUNT = 3

// 变量和函数：camelCase
const userName = 'admin'
const isLoggedIn = true
const getUserList = () => {}

// 类和接口：PascalCase
class UserService {}
interface ApiResponse {}
type UserRole = 'admin' | 'user'

// 私有属性：下划线前缀
class UserService {
  private _cache = new Map()
}
```

### 3.3 CSS类名命名
```scss
// BEM命名规范
.user-card {}                    // 块
.user-card__header {}            // 元素
.user-card--loading {}           // 修饰符
.user-card__header--active {}    // 元素修饰符
```

---

## 4. Vue组件开发规范

### 4.1 组件结构模板
```vue
<template>
  <div class="component-name">
    <!-- 模板内容 -->
  </div>
</template>

<script setup lang="ts">
// 1. 导入外部依赖
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'

// 2. 导入内部模块
import { useAuth } from '@/composables/useAuth'
import type { User } from '@/api/typings'

// 3. 定义接口和类型
interface Props {
  title: string
  visible?: boolean
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', data: User): void
}

// 4. 定义 props 和 emits
const props = withDefaults(defineProps<Props>(), {
  visible: false
})

const emits = defineEmits<Emits>()

// 5. 响应式数据
const loading = ref(false)
const formData = ref<User>({})

// 6. 计算属性
const isValid = computed(() => {
  return formData.value.name && formData.value.email
})

// 7. 方法定义
const handleSubmit = () => {
  // 处理逻辑
}

// 8. 生命周期
onMounted(() => {
  // 初始化逻辑
})
</script>

<style scoped lang="scss">
.component-name {
  // 组件样式
}
</style>
```

### 4.2 Props定义规范
```typescript
// ✅ 推荐：完整的类型定义
interface Props {
  // 必需属性
  title: string
  data: User[]
  
  // 可选属性，提供默认值
  visible?: boolean
  size?: 'small' | 'medium' | 'large'
  
  // 函数属性
  onConfirm?: (data: User) => void
}

// ✅ 推荐：使用 withDefaults
const props = withDefaults(defineProps<Props>(), {
  visible: false,
  size: 'medium'
})

// ❌ 避免：运行时props定义
const props = defineProps({
  title: String,
  visible: Boolean
})
```

### 4.3 事件定义规范
```typescript
// ✅ 推荐：TypeScript接口定义
interface Emits {
  // 标准事件
  (e: 'update:visible', value: boolean): void
  (e: 'change', value: string): void
  
  // 业务事件
  (e: 'submit', data: User): void
  (e: 'delete', id: string): void
}

const emits = defineEmits<Emits>()

// 使用事件
const handleClick = () => {
  emits('update:visible', false)
  emits('submit', formData.value)
}
```

### 4.4 组件通信规范
```typescript
// 父子组件通信：Props + Emits
// 兄弟组件通信：共同父组件或状态管理
// 跨层级通信：provide/inject 或状态管理

// ✅ 推荐：provide/inject
// 父组件
provide('theme', 'dark')

// 子组件
const theme = inject<string>('theme', 'light')
```

---

## 5. TypeScript开发规范

### 5.1 类型定义规范
```typescript
// 基础类型
type Theme = 'light' | 'dark'
type UserRole = 'admin' | 'referee' | 'user'
type Status = 'pending' | 'success' | 'error'

// 接口定义
interface User {
  id: string
  name: string
  email: string
  role: UserRole
  avatar?: string
  createdAt: Date
  updatedAt?: Date
}

// API响应类型
interface ApiResponse<T = any> {
  code: number
  message: string
  data: T
  timestamp?: number
}

// 分页类型
interface PaginationParams {
  page: number
  size: number
  keyword?: string
}

interface PaginationResult<T> {
  list: T[]
  total: number
  page: number
  size: number
}
```

### 5.2 类型文件组织
```
src/types/
├── global.d.ts          # 全局类型定义
├── api.d.ts             # API相关类型
├── components.d.ts      # 组件类型定义
└── utils.d.ts           # 工具类型定义
```

### 5.3 类型使用最佳实践
```typescript
// ✅ 推荐：明确的类型定义
const users: User[] = []
const getUserById = (id: string): Promise<User | null> => {
  return api.get(`/users/${id}`)
}

// ✅ 推荐：使用泛型
const createApiCall = <T>(url: string): Promise<ApiResponse<T>> => {
  return request.get(url)
}

// ✅ 推荐：类型守卫
const isUser = (obj: any): obj is User => {
  return obj && typeof obj.id === 'string' && typeof obj.name === 'string'
}

// ❌ 尽量避免：使用 any
const data: any = {}

// ❌ 尽量避免：不必要的类型断言,除非非常确定类型
const user = data as User // 应该使用类型守卫
```

### 5.4 工具类型使用
```typescript
// 内置工具类型
type PartialUser = Partial<User>          // 所有属性可选
type RequiredUser = Required<User>        // 所有属性必需
type UserName = Pick<User, 'name'>        // 选择特定属性
type UserWithoutId = Omit<User, 'id'>     // 排除特定属性

// 自定义工具类型
type Optional<T, K extends keyof T> = Omit<T, K> & Partial<Pick<T, K>>
type CreateUser = Optional<User, 'id' | 'createdAt'>
```

---

## 6. Ant Design Vue组件规范

### 6.1 组件导入规范

```typescript
// ✅ 推荐：按需导入组件
import { Button, Form, Input, Table, Modal, Message, Notification } from 'ant-design-vue'
import type { FormInstance } from 'ant-design-vue'

// ❌ 避免：全局导入所有组件
import AntDesignVue from 'ant-design-vue'
```

### 6.2 常用组件使用规范

#### 6.2.1 Button按钮组件
```vue
<template>
  <!-- 主要按钮 -->
  <a-button type="primary" @click="handleSubmit">提交</a-button>
  
  <!-- 次要按钮 -->
  <a-button>默认</a-button>
  
  <!-- 危险按钮 -->
  <a-button danger @click="handleDelete">删除</a-button>
  
  <!-- 禁用状态 -->
  <a-button :disabled="!isValid">保存</a-button>
  
  <!-- 加载状态 -->
  <a-button :loading="loading">加载中</a-button>
  
  <!-- 按钮组 -->
  <a-button-group>
    <a-button>左</a-button>
    <a-button>中</a-button>
    <a-button>右</a-button>
  </a-button-group>
</template>
```

#### 6.2.2 Form表单组件
```vue
<template>
  <a-form
    :model="formData"
    :rules="rules"
    layout="vertical"
    @finish="onFinish"
    @finishFailed="onFinishFailed"
  >
    <!-- 文本输入 -->
    <a-form-item label="用户名" name="username">
      <a-input 
        v-model:value="formData.username"
        placeholder="请输入用户名"
        allow-clear
      />
    </a-form-item>

    <!-- 密码输入 -->
    <a-form-item label="密码" name="password">
      <a-input-password 
        v-model:value="formData.password"
        placeholder="请输入密码"
      />
    </a-form-item>

    <!-- 选择框 -->
    <a-form-item label="角色" name="role">
      <a-select 
        v-model:value="formData.role"
        placeholder="请选择角色"
      >
        <a-select-option value="admin">管理员</a-select-option>
        <a-select-option value="user">普通用户</a-select-option>
      </a-select>
    </a-form-item>

    <!-- 日期选择 -->
    <a-form-item label="出生日期" name="birthDate">
      <a-date-picker 
        v-model:value="formData.birthDate"
        style="width: 100%"
      />
    </a-form-item>

    <!-- 复选框 -->
    <a-form-item name="agree" value-prop-name="checked">
      <a-checkbox v-model:checked="formData.agree">
        我同意服务条款
      </a-checkbox>
    </a-form-item>

    <!-- 提交按钮 -->
    <a-form-item>
      <a-button type="primary" html-type="submit" :loading="loading">
        提交
      </a-button>
      <a-button style="margin-left: 8px" @click="resetForm">
        重置
      </a-button>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'
import type { FormInstance } from 'ant-design-vue'

interface FormData {
  username: string
  password: string
  role: string
  birthDate: any
  agree: boolean
}

const formRef = ref<FormInstance>()
const loading = ref(false)
const formData = reactive<FormData>({
  username: '',
  password: '',
  role: '',
  birthDate: null,
  agree: false
})

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6个字符', trigger: 'blur' }
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' }
  ]
}

const onFinish = async (values: any) => {
  loading.value = true
  try {
    // 提交表单
    console.log('表单数据:', values)
  } finally {
    loading.value = false
  }
}

const onFinishFailed = (errorInfo: any) => {
  console.log('Failed:', errorInfo)
}

const resetForm = () => {
  formRef.value?.resetFields()
}
</script>
```

#### 6.2.3 Table表格组件
```vue
<template>
  <a-table
    :columns="columns"
    :data-source="tableData"
    :loading="loading"
    :pagination="pagination"
    :row-selection="rowSelection"
    @change="handleTableChange"
  >
    <!-- 自定义列 -->
    <template #bodyCell="{ column, record }">
      <template v-if="column.key === 'action'">
        <a-space>
          <a-button type="link" size="small" @click="handleEdit(record)">
            编辑
          </a-button>
          <a-popconfirm
            title="确定删除?"
            ok-text="确定"
            cancel-text="取消"
            @confirm="handleDelete(record.id)"
          >
            <a-button type="link" danger size="small">
              删除
            </a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </template>
  </a-table>
</template>

<script setup lang="ts">
import { ref, reactive } from 'vue'

interface User {
  id: string
  name: string
  email: string
  role: string
  status: string
}

const columns = [
  { title: '姓名', dataIndex: 'name', key: 'name', width: 150 },
  { title: '邮箱', dataIndex: 'email', key: 'email', width: 200 },
  { title: '角色', dataIndex: 'role', key: 'role', width: 100 },
  { title: '状态', dataIndex: 'status', key: 'status', width: 100 },
  { title: '操作', key: 'action', width: 150 }
]

const loading = ref(false)
const tableData = ref<User[]>([])
const pagination = reactive({
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  pageSizeOptions: ['10', '20', '50', '100']
})

const rowSelection = reactive({
  selectedRowKeys: [] as string[],
  onChange: (selectedKeys: string[]) => {
    rowSelection.selectedRowKeys = selectedKeys
  }
})

const handleTableChange = (pag: any, filters: any, sorter: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  // 重新加载数据
}

const handleEdit = (record: User) => {
  console.log('编辑:', record)
}

const handleDelete = (id: string) => {
  console.log('删除:', id)
}
</script>
```

#### 6.2.4 Modal对话框组件
```vue
<template>
  <!-- 基础对话框 -->
  <a-modal
    v-model:visible="visible"
    title="用户信息"
    ok-text="确定"
    cancel-text="取消"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <p>这是一个对话框</p>
  </a-modal>

  <!-- 确认对话框 -->
  <a-button @click="showConfirm">显示确认</a-button>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { Modal } from 'ant-design-vue'

const visible = ref(false)

const handleOk = () => {
  console.log('确定')
  visible.value = false
}

const handleCancel = () => {
  console.log('取消')
  visible.value = false
}

const showConfirm = () => {
  Modal.confirm({
    title: '确认删除?',
    content: '删除后无法恢复，请谨慎操作',
    okText: '确定',
    cancelText: '取消',
    onOk() {
      console.log('确定删除')
    },
    onCancel() {
      console.log('取消删除')
    }
  })
}
</script>
```

#### 6.2.5 Message消息提示
```typescript
import { message } from 'ant-design-vue'

// 成功消息
message.success('操作成功')

// 错误消息
message.error('操作失败')

// 警告消息
message.warning('请注意')

// 信息消息
message.info('这是一条信息')

// 加载消息
const hide = message.loading('加载中...')
setTimeout(() => {
  hide()
  message.success('加载完成')
}, 2000)
```

#### 6.2.6 Notification通知
```typescript
import { notification } from 'ant-design-vue'

// 成功通知
notification.success({
  message: '成功',
  description: '操作成功完成',
  duration: 4.5
})

// 错误通知
notification.error({
  message: '错误',
  description: '操作失败，请重试',
  duration: 4.5
})

// 自定义通知
notification.open({
  message: '自定义通知',
  description: '这是一条自定义通知',
  duration: 0 // 不自动关闭
})
```

### 6.3 组件最佳实践

#### 6.3.1 表单验证
```typescript
// ✅ 推荐：完整的验证规则
const rules = {
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '邮箱格式不正确', trigger: 'blur' }
  ],
  phone: [
    { required: true, message: '请输入手机号', trigger: 'blur' },
    { pattern: /^1[3-9]\d{9}$/, message: '手机号格式不正确', trigger: 'blur' }
  ]
}
```

#### 6.3.2 表格数据加载
```typescript
// ✅ 推荐：异步加载表格数据
const fetchTableData = async () => {
  loading.value = true
  try {
    const response = await getUserList({
      page: pagination.current,
      pageSize: pagination.pageSize
    })
    tableData.value = response.data.list
    pagination.total = response.data.total
  } catch (error) {
    message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}
```

#### 6.3.3 响应式布局
```vue
<template>
  <a-row :gutter="[16, 16]">
    <a-col :xs="24" :sm="12" :md="8" :lg="6">
      <a-card>卡片1</a-card>
    </a-col>
    <a-col :xs="24" :sm="12" :md="8" :lg="6">
      <a-card>卡片2</a-card>
    </a-col>
  </a-row>
</template>
```

### 6.4 禁止事项

- ❌ 不要使用过时的组件API
- ❌ 不要在组件上硬编码颜色值
- ❌ 不要忽视组件的无障碍属性

---

## 7. 样式开发规范

### 7.1 CSS类名规范
```scss
// BEM命名规范
.user-table {
  // 块样式
  
  &__header {
    // 元素样式
    padding: 16px;
  }
  
  &__row {
    // 元素样式
    border-bottom: 1px solid #f0f0f0;
    
    &--selected {
      // 元素修饰符
      background-color: #e6f7ff;
    }
  }
  
  &--loading {
    // 块修饰符
    opacity: 0.6;
  }
}
```

### 7.2 主题变量使用
```css
// ✅ 推荐：使用CSS变量（支持主题切换）
.custom-component {
  background-color: var(--background-color);
  color: var(--text-color);
  border: 1px solid var(--border-color);
}
```

### 7.3 响应式设计
```scss
// 移动端优先
.component {
  // 移动端样式
  padding: 8px;
  
  @include respond-to(tablet) {
    // 平板样式
    padding: 16px;
  }
  
  @include respond-to(desktop) {
    // 桌面样式
    padding: 24px;
  }
}
```

---

## 8. API接口规范

### 8.1 接口文件组织
```typescript
// src/api/userController.ts
import { request } from '@/utils/request'
import type { User, ApiResponse, PaginationParams } from './typings'

/**
 * 获取用户列表
 * @param params 分页参数
 * @returns 用户列表响应
 */
export const getUserList = (
  params: PaginationParams
): Promise<ApiResponse<User[]>> => {
  return request.get('/api/users', { params })
}

/**
 * 获取用户详情
 * @param id 用户ID
 * @returns 用户详情响应
 */
export const getUserById = (id: string): Promise<ApiResponse<User>> => {
  return request.get(`/api/users/${id}`)
}

/**
 * 创建用户
 * @param user 用户信息
 * @returns 创建结果
 */
export const createUser = (
  user: Omit<User, 'id'>
): Promise<ApiResponse<User>> => {
  return request.post('/api/users', user)
}
```

### 8.2 接口命名规范
```typescript
// 查询操作：get + 资源名 + [条件]
getUserList()
getUserById()
getCompetitionsByStatus()

// 创建操作：create + 资源名
createUser()
createCompetition()

// 更新操作：update + 资源名
updateUser()
updateUserProfile()

// 删除操作：delete + 资源名
deleteUser()
deleteCompetition()

// 业务操作：动词 + 资源名/操作
submitAppeal()
reviewApplication()
assignTask()
```

### 8.3 错误处理
```typescript
// 统一错误处理
export const getUserList = async (params: PaginationParams) => {
  try {
    const response = await request.get('/api/users', { params })
    return response
  } catch (error) {
    console.error('获取用户列表失败:', error)
    throw error
  }
}
```

---

## 9. 状态管理规范

### 9.1 Pinia Store结构
```typescript
// src/stores/user.ts
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import type { User } from '@/api/typings'

export const useUserStore = defineStore('user', () => {
  // 1. 状态定义
  const users = ref<User[]>([])
  const currentUser = ref<User | null>(null)
  const loading = ref(false)
  
  // 2. 计算属性
  const userCount = computed(() => users.value.length)
  const adminUsers = computed(() => 
    users.value.filter(user => user.role === 'admin')
  )
  
  // 3. 异步操作
  const fetchUsers = async () => {
    loading.value = true
    try {
      const response = await getUserList()
      users.value = response.data
    } catch (error) {
      console.error('获取用户列表失败:', error)
    } finally {
      loading.value = false
    }
  }
  
  // 4. 同步操作
  const addUser = (user: User) => {
    users.value.push(user)
  }
  
  const removeUser = (userId: string) => {
    const index = users.value.findIndex(user => user.id === userId)
    if (index > -1) {
      users.value.splice(index, 1)
    }
  }
  
  // 5. 重置状态
  const $reset = () => {
    users.value = []
    currentUser.value = null
    loading.value = false
  }
  
  return {
    // 状态（只读）
    users: readonly(users),
    currentUser: readonly(currentUser),
    loading: readonly(loading),
    
    // 计算属性
    userCount,
    adminUsers,
    
    // 操作
    fetchUsers,
    addUser,
    removeUser,
    $reset
  }
})
```

### 9.2 Store使用规范
```typescript
// 在组件中使用
export default defineComponent({
  setup() {
    const userStore = useUserStore()
    
    // 响应式解构
    const { users, loading } = storeToRefs(userStore)
    
    // 方法直接解构
    const { fetchUsers, addUser } = userStore
    
    onMounted(() => {
      fetchUsers()
    })
    
    return {
      users,
      loading,
      fetchUsers,
      addUser
    }
  }
})
```

---

## 10. 错误处理规范

### 10.1 统一错误处理
```typescript
// src/utils/errorHandler.ts
import { message } from 'ant-design-vue'

export class AppError extends Error {
  constructor(
    message: string,
    public code?: string,
    public statusCode?: number
  ) {
    super(message)
    this.name = 'AppError'
  }
}

export const handleError = (error: unknown) => {
  if (error instanceof AppError) {
    message.error(error.message)
  } else if (error instanceof Error) {
    message.error(`系统错误: ${error.message}`)
  } else {
    message.error('未知错误')
  }
  
  // 记录错误日志
  console.error('Error:', error)
}
```

### 10.2 组件中的错误处理
```typescript
// 异步操作错误处理
const handleSubmit = async () => {
  try {
    loading.value = true
    await submitForm()
    message.success('提交成功')
  } catch (error) {
    handleError(error)
  } finally {
    loading.value = false
  }
}

// 全局错误边界
app.config.errorHandler = (err, vm, info) => {
  console.error('全局错误:', err, info)
  handleError(err)
}
```

---

## 11. Git提交规范

### 11.1 提交信息格式
```
<type>(<scope>): <subject>

<body>

<footer>
```

### 11.2 提交类型
- `feat`: 新功能
- `fix`: 修复bug
- `docs`: 文档更新
- `style`: 代码格式调整（不影响代码运行）
- `refactor`: 代码重构
- `perf`: 性能优化
- `test`: 测试相关
- `build`: 构建系统或外部依赖变更
- `ci`: CI配置文件和脚本变更
- `chore`: 其他不修改src或test文件的变更
- `revert`: 回滚之前的提交

### 11.3 提交示例
```bash
# 新功能
feat(auth): 添加用户登录功能

# 修复bug
fix(table): 修复分页组件显示错误

# 文档更新
docs: 更新API接口文档

# 代码重构
refactor(utils): 重构请求工具函数

# 性能优化
perf(table): 优化大数据量表格渲染性能
```

---

## 12. 代码审查规范

### 12.1 审查清单
- [ ] 代码符合命名规范
- [ ] TypeScript类型定义完整
- [ ] 组件结构清晰合理
- [ ] 样式使用规范
- [ ] 错误处理完善
- [ ] 性能考虑充分
- [ ] 测试覆盖完整
- [ ] 文档注释清晰
- [ ] 安全性检查通过

### 12.2 审查重点
1. **功能正确性**：代码是否实现了预期功能
2. **代码质量**：是否遵循最佳实践
3. **性能影响**：是否存在性能问题
4. **安全性**：是否存在安全隐患
5. **可维护性**：代码是否易于理解和修改

---

## 13. 性能规范

### 13.1 性能指标
- 组件渲染时间 < 100ms
- 页面首屏加载时间 < 2s
- 路由切换时间 < 500ms
- 内存使用合理，无明显泄漏

### 13.2 性能优化策略
```typescript
// 1. 组件懒加载
const UserManagePage = defineAsyncComponent(() => 
  import('@/pages/admin/UserManagePage.vue')
)

// 2. 计算属性缓存
const expensiveValue = computed(() => {
  return heavyCalculation(props.data)
})

// 3. 防抖和节流
import { debounce } from 'lodash-es'

const handleSearch = debounce((keyword: string) => {
  // 搜索逻辑
}, 300)

// 4. 虚拟滚动（大数据量）
import { VirtualList } from '@tanstack/vue-virtual'

// 5. 图片懒加载
<img v-lazy="imageUrl" alt="description" />
```

### 13.3 内存管理
```typescript
// 清理定时器
onUnmounted(() => {
  if (timer) {
    clearInterval(timer)
  }
})

// 清理事件监听
onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})

// 清理观察者
onUnmounted(() => {
  observer?.disconnect()
})
```

---

## 14. Ant Design Vue快速参考

### 14.1 常用组件速查表

| 组件 | 用途 | 常用属性 |
|------|------|---------|
| Button | 按钮 | type, danger, loading, disabled |
| Form | 表单 | model, rules, layout |
| Input | 输入框 | v-model:value, placeholder, allow-clear |
| Select | 选择框 | v-model:value, placeholder, options |
| Table | 表格 | columns, dataSource, pagination, loading |
| Modal | 对话框 | v-model:visible, title, okText, cancelText |
| Message | 消息提示 | success, error, warning, info, loading |
| Notification | 通知 | success, error, warning, info |
| Card | 卡片 | title, bordered, hoverable |
| Drawer | 抽屉 | v-model:open, title, placement |
| Tabs | 标签页 | v-model:activeKey, type |
| Tree | 树形 | data, defaultExpandAll, checkable |
| DatePicker | 日期选择 | v-model:value, format, range |
| TimePicker | 时间选择 | v-model:value, format |
| Upload | 文件上传 | action, multiple, beforeUpload |
| Pagination | 分页 | v-model:current, total, pageSize |
| Spin | 加载中 | spinning, size, tip |
| Empty | 空状态 | description, image |
| Result | 结果页 | status, title, subTitle |
| Statistic | 统计数值 | title, value, prefix, suffix |

### 14.2 常用属性速查

```typescript
// 尺寸
size: 'large' | 'middle' | 'small'

// 类型
type: 'primary' | 'dashed' | 'text' | 'link'

// 状态
loading: boolean
disabled: boolean
danger: boolean

// 布局
layout: 'horizontal' | 'vertical' | 'inline'

// 位置
placement: 'top' | 'right' | 'bottom' | 'left'

// 对齐
align: 'start' | 'center' | 'end'
justify: 'start' | 'center' | 'end' | 'space-between' | 'space-around'
```

### 14.3 常见问题解决

**Q: 如何禁用表单项?**
```typescript
const rules = {
  field: [{ required: true, message: '必填' }]
}
// 在模板中使用 :disabled="isDisabled"
```

**Q: 如何自定义表格列?**
```vue
<template #bodyCell="{ column, record }">
  <template v-if="column.key === 'custom'">
    <!-- 自定义内容 -->
  </template>
</template>
```

**Q: 如何处理表单提交?**
```typescript
const onFinish = async (values: any) => {
  // values 包含所有表单数据
  // 已自动验证通过
}
```

---

## 15. 主题样式编写规范

### 1. 在样式中使用 CSS 变量（必须遵守）

```vue
<style scoped>
.custom-component {
  /* ✅ 推荐：使用 CSS 变量 */
  background-color: var(--background-color-container);
  color: var(--text-color);
  border: 1px solid var(--border-color-base);
}

.custom-component:hover {
  background-color: var(--background-color-light);
  border-color: var(--primary-color);
}

/* ❌ 避免：硬编码颜色值 */
.bad-component {
  background-color: #ffffff;
  color: #000000;
}
</style>
```

---

### 2. 可用的主题变量

#### 颜色变量分类

**主题色**
```css
--primary-color          /* 主色 #1890ff / #177ddc */
--primary-hover          /* 悬停态 */
--primary-active         /* 激活态 */
--primary-light          /* 浅色背景 */
```

**状态色**
```css
--success-color          /* 成功色 */
--warning-color          /* 警告色 */
--error-color            /* 错误色 */
--info-color             /* 信息色 */
```

**文本色**
```css
--text-color             /* 主文本色 */
--text-color-secondary   /* 次要文本色 */
--text-color-tertiary    /* 三级文本色 */
--text-color-disabled    /* 禁用文本色 */
```

**背景色**
```css
--background-color                /* 页面背景 */
--background-color-light          /* 浅色背景 */
--background-color-container      /* 容器背景 */
```

**边框色**
```css
--border-color-base      /* 基础边框 */
--border-color-split     /* 分割线 */
--border-color-light     /* 浅色边框 */
```

**组件专用色**
```css
--header-bg              /* 头部背景 */
--header-border          /* 头部边框 */
--card-bg                /* 卡片背景 */
--card-hover-bg          /* 卡片悬停背景 */
```

---

### 3. 必须遵守的规则

#### ✅ 正确示例

```vue
<style scoped>
/* 使用 CSS 变量 */
.my-component {
  background-color: var(--background-color-container);
  color: var(--text-color);
  border: 1px solid var(--border-color-base);
}

.my-component:hover {
  background-color: var(--background-color-light);
  border-color: var(--primary-color);
}

.my-button {
  background-color: var(--primary-color);
  color: #ffffff;
}

.my-button:hover {
  background-color: var(--primary-hover);
}
</style>
```

#### ❌ 错误示例

```vue
<style scoped>
/* 禁止硬编码颜色 */
.my-component {
  background-color: #ffffff;  /* ❌ 错误 */
  color: #000000;             /* ❌ 错误 */
  border: 1px solid #d9d9d9;  /* ❌ 错误 */
}
</style>
```

---

### 4. 常见场景示例

#### 场景 1：卡片组件
```vue
<style scoped>
.card {
  background-color: var(--card-bg);
  border: 1px solid var(--border-color-base);
  border-radius: 8px;
  padding: 16px;
}

.card:hover {
  background-color: var(--card-hover-bg);
  box-shadow: 0 2px 8px var(--shadow-color);
}

.card-title {
  color: var(--text-color);
  font-size: 16px;
  font-weight: 600;
}

.card-description {
  color: var(--text-color-secondary);
  font-size: 14px;
}
</style>
```

#### 场景 2：表单组件
```vue
<style scoped>
.form-item {
  margin-bottom: 16px;
}

.form-label {
  color: var(--text-color);
  margin-bottom: 8px;
}

.form-input {
  background-color: var(--background-color-container);
  border: 1px solid var(--border-color-base);
  color: var(--text-color);
  padding: 8px 12px;
  border-radius: 4px;
}

.form-input:focus {
  border-color: var(--primary-color);
  outline: none;
  box-shadow: 0 0 0 2px var(--primary-light);
}

.form-input:disabled {
  background-color: var(--background-color-light);
  color: var(--text-color-disabled);
}
</style>
```

#### 场景 3：按钮组件
```vue
<style scoped>
.btn-primary {
  background-color: var(--primary-color);
  color: #ffffff;
  border: none;
}

.btn-primary:hover {
  background-color: var(--primary-hover);
}

.btn-primary:active {
  background-color: var(--primary-active);
}

.btn-default {
  background-color: var(--background-color-container);
  color: var(--text-color);
  border: 1px solid var(--border-color-base);
}

.btn-default:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}
</style>
```

#### 场景 4：列表组件
```vue
<style scoped>
.list {
  background-color: var(--background-color-container);
  border: 1px solid var(--border-color-base);
  border-radius: 4px;
}

.list-item {
  padding: 12px 16px;
  border-bottom: 1px solid var(--border-color-split);
  color: var(--text-color);
}

.list-item:last-child {
  border-bottom: none;
}

.list-item:hover {
  background-color: var(--background-color-light);
}

.list-item-active {
  background-color: var(--primary-light);
  color: var(--primary-color);
}
</style>
```

---

### 5. 注意事项

1. **所有颜色值都必须使用 CSS 变量**，尽量不使用硬编码颜色值
2. **白色文字可以直接使用** `#ffffff` 或 `white`（用于主题色按钮等）
3. **阴影颜色使用** `var(--shadow-color)` 或 `var(--shadow-color-light)`
4. **透明度使用** rgba 格式的变量，如 `var(--text-color-secondary)`
5. **边框圆角、间距等非颜色属性** 可以直接使用具体数值

---

### 6. 快速检查清单

编写组件样式时，请检查：

- [ ] 所有 `background-color` 使用了 CSS 变量
- [ ] 所有 `color` 使用了 CSS 变量（白色除外）
- [ ] 所有 `border-color` 使用了 CSS 变量
- [ ] 悬停、激活等状态使用了对应的变量（如 `--primary-hover`）
- [ ] 没有硬编码的颜色值（如 `#ffffff`、`#000000` 等）