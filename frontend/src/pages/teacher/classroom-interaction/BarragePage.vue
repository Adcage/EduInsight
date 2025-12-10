<template>
  <div class="barrage-page">
    <a-page-header title="弹幕管理" sub-title="实时查看和管理课堂弹幕">
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
        <BarrageWall ref="barrageWallRef" :course-id="courseId" :height="600" @barrage-click="handleBarrageClick" />
      </a-card>

      <!-- 统计信息 -->
      <a-row :gutter="16" style="margin-bottom: 16px">
        <a-col :xs="24" :sm="8">
          <a-card>
            <a-statistic title="总弹幕数" :value="statistics.total" :value-style="{ color: '#1890ff' }">
              <template #prefix><MessageOutlined /></template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="8">
          <a-card>
            <a-statistic title="答案弹幕" :value="statistics.answer" :value-style="{ color: '#52c41a' }">
              <template #prefix><CheckCircleOutlined /></template>
            </a-statistic>
          </a-card>
        </a-col>
        <a-col :xs="24" :sm="8">
          <a-card>
            <a-statistic title="自由弹幕" :value="statistics.free" :value-style="{ color: '#faad14' }">
              <template #prefix><CommentOutlined /></template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <!-- 弹幕列表 -->
      <a-card title="弹幕列表" :bordered="false">
        <template #extra>
          <a-space>
            <a-radio-group v-model:value="filterType" button-style="solid" @change="loadBarrages">
              <a-radio-button value="all">全部</a-radio-button>
              <a-radio-button value="answer">答案弹幕</a-radio-button>
              <a-radio-button value="free">自由弹幕</a-radio-button>
            </a-radio-group>
          </a-space>
        </template>

        <a-spin :spinning="loading">
          <a-empty v-if="filteredBarrages.length === 0 && !loading" description="暂无弹幕" />

          <a-list v-else :data-source="filteredBarrages" :pagination="paginationConfig">
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
                      <span>{{ item.user_name }}</span>
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
                      <a-space>
                        <span>{{ formatTime(item.created_at) }}</span>
                        <span v-if="item.question_id">
                          <a @click="viewQuestion(item.question_id)">查看问题</a>
                        </span>
                      </a-space>
                    </div>
                  </template>
                </a-list-item-meta>

                <template #actions>
                  <a-popconfirm title="确定删除这条弹幕吗？" @confirm="deleteBarrage(item)">
                    <a style="color: #ff4d4f">
                      <DeleteOutlined /> 删除
                    </a>
                  </a-popconfirm>
                </template>
              </a-list-item>
            </template>
          </a-list>
        </a-spin>
      </a-card>
    </div>

    <!-- 弹幕详情对话框 -->
    <a-modal v-model:open="detailModalVisible" title="弹幕详情" width="600px" :footer="null">
      <div v-if="currentBarrage">
        <a-descriptions :column="2" bordered>
          <a-descriptions-item label="内容" :span="2">
            {{ currentBarrage.content }}
          </a-descriptions-item>
          <a-descriptions-item label="发送者">
            {{ currentBarrage.user_name }}
          </a-descriptions-item>
          <a-descriptions-item label="类型">
            <a-tag :color="currentBarrage.question_id ? 'green' : 'blue'">
              {{ currentBarrage.question_id ? '答案弹幕' : '自由弹幕' }}
            </a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="是否匿名">
            {{ currentBarrage.is_anonymous ? '是' : '否' }}
          </a-descriptions-item>
          <a-descriptions-item label="发送时间">
            {{ formatTime(currentBarrage.created_at) }}
          </a-descriptions-item>
          <a-descriptions-item v-if="currentBarrage.question_id" label="关联问题" :span="2">
            <a @click="viewQuestion(currentBarrage.question_id)">查看问题详情</a>
          </a-descriptions-item>
        </a-descriptions>
      </div>
    </a-modal>
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
  DeleteOutlined,
} from '@ant-design/icons-vue'
import BarrageWall from '@/components/interaction/BarrageWall.vue'
import { barrageApiGet, barrageApiIntBarrageIdDelete } from '@/api/interactionController'
import { useBarrageSocket } from '@/composables/useSocket'
import dayjs from 'dayjs'

// 用户信息
const userId = ref(1)
const userName = ref('教师')
const courseId = ref(1)

// WebSocket
const { isConnected, onNewBarrage, onBarrageRemoved, notifyBarrageDeleted } = useBarrageSocket(
  courseId.value,
  userId.value,
  userName.value
)

// 数据
const loading = ref(false)
const barrages = ref<any[]>([])
const filterType = ref('all')
const detailModalVisible = ref(false)
const currentBarrage = ref<any>(null)

const barrageWallRef = ref()

// 分页配置
const paginationConfig = reactive({
  pageSize: 10,
  showSizeChanger: true,
  showQuickJumper: true,
  showTotal: (total: number) => `共 ${total} 条`,
})

// 统计信息
const statistics = computed(() => {
  const total = barrages.value.length
  const answer = barrages.value.filter((b) => b.question_id !== null).length
  const free = barrages.value.filter((b) => b.question_id === null).length
  return { total, answer, free }
})

// 过滤后的弹幕列表
const filteredBarrages = computed(() => {
  if (filterType.value === 'all') {
    return barrages.value
  } else if (filterType.value === 'answer') {
    return barrages.value.filter((b) => b.question_id !== null)
  } else {
    return barrages.value.filter((b) => b.question_id === null)
  }
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

    // 将历史弹幕添加到弹幕墙（延迟添加，避免卡顿）
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

// 删除弹幕
const deleteBarrage = async (barrage: any) => {
  try {
    await barrageApiIntBarrageIdDelete({
      barrageId: barrage.id,
    })

    // WebSocket通知
    notifyBarrageDeleted(barrage.id)

    message.success('删除成功')

    // 从本地列表移除
    const index = barrages.value.findIndex((b) => b.id === barrage.id)
    if (index > -1) {
      barrages.value.splice(index, 1)
    }

    // 从弹幕墙移除
    barrageWallRef.value?.removeBarrage(barrage.id)
  } catch (error: any) {
    message.error(error.response?.data?.message || '删除失败')
  }
}

// 弹幕点击事件
const handleBarrageClick = (barrage: any) => {
  currentBarrage.value = barrage
  detailModalVisible.value = true
}

// 查看问题
const viewQuestion = (questionId: number) => {
  // 跳转到问题详情页面
  message.info(`查看问题 ${questionId}`)
  // router.push(`/teacher/question?id=${questionId}`)
}

// 格式化时间
const formatTime = (time: string) => {
  return dayjs(time).format('YYYY-MM-DD HH:mm:ss')
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

    // 显示通知
    const type = data.barrage.question_id ? '答案弹幕' : '自由弹幕'
    message.info(`收到新${type}`)
  })

  // 监听弹幕删除
  onBarrageRemoved((data) => {
    console.log('弹幕被删除:', data)

    // 从本地列表移除
    const index = barrages.value.findIndex((b) => b.id === data.barrage_id)
    if (index > -1) {
      barrages.value.splice(index, 1)
    }

    // 从弹幕墙移除
    barrageWallRef.value?.removeBarrage(data.barrage_id)
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
