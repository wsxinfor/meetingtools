<template>
  <div class="asr-configs-view">
    <div class="page-header">
      <el-button type="primary" class="btn-new-config" @click="openCreate">新增配置</el-button>
    </div>

    <el-table :data="configs" v-loading="loading" class="config-table">
      <el-table-column label="名称" prop="name" min-width="140" />
      <el-table-column label="类型" width="110">
        <template #default="{ row }">{{ providerLabel(row.provider) }}</template>
      </el-table-column>
      <el-table-column label="地址" prop="base_url" min-width="200" show-overflow-tooltip />
      <el-table-column label="说话人分离" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.enable_diarization" type="success" size="small">开</el-tag>
          <el-tag v-else type="info" size="small">关</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="语气词去除" width="100">
        <template #default="{ row }">
          <el-tag v-if="row.enable_filler_removal" type="success" size="small">开</el-tag>
          <el-tag v-else type="info" size="small">关</el-tag>
        </template>
      </el-table-column>
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
      :title="editingConfig ? '编辑ASR配置' : '新增ASR配置'"
      width="520px"
      destroy-on-close
    >
      <el-form :model="form" label-width="110px">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" placeholder="如：远程ASR服务" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.provider" style="width: 100%">
            <el-option label="本地 FunASR" value="local" />
            <el-option label="远程 ASR 服务" value="remote" />
          </el-select>
        </el-form-item>
        <el-form-item v-if="form.provider === 'remote'" label="API地址" required>
          <el-input v-model="form.base_url" placeholder="如：http://192.168.10.71:18080/api" />
        </el-form-item>
        <el-form-item v-if="form.provider === 'remote'" label="API Key">
          <el-input
            v-model="form.api_key"
            type="password"
            show-password
            placeholder="远程服务的API Key"
          />
        </el-form-item>
        <el-form-item label="说话人分离">
          <el-switch v-model="form.enable_diarization" />
        </el-form-item>
        <el-form-item label="语气词去除">
          <el-switch v-model="form.enable_filler_removal" />
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
  listAsrConfigs,
  createAsrConfig,
  updateAsrConfig,
  deleteAsrConfig,
  setDefaultAsrConfig,
  testAsrConfig,
  type AsrConfig,
} from '@/api/asr_configs'

const configs = ref<AsrConfig[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const saving = ref(false)
const testingId = ref<string | null>(null)
const editingConfig = ref<AsrConfig | null>(null)

const form = ref({
  name: '',
  provider: 'remote',
  base_url: '',
  api_key: '',
  enable_diarization: true,
  enable_filler_removal: true,
  is_default: false,
})

async function load() {
  loading.value = true
  try {
    configs.value = await listAsrConfigs()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingConfig.value = null
  form.value = {
    name: '', provider: 'remote', base_url: '', api_key: '',
    enable_diarization: true, enable_filler_removal: true, is_default: false,
  }
  dialogVisible.value = true
}

function openEdit(cfg: AsrConfig) {
  editingConfig.value = cfg
  form.value = {
    name: cfg.name,
    provider: cfg.provider,
    base_url: cfg.base_url,
    api_key: cfg.api_key,
    enable_diarization: cfg.enable_diarization,
    enable_filler_removal: cfg.enable_filler_removal,
    is_default: cfg.is_default,
  }
  dialogVisible.value = true
}

async function handleSave() {
  if (!form.value.name.trim()) {
    ElMessage.warning('名称不能为空')
    return
  }
  if (form.value.provider === 'remote' && !form.value.base_url.trim()) {
    ElMessage.warning('远程服务必须填写API地址')
    return
  }
  saving.value = true
  try {
    if (editingConfig.value) {
      const updated = await updateAsrConfig(editingConfig.value.id, form.value)
      const idx = configs.value.findIndex(c => c.id === updated.id)
      if (idx >= 0) configs.value[idx] = updated
      if (form.value.is_default) {
        configs.value.forEach(c => { if (c.id !== updated.id) c.is_default = false })
      }
    } else {
      const created = await createAsrConfig(form.value)
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

async function toggleEnabled(cfg: AsrConfig, is_enabled: boolean) {
  try {
    const updated = await updateAsrConfig(cfg.id, { is_enabled })
    const idx = configs.value.findIndex(c => c.id === updated.id)
    if (idx >= 0) configs.value[idx] = updated
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleSetDefault(cfg: AsrConfig) {
  try {
    await setDefaultAsrConfig(cfg.id)
    configs.value.forEach(c => { c.is_default = c.id === cfg.id })
    ElMessage.success('已设为默认')
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleTest(cfg: AsrConfig) {
  testingId.value = cfg.id
  try {
    const result = await testAsrConfig(cfg.id)
    if (result.success) {
      ElMessage.success(result.message ?? '连接成功')
    } else {
      ElMessage.error(`连接失败：${result.error ?? '未知错误'}`)
    }
  } catch {
    ElMessage.error('测试请求失败')
  } finally {
    testingId.value = null
  }
}

async function handleDelete(cfg: AsrConfig) {
  await ElMessageBox.confirm(`确认删除配置「${cfg.name}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  try {
    await deleteAsrConfig(cfg.id)
    configs.value = configs.value.filter(c => c.id !== cfg.id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}

function providerLabel(p: string) {
  return p === 'local' ? '本地 FunASR' : '远程服务'
}

onMounted(load)
</script>

<style scoped>
.asr-configs-view {
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
