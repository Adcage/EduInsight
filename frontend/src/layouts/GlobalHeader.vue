<template>
  <a-layout-header class="global-header">
    <div class="header-content">
      <div class="logo">
        <router-link to="/">
          <h1>慧教通</h1>
        </router-link>
      </div>

      <a-menu v-model:selectedKeys="selectedKeys" mode="horizontal" class="header-menu">
        <a-menu-item key="home">
          <router-link to="/">首页</router-link>
        </a-menu-item>
        <a-menu-item key="about">
          <router-link to="/about">关于</router-link>
        </a-menu-item>
      </a-menu>

      <div class="header-actions">
        <ThemeToggle />
        <UserAvatar />
      </div>
    </div>
  </a-layout-header>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import ThemeToggle from '@/components/common/ThemeToggle.vue'
import UserAvatar from '@/components/common/UserAvatar.vue'

const route = useRoute()
const selectedKeys = ref<string[]>(['home'])

watch(
  () => route.path,
  (newPath) => {
    if (newPath === '/') {
      selectedKeys.value = ['home']
    } else if (newPath.startsWith('/about')) {
      selectedKeys.value = ['about']
    }
  },
  { immediate: true },
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

.logo h1 {
  margin: 0;
  font-size: var(--heading-4-size);
  color: var(--primary-color);
  font-weight: 600;
  line-height: normal;
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
