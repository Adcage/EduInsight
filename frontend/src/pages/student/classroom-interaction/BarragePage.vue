<template>
  <div class="barrage-page">
    <a-page-header title="弹幕互动" sub-title="发送弹幕，参与课堂互动">
      <template #extra>
        <a-space>
          <a-badge :status="isConnected ? 'success' : 'error'" :text="isConnected ? '已连接' : '未连接'" />
          <a-button @click="loadBarrages">
            <template #icon><ReloadOutlined /></template>
            刷新
          </a-button>
        </a-space>
      </template>
    </a-page-header>

    <div class="content-container">
      <!-- 弹幕墙 -->
      <a-card title="弹幕墙" :bordered="false" style="margin-bottom: 16px">
        <template #extra>
          <a-space>
            <a-tag color="green">
              <CheckCircleOutlined /> 绿色 = 答案弹幕
            </a-tag>
            <a-tag color="blue">
              <CommentOutlined /> 蓝色 = 自由弹幕
            </a-tag>
          </a-space>
        </template>

        <BarrageWall ref="barrageWallRef" :course-id="courseId" :height="500" />
      </a-card>

      <!-- 发送弹幕 -->
      <a-card title="发送弹幕" :bordered="false" style="margin-bottom: 16px">
        <a-alert
          message="提示"
          description="回答问题的答案会自动转为绿色弹幕，这里发送的是蓝色自由弹幕"
          type="info"
          show-icon
          style="margin-bottom: 16px"
        />

        <a-input-search
          v-model:value="barrageContent"
          placeholder="输入弹幕内容，按回车或点击发送..."
          enter-button="发送"
          size="large"
          :loading="sendLoading"
          @search="handleSendBarrage"
        >
          <template #prefix>
            <MessageOutlined />
          </template>
        </a-input-search>

        <div style="margin-top: 12px">
          <a-checkbox v-model:checked="isAnonymous"> 匿名发送 </a-checkbox>
        </div>
      </a-card>

      <!-- 我的弹幕 -->
      <a-card title="我的弹幕" :bordered="false">
        <a-spin :spinning="loading">
          <a-empty v-if="myBarrages.length === 0 && !loading" description="你还没有发送过弹幕" />

          <a-list v-else :data-source="myBarrages" :pagination="paginationConfig">
            <template #renderItem="{ item }">
              <a-list-item>
                <a-list-item-meta>
                  <template #avatar>
                    <a-avatar :style="{ backgroundColor: item.question_id ? '#52c41a' : '#1890ff' }">
                      <MessageOutlined />
                    </a-avatar>
                  </template>

                  <template #title>
                    <a-space>
                      <a-tag v-if="item.question_id" color="green">
                        <CheckCircleOutlined /> 答案弹幕
                      </a-tag>
                      <a-tag v-else color="blue">
                        <CommentOutlined /> 自由弹幕
                      </a-tag>
                      <a-tag v-if="item.is_anonymous" color="orange"> 匿名 </a-tag>
                    </a-space>
                  </template>

                  <template #description>
                    <div class="barrage-content">{{ item.content }}</div>
                    <div class="barrage-meta">
                      <span>{{ formatTime(item.created_at) }}</span>
                    </div>
                  </template>
                </a-list-item-meta>

                <template #actions>
                  <a @click="resendBarrage(item)">
                    <ReloadOutlined /> 重发
                  </a>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  ReloadOutlined,
  MessageOutlined,
  CheckCircleOutlined,
  CommentOutlined,
} from '@ant-design/icons-vue'
import BarrageWall from '@/components/interaction/BarrageWall.vue'
import { barrageApiPost, barrageApiGet } from '@/api/interactionController'
import { useBarrageSocket } from '@/composables/useSocket'
import dayjs from 'dayjs'

// 用户信息
const userId = ref(1)
const userName = ref('学生')
const courseId = ref(1)

// WebSocket
const { isConnected, onNewBarrage, sendBarrage } = useBarrageSocket(courseId.value, userId.value, userName.value)

// 数据
const loading = ref(false)
const sendLoading = ref(false)
const barrages = ref<any[]>([])
const barrageContent = ref('')
const isAnonymous = ref(false)

const barrageWallRef = ref()

// 分页配置
const paginationConfig = reactive({
  pageSize: 10,
  showSizeChanger: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

// 我的弹幕
const myBarrages = computed(() => {
  return barrages.value.filter((b) => b.user_id === userId.value)
})

// 加载弹幕列表
const loadBarrages = async () => {
  loading.value = true
  try {
    const response = await barrageApiGet({
      courseId: courseId.value,
      page: 1,
      perPage: 200,
    })

    barrages.value = response.data.data.barrages

    // 将历史弹幕添加到弹幕墙
    if (barrageWallRef.value) {
      // 只添加最近的50条
      const recentBarrages = barrages.value.slice(0, 50)
      barrageWallRef.value.addBarrages(recentBarrages)
    }
  } catch (error: any) {
    message.error(error.response?.data?.message || '加载弹幕列表失败')
  } finally {
    loading.value = false
  }
}

// 发送弹幕
const handleSendBarrage = async () => {
  if (!barrageContent.value.trim()) {
    message.warning('请输入弹幕内容')
    return
  }

  if (barrageContent.value.length < 2) {
    message.warning('弹幕内容至少2个字符')
    return
  }

  sendLoading.value = true
  try {
    const response = await barrageApiPost({
      content: barrageContent.value,
      courseId: courseId.value,
      isAnonymous: isAnonymous.value,
    })

    const newBarrage = response.data.data

    // WebSocket广播
    sendBarrage(newBarrage)

    // 添加到本地列表
    barrages.value.unshift(newBarrage)

    // 添加到弹幕墙
    barrageWallRef.value?.addBarrage(newBarrage)

    message.success('发送成功')
    barrageContent.value = ''
  } catch (error: any) {
    message.error(error.response?.data?.message || '发送失败')
  } finally {
    sendLoading.value = false
  }
}

// 重发弹幕
const resendBarrage = async (barrage: any) => {
  barrageContent.value = barrage.content
  isAnonymous.value = barrage.is_anonymous
  message.info('已填充弹幕内容，点击发送即可重发')
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('MM-DD HH:mm')
}

// WebSocket事件监听
onMounted(() => {
  loadBarrages()

  // 监听新弹幕
  onNewBarrage((data) => {
    console.log('收到新弹幕:', data)

    // 添加到列表
    barrages.value.unshift(data.barrage)

    // 添加到弹幕墙
    barrageWallRef.value?.addBarrage(data.barrage)
  })
})
</script>

<style scoped lang="scss">
.barrage-page {
  min-height: 100vh;
  background: var(--bg-color);
}

.content-container {
  padding: 24px;
}

.barrage-content {
  font-size: 15px;
  line-height: 1.6;
  margin-bottom: 8px;
  color: var(--text-color);
}

.barrage-meta {
  font-size: 13px;
  color: var(--text-color-secondary);
}
</style>
