<template>
  <div class="home">
    <div class="welcome-card">
      <h1 class="welcome-title">会议记录工具</h1>
      <p class="welcome-desc">本地私有化会议记录 AI 工具，音频不出境，纪要一键生成。</p>
      <div class="health-row">
        <el-tag v-if="healthy === true" type="success">后端连接正常</el-tag>
        <el-tag v-else-if="healthy === false" type="danger">后端连接失败，请检查服务</el-tag>
        <el-tag v-else type="info">连接检测中...</el-tag>
      </div>
      <div class="quick-actions">
        <el-button type="primary" @click="$router.push('/meetings/create')">新建会议</el-button>
        <el-button @click="$router.push('/meetings')">查看会议列表</el-button>
      </div>
    </div>

    <div class="flow-card">
      <div class="flow-title">使用流程</div>
      <div class="flow-steps">
        <div class="flow-step" v-for="(step, i) in steps" :key="i">
          <span class="step-num">{{ i + 1 }}</span>
          <span class="step-text">{{ step }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { checkHealth } from '@/api/health'

const healthy = ref<boolean | null>(null)

const steps = [
  '配置 LLM（本地 Ollama 或外部服务）',
  '新建会议，上传音频',
  '启动 ASR 识别，查看转写结果',
  '编辑文本，应用术语纠错',
  '选择模板，生成会议纪要',
  '导出 Markdown 或 Word 文档',
]

onMounted(async () => {
  try {
    await checkHealth()
    healthy.value = true
  } catch {
    healthy.value = false
  }
})
</script>

<style scoped>
.home {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-5);
  max-width: 720px;
}

.welcome-card {
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-6);
}

.welcome-title {
  font-size: var(--meeting-font-size-lg);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
  margin: 0 0 var(--meeting-space-2);
}

.welcome-desc {
  font-size: var(--meeting-font-size-base);
  color: var(--meeting-text-secondary);
  margin: 0 0 var(--meeting-space-4);
}

.health-row {
  margin-bottom: var(--meeting-space-4);
}

.quick-actions {
  display: flex;
  gap: var(--meeting-space-3);
}

.flow-card {
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-6);
}

.flow-title {
  font-size: var(--meeting-font-size-md);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
  margin-bottom: var(--meeting-space-4);
}

.flow-steps {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-3);
}

.flow-step {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-3);
}

.step-num {
  width: 24px;
  height: 24px;
  border-radius: 50%;
  background: var(--meeting-color-primary);
  color: var(--meeting-text-on-primary);
  font-size: var(--meeting-font-size-xs);
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.step-text {
  font-size: var(--meeting-font-size-base);
  color: var(--meeting-text-primary);
}
</style>
