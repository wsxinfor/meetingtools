<template>
  <div class="login-page">
    <div class="login-card">
      <div class="login-title">会议记录工具</div>
      <div class="login-subtitle">请登录以继续</div>

      <el-form ref="formRef" :model="form" :rules="rules" label-position="top" @submit.prevent="submit">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" autocomplete="username" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input
            v-model="form.password"
            type="password"
            placeholder="请输入密码"
            show-password
            autocomplete="current-password"
            @keyup.enter="submit"
          />
        </el-form-item>
        <el-form-item>
          <el-button
            type="primary"
            :loading="loading"
            style="width: 100%"
            @click="submit"
          >
            登录
          </el-button>
        </el-form-item>
      </el-form>

      <div class="login-hint">账号由管理员创建，请联系管理员获取账号。</div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { useAuthStore } from '@/stores/useAuthStore'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)

const form = ref({ username: '', password: '' })

const rules: FormRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function submit() {
  await formRef.value?.validate()
  loading.value = true
  try {
    await authStore.login(form.value.username, form.value.password)
    router.push('/meetings')
  } catch {
    ElMessage.error('用户名或密码错误')
  } finally {
    loading.value = false
  }
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  background: var(--meeting-bg-base);
  display: flex;
  align-items: center;
  justify-content: center;
}

.login-card {
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-6);
  width: 360px;
}

.login-title {
  font-size: var(--meeting-font-size-lg);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
  text-align: center;
  margin-bottom: var(--meeting-space-2);
}

.login-subtitle {
  font-size: var(--meeting-font-size-base);
  color: var(--meeting-text-secondary);
  text-align: center;
  margin-bottom: var(--meeting-space-5);
}

.login-hint {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-tertiary);
  text-align: center;
  margin-top: var(--meeting-space-3);
}
</style>
