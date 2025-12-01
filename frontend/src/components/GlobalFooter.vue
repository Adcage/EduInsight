<template>
  <a-layout-footer class="global-footer">
    <div class="footer-content">
      <p>&copy; 2024 Learning Study. All rights reserved.</p>
    </div>
  </a-layout-footer>
</template>

<script setup lang="ts"></script>

<style scoped>
.global-footer {
  background-color: var(--header-bg);
  border-top: 1px solid var(--header-border);
  text-align: center;
  padding: var(--spacing-lg);
  color: var(--text-color-secondary);
}

.footer-content {
  max-width: 1400px;
  margin: 0 auto;
}

.footer-content p {
  margin: 0;
  font-size: var(--font-size-sm);
}
</style>
