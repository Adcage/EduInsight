<template>
  <div class="image-preview">
    <div class="image-container">
      <div class="image-wrapper">
        <img
            :alt="alt"
            :src="url"
            class="preview-img"
            @click="openFullscreen"
            @error="handleError"
        />
      </div>
    </div>
    <div class="image-toolbar">
      <a-space>
        <span class="image-info">图片已自适应显示，点击可全屏查看</span>
        <a-button size="small" type="link" @click="openFullscreen">
          <template #icon>
            <ExpandOutlined/>
          </template>
          全屏
        </a-button>
      </a-space>
    </div>

    <!-- 全屏预览 -->
    <a-modal
        v-model:open="fullscreenVisible"
        :bodyStyle="{ padding: 0, background: '#000' }"
        :destroyOnClose="true"
        :footer="null"
        :title="alt"
        :wrapStyle="{ top: 0 }"
        width="100%"
    >
      <div class="fullscreen-container">
        <img :alt="alt" :src="url" class="fullscreen-img"/>
      </div>
    </a-modal>
  </div>
</template>

<script lang="ts" setup>
import {ref} from 'vue'
import {message} from 'ant-design-vue'
import {ExpandOutlined} from '@ant-design/icons-vue'

interface Props {
  url: string
  alt?: string
}

const props = withDefaults(defineProps<Props>(), {
  alt: '图片预览'
})

const fullscreenVisible = ref(false)

const openFullscreen = () => {
  fullscreenVisible.value = true
}

const handleError = () => {
  message.error('图片加载失败')
}
</script>

<style scoped>
.image-preview {
  width: 100%;
  height: 100%;
  display: flex;
  flex-direction: column;
  background: #f5f5f5;
}

.image-container {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 20px;
  overflow: auto;
  background: #fff;
  min-height: 0;
}

.image-wrapper {
  max-width: 100%;
  max-height: 100%;
  display: flex;
  justify-content: center;
  align-items: center;
}

.preview-img {
  max-width: 100%;
  max-height: 50vh; /* 限制最大高度为视口高度的50% */
  width: auto;
  height: auto;
  object-fit: contain;
  display: block;
  cursor: pointer;
  transition: transform 0.3s ease;
  border-radius: 4px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.preview-img:hover {
  transform: scale(1.05);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}

.image-toolbar {
  padding: 16px 20px;
  background: #fafafa;
  border-top: 1px solid #e8e8e8;
  display: flex;
  justify-content: center;
  flex-shrink: 0;
}

.image-info {
  color: #666;
  font-size: 13px;
}

.fullscreen-container {
  width: 100%;
  height: 100vh;
  display: flex;
  justify-content: center;
  align-items: center;
  background: #000;
  padding: 20px;
  overflow: auto;
}

.fullscreen-img {
  max-width: 95%;
  max-height: 95%;
  object-fit: contain;
}
</style>
