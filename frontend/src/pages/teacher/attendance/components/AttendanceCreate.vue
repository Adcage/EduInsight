<template>
  <div class="attendance-create">
    <a-form
        :model="formState"
        layout="vertical"
        @finish="onFinish"
    >
      <a-form-item
          :rules="[{ required: true, message: '请选择课程' }]"
          label="课程"
          name="courseId"
      >
        <a-select v-model:value="formState.courseId" placeholder="请选择课程">
          <a-select-option v-for="course in courses" :key="course.id" :value="course.id">
            {{ course.name }}
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item
          :rules="[{ required: true, message: '请选择班级' }]"
          label="班级"
          name="classId"
      >
        <a-select v-model:value="formState.classId" placeholder="请选择班级">
          <a-select-option v-for="cls in classes" :key="cls.id" :value="cls.id">
            {{ cls.name }}
          </a-select-option>
        </a-select>
      </a-form-item>

      <a-form-item
          :rules="[{ required: true, message: '请选择考勤方式' }]"
          label="考勤方式"
          name="type"
      >
        <a-radio-group v-model:value="formState.type">
          <a-radio value="qrcode">二维码考勤</a-radio>
          <a-radio value="location">定位考勤</a-radio>
          <a-radio value="manual">手动考勤</a-radio>
        </a-radio-group>
      </a-form-item>

      <a-form-item>
        <a-button :loading="loading" html-type="submit" type="primary">发起考勤</a-button>
        <a-button style="margin-left: 10px" @click="$emit('cancel')">取消</a-button>
      </a-form-item>
    </a-form>
  </div>
</template>

<script lang="ts" setup>
import {reactive, ref} from 'vue';
import {message} from 'ant-design-vue';
import {MOCK_CLASSES, MOCK_COURSES} from '../mock';

interface FormState {
  courseId: string;
  classId: string;
  type: string;
}

interface Emits {
  (e: 'success', data: any): void;

  (e: 'cancel'): void;
}

const emits = defineEmits<Emits>();

const loading = ref(false);
const courses = MOCK_COURSES;
const classes = MOCK_CLASSES;

const formState = reactive<FormState>({
  courseId: '',
  classId: '',
  type: 'qrcode',
});

const onFinish = (values: FormState) => {
  loading.value = true;
  // Mock API call
  setTimeout(() => {
    loading.value = false;
    message.success('考勤任务创建成功');
    emits('success', {
      ...values,
      createTime: new Date().toLocaleString(),
      status: 'active',
      totalStudents: 40,
      attendedCount: 0,
      teacherId: 'current_user',
      title: '新建考勤任务',
      requireLocation: values.type === 'location',
    });
  }, 1000);
};
</script>

<style lang="less" scoped>
.attendance-create {
  max-width: 600px;
  margin: 0 auto;
  padding: 24px;
  background-color: var(--background-color-container);
  border-radius: 8px;
}
</style>
