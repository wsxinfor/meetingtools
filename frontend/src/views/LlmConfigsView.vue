<template>
  <div class="llm-configs-view">
    <div class="page-header">
      <el-button type="primary" class="btn-new-config" @click="openCreate">新增配置</el-button>
    </div>

    <el-table :data="configs" v-loading="loading" class="config-table">
      <el-table-column label="名称" prop="name" min-width="140" />
      <el-table-column label="类型" width="110">
        <template #default="{ row }">{{ providerLabel(row.provider) }}</template>
      </el-table-column>
      <el-table-column label="模型" prop="model_name" min-width="160" />
      <el-table-column label="地址" prop="base_url" min-width="200" show-overflow-tooltip />
      <el-table-column label="默认" width="70">
        <template #default="{ row }">
          <el-tag v-if="row.is_default" type="success" size="small">默认</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="启用" width="70">
        <template #default="{ row }">
          <el-switch
            :model-value="row.is_enabled"
            @change="(v: boolean) => toggleEnabled(row, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <el-button size="small" link :loading="testingId === row.id" @click="handleTest(row)">
            测试
          </el-button>
          <el-button size="small" link @click="handleSetDefault(row)" :disabled="row.is_default">
            设为默认
          </el-button>
          <el-button size="small" link @click="openEdit(row)">编辑</el-button>
          <el-button size="small" link type="danger" @click="handleDelete(row)">删除</el-button>
        </template>
      </el-table-column>
    </el-table>

    <el-dialog
      v-model="dialogVisible"
      :title="editingConfig ? '编辑LLM配置' : '新增LLM配置'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="form" label-width="90px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="如：本地Ollama" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.provider" style="width: 100%">
            <el-option label="Ollama（本地）" value="ollama" />
            <el-option label="OpenAI兼容（外部）" value="openai_compatible" />
          </el-select>
        </el-form-item>
        <el-form-item label="API地址" required>
          <el-input v-model="form.base_url" placeholder="如：http://localhost:6014/v1" />
        </el-form-item>
        <el-form-item label="API Key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            placeholder="Ollama可填ollama，外部服务填真实Key"
          />
        </el-form-item>
        <el-form-item label="模型名称" required>
          <el-input v-model="form.model_name" placeholder="如：qwen2.5:7b" />
        </el-form-item>
        <el-form-item label="设为默认">
          <el-switch v-model="form.is_default" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listLlmConfigs,
  createLlmConfig,
  updateLlmConfig,
  deleteLlmConfig,
  setDefaultLlmConfig,
  testLlmConfig,
  type LlmConfig,
} from '@/api/llm_configs'

const configs = ref<LlmConfig[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const testingId = ref<string | null>(null)
const editingConfig = ref<LlmConfig | null>(null)

const form = ref({
  name: '',
  provider: 'ollama',
  base_url: '',
  api_key: '',
  model_name: '',
  is_default: false,
})

async function load() {
  loading.value = true
  try {
    configs.value = await listLlmConfigs()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingConfig.value = null
  form.value = { name: '', provider: 'ollama', base_url: '', api_key: '', model_name: '', is_default: false }
  dialogVisible.value = true
}

function openEdit(cfg: LlmConfig) {
  editingConfig.value = cfg
  form.value = {
    name: cfg.name,
    provider: cfg.provider,
    base_url: cfg.base_url,
    api_key: cfg.api_key,
    model_name: cfg.model_name,
    is_default: cfg.is_default,
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.name.trim() || !form.value.base_url.trim() || !form.value.model_name.trim()) {
    ElMessage.warning('名称、API地址和模型名称不能为空')
    return
  }
  saving.value = true
  try {
    if (editingConfig.value) {
      const updated = await updateLlmConfig(editingConfig.value.id, form.value)
      const idx = configs.value.findIndex(c => c.id === updated.id)
      if (idx >= 0) configs.value[idx] = updated
      if (form.value.is_default) {
        configs.value.forEach(c => { if (c.id !== updated.id) c.is_default = false })
      }
    } else {
      const created = await createLlmConfig(form.value)
      configs.value.push(created)
      if (form.value.is_default) {
        configs.value.forEach(c => { if (c.id !== created.id) c.is_default = false })
      }
    }
    dialogVisible.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(cfg: LlmConfig, is_enabled: boolean) {
  try {
    const updated = await updateLlmConfig(cfg.id, { is_enabled })
    const idx = configs.value.findIndex(c => c.id === updated.id)
    if (idx >= 0) configs.value[idx] = updated
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleSetDefault(cfg: LlmConfig) {
  try {
    await setDefaultLlmConfig(cfg.id)
    configs.value.forEach(c => { c.is_default = c.id === cfg.id })
    ElMessage.success('已设为默认')
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleTest(cfg: LlmConfig) {
  testingId.value = cfg.id
  try {
    const result = await testLlmConfig(cfg.id)
    if (result.success) {
      ElMessage.success(`连接成功，延迟 ${result.latency_ms}ms`)
    } else {
      ElMessage.error(`连接失败：${result.error ?? '未知错误'}`)
    }
  } catch {
    ElMessage.error('测试请求失败')
  } finally {
    testingId.value = null
  }
}

async function handleDelete(cfg: LlmConfig) {
  await ElMessageBox.confirm(`确认删除配置「${cfg.name}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  try {
    await deleteLlmConfig(cfg.id)
    configs.value = configs.value.filter(c => c.id !== cfg.id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}

function providerLabel(p: string) {
  return p === 'ollama' ? 'Ollama（本地）' : 'OpenAI兼容（外部）'
}

onMounted(load)
</script>

<style scoped>
.llm-configs-view {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-4);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.btn-new-config {
  border-radius: var(--meeting-radius-md);
  padding: 7px 16px;
  font-weight: var(--meeting-font-weight-medium);
}

.config-table {
  border-radius: var(--meeting-radius-lg);
  overflow: hidden;
}
</style>
