<template>
  <a-layout-sider
      v-model:collapsed="isCollapsed"
      :collapsed-width="80"
      :trigger="null"
      :width="220"
      class="layout-sider"
      collapsible
  >
    <div class="sider-content">
      <!-- 顶部标题 -->
      <div v-if="title" class="sider-header">
        <span v-if="!isCollapsed" class="sider-title">{{ title }}</span>
        <span v-else class="sider-title-collapsed">{{ title.charAt(0) }}</span>
      </div>

      <!-- 菜单容器 -->
      <div class="sider-menu-container">
        <a-menu
            v-model:openKeys="openKeys"
            v-model:selectedKeys="selectedKeys"
            class="sider-menu"
            mode="inline"
            theme="light"
            @click="handleMenuClick"
        >
          <template v-for="item in menuItems" :key="item.key">
            <!-- 子菜单 -->
            <a-sub-menu v-if="item.children" :key="item.key">
              <template #icon>
                <component :is="item.icon"/>
              </template>
              <template #title>{{ item.label }}</template>
              <a-menu-item v-for="child in item.children" :key="child.key">
                <component :is="child.icon"/>
                {{ child.label }}
              </a-menu-item>
            </a-sub-menu>

            <!-- 普通菜单项 -->
            <template v-else>
              <a-menu-item :key="item.key">
                <template #icon>
                  <component :is="item.icon"/>
                </template>
                <span>{{ item.label }}</span>
              </a-menu-item>
            </template>
          </template>
        </a-menu>
      </div>

      <!-- 折叠按钮（底部） -->
      <div class="sider-trigger" @click="toggleCollapsed">
        <MenuUnfoldOutlined v-if="isCollapsed"/>
        <MenuFoldOutlined v-else/>
      </div>
    </div>
  </a-layout-sider>
</template>

<script lang="ts" setup>
import {type Component, onMounted, ref, watch} from 'vue'
import {useRoute, useRouter} from 'vue-router'
import {MenuFoldOutlined, MenuUnfoldOutlined} from '@ant-design/icons-vue'

// 定义菜单项类型
export interface MenuItem {
  key: string
  label: string
  icon: Component
  path?: string
  children?: MenuItem[]
}

// Props
interface Props {
  menuItems: MenuItem[]
  title?: string // 可选的顶部标题，如"教师"、"学生"、"管理员"
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'collapse-change', collapsed: boolean): void
}>()

const router = useRouter()
const route = useRoute()

// 响应式数据
const isCollapsed = ref(false)
const selectedKeys = ref<string[]>([])
const openKeys = ref<string[]>([])

// 方法
const toggleCollapsed = () => {
  isCollapsed.value = !isCollapsed.value
  emit('collapse-change', isCollapsed.value)
}

const handleMenuClick = ({key}: { key: string }) => {
  selectedKeys.value = [key]

  // 从菜单配置中查找对应的路径
  const findPath = (items: MenuItem[]): string | undefined => {
    for (const item of items) {
      if (item.key === key && item.path) {
        return item.path
      }
      if (item.children) {
        const childPath = item.children.find((child) => child.key === key)?.path
        if (childPath) return childPath
      }
    }
    return undefined
  }

  const targetRoute = findPath(props.menuItems)
  if (targetRoute) {
    router.push(targetRoute).catch((err) => {
      console.error('路由跳转失败:', err)
    })
  }
}

// 根据当前路由设置选中的菜单项
const updateSelectedKeys = () => {
  const path = route.path

  // 从菜单配置中查找匹配的菜单项
  const findMenuByPath = (
      items: MenuItem[],
      parentKey?: string,
  ): { key: string; openKey?: string } | null => {
    for (const item of items) {
      // 检查当前项
      if (item.path === path) {
        return {key: item.key, openKey: parentKey}
      }
      // 检查子项
      if (item.children) {
        for (const child of item.children) {
          if (child.path === path) {
            return {key: child.key, openKey: item.key}
          }
        }
      }
    }
    return null
  }

  const menuInfo = findMenuByPath(props.menuItems)
  if (menuInfo) {
    selectedKeys.value = [menuInfo.key]
    if (menuInfo.openKey && !openKeys.value.includes(menuInfo.openKey)) {
      openKeys.value.push(menuInfo.openKey)
    }
  }
}

// 生命周期
onMounted(() => {
  updateSelectedKeys()
})

// 监听路由变化
watch(
    () => route.path,
    () => {
      updateSelectedKeys()
    },
)

// 暴露折叠状态给父组件
defineExpose({
  collapsed: isCollapsed,
})
</script>

<style scoped>
.layout-sider {
  background: var(--background-color-container, #fff) !important;
  border-right: 1px solid var(--border-color-split, #f0f0f0);
  position: fixed !important;
  left: 0;
  top: 64px;
  bottom: 0;
  height: auto !important;
  z-index: 100;
}

/* 强制覆盖 Ant Design Sider 的默认样式 */
.layout-sider :deep(.ant-layout-sider-children) {
  background: var(--background-color-container, #fff) !important;
  height: 100% !important;
}

.layout-sider :deep(.ant-layout-sider) {
  background: var(--background-color-container, #fff) !important;
}

/* 侧边栏内容容器 */
.sider-content {
  display: flex;
  flex-direction: column;
  height: 100%;
}

/* 菜单容器 */
.sider-menu-container {
  flex: 1;
  overflow-y: auto;
  overflow-x: hidden;
}

/* 顶部标题区域 */
.sider-header {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 56px;
  background: var(--primary-color, #1890ff);
  border-bottom: 1px solid var(--border-color-split, #f0f0f0);
  padding: 0 var(--spacing-md, 16px);
}

.sider-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-color-inverse, #fff);
  text-align: center;
}

.sider-title-collapsed {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-color-inverse, #fff);
  text-align: center;
}

/* 折叠按钮（底部） */
.sider-trigger {
  display: flex;
  align-items: center;
  justify-content: center;
  height: 48px;
  background: var(--background-color-light, #fafafa);
  border-top: 1px solid var(--border-color-split, #f0f0f0);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.sider-trigger:hover {
  background: var(--primary-light, #e6f7ff);
  color: var(--primary-color, #1890ff);
}

.sider-menu {
  border-right: none;
  background: transparent;
}

/* 菜单项样式优化 */
.sider-menu :deep(.ant-menu-item) {
  margin: 4px 8px;
  border-radius: var(--border-radius-base, 6px);
}

.sider-menu :deep(.ant-menu-submenu) {
  margin: 4px 8px;
}

.sider-menu :deep(.ant-menu-submenu > .ant-menu-submenu-title) {
  border-radius: var(--border-radius-base, 6px);
}

.sider-menu :deep(.ant-menu-item-selected) {
  background-color: var(--primary-light, #e6f7ff);
  color: var(--primary-color, #1890ff);
}

.sider-menu :deep(.ant-menu-item:hover) {
  background-color: var(--background-color-light, #fafafa);
}
</style>
