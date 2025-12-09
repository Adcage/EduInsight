<template>
  <a-modal
    v-model:open="visible"
    :title="isEdit ? '编辑用户' : '添加用户'"
    :width="600"
    @ok="handleSubmit"
    @cancel="handleCancel"
  >
    <a-form
      ref="formRef"
      :model="formData"
      :rules="rules"
      :label-col="{ span: 6 }"
      :wrapper-col="{ span: 16 }"
    >
      <a-form-item label="用户名" name="username">
        <a-input v-model:value="formData.username" placeholder="请输入用户名" />
      </a-form-item>

      <a-form-item label="工号/学号" name="userCode">
        <a-input v-model:value="formData.userCode" placeholder="请输入工号或学号" />
      </a-form-item>

      <a-form-item label="真实姓名" name="realName">
        <a-input v-model:value="formData.realName" placeholder="请输入真实姓名" />
      </a-form-item>

      <a-form-item label="邮箱" name="email">
        <a-input v-model:value="formData.email" placeholder="请输入邮箱地址" />
      </a-form-item>

      <a-form-item label="角色" name="role">
        <a-select v-model:value="formData.role" placeholder="请选择角色">
          <a-select-option value="admin">管理员</a-select-option>
          <a-select-option value="teacher">教师</a-select-option>
          <a-select-option value="student">学生</a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item label="手机号" name="phone">
        <a-input v-model:value="formData.phone" placeholder="请输入手机号(可选)" />
      </a-form-item>

      <a-form-item
        v-if="formData.role === 'student'"
        label="班级ID"
        name="classId"
      >
        <a-input-number
          v-model:value="formData.classId"
          placeholder="请输入班级ID"
          :min="1"
          style="width: 100%"
        />
      </a-form-item>

      <a-form-item v-if="!isEdit" label="密码" name="password">
        <a-input-password
          v-model:value="formData.password"
          placeholder="请输入密码(至少6位)"
        />
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { message } from 'ant-design-vue'
import type { FormInstance, Rule } from 'ant-design-vue'
import { userApiIntUserIdPut, userApiCreatePost } from '@/api/userController'

// Props
interface Props {
  visible: boolean
  userData: any
  isEdit: boolean
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'update:visible', value: boolean): void
  (e: 'success'): void
}>()

// 响应式数据
const formRef = ref<FormInstance>()
const formData = reactive({
  username: '',
  userCode: '',
  realName: '',
  email: '',
  role: 'student',
  phone: '',
  classId: undefined as number | undefined,
  password: '',
})

// 表单验证规则
const rules: Record<string, Rule[]> = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 50, message: '用户名长度为3-50个字符', trigger: 'blur' },
  ],
  userCode: [
    { required: true, message: '请输入工号/学号', trigger: 'blur' },
  ],
  realName: [
    { required: true, message: '请输入真实姓名', trigger: 'blur' },
  ],
  email: [
    { required: true, message: '请输入邮箱地址', trigger: 'blur' },
    { type: 'email', message: '请输入有效的邮箱地址', trigger: 'blur' },
  ],
  role: [
    { required: true, message: '请选择角色', trigger: 'change' },
  ],
  phone: [
    { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的手机号', trigger: 'blur' },
  ],
  classId: [
    {
      validator: (_rule: any, value: any) => {
        if (formData.role === 'student' && !value) {
          return Promise.reject('学生角色必须指定班级ID')
        }
        return Promise.resolve()
      },
      trigger: 'change',
    },
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码至少6位', trigger: 'blur' },
  ],
}

// 计算属性
const visible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

// 重置表单
const resetForm = () => {
  Object.assign(formData, {
    username: '',
    userCode: '',
    realName: '',
    email: '',
    role: 'student',
    phone: '',
    classId: undefined,
    password: '',
  })
  formRef.value?.clearValidate()
}

// 提交表单
const handleSubmit = async () => {
  try {
    await formRef.value?.validate()

    const { default: request } = await import('@/request')

    if (props.isEdit) {
      // 编辑用户
      await userApiIntUserIdPut(
        { userId: props.userData.id },
        {
          username: formData.username,
          email: formData.email,
          realName: formData.realName,
          phone: formData.phone || undefined,
        }
      )
      message.success('用户更新成功')
    } else {
      // 创建用户
      await userApiCreatePost({
        username: formData.username,
        userCode: formData.userCode,
        realName: formData.realName,
        email: formData.email,
        role: formData.role,
        phone: formData.phone || undefined,
        classId: formData.role === 'student' ? formData.classId : undefined,
        password: formData.password,
      })
      message.success('用户创建成功')
    }

    emit('success')
    visible.value = false
  } catch (error: any) {
    if (error.errorFields) {
      // 表单验证错误
      return
    }
    message.error(error.message || '操作失败')
  }
}

// 取消
const handleCancel = () => {
  resetForm()
  visible.value = false
}


// 监听用户数据变化
watch(
  () => props.userData,
  (newData) => {
    if (newData) {
      Object.assign(formData, {
        username: newData.username || '',
        userCode: newData.userCode || '',
        realName: newData.realName || '',
        email: newData.email || '',
        role: newData.role || 'student',
        phone: newData.phone || '',
        classId: newData.classId || undefined,
        password: '',
      })
    } else {
      resetForm()
    }
  },
  { immediate: true }
)
</script>

<style scoped>
/* 可以添加自定义样式 */
</style>
