<template>
  <a-button
    type="text"
    class="theme-toggle"
    @click="toggleTheme"
    :title="themeName"
  >
    <template #icon>
      <span v-if="isDark" class="icon">🌙</span>
      <span v-else class="icon">☀️</span>
    </template>
  </a-button>
</template>

<script setup lang="ts">
import { useTheme } from '@/composables/useTheme'

const { isDark, themeName, toggleTheme } = useTheme()
</script>

<style scoped>
.theme-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 40px;
  height: 40px;
  border-radius: var(--border-radius-base);
  transition: all var(--animation-duration-base);
}

.theme-toggle:hover {
  background-color: var(--background-color-light);
}

.icon {
  font-size: 20px;
  display: inline-block;
}
</style>
