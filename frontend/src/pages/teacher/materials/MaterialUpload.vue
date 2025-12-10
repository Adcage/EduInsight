<template>
  <div class="material-upload">
    <a-page-header
        sub-title="上传教学资料文件"
        title="上传资料"
        @back="handleBack"
    />

    <div class="content-container">
      <a-row :gutter="16">
        <!-- 左侧：上传表单 -->
        <a-col :span="uploadedMaterialId ? 16 : 24">
          <a-card :bordered="false">
            <a-form
                ref="formRef"
                :label-col="{ span: 4 }"
                :model="formData"
                :rules="rules"
                :wrapper-col="{ span: 16 }"
            >
              <!-- 文件上传 -->
              <a-form-item label="上传文件" name="file" required>
                <a-upload-dragger
                    v-model:file-list="fileList"
                    :accept="acceptedFileTypes"
                    :before-upload="beforeUpload"
                    :custom-request="customUpload"
                    :disabled="!!uploadedMaterialId"
                    :max-count="1"
                >
                  <p class="ant-upload-drag-icon">
                    <InboxOutlined/>
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
                    :maxlength="100"
                    placeholder="请输入资料标题"
                    show-count
                />
              </a-form-item>

              <!-- 资料描述 -->
              <a-form-item label="资料描述" name="description">
                <a-textarea
                    v-model:value="formData.description"
                    :maxlength="500"
                    :rows="4"
                    placeholder="请输入资料描述"
                    show-count
                />
              </a-form-item>

              <!-- 分类 -->
              <a-form-item label="资料分类" name="categoryId">
                <a-tree-select
                    v-model:value="formData.categoryId"
                    :field-names="{ label: 'name', value: 'id', children: 'children' }"
                    :tree-data="categoryTree"
                    allow-clear
                    placeholder="请选择分类（或使用智能推荐）"
                    tree-default-expand-all
                />
              </a-form-item>

              <!-- 标签 -->
              <a-form-item label="标签" name="tags">
                <a-select
                    v-model:value="formData.tags"
                    :max-tag-count="5"
                    allow-clear
                    mode="tags"
                    placeholder="输入标签后按回车添加（或使用智能推荐）"
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
                  v-if="uploading || classifying"
                  :wrapper-col="{ span: 16 }"
                  label="处理进度"
              >
                <a-steps :current="currentStep" size="small">
                  <a-step :status="getStepStatus(0)" title="上传文件"/>
                  <a-step :status="getStepStatus(1)" title="智能分析"/>
                  <a-step :status="getStepStatus(2)" title="完成"/>
                </a-steps>
                <a-progress
                    v-if="uploading"
                    :percent="uploadProgress"
                    :status="uploadStatus"
                    style="margin-top: 12px"
                />
              </a-form-item>

              <!-- 操作按钮 -->
              <a-form-item :wrapper-col="{ span: 16, offset: 4 }">
                <a-space>
                  <a-button
                      v-if="!uploadedMaterialId"
                      :loading="uploading"
                      type="primary"
                      @click="handleSubmit"
                  >
                    <template #icon>
                      <UploadOutlined/>
                    </template>
                    {{ uploading ? '上传中...' : '开始上传' }}
                  </a-button>
                  <a-button
                      v-else
                      type="primary"
                      @click="handleFinish"
                  >
                    <template #icon>
                      <CheckOutlined/>
                    </template>
                    完成
                  </a-button>
                  <a-button v-if="!uploadedMaterialId" @click="handleReset">重置</a-button>
                  <a-button @click="handleBack">{{ uploadedMaterialId ? '返回列表' : '取消' }}</a-button>
                </a-space>
              </a-form-item>
            </a-form>
          </a-card>
        </a-col>

        <!-- 右侧：智能分类面板（上传完成后显示） -->
        <a-col v-if="uploadedMaterialId" :span="8">
          <!-- 智能分类 -->
          <ClassificationPanel
              ref="classificationPanelRef"
              :auto-analyze="true"
              :material-id="uploadedMaterialId"
              @accepted="handleCategoryAccepted"
              @classified="handleClassified"
          />

          <!-- 标签推荐 -->
          <TagSuggestions
              ref="tagSuggestionsRef"
              v-model:selected-tags="formData.tags"
              :auto-load="true"
              :material-id="uploadedMaterialId"
          />
        </a-col>
      </a-row>
    </div>
  </div>
</template>

<script lang="ts" setup>
import {onMounted, reactive, ref} from 'vue'
import {useRouter} from 'vue-router'
import type {FormInstance, UploadProps} from 'ant-design-vue'
import {message} from 'ant-design-vue'
import {CheckOutlined, InboxOutlined, UploadOutlined} from '@ant-design/icons-vue'
import {materialApiUploadPost} from '@/api/materialController.ts'
import {categoryApiGet} from '@/api/categoryController.ts'
import {tagApiGet} from '@/api/tagController.ts'
import ClassificationPanel from '@/components/materials/ClassificationPanel.vue'
import TagSuggestions from '@/components/materials/TagSuggestions.vue'

const router = useRouter()

// 表单引用
const formRef = ref<FormInstance>()

// 组件引用
const classificationPanelRef = ref()
const tagSuggestionsRef = ref()

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

// 智能分类状态
const uploadedMaterialId = ref<number | null>(null)
const classifying = ref(false)
const currentStep = ref(0)

// 支持的文件类型
const acceptedFileTypes = '.pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.txt,.md,.jpg,.jpeg,.png,.gif,.bmp,.svg,.zip,.rar,.7z,.mp4,.avi,.mov'

// 表单验证规则
const rules = {
  title: [
    {required: true, message: '请输入资料标题', trigger: 'blur'},
    {min: 2, max: 100, message: '标题长度在 2 到 100 个字符', trigger: 'blur'}
  ],
  description: [
    {max: 500, message: '描述不能超过 500 个字符', trigger: 'blur'}
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
    // axios拦截器返回完整的response对象,需要通过response.data访问后端数据
    // 后端返回的数据结构是 { code: 200, data: { categories: [...] } }
    if (response.data?.code === 200 && response.data?.data) {
      const categories = response.data.data.categories || []
      categoryTree.value = buildCategoryTree(categories)
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
    map.set(cat.id, {...cat, children: []})
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
    // axios拦截器返回完整的response对象,需要通过response.data访问后端数据
    // 后端返回的数据结构是 { code: 200, data: { tags: [...], total, page, per_page, pages } }
    if (response.data?.code === 200 && response.data?.data) {
      existingTags.value = response.data.data.tags || []
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

// 获取步骤状态
const getStepStatus = (step: number): 'wait' | 'process' | 'finish' | 'error' => {
  if (step < currentStep.value) return 'finish'
  if (step === currentStep.value) {
    if (uploadStatus.value === 'exception') return 'error'
    return 'process'
  }
  return 'wait'
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
    currentStep.value = 0

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
    uploading.value = false

    // 解析响应数据 - axios 返回 response.data，后端返回 { code, message, data }
    const materialData = response.data?.data || response.data

    // 获取上传的资料ID，触发智能分类
    if (materialData?.id) {
      message.success('上传成功! 正在进行智能分析...')
      uploadedMaterialId.value = materialData.id
      currentStep.value = 1
      classifying.value = true
    } else {
      message.success('上传成功!')
      // 如果没有返回ID，直接跳转
      setTimeout(() => {
        router.push('/teacher/materials')
      }, 1000)
    }
  } catch (error: any) {
    uploadStatus.value = 'exception'
    message.error(error.message || '上传失败')
    uploading.value = false
  }
}

// 处理分类完成
const handleClassified = (result: API.ClassifyMaterialResponseModel) => {
  classifying.value = false
  currentStep.value = 2

  // 如果有高置信度的分类建议且尚未选择分类，自动填充
  if (result.suggestedCategoryId && !formData.categoryId && result.shouldAutoApply) {
    formData.categoryId = result.suggestedCategoryId
    message.info(`已自动应用分类: ${result.suggestedCategoryName}`)
  }
}

// 处理接受分类建议
const handleCategoryAccepted = (categoryId: number) => {
  formData.categoryId = categoryId
}

// 完成上传流程
const handleFinish = () => {
  message.success('资料上传完成!')
  router.push('/teacher/materials')
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
