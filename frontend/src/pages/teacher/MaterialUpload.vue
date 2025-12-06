<template>
  <div class="material-upload">
    <a-page-header
      title="上传资料"
      sub-title="上传教学资料文件"
      @back="handleBack"
    />

    <div class="content-container">
      <a-card :bordered="false">
        <a-form
          ref="formRef"
          :model="formData"
          :rules="rules"
          :label-col="{ span: 4 }"
          :wrapper-col="{ span: 16 }"
        >
          <!-- 文件上传 -->
          <a-form-item label="上传文件" name="file" required>
            <a-upload-dragger
              v-model:file-list="fileList"
              :before-upload="beforeUpload"
              :custom-request="customUpload"
              :max-count="1"
              :accept="acceptedFileTypes"
            >
              <p class="ant-upload-drag-icon">
                <InboxOutlined />
              </p>
              <p class="ant-upload-text">点击或拖拽文件到此区域上传</p>
              <p class="ant-upload-hint">
                支持 PDF, Word, PPT, Excel, 图片等格式，单个文件不超过 100MB
              </p>
            </a-upload-dragger>
          </a-form-item>

          <!-- 资料标题 -->
          <a-form-item label="资料标题" name="title" required>
            <a-input
              v-model:value="formData.title"
              placeholder="请输入资料标题"
              :maxlength="100"
              show-count
            />
          </a-form-item>

          <!-- 资料描述 -->
          <a-form-item label="资料描述" name="description">
            <a-textarea
              v-model:value="formData.description"
              placeholder="请输入资料描述"
              :rows="4"
              :maxlength="500"
              show-count
            />
          </a-form-item>

          <!-- 分类 -->
          <a-form-item label="资料分类" name="categoryId">
            <a-tree-select
              v-model:value="formData.categoryId"
              :tree-data="categoryTree"
              :field-names="{ label: 'name', value: 'id', children: 'children' }"
              placeholder="请选择分类"
              allow-clear
              tree-default-expand-all
            />
          </a-form-item>

          <!-- 标签 -->
          <a-form-item label="标签" name="tags">
            <a-select
              v-model:value="formData.tags"
              mode="tags"
              placeholder="输入标签后按回车添加"
              :max-tag-count="5"
              allow-clear
            >
              <a-select-option
                v-for="tag in existingTags"
                :key="tag.id"
                :value="tag.name"
              >
                {{ tag.name }}
              </a-select-option>
            </a-select>
          </a-form-item>

          <!-- 上传进度 -->
          <a-form-item
            v-if="uploading"
            label="上传进度"
            :wrapper-col="{ span: 16 }"
          >
            <a-progress :percent="uploadProgress" :status="uploadStatus" />
          </a-form-item>

          <!-- 操作按钮 -->
          <a-form-item :wrapper-col="{ span: 16, offset: 4 }">
            <a-space>
              <a-button
                type="primary"
                :loading="uploading"
                @click="handleSubmit"
              >
                <template #icon><UploadOutlined /></template>
                {{ uploading ? '上传中...' : '开始上传' }}
              </a-button>
              <a-button @click="handleReset">重置</a-button>
              <a-button @click="handleBack">取消</a-button>
            </a-space>
          </a-form-item>
        </a-form>
      </a-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { message } from 'ant-design-vue'
import type { FormInstance, UploadProps } from 'ant-design-vue'
import {
  InboxOutlined,
  UploadOutlined
} from '@ant-design/icons-vue'
import { materialApiUploadPost } from '@/api/materialController'
import { categoryApiGet } from '@/api/categoryController'
import { tagApiGet } from '@/api/tagController'

const router = useRouter()

// 表单引用
const formRef = ref<FormInstance>()

// 文件列表
const fileList = ref<any[]>([])

// 表单数据
const formData = reactive({
  title: '',
  description: '',
  categoryId: undefined as number | undefined,
  tags: [] as string[]
})

// 分类树
const categoryTree = ref<any[]>([])

// 已有标签
const existingTags = ref<any[]>([])

// 上传状态
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref<'normal' | 'active' | 'success' | 'exception'>('normal')

// 支持的文件类型
const acceptedFileTypes = '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.jpg,.jpeg,.png,.gif,.bmp,.svg,.zip,.rar,.7z,.mp4,.avi,.mov'

// 表单验证规则
const rules = {
  title: [
    { required: true, message: '请输入资料标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  description: [
    { max: 500, message: '描述不能超过 500 个字符', trigger: 'blur' }
  ],
  file: [
    { 
      required: true, 
      validator: (_rule: any, _value: any) => {
        if (fileList.value.length === 0) {
          return Promise.reject('请选择要上传的文件')
        }
        return Promise.resolve()
      },
      trigger: 'change'
    }
  ]
}

// 加载分类列表
const loadCategories = async () => {
  try {
    const response = await categoryApiGet()
    if (response.code === 200 && response.data) {
      categoryTree.value = buildCategoryTree(response.data)
    }
  } catch (error: any) {
    console.error('加载分类失败:', error)
  }
}

// 构建分类树
const buildCategoryTree = (categories: any[]): any[] => {
  const map = new Map()
  const tree: any[] = []

  // 创建映射
  categories.forEach(cat => {
    map.set(cat.id, { ...cat, children: [] })
  })

  // 构建树结构
  categories.forEach(cat => {
    const node = map.get(cat.id)
    if (cat.parentId === null || cat.parentId === undefined) {
      tree.push(node)
    } else {
      const parent = map.get(cat.parentId)
      if (parent) {
        parent.children.push(node)
      }
    }
  })

  return tree
}

// 加载标签列表
const loadTags = async () => {
  try {
    const response = await tagApiGet()
    if (response.code === 200 && response.data) {
      existingTags.value = response.data || []
    }
  } catch (error: any) {
    console.error('加载标签失败:', error)
  }
}

// 文件上传前验证
const beforeUpload: UploadProps['beforeUpload'] = (file) => {
  // 验证文件大小（100MB）
  const isLt100M = file.size / 1024 / 1024 < 100
  if (!isLt100M) {
    message.error('文件大小不能超过 100MB!')
    return false
  }

  // 自动填充标题（如果为空）
  if (!formData.title && file.name) {
    formData.title = file.name.substring(0, file.name.lastIndexOf('.'))
  }

  return false // 阻止自动上传
}

// 自定义上传
const customUpload: UploadProps['customRequest'] = (options) => {
  // 不做任何处理，由 handleSubmit 统一处理
  return
}

// 提交表单
const handleSubmit = async () => {
  try {
    // 验证表单
    await formRef.value?.validate()

    // 验证文件
    if (fileList.value.length === 0) {
      message.error('请选择要上传的文件')
      return
    }

    uploading.value = true
    uploadProgress.value = 0
    uploadStatus.value = 'active'

    // 构建 FormData
    const formDataToSend = new FormData()
    formDataToSend.append('file', fileList.value[0].originFileObj)
    formDataToSend.append('title', formData.title)
    
    if (formData.description) {
      formDataToSend.append('description', formData.description)
    }
    if (formData.categoryId) {
      formDataToSend.append('category_id', formData.categoryId.toString())
    }
    if (formData.tags.length > 0) {
      formDataToSend.append('tags', formData.tags.join(','))
    }

    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += 10
      }
    }, 200)

    // 调用上传接口
    const response = await materialApiUploadPost({
      data: formDataToSend,
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })

    clearInterval(progressInterval)
    uploadProgress.value = 100
    uploadStatus.value = 'success'

    message.success('上传成功!')
    
    // 延迟跳转
    setTimeout(() => {
      router.push('/teacher/materials')
    }, 1000)
  } catch (error: any) {
    uploadStatus.value = 'exception'
    message.error(error.message || '上传失败')
  } finally {
    uploading.value = false
  }
}

// 重置表单
const handleReset = () => {
  formRef.value?.resetFields()
  fileList.value = []
  uploadProgress.value = 0
  uploadStatus.value = 'normal'
}

// 返回
const handleBack = () => {
  router.back()
}

// 初始化
onMounted(() => {
  loadCategories()
  loadTags()
})
</script>

<style scoped>
.material-upload .content-container {
  padding: 16px;
}

:deep(.ant-upload-drag) {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  background: #fafafa;
  transition: all 0.3s;
}

:deep(.ant-upload-drag:hover) {
  border-color: #1890ff;
}

:deep(.ant-upload-drag-icon) {
  font-size: 48px;
  color: #1890ff;
}

:deep(.ant-upload-text) {
  font-size: 16px;
  color: rgba(0, 0, 0, 0.85);
  margin-top: 8px;
}

:deep(.ant-upload-hint) {
  font-size: 14px;
  color: rgba(0, 0, 0, 0.45);
}
</style>
