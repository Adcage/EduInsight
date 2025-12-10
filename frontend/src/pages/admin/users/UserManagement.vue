<template>
  <div class="user-management">
    <a-card :bordered="false">
      <!-- 顶部操作栏 -->
      <div class="toolbar">
        <div class="toolbar-left">
          <a-input-search v-model:value="searchKeyword" placeholder="搜索用户名、姓名、邮箱或工号" style="width: 300px" @search="handleSearch" />
          <a-select v-model:value="filterRole" placeholder="角色筛选" style="width: 120px; margin-left: 12px" allow-clear @change="handleSearch">
            <a-select-option value="ADMIN">管理员</a-select-option>
            <a-select-option value="TEACHER">教师</a-select-option>
            <a-select-option value="STUDENT">学生</a-select-option>
          </a-select>
        </div>
        <div class="toolbar-right">
          <a-button type="primary" @click="showAddModal">
            <template #icon><PlusOutlined /></template>
            添加用户
          </a-button>
          <a-button @click="showImportModal" style="margin-left: 8px">
            <template #icon><UploadOutlined /></template>
            批量导入
          </a-button>
          <a-button danger :disabled="selectedRowKeys.length === 0" @click="handleBatchDelete" style="margin-left: 8px">
            <template #icon><DeleteOutlined /></template>
            批量删除
          </a-button>
        </div>
      </div>

      <!-- 用户列表表格 -->
      <a-table
        :columns="columns"
        :data-source="userList"
        :loading="loading"
        :pagination="pagination"
        :row-selection="rowSelection"
        :row-key="(record) => record.id"
        @change="handleTableChange"
        class="user-table"
      >
        <template #bodyCell="{ column, record }">
          <template v-if="column.key === 'role'">
            <a-tag :color="getRoleColor(record.role)">
              {{ getRoleText(record.role) }}
            </a-tag>
          </template>
          <template v-else-if="column.key === 'status'">
            <a-badge :status="record.status ? 'success' : 'error'" :text="record.status ? '正常' : '禁用'" />
          </template>
          <template v-else-if="column.key === 'phone'">
            {{ record.phone || '未绑定' }}
          </template>
          <template v-else-if="column.key === 'createdAt'">
            {{ dayjs(record.createdAt).format('YYYY-MM-DD HH:mm:ss') }}
          </template>
          <template v-else-if="column.key === 'action'">
            <a-space>
              <a-button type="link" size="small" @click="handleEdit(record)"> 编辑 </a-button>
              <a-popconfirm title="确定要删除该用户吗?" ok-text="确定" cancel-text="取消" @confirm="handleDelete(record.id)">
                <a-button type="link" danger size="small">删除</a-button>
              </a-popconfirm>
            </a-space>
          </template>
        </template>
      </a-table>
    </a-card>

    <!-- 添加/编辑用户弹窗 -->
    <UserForm v-model:visible="formVisible" :user-data="currentUser" :is-edit="isEdit" @success="handleFormSuccess" />

    <!-- Excel导入弹窗 -->
    <ExcelImportModal v-model:visible="importVisible" @success="handleImportSuccess" />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { message, Modal } from 'ant-design-vue'
import { PlusOutlined, UploadOutlined, DeleteOutlined } from '@ant-design/icons-vue'
import { userApiListGet, userApiIntUserIdDeactivatePost } from '@/api/userController'
import UserForm from './components/UserForm.vue'
import ExcelImportModal from './components/ExcelImportModal.vue'
import type { TableColumnsType, TableProps } from 'ant-design-vue'
import dayjs from 'dayjs'

// 用户数据类型
interface User {
  id: number
  username: string
  userCode: string
  email: string
  realName: string
  role: string
  phone?: string
  status: boolean
  createdAt: string
}

// 响应式数据
const loading = ref(false)
const userList = ref<User[]>([])
const searchKeyword = ref('')
const filterRole = ref<string | undefined>(undefined)
const selectedRowKeys = ref<number[]>([])
const formVisible = ref(false)
const importVisible = ref(false)
const isEdit = ref(false)
const currentUser = ref<User | null>(null)

// 分页配置
const pagination = reactive({
  current: 1,
  pageSize: 20,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

// 表格列配置
const columns: TableColumnsType = [
  {
    title: '用户名',
    dataIndex: 'username',
    key: 'username',
    width: 120,
  },
  {
    title: '工号/学号',
    dataIndex: 'userCode',
    key: 'userCode',
    width: 120,
  },
  {
    title: '真实姓名',
    dataIndex: 'realName',
    key: 'realName',
    width: 120,
  },
  {
    title: '邮箱',
    dataIndex: 'email',
    key: 'email',
    width: 200,
  },
  {
    title: '角色',
    dataIndex: 'role',
    key: 'role',
    width: 100,
  },
  {
    title: '手机号',
    dataIndex: 'phone',
    key: 'phone',
    width: 130,
  },
  {
    title: '状态',
    dataIndex: 'status',
    key: 'status',
    width: 100,
  },
  {
    title: '创建时间',
    dataIndex: 'createdAt',
    key: 'createdAt',
    width: 180,
  },
  {
    title: '操作',
    key: 'action',
    fixed: 'right',
    width: 150,
  },
]

// 行选择配置
const rowSelection: TableProps['rowSelection'] = {
  selectedRowKeys: selectedRowKeys,
  onChange: (keys: any[]) => {
    selectedRowKeys.value = keys
  },
}

// 获取用户列表
const fetchUserList = async () => {
  loading.value = true
  try {
    const response = await userApiListGet({
      page: pagination.current,
      perPage: pagination.pageSize,
      role: filterRole.value,
      search: searchKeyword.value || undefined,
    })
    console.log(response)
    if (response) {
      userList.value = response.data?.users || []
      pagination.total = response.data?.total || 0
    }
  } catch (error: any) {
    message.error(error.message || '获取用户列表失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  pagination.current = 1
  fetchUserList()
}

// 表格变化
const handleTableChange = (pag: any) => {
  pagination.current = pag.current
  pagination.pageSize = pag.pageSize
  fetchUserList()
}

// 显示添加弹窗
const showAddModal = () => {
  isEdit.value = false
  currentUser.value = null
  formVisible.value = true
}

// 显示编辑弹窗
const handleEdit = (user: User) => {
  isEdit.value = true
  currentUser.value = { ...user }
  formVisible.value = true
}

// 删除用户
const handleDelete = async (userId: number) => {
  try {
    await userApiIntUserIdDeactivatePost({ userId })
    message.success('删除成功')
    fetchUserList()
  } catch (error: any) {
    message.error(error.message || '删除失败')
  }
}

// 批量删除
const handleBatchDelete = () => {
  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedRowKeys.value.length} 个用户吗?此操作不可恢复!`,
    okText: '确定',
    okType: 'danger',
    cancelText: '取消',
    async onOk() {
      try {
        // 调用批量删除API
        const { default: request } = await import('@/request')
        await request('/api/v1/users/batch-delete', {
          method: 'DELETE',
          data: { userIds: selectedRowKeys.value },
        })
        message.success('批量删除成功')
        selectedRowKeys.value = []
        fetchUserList()
      } catch (error: any) {
        message.error(error.message || '批量删除失败')
      }
    },
  })
}

// 显示导入弹窗
const showImportModal = () => {
  importVisible.value = true
}

// 表单提交成功
const handleFormSuccess = () => {
  formVisible.value = false
  fetchUserList()
}

// 导入成功
const handleImportSuccess = () => {
  importVisible.value = false
  fetchUserList()
}

// 获取角色颜色
const getRoleColor = (role: string) => {
  const colorMap: Record<string, string> = {
    admin: 'red',
    teacher: 'blue',
    student: 'green',
  }
  return colorMap[role] || 'default'
}

// 获取角色文本
const getRoleText = (role: string) => {
  const textMap: Record<string, string> = {
    admin: '管理员',
    teacher: '教师',
    student: '学生',
  }
  return textMap[role] || role
}

// 初始化
onMounted(() => {
  fetchUserList()
})
</script>

<style scoped>
.user-management {
  padding: 24px;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.toolbar-left {
  display: flex;
  align-items: center;
}

.toolbar-right {
  display: flex;
  align-items: center;
}

.user-table {
  margin-top: 16px;
}
</style>
