<template>
  <a-layout class="admin-layout">
    <!-- 全局头部 -->
    <GlobalHeader />

    <a-layout class="main-layout">
      <!-- 左侧菜单栏 -->
      <LayoutSider
        title="管理员"
        :menu-items="menuItems"
        @collapse-change="handleCollapseChange"
      />

      <!-- 主内容区域 -->
      <a-layout class="content-layout" :class="{ 'collapsed-layout': collapsed }">
        <a-layout-content class="content">
          <div class="content-wrapper">
            <router-view v-slot="{ Component }">
              <transition name="fade" mode="out-in">
                <component :is="Component" />
              </transition>
            </router-view>
          </div>
        </a-layout-content>
      </a-layout>
    </a-layout>

    <!-- 全局底部 -->
    <GlobalFooter />
  </a-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import {
  DashboardOutlined,
  UserOutlined,
  BookOutlined,
  TeamOutlined,
  SettingOutlined,
} from '@ant-design/icons-vue'
import GlobalHeader from '@/layouts/GlobalHeader.vue'
import GlobalFooter from '@/layouts/GlobalFooter.vue'
import LayoutSider from '@/components/layout/LayoutSider.vue'
import type { MenuItem } from '@/components/layout/LayoutSider.vue'

// 响应式数据
const collapsed = ref(false)

// 管理员菜单配置
const menuItems: MenuItem[] = [
  {
    key: 'dashboard',
    label: '控制台',
    icon: DashboardOutlined,
    path: '/admin/dashboard',
  },
  {
    key: 'users',
    label: '用户管理',
    icon: UserOutlined,
    path: '/admin/users',
  },
  {
    key: 'courses',
    label: '课程管理',
    icon: BookOutlined,
    path: '/admin/courses',
  },
  {
    key: 'classes',
    label: '班级管理',
    icon: TeamOutlined,
    path: '/admin/classes',
  },
  {
    key: 'settings',
    label: '系统设置',
    icon: SettingOutlined,
    path: '/admin/settings',
  },
]

// 方法
const handleCollapseChange = (isCollapsed: boolean) => {
  collapsed.value = isCollapsed
}
</script>

<style scoped>
.admin-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

/* 主布局样式 */
.main-layout {
  flex: 1;
  display: flex;
  position: relative;
  margin-top: 64px; /* GlobalHeader 的高度 */
}

/* 内容区域样式 */
.content-layout {
  flex: 1;
  display: flex;
  flex-direction: column;
  margin-left: 240px; /* 侧边栏展开时的宽度 */
  transition: margin-left 0.2s;
}

/* 侧边栏收起时调整内容区域左边距 */
.content-layout.collapsed-layout {
  margin-left: 80px; /* 侧边栏收起时的宽度 */
}

.content {
  flex: 1;
  background: var(--background-color, #f5f5f5);
  padding: var(--spacing-lg, 24px);
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  min-height: 600px;
}

/* 页面切换动画 */
.fade-enter-active,
.fade-leave-active {
  transition:
    opacity 0.3s ease,
    transform 0.3s ease;
}

.fade-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .content {
    padding: var(--spacing-md, 16px);
  }

  .content-wrapper {
    padding: var(--spacing-md, 16px);
  }
}
</style>
