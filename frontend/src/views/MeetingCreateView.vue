<template>
  <div class="meeting-create">
    <el-page-header @back="$router.back()" content="新建会议" />

    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      class="create-form"
    >
      <el-form-item label="会议标题" prop="title">
        <el-input v-model="form.title" placeholder="请输入会议标题" />
      </el-form-item>

      <el-form-item label="会议类型">
        <el-select v-model="form.meeting_type" placeholder="请选择" clearable style="width: 100%">
          <el-option label="售前交流" value="presales" />
          <el-option label="项目推进" value="project" />
          <el-option label="技术方案" value="technical" />
          <el-option label="招投标沟通" value="bidding" />
          <el-option label="其他" value="other" />
        </el-select>
      </el-form-item>

      <el-form-item label="客户">
        <el-select
          v-model="form.customer_id"
          placeholder="请选择客户"
          clearable
          style="width: 100%"
          @change="onCustomerChange"
        >
          <el-option v-for="c in customers" :key="c.id" :label="c.name" :value="c.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="项目">
        <el-select
          v-model="form.project_id"
          placeholder="请先选择客户"
          clearable
          :disabled="!form.customer_id"
          style="width: 100%"
        >
          <el-option v-for="p in projects" :key="p.id" :label="p.name" :value="p.id" />
        </el-select>
      </el-form-item>

      <el-form-item label="会议时间">
        <el-date-picker
          v-model="form.meeting_time"
          type="datetime"
          placeholder="请选择会议时间"
          style="width: 100%"
        />
      </el-form-item>

      <el-form-item label="参会人">
        <el-tag
          v-for="(p, i) in form.participants"
          :key="i"
          closable
          @close="removeParticipant(i)"
          class="participant-tag"
        >
          {{ p }}
        </el-tag>
        <el-input
          v-if="inputVisible"
          ref="inputRef"
          v-model="inputValue"
          size="small"
          style="width: 100px"
          @keyup.enter="addParticipant"
          @blur="addParticipant"
        />
        <el-button v-else size="small" @click="showInput">+ 添加</el-button>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="submit">创建会议</el-button>
        <el-button @click="$router.back()">取消</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { listCustomers, type Customer } from '@/api/customers'
import { listProjects, type Project } from '@/api/projects'
import { createMeeting } from '@/api/meetings'

const router = useRouter()
const formRef = ref<FormInstance>()
const customers = ref<Customer[]>([])
const projects = ref<Project[]>([])
const submitting = ref(false)
const inputVisible = ref(false)
const inputValue = ref('')
const inputRef = ref<HTMLInputElement>()

const form = ref({
  title: '',
  meeting_type: '',
  customer_id: '',
  project_id: '',
  meeting_time: null as Date | null,
  participants: [] as string[],
})

const rules: FormRules = {
  title: [{ required: true, message: '请输入会议标题', trigger: 'blur' }],
}

async function onCustomerChange(id: string) {
  form.value.project_id = ''
  projects.value = id ? await listProjects(id) : []
}

function removeParticipant(i: number) {
  form.value.participants.splice(i, 1)
}

function showInput() {
  inputVisible.value = true
  nextTick(() => inputRef.value?.focus())
}

function addParticipant() {
  const v = inputValue.value.trim()
  if (v && !form.value.participants.includes(v)) {
    form.value.participants.push(v)
  }
  inputVisible.value = false
  inputValue.value = ''
}

async function submit() {
  await formRef.value?.validate()
  submitting.value = true
  try {
    const meeting = await createMeeting({
      title: form.value.title,
      meeting_type: form.value.meeting_type || undefined,
      customer_id: form.value.customer_id || undefined,
      project_id: form.value.project_id || undefined,
      meeting_time: form.value.meeting_time?.toISOString(),
      participants: form.value.participants.length ? form.value.participants : undefined,
    })
    ElMessage.success('创建成功')
    router.push(`/meetings/${meeting.id}`)
  } finally {
    submitting.value = false
  }
}

onMounted(async () => {
  customers.value = await listCustomers()
})
</script>

<style scoped>
.meeting-create {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-5);
}

.create-form {
  max-width: 600px;
  margin-top: var(--meeting-space-2);
}

.participant-tag {
  margin-right: var(--meeting-space-2);
  margin-bottom: var(--meeting-space-1);
  border-radius: var(--meeting-radius-sm);
}
</style>
