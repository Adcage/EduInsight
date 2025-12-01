<template>
  <a-layout class="basic-layout">
    <!-- 全局头部 -->
    <GlobalHeader />

    <!-- 主内容区 -->
    <a-layout-content class="layout-content">
      <div class="content-wrapper">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
          </transition>
        </router-view>
      </div>
    </a-layout-content>

    <!-- 全局底部 -->
    <GlobalFooter />
  </a-layout>
</template>

<script setup lang="ts">
import GlobalHeader from '@/components/GlobalHeader.vue'
import GlobalFooter from '@/components/GlobalFooter.vue'
</script>

<style scoped>
.basic-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.layout-content {
  flex: 1;
  background-color: var(--background-color);
  padding: var(--spacing-lg);
  margin-top: 64px;
}

.content-wrapper {
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
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

@media (max-width: 768px) {
  .layout-content {
    padding: var(--spacing-md);
  }
}
</style>
