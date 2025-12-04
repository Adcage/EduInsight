<template>
  <a-layout class="auth-test-page">
    <!-- 顶部导航栏 -->
    <a-layout-header class="header">
      <div class="header-content">
        <div class="logo-section">
          <span class="logo-icon">🔐</span>
          <h1 class="logo-text">认证测试中心</h1>
        </div>
        <div v-if="currentUser" class="user-section">
          <a-space>
            <a-avatar :size="40" style="background-color: #1890ff">
              {{ currentUser.real_name.charAt(0) }}
            </a-avatar>
            <div class="user-info">
              <div class="user-name">{{ currentUser.real_name }}</div>
              <a-tag :color="getRoleTagColor(currentUser.role)">
                {{ getRoleText(currentUser.role) }}
              </a-tag>
            </div>
            <a-button type="primary" danger @click="testLogout" :loading="loading.logout">
              登出
            </a-button>
          </a-space>
        </div>
      </div>
    </a-layout-header>

    <a-layout-content class="content">
      <!-- 用户状态卡片 -->
      <a-card v-if="currentUser" class="user-status-card" :bordered="false">
        <a-row :gutter="[24, 24]">
          <a-col :xs="24" :sm="12" :md="8" :lg="4.8">
            <a-statistic title="用户名" :value="currentUser.username" />
          </a-col>
          <a-col :xs="24" :sm="12" :md="8" :lg="4.8">
            <a-statistic title="真实姓名" :value="currentUser.real_name" />
          </a-col>
          <a-col :xs="24" :sm="12" :md="8" :lg="4.8">
            <div class="statistic-item">
              <div class="statistic-title">角色</div>
              <a-tag :color="getRoleTagColor(currentUser.role)" style="font-size: 14px; padding: 4px 12px">
                {{ getRoleText(currentUser.role) }}
              </a-tag>
            </div>
          </a-col>
          <a-col :xs="24" :sm="12" :md="8" :lg="4.8">
            <a-statistic title="工号/学号" :value="currentUser.user_code" />
          </a-col>
          <a-col :xs="24" :sm="12" :md="8" :lg="4.8">
            <a-statistic title="邮箱" :value="currentUser.email" />
          </a-col>
        </a-row>
      </a-card>

      <!-- 功能测试区域 -->
      <a-row :gutter="[24, 24]" class="test-area">
        <!-- 用户注册测试 -->
        <a-col :xs="24" :sm="12" :md="8">
          <a-card title="📝 用户注册" :bordered="false">
            <a-form layout="vertical" :model="registerForm" @finish="testRegister">
              <a-form-item label="用户名" name="username">
                <a-input v-model:value="registerForm.username" placeholder="请输入用户名" />
              </a-form-item>
              <a-form-item label="工号/学号" name="user_code">
                <a-input v-model:value="registerForm.user_code" placeholder="请输入工号或学号" />
              </a-form-item>
              <a-form-item label="密码" name="password">
                <a-input-password v-model:value="registerForm.password" placeholder="请输入密码" />
              </a-form-item>
              <a-form-item label="邮箱" name="email">
                <a-input v-model:value="registerForm.email" type="email" placeholder="请输入邮箱" />
              </a-form-item>
              <a-form-item label="真实姓名" name="real_name">
                <a-input v-model:value="registerForm.real_name" placeholder="请输入真实姓名" />
              </a-form-item>
              <a-form-item label="角色" name="role">
                <a-select v-model:value="registerForm.role" placeholder="请选择角色">
                  <a-select-option value="student">学生</a-select-option>
                  <a-select-option value="teacher">教师</a-select-option>
                  <a-select-option value="admin">管理员</a-select-option>
                </a-select>
              </a-form-item>
              <a-form-item v-if="registerForm.role === 'student'" label="班级ID" name="class_id">
                <a-input-number v-model:value="registerForm.class_id" placeholder="请输入班级ID" :min="1" style="width: 100%" />
              </a-form-item>
              <a-form-item label="手机号(可选)" name="phone">
                <a-input v-model:value="registerForm.phone" placeholder="请输入手机号" />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" block :loading="loading.register">
                  {{ loading.register ? '注册中...' : '测试注册' }}
                </a-button>
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>

        <!-- 用户登录测试 -->
        <a-col :xs="24" :sm="12" :md="8">
          <a-card title="🔑 用户登录" :bordered="false">
            <a-form layout="vertical" :model="loginForm" @finish="testLogin">
              <a-form-item label="邮箱/用户名/工号" name="login_identifier">
                <a-input v-model:value="loginForm.login_identifier" placeholder="请输入邮箱、用户名或工号" />
              </a-form-item>
              <a-form-item label="密码" name="password">
                <a-input-password v-model:value="loginForm.password" placeholder="请输入密码" />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" block :loading="loading.login">
                  {{ loading.login ? '登录中...' : '测试登录' }}
                </a-button>
              </a-form-item>
            </a-form>
            <a-divider />
            <a-space direction="vertical" style="width: 100%">
              <a-button block @click="checkLoginStatus" :loading="loading.status">
                {{ loading.status ? '检查中...' : '检查登录状态' }}
              </a-button>
              <a-button block danger @click="testLogout" :loading="loading.logout">
                {{ loading.logout ? '登出中...' : '测试登出' }}
              </a-button>
            </a-space>
          </a-card>
        </a-col>

        <!-- 密码修改测试 -->
        <a-col :xs="24" :sm="12" :md="8">
          <a-card title="🔒 密码修改" :bordered="false">
            <a-form layout="vertical" :model="passwordForm" @finish="testChangePassword">
              <a-form-item label="原密码" name="old_password">
                <a-input-password v-model:value="passwordForm.old_password" placeholder="请输入原密码" />
              </a-form-item>
              <a-form-item label="新密码" name="new_password">
                <a-input-password v-model:value="passwordForm.new_password" placeholder="请输入新密码" />
              </a-form-item>
              <a-form-item label="确认新密码" name="confirm_password">
                <a-input-password v-model:value="passwordForm.confirm_password" placeholder="请再次输入新密码" />
              </a-form-item>
              <a-form-item>
                <a-button type="primary" html-type="submit" block :loading="loading.changePassword" :disabled="!currentUser">
                  {{ loading.changePassword ? '修改中...' : '测试修改密码' }}
                </a-button>
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>

        <!-- 用户管理测试 -->
        <a-col :xs="24" :sm="12" :md="8">
          <a-card title="👥 用户管理" :bordered="false">
            <a-space direction="vertical" style="width: 100%">
              <a-button block @click="testGetUserList" :loading="loading.userList">
                {{ loading.userList ? '获取中...' : '获取用户列表' }}
              </a-button>
              <a-button block @click="testGetUserStats" :loading="loading.userStats">
                {{ loading.userStats ? '获取中...' : '获取用户统计' }}
              </a-button>
              <a-input-group compact>
                <a-input v-model:value="testUserId" placeholder="用户ID" type="number" style="width: calc(100% - 50px)" />
                <a-button type="primary" @click="testGetUser" :loading="loading.getUser" :disabled="!testUserId">
                  获取
                </a-button>
              </a-input-group>
            </a-space>
          </a-card>
        </a-col>

        <!-- 权限测试 -->
        <a-col :xs="24" :sm="12" :md="8">
          <a-card title="🛡️ 权限测试" :bordered="false">
            <a-space direction="vertical" style="width: 100%">
              <a-button block @click="testPermission('material:create')" :loading="loading.permission">
                测试创建资料权限
              </a-button>
              <a-button block @click="testPermission('grade:read')" :loading="loading.permission">
                测试查看成绩权限
              </a-button>
              <a-button block @click="testPermission('user:manage')" :loading="loading.permission">
                测试用户管理权限
              </a-button>
            </a-space>
          </a-card>
        </a-col>

        <!-- API健康检查 -->
        <a-col :xs="24" :sm="12" :md="8">
          <a-card title="💚 API健康检查" :bordered="false">
            <a-space direction="vertical" style="width: 100%">
              <a-button block @click="testAuthHealth" :loading="loading.authHealth">
                {{ loading.authHealth ? '检查中...' : '认证API健康检查' }}
              </a-button>
              <a-button block @click="testUserHealth" :loading="loading.userHealth">
                {{ loading.userHealth ? '检查中...' : '用户API健康检查' }}
              </a-button>
            </a-space>
          </a-card>
        </a-col>
      </a-row>

      <!-- 测试结果显示 -->
      <a-card title="📋 测试结果日志" class="test-logs-card" :bordered="false">
        <template #extra>
          <a-button @click="clearLogs">清空日志</a-button>
        </template>
        <a-empty v-if="testLogs.length === 0" description="暂无测试结果" />
        <a-list v-else :data-source="testLogs" :bordered="false">
          <template #renderItem="{ item }">
            <a-list-item>
              <a-list-item-meta>
                <template #avatar>
                  <a-tag :color="getLogTagColor(item.type)">
                    {{ item.type.toUpperCase() }}
                  </a-tag>
                </template>
                <template #title>
                  {{ item.message }}
                </template>
                <template #description>
                  {{ item.timestamp }}
                </template>
              </a-list-item-meta>
              <template v-if="item.data" #extra>
                <a-button type="link" size="small" @click="showLogDetail(item)">
                  详情
                </a-button>
              </template>
            </a-list-item>
          </template>
        </a-list>
      </a-card>
    </a-layout-content>
  </a-layout>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { message } from 'ant-design-vue'
import {
  authApiRegisterPost,
  authApiLoginPost,
  authApiStatusGet,
  authApiLogoutPost,
  authApiChangePasswordPost,
  authApiGetLoginuserGet,
  authApiHealthGet
} from '@/api/authController'
import {
  userApiGet,
  userApiIntUserIdGet,
  userApiStatsGet,
  userApiHealthGet
} from '@/api/userController'

// 响应式数据
const currentUser = ref(null)
const testUserId = ref('')

// 表单数据
const registerForm = reactive({
  username: 'testuser' + Date.now(),  // 使用时间戳生成唯一用户名
  user_code: 'TEST' + Math.floor(Math.random() * 10000),  // 生成随机学号
  password: 'password123',
  email: 'test' + Date.now() + '@example.com',  // 生成唯一邮箱
  real_name: '测试用户',
  role: 'admin',  // 改为管理员角色，便于测试所有接口
  phone: '13800138000',
  class_id: null  // 管理员不需要班级ID
})

const loginForm = reactive({
  login_identifier: 'test@example.com',
  password: 'password123'
})

const passwordForm = reactive({
  old_password: '',
  new_password: '',
  confirm_password: ''
})

// 加载状态
const loading = reactive({
  register: false,
  login: false,
  logout: false,
  status: false,
  changePassword: false,
  userList: false,
  userStats: false,
  getUser: false,
  permission: false,
  authHealth: false,
  userHealth: false
})

// 测试日志
const testLogs = ref([])

// API基础URL
const API_BASE = 'http://localhost:5001/api/v1'

// 工具函数
const addLog = (type, message, data = null) => {
  testLogs.value.unshift({
    type,
    message,
    data,
    timestamp: new Date().toLocaleTimeString()
  })
}

const getLogColor = (type) => {
  const colors = {
    success: 'bg-green-100 text-green-800 border border-green-200',
    error: 'bg-red-100 text-red-800 border border-red-200',
    info: 'bg-blue-100 text-blue-800 border border-blue-200',
    warning: 'bg-yellow-100 text-yellow-800 border border-yellow-200'
  }
  return colors[type] || colors.info
}

const getRoleColor = (role) => {
  const colors = {
    admin: 'bg-red-100 text-red-800',
    teacher: 'bg-blue-100 text-blue-800',
    student: 'bg-green-100 text-green-800'
  }
  return colors[role] || 'bg-gray-100 text-gray-800'
}

const getRoleText = (role) => {
  const texts = {
    admin: '管理员',
    teacher: '教师',
    student: '学生'
  }
  return texts[role] || role
}

const getRoleTagColor = (role) => {
  const colors = {
    admin: 'red',
    teacher: 'blue',
    student: 'green'
  }
  return colors[role] || 'default'
}

const getLogTagColor = (type) => {
  const colors = {
    success: 'green',
    error: 'red',
    info: 'blue',
    warning: 'orange'
  }
  return colors[type] || 'default'
}

const showLogDetail = (log) => {
  console.log('Log Detail:', log)
  // 可以在这里添加Modal显示详情
}

// 测试函数
const testRegister = async () => {
  loading.register = true
  try {
    const response = await authApiRegisterPost(registerForm)
    currentUser.value = response.data
    addLog('success', '注册成功', response)
    message.success('注册成功')
  } catch (error) {
    // 获取详细的错误信息
    let errorMsg = error.message
    if (error.response?.data) {
      errorMsg = error.response.data.message || error.response.data.detail || errorMsg
      if (error.response.data.errors) {
        errorMsg = JSON.stringify(error.response.data.errors)
      }
    }
    addLog('error', '注册失败', { message: errorMsg, status: error.response?.status })
    message.error('注册失败: ' + errorMsg)
  } finally {
    loading.register = false
  }
}

const testLogin = async () => {
  loading.login = true
  try {
    const response = await authApiLoginPost(loginForm)
    currentUser.value = response.data
    addLog('success', '登录成功', response)
    message.success('登录成功')
  } catch (error) {
    addLog('error', '登录失败', { message: error.message })
    message.error('登录失败: ' + error.message)
  } finally {
    loading.login = false
  }
}

const checkLoginStatus = async () => {
  loading.status = true
  try {
    const response = await authApiStatusGet()
    addLog('info', '登录状态检查', response)
    message.info('已检查登录状态')
  } catch (error) {
    addLog('error', '状态检查失败', { message: error.message })
    message.error('状态检查失败: ' + error.message)
  } finally {
    loading.status = false
  }
}

const testLogout = async () => {
  loading.logout = true
  try {
    const response = await authApiLogoutPost()
    currentUser.value = null
    addLog('success', '登出成功', response)
    message.success('登出成功')
  } catch (error) {
    addLog('error', '登出失败', { message: error.message })
    message.error('登出失败: ' + error.message)
  } finally {
    loading.logout = false
  }
}

const testChangePassword = async () => {
  loading.changePassword = true
  try {
    const response = await authApiChangePasswordPost(passwordForm)
    addLog('success', '密码修改成功', response)
    message.success('密码修改成功')
  } catch (error) {
    addLog('error', '密码修改失败', { message: error.message })
    message.error('密码修改失败: ' + error.message)
  } finally {
    loading.changePassword = false
  }
}

const testGetUserList = async () => {
  loading.userList = true
  try {
    const response = await userApiGet({ page: 1, per_page: 10 })
    addLog('success', '获取用户列表成功', response)
    message.success('获取用户列表成功')
  } catch (error) {
    addLog('error', '获取用户列表失败', { message: error.message })
    message.error('获取用户列表失败: ' + error.message)
  } finally {
    loading.userList = false
  }
}

const testGetUserStats = async () => {
  loading.userStats = true
  try {
    const response = await userApiStatsGet()
    addLog('success', '获取用户统计成功', response)
    message.success('获取用户统计成功')
  } catch (error) {
    addLog('error', '获取用户统计失败', { message: error.message })
    message.error('获取用户统计失败: ' + error.message)
  } finally {
    loading.userStats = false
  }
}

const testGetUser = async () => {
  loading.getUser = true
  try {
    const response = await userApiIntUserIdGet({ user_id: testUserId.value })
    addLog('success', `获取用户 ${testUserId.value} 成功`, response)
    message.success(`获取用户 ${testUserId.value} 成功`)
  } catch (error) {
    addLog('error', '获取用户失败', { message: error.message })
    message.error('获取用户失败: ' + error.message)
  } finally {
    loading.getUser = false
  }
}

const testPermission = async (permission) => {
  loading.permission = true
  try {
    if (!currentUser.value) {
      addLog('warning', '请先登录再测试权限')
      message.warning('请先登录再测试权限')
      return
    }
    
    // 这里模拟权限检查，实际应该调用后端API
    const userRole = currentUser.value.role
    let hasPermission = false
    
    // 简单的权限检查逻辑
    if (userRole === 'admin') {
      hasPermission = true
    } else if (userRole === 'teacher') {
      hasPermission = ['material:create', 'grade:read', 'course:manage'].includes(permission)
    } else if (userRole === 'student') {
      hasPermission = ['material:read', 'grade:read'].includes(permission)
    }
    
    if (hasPermission) {
      addLog('success', `权限检查通过: ${permission}`)
      message.success(`权限检查通过: ${permission}`)
    } else {
      addLog('warning', `权限不足: ${permission}`)
      message.warning(`权限不足: ${permission}`)
    }
  } catch (error) {
    addLog('error', `权限检查异常: ${error.message}`)
    message.error('权限检查失败: ' + error.message)
  } finally {
    loading.permission = false
  }
}

const testAuthHealth = async () => {
  loading.authHealth = true
  try {
    const response = await authApiHealthGet()
    addLog('success', '认证API健康检查通过', response)
    message.success('认证API健康检查通过')
  } catch (error) {
    addLog('error', '认证API健康检查失败', { message: error.message })
    message.error('认证API健康检查失败: ' + error.message)
  } finally {
    loading.authHealth = false
  }
}

const testUserHealth = async () => {
  loading.userHealth = true
  try {
    const response = await userApiHealthGet()
    addLog('success', '用户API健康检查通过', response)
    message.success('用户API健康检查通过')
  } catch (error) {
    addLog('error', '用户API健康检查失败', { message: error.message })
    message.error('用户API健康检查失败: ' + error.message)
  } finally {
    loading.userHealth = false
  }
}

const clearLogs = () => {
  testLogs.value = []
}

// 监听角色变更，自动设置或清除班级ID
watch(() => registerForm.role, (newRole) => {
  if (newRole === 'student') {
    registerForm.class_id = 1  // 默认班级ID
  } else {
    registerForm.class_id = null  // 非学生角色清除班级ID
  }
})

// 页面加载时检查登录状态
onMounted(() => {
  checkLoginStatus()
})
</script>

<style scoped>
.auth-test-page {
  min-height: 100vh;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
}

.header {
  background: linear-gradient(90deg, #1890ff 0%, #1890ff 100%);
  padding: 0 24px;
  display: flex;
  align-items: center;
  height: 64px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.header-content {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.logo-section {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 24px;
}

.logo-text {
  color: white;
  font-size: 18px;
  font-weight: 600;
  margin: 0;
}

.user-section {
  display: flex;
  align-items: center;
}

.user-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.user-name {
  color: white;
  font-weight: 500;
}

.content {
  padding: 24px;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
}

.user-status-card {
  margin-bottom: 24px;
}

.statistic-item {
  text-align: center;
}

.statistic-title {
  font-size: 12px;
  color: rgba(0, 0, 0, 0.45);
  margin-bottom: 8px;
}

.test-area {
  margin-bottom: 24px;
}

.test-logs-card {
  margin-top: 24px;
}

/* 自定义滚动条 */
::-webkit-scrollbar {
  width: 8px;
  height: 8px;
}

::-webkit-scrollbar-track {
  background: #f3f4f6;
  border-radius: 10px;
}

::-webkit-scrollbar-thumb {
  background: linear-gradient(180deg, #3b82f6 0%, #1e40af 100%);
  border-radius: 10px;
}

::-webkit-scrollbar-thumb:hover {
  background: linear-gradient(180deg, #2563eb 0%, #1e3a8a 100%);
}
</style>
