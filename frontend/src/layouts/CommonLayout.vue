<template>
  <div class="common-layout">
    <router-view />
  </div>
</template>

<script setup lang="ts">
// 公共布局组件,用于登录、注册等不需要头部和侧边栏的页面
</script>

<style scoped>
.common-layout {
  min-height: 100vh;
  width: 100%;
}
</style>
