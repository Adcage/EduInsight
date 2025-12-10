<template>
  <div class="my-warnings-page">
    <a-card title="预警与通知" :bordered="false">
      <!-- 统计信息 -->
      <a-row :gutter="[16, 16]" class="statistics-cards">
        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card stat-card-high">
            <a-statistic
              title="高风险预警"
              :value="statistics.highRisk"
              :value-style="{ color: 'var(--error-color)' }"
            >
              <template #prefix>
                <WarningOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card stat-card-medium">
            <a-statistic
              title="中风险预警"
              :value="statistics.mediumRisk"
              :value-style="{ color: 'var(--warning-color)' }"
            >
              <template #prefix>
                <ExclamationCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card stat-card-low">
            <a-statistic
              title="低风险预警"
              :value="statistics.lowRisk"
              :value-style="{ color: 'var(--primary-color)' }"
            >
              <template #prefix>
                <InfoCircleOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>

        <a-col :xs="24" :sm="12" :md="6">
          <a-card class="stat-card stat-card-total">
            <a-statistic
              title="总预警数"
              :value="statistics.total"
              :value-style="{ color: 'var(--text-color)' }"
            >
              <template #prefix>
                <BellOutlined />
              </template>
            </a-statistic>
          </a-card>
        </a-col>
      </a-row>

      <!-- 预警列表 -->
      <a-list
        :data-source="warnings"
        :loading="loading"
        class="warnings-list"
      >
        <template #renderItem="{ item }">
          <a-list-item>
            <a-card class="warning-card" :bordered="false">
              <div class="warning-header">
                <div class="course-info">
                  <h3>{{ item.courseName }}</h3>
                  <a-tag>{{ item.courseCode }}</a-tag>
                  <a-tag>{{ item.semester }}</a-tag>
                </div>
                <a-badge
                  :count="item.warningCount"
                  :number-style="{ backgroundColor: getRiskColor(item.latestWarning.riskLevel) }"
                />
              </div>

              <a-divider />

              <div class="warning-content">
                <a-row :gutter="16">
                  <a-col :span="8">
                    <div class="info-item">
                      <span class="label">预测分数:</span>
                      <span class="value" :style="{ color: getScoreColor(item.latestWarning.predictedScore) }">
                        {{ item.latestWarning.predictedScore.toFixed(1) }} 分
                      </span>
                    </div>
                  </a-col>
                  <a-col :span="8">
                    <div class="info-item">
                      <span class="label">风险等级:</span>
                      <a-tag :color="getRiskColor(item.latestWarning.riskLevel)">
                        {{ getRiskLabel(item.latestWarning.riskLevel) }}
                      </a-tag>
                    </div>
                  </a-col>
                  <a-col :span="8">
                    <div class="info-item">
                      <span class="label">置信度:</span>
                      <span class="value">{{ item.latestWarning.confidence.toFixed(1) }}%</span>
                    </div>
                  </a-col>
                </a-row>

                <a-row :gutter="16" style="margin-top: 12px">
                  <a-col :span="12">
                    <div class="info-item">
                      <span class="label">预测日期:</span>
                      <span class="value">{{ item.latestWarning.predictionDate }}</span>
                    </div>
                  </a-col>

                </a-row>
              </div>

              <a-divider />

              <div class="warning-actions">
                <a-button type="primary" @click="showDetail(item.latestWarning.id)">
                  查看详情
                </a-button>
              </div>
            </a-card>
          </a-list-item>
        </template>

        <template #header>
          <div class="list-header">
            <h3>预警列表</h3>
            <a-button @click="loadWarnings" :loading="loading">
              <template #icon><ReloadOutlined /></template>
              刷新
            </a-button>
          </div>
        </template>
      </a-list>

      <!-- 预警详情抽屉 -->
      <a-drawer
        v-model:open="detailVisible"
        title="预警详情"
        width="600"
        :body-style="{ paddingBottom: '80px' }"
      >
        <div v-if="currentDetail" class="detail-content">
          <!-- 基本信息 -->
          <a-descriptions title="基本信息" :column="1" bordered>
            <a-descriptions-item label="课程名称">
              {{ currentDetail.courseName }}
            </a-descriptions-item>
            <a-descriptions-item label="课程代码">
              {{ currentDetail.courseCode }}
            </a-descriptions-item>
            <a-descriptions-item label="学期">
              {{ currentDetail.semester }}
            </a-descriptions-item>
            <a-descriptions-item label="预测分数">
              <span :style="{ color: getScoreColor(currentDetail.predictedScore), fontWeight: 'bold' }">
                {{ currentDetail.predictedScore.toFixed(1) }} 分
              </span>
            </a-descriptions-item>
            <a-descriptions-item label="风险等级">
              <a-tag :color="getRiskColor(currentDetail.riskLevel)">
                {{ getRiskLabel(currentDetail.riskLevel) }}
              </a-tag>
            </a-descriptions-item>
            <a-descriptions-item label="置信度">
              {{ currentDetail.confidence.toFixed(1) }}%
            </a-descriptions-item>
            <a-descriptions-item label="预测日期">
              {{ currentDetail.predictionDate }}
            </a-descriptions-item>

          </a-descriptions>

          <!-- 干预记录 -->
          <a-divider>干预记录</a-divider>
          <a-timeline v-if="currentDetail.interventions && currentDetail.interventions.length > 0">
            <a-timeline-item
              v-for="intervention in currentDetail.interventions"
              :key="intervention.id"
              :color="getInterventionColor(intervention.interventionType)"
            >
              <div class="intervention-item">
                <div class="intervention-header">
                  <strong>{{ intervention.teacherName }}</strong>
                  <span class="intervention-date">{{ intervention.interventionDate }}</span>
                </div>
                <div class="intervention-type">
                  <a-tag :color="getInterventionColor(intervention.interventionType)">
                    {{ getInterventionLabel(intervention.interventionType) }}
                  </a-tag>
                </div>
                <div class="intervention-description">
                  {{ intervention.description }}
                </div>
                <div v-if="intervention.expectedEffect" class="intervention-effect">
                  <strong>预期效果:</strong> {{ intervention.expectedEffect }}
                </div>
                <div v-if="intervention.actualEffect" class="intervention-effect">
                  <strong>实际效果:</strong> {{ intervention.actualEffect }}
                </div>
                <div v-if="intervention.studentFeedback" class="intervention-feedback">
                  <strong>学生反馈:</strong> {{ intervention.studentFeedback }}
                </div>
              </div>
            </a-timeline-item>
          </a-timeline>
          <a-empty v-else description="暂无干预记录" />
        </div>
      </a-drawer>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue'
import { message } from 'ant-design-vue'
import {
  WarningOutlined,
  ExclamationCircleOutlined,
  InfoCircleOutlined,
  BellOutlined,
  ReloadOutlined
} from '@ant-design/icons-vue'
import {
  predictionApiStudentMyWarningsGet,
  predictionApiStudentMyWarningsIntPredictionIdGet
} from '@/api/predictionController'

// 预警列表
const warnings = ref<any[]>([])
const loading = ref(false)

// 详情抽屉
const detailVisible = ref(false)
const currentDetail = ref<any>(null)

// 统计数据
const statistics = computed(() => {
  const stats = {
    highRisk: 0,
    mediumRisk: 0,
    lowRisk: 0,
    total: 0
  }

  warnings.value.forEach((warning) => {
    const riskLevel = warning.latestWarning.riskLevel
    if (riskLevel === 'high') stats.highRisk++
    else if (riskLevel === 'medium') stats.mediumRisk++
    else if (riskLevel === 'low') stats.lowRisk++
    stats.total++
  })

  return stats
})

// 获取风险等级颜色
const getRiskColor = (level: string) => {
  const colorMap: Record<string, string> = {
    high: '#ff4d4f',
    medium: '#faad14',
    low: '#1890ff',
    none: '#52c41a'
  }
  return colorMap[level] || '#d9d9d9'
}

// 获取风险等级标签
const getRiskLabel = (level: string) => {
  const labelMap: Record<string, string> = {
    high: '高风险',
    medium: '中风险',
    low: '低风险',
    none: '无风险'
  }
  return labelMap[level] || level
}

// 获取分数颜色
const getScoreColor = (score: number) => {
  if (score >= 90) return 'var(--success-color)'
  if (score >= 80) return 'var(--primary-color)'
  if (score >= 60) return 'var(--warning-color)'
  return 'var(--error-color)'
}

// 获取干预类型颜色
const getInterventionColor = (type: string) => {
  const colorMap: Record<string, string> = {
    talk: 'blue',
    tutoring: 'green',
    homework: 'orange',
    other: 'default'
  }
  return colorMap[type] || 'default'
}

// 获取干预类型标签
const getInterventionLabel = (type: string) => {
  const labelMap: Record<string, string> = {
    talk: '谈话',
    tutoring: '辅导',
    homework: '作业',
    other: '其他'
  }
  return labelMap[type] || type
}

// 加载预警列表
const loadWarnings = async () => {
  loading.value = true
  try {
    const response = await predictionApiStudentMyWarningsGet()
    const data = response.data || response

    // 转换字段名
    const warningList = (data || []).map((warning: any) => ({
      courseId: warning.course_id,
      courseName: warning.course_name,
      courseCode: warning.course_code,
      semester: warning.semester,
      warningCount: warning.warning_count,
      latestWarning: {
        id: warning.latest_warning.id,
        predictedScore: warning.latest_warning.predicted_score,
        confidence: warning.latest_warning.confidence,
        riskLevel: warning.latest_warning.risk_level,
        predictionDate: warning.latest_warning.prediction_date,
        isSent: warning.latest_warning.is_sent
      }
    }))

    warnings.value = warningList
  } catch (error: any) {
    console.error('加载预警列表失败:', error)
    message.error('加载预警列表失败')
  } finally {
    loading.value = false
  }
}

// 显示详情
const showDetail = async (predictionId: number) => {
  try {
    const response = await predictionApiStudentMyWarningsIntPredictionIdGet({
      prediction_id: predictionId
    })
    const data = response.data || response

    // 转换字段名
    currentDetail.value = {
      id: data.id,
      courseId: data.course_id,
      courseName: data.course_name,
      courseCode: data.course_code,
      semester: data.semester,
      studentId: data.student_id,
      studentName: data.student_name,
      studentCode: data.student_code,
      predictedScore: data.predicted_score,
      confidence: data.confidence,
      riskLevel: data.risk_level,
      predictionDate: data.prediction_date,
      isSent: data.is_sent,
      interventions: (data.interventions || []).map((intervention: any) => ({
        id: intervention.id,
        teacherName: intervention.teacher_name,
        interventionDate: intervention.intervention_date,
        interventionType: intervention.intervention_type,
        description: intervention.description,
        expectedEffect: intervention.expected_effect,
        actualEffect: intervention.actual_effect,
        studentFeedback: intervention.student_feedback,
        createdAt: intervention.created_at
      })),
      createdAt: data.created_at
    }

    detailVisible.value = true
  } catch (error: any) {
    console.error('加载预警详情失败:', error)
    message.error('加载预警详情失败')
  }
}

// 初始化
onMounted(() => {
  loadWarnings()
})
</script>

<style scoped lang="scss">
.my-warnings-page {
  padding: 24px;

  .statistics-cards {
    margin-bottom: 24px;

    .stat-card {
      background-color: var(--background-color-container);
      border: 1px solid var(--border-color-base);
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 2px 8px var(--shadow-color);
      }

      &.stat-card-high {
        border-left: 4px solid var(--error-color);
      }

      &.stat-card-medium {
        border-left: 4px solid var(--warning-color);
      }

      &.stat-card-low {
        border-left: 4px solid var(--primary-color);
      }

      &.stat-card-total {
        border-left: 4px solid var(--text-color);
      }
    }
  }

  .warnings-list {
    .list-header {
      display: flex;
      justify-content: space-between;
      align-items: center;

      h3 {
        margin: 0;
      }
    }

    .warning-card {
      background-color: var(--background-color-container);
      border: 1px solid var(--border-color-base);
      border-radius: 8px;
      transition: all 0.3s;

      &:hover {
        box-shadow: 0 2px 8px var(--shadow-color);
      }

      .warning-header {
        display: flex;
        justify-content: space-between;
        align-items: center;

        .course-info {
          h3 {
            margin: 0 0 8px 0;
            color: var(--text-color);
          }

          .ant-tag {
            margin-right: 8px;
          }
        }
      }

      .warning-content {
        .info-item {
          display: flex;
          flex-direction: column;
          gap: 4px;

          .label {
            color: var(--text-color-secondary);
            font-size: 14px;
          }

          .value {
            color: var(--text-color);
            font-size: 16px;
            font-weight: 500;
          }
        }
      }

      .warning-actions {
        display: flex;
        justify-content: flex-end;
      }
    }
  }

  .detail-content {
    .intervention-item {
      .intervention-header {
        display: flex;
        justify-content: space-between;
        margin-bottom: 8px;

        .intervention-date {
          color: var(--text-color-secondary);
          font-size: 12px;
        }
      }

      .intervention-type {
        margin-bottom: 8px;
      }

      .intervention-description {
        margin-bottom: 8px;
        color: var(--text-color);
      }

      .intervention-effect,
      .intervention-feedback {
        margin-top: 8px;
        padding: 8px;
        background-color: var(--background-color-light);
        border-radius: 4px;
        font-size: 14px;
        color: var(--text-color-secondary);
      }
    }
  }
}
</style>
