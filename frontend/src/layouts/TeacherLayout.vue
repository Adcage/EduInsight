<template>
  <a-layout class="teacher-layout">
    <!-- 全局头部 -->
    <GlobalHeader/>

    <a-layout class="main-layout">
      <!-- 左侧菜单栏 -->
      <LayoutSider
          :menu-items="menuItems"
          title="教师"
          @collapse-change="handleCollapseChange"
      />

      <!-- 主内容区域 -->
      <a-layout :class="{ 'collapsed-layout': collapsed }" class="content-layout">
        <a-layout-content class="content">
          <div class="content-wrapper">
            <router-view v-slot="{ Component }">
              <transition mode="out-in" name="fade">
                <component :is="Component"/>
              </transition>
            </router-view>
          </div>
        </a-layout-content>
      </a-layout>
    </a-layout>

    <!-- 全局底部 -->
    <GlobalFooter/>
  </a-layout>
</template>

<script lang="ts" setup>
import {ref} from 'vue'
import {
  BarChartOutlined,
  BookOutlined,
  CalendarOutlined,
  DashboardOutlined,
  FileAddOutlined,
  FileDoneOutlined,
  FolderOutlined,
  LineChartOutlined,
  MessageOutlined,
} from '@ant-design/icons-vue'
import GlobalHeader from '@/layouts/GlobalHeader.vue'
import GlobalFooter from '@/layouts/GlobalFooter.vue'
import type {MenuItem} from '@/components/layout/LayoutSider.vue'
import LayoutSider from '@/components/layout/LayoutSider.vue'

// 响应式数据
const collapsed = ref(false)

// 教师菜单配置(参考需求文档 4.2)
const menuItems: MenuItem[] = [
  {
    key: 'profile',
    label: '教师首页',
    icon: DashboardOutlined,
    path: '/teacher/profile',
  },
  {
    key: 'courses',
    label: '课程管理',
    icon: BookOutlined,
    path: '/teacher/courses',
  },
  {
    key: 'materials',
    label: '资料管理',
    icon: FolderOutlined,
    children: [
      {
        key: 'material-center',
        label: '资料中心',
        icon: FolderOutlined,
        path: '/teacher/materials',
      },
      {
        key: 'material-upload',
        label: '上传资料',
        icon: FileAddOutlined,
        path: '/teacher/materials/upload',
      },
      {
        key: 'my-materials',
        label: '我的资料',
        icon: FileDoneOutlined,
        path: '/teacher/materials/my',
      },
    ],
  },
  {
    key: 'attendance',
    label: '考勤管理',
    icon: CalendarOutlined,
    path: '/teacher/attendance',
  },
  {
    key: 'grades',
    label: '成绩管理',
    icon: BarChartOutlined,
    path: '/teacher/grades',
  },
  {
    key: 'interaction',
    label: '课堂互动',
    icon: MessageOutlined,
    path: '/teacher/interaction',
  },
  {
    key: 'analysis',
    label: '学情分析',
    icon: LineChartOutlined,
    path: '/teacher/analysis',
  },
]

// 方法
const handleCollapseChange = (isCollapsed: boolean) => {
  collapsed.value = isCollapsed
}
</script>

<style scoped>
.teacher-layout {
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
  transition: opacity 0.3s ease,
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
