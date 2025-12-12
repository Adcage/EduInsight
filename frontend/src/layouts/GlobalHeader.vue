<template>
  <a-layout-header class="global-header">
    <div class="header-content">
      <div class="logo">

        <router-link :to="homePath" class="logo-link">
          <img alt="网站Logo" class="site-logo" src="@/assets/logo48-48.ico"/>
          <h1>慧教通</h1>
        </router-link>
      </div>

      <div class="header-actions">
        <ThemeToggle/>
        <UserAvatar/>
      </div>
    </div>
  </a-layout-header>
</template>

<script lang="ts" setup>
import {computed, ref, watch} from 'vue'
import {useRoute} from 'vue-router'
import {useAuthStore} from '@/stores/auth'
import {getDefaultHomeByRole} from '@/utils/roleRoutes'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

const route = useRoute()
const authStore = useAuthStore()
const selectedKeys = ref<string[]>(['home'])

const homePath = computed(() => {
  return getDefaultHomeByRole(authStore.user?.role)
})

watch(
    () => route.path,
    (newPath) => {
      if (newPath === '/') {
        selectedKeys.value = ['home']
      } else if (newPath.startsWith('/about')) {
        selectedKeys.value = ['about']
      }
    },
    {immediate: true},
)
</script>

<style scoped>
.global-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  z-index: 1000;
  background-color: var(--header-bg);
  border-bottom: 1px solid var(--header-border);
  padding: 0 var(--spacing-xl);
  height: 64px;
}

.header-content {
  max-width: 100%;
  height: 100%;
  margin: 0 auto;
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo-link {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 16px;
}

.logo {
  display: flex;
  align-items: center;
  margin-top: 6px;
}

.logo h1 {
  margin: 0;
  font-size: var(--heading-4-size);
  color: var(--primary-color);
  font-weight: 600;
  line-height: 1;
  font-size: 24px;
}

.logo a {
  color: inherit;
  text-decoration: none;
}

.header-menu {
  flex: 1;
  margin: 0 var(--spacing-xl);
  border-bottom: none;
  background: transparent;
  line-height: 64px;
  height: 64px;
}

.header-menu :deep(.ant-menu-item) {
  line-height: 64px;
  height: 64px;
  border-bottom: 2px solid transparent;
}

.header-menu :deep(.ant-menu-item-selected) {
  border-bottom-color: var(--primary-color);
}

.header-menu :deep(.ant-menu-item::after) {
  display: none;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: var(--spacing-md);
}

@media (max-width: 768px) {
  .global-header {
    padding: 0 var(--spacing-md);
  }

  .header-menu {
    margin: 0 var(--spacing-md);
  }
}
</style>
