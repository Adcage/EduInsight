<template>
  <div class="user-avatar-wrapper">
    <!-- 未登录状态 -->
    <a-button v-if="!isLoggedIn" type="primary" @click="handleLogin">
      登录
    </a-button>

    <!-- 已登录状态 -->
    <a-dropdown v-else :trigger="['click']" v-model:open="dropdownVisible">
      <div class="user-info-trigger">
        <!-- 用户头像 -->
        <a-avatar v-if="user?.avatar" :src="user.avatar" :size="size" class="user-avatar" />
        <!-- 默认头像 -->
        <a-avatar v-else :size="size" class="user-avatar default-avatar">
          <template #icon>
            <UserOutlined />
          </template>
          {{ defaultAvatar }}
        </a-avatar>
        {{ user?.username }}
      </div>

      <template #overlay>
        <a-menu class="user-dropdown-menu">
          <a-menu-item key="profile" @click="handleProfileClick">
            <UserOutlined class="menu-icon" />
            个人信息
          </a-menu-item>
          <a-menu-divider />
          <a-menu-item key="logout" @click="handleLogout" :loading="logoutLoading">
            <LogoutOutlined class="menu-icon" />
            退出登录
          </a-menu-item>
        </a-menu>
      </template>
    </a-dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { UserOutlined, DownOutlined, LogoutOutlined } from '@ant-design/icons-vue'
import { useAuth } from '@/composables/useAuth'
import { log } from 'console'

// Props
interface Props {
  size?: number | 'small' | 'default' | 'large'
  showDropdown?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'default',
  showDropdown: true
})

// 组件状态
const dropdownVisible = ref(false)
const logoutLoading = ref(false)

// 使用 useAuth 组合式函数
const { user, isLoggedIn, userDisplayName, logout } = useAuth()
const router = useRouter()

// 计算默认头像
const defaultAvatar = computed(() => {
  if (!user.value) return 'U'
  const name = user.value.realName || user.value.username
  return name ? name.charAt(0).toUpperCase() : 'U'
})

/**
 * 跳转到登录页面
 */
const handleLogin = () => {
  router.push('/login')
}

/**
 * 处理用户登出
 */
const handleLogout = async () => {
  try {
    logoutLoading.value = true
    await logout()
    dropdownVisible.value = false
  } catch (error) {
    console.error('Logout failed:', error)
  } finally {
    logoutLoading.value = false
  }
}

/**
 * 跳转到个人信息页面
 */
const handleProfileClick = () => {
  dropdownVisible.value = false
  router.push('/profile')
}
</script>

<style scoped>
.user-avatar-wrapper {
  display: flex;
  align-items: center;
}

.user-info-trigger {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  padding: 0;
  transition: opacity 0.3s;
}

.user-info-trigger:hover {
  opacity: 0.8;
}

.user-avatar {
  cursor: pointer;
}

.default-avatar {
  background-color: #1890ff;
  color: white;
  font-weight: 500;
}

.user-name {
  font-size: 14px;
  color: #333;
  max-width: 120px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.dropdown-icon {
  font-size: 12px;
  color: #999;
  transition: transform 0.3s;
}

.user-dropdown-menu {
  min-width: 160px;
}

.menu-icon {
  margin-right: 8px;
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .user-name {
    color: #fff;
  }
}
</style>
