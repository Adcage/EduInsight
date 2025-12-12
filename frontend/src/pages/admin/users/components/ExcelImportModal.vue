<template>
  <a-modal
      v-model:open="visible"
      :width="700"
      title="批量导入用户"
      @cancel="handleCancel"
      @ok="handleSubmit"
  >
    <div class="import-container">
      <!-- 说明信息 -->
      <a-alert
          message="导入说明"
          show-icon
          style="margin-bottom: 16px"
          type="info"
      >
        <template #description>
          <div>
            <p>1. Excel文件应包含以下列:</p>
            <ul>
              <li><strong>用户名</strong>: 用于登录的用户名</li>
              <li><strong>工号/学号</strong>: 教师工号或学生学号</li>
              <li><strong>邮箱</strong>: 邮箱地址</li>
              <li><strong>真实姓名</strong>: 用户的真实姓名</li>
              <li><strong>角色</strong>: admin(管理员)/teacher(教师)/student(学生)</li>
              <li><strong>手机号</strong>: 手机号码(可选)</li>
              <li><strong>班级ID</strong>: 班级ID(学生必填)</li>
            </ul>
            <p>2. 默认密码为: <strong>123456</strong>,用户首次登录后需修改</p>
            <p>3. 支持 .xlsx 和 .xls 格式</p>
          </div>
        </template>
      </a-alert>

      <!-- 下载模板 -->
      <div style="margin-bottom: 16px">
        <a-button @click="downloadTemplate">
          <template #icon>
            <DownloadOutlined/>
          </template>
          下载导入模板
        </a-button>
      </div>

      <!-- 文件上传 -->
      <a-upload-dragger
          v-model:file-list="fileList"
          :before-upload="beforeUpload"
          :max-count="1"
          accept=".xlsx,.xls"
          name="file"
          @remove="handleRemove"
      >
        <p class="ant-upload-drag-icon">
          <InboxOutlined/>
        </p>
        <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
        <p class="ant-upload-hint">支持 .xlsx 和 .xls 格式的Excel文件</p>
      </a-upload-dragger>

      <!-- 导入进度 -->
      <div v-if="importing" style="margin-top: 16px">
        <a-spin>
          <template #tip>正在导入,请稍候...</template>
        </a-spin>
      </div>

      <!-- 导入结果 -->
      <div v-if="importResult" style="margin-top: 16px">
        <a-result
            :status="importResult.failedCount > 0 ? 'warning' : 'success'"
            :title="importResult.message"
        >
          <template #subTitle>
            <div>
              <p>总数: {{ importResult.totalCount }}</p>
              <p>成功: {{ importResult.successCount }}</p>
              <p>失败: {{ importResult.failedCount }}</p>
            </div>
          </template>
          <template #extra>
            <div v-if="importResult.errors.length > 0">
              <a-collapse>
                <a-collapse-panel key="1" header="查看错误详情">
                  <ul style="text-align: left">
                    <li
                        v-for="(error, index) in importResult.errors"
                        :key="index"
                        style="color: red"
                    >
                      {{ error }}
                    </li>
                  </ul>
                </a-collapse-panel>
              </a-collapse>
            </div>
          </template>
        </a-result>
      </div>
    </div>

    <template #footer>
      <a-button @click="handleCancel">取消</a-button>
      <a-button
          :disabled="fileList.length === 0"
          :loading="importing"
          type="primary"
          @click="handleSubmit"
      >
        开始导入
      </a-button>
    </template>
  </a-modal>
</template>

<script lang="ts" setup>
import {computed, ref} from 'vue'
import type {UploadProps} from 'ant-design-vue'
import {message} from 'ant-design-vue'
import {DownloadOutlined, InboxOutlined,} from '@ant-design/icons-vue'
import * as XLSX from 'xlsx'

// Props
interface Props {
  visible: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}>()

// 响应式数据
const fileList = ref<any[]>([])
const importing = ref(false)
const importResult = ref<any>(null)

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

// 上传前验证
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  const isExcel =
      file.type === 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' ||
      file.type === 'application/vnd.ms-excel'

  if (!isExcel) {
    message.error('只能上传Excel文件!')
    return false
  }

  const isLt10M = file.size / 1024 / 1024 < 10
  if (!isLt10M) {
    message.error('文件大小不能超过10MB!')
    return false
  }

  return false // 阻止自动上传
}

// 移除文件
const handleRemove = () => {
  fileList.value = []
  importResult.value = null
}

// 下载模板
const downloadTemplate = () => {
  // 创建模板数据(使用中文列名)
  const templateData = [
    {
      '用户名': 'zhangsan',
      '工号/学号': '2024001',
      '邮箱': 'zhangsan@example.com',
      '真实姓名': '张三',
      '角色': 'student',
      '手机号': '13800138000',
      '班级ID': 1,
    },
    {
      '用户名': 'lisi',
      '工号/学号': 'T2024001',
      '邮箱': 'lisi@example.com',
      '真实姓名': '李四',
      '角色': 'teacher',
      '手机号': '13800138001',
      '班级ID': '',
    },
  ]

  // 创建工作簿
  const ws = XLSX.utils.json_to_sheet(templateData)
  const wb = XLSX.utils.book_new()
  XLSX.utils.book_append_sheet(wb, ws, '用户导入模板')

  // 下载文件
  XLSX.writeFile(wb, '用户导入模板.xlsx')
  message.success('模板下载成功')
}

// 提交导入
const handleSubmit = async () => {
  if (fileList.value.length === 0) {
    message.warning('请先选择要导入的文件')
    return
  }

  importing.value = true
  importResult.value = null

  try {
    const file = fileList.value[0].originFileObj || fileList.value[0]
    const formData = new FormData()
    formData.append('file', file)

    const {default: request} = await import('@/request')
    const response = await request('/api/v1/users/batch-import', {
      method: 'POST',
      data: formData,
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    })

    importResult.value = response
    message.success('导入完成')

    if (response.failedCount === 0) {
      // 全部成功,延迟关闭
      setTimeout(() => {
        emit('success')
        visible.value = false
      }, 2000)
    }
  } catch (error: any) {
    message.error(error.message || '导入失败')
  } finally {
    importing.value = false
  }
}

// 取消
const handleCancel = () => {
  fileList.value = []
  importResult.value = null
  visible.value = false
}
</script>

<style scoped>
.import-container {
  padding: 8px 0;
}

:deep(.ant-upload-list) {
  margin-top: 16px;
}
</style>
