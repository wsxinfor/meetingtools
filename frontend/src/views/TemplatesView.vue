<template>
  <div class="templates-view">
    <div class="page-header">
      <span class="page-title">纪要模板</span>
      <el-button type="primary" @click="openCreate">新增模板</el-button>
    </div>

    <el-table :data="templates" v-loading="loading" border style="width: 100%">
      <el-table-column label="模板名称" prop="name" min-width="160" />
      <el-table-column label="来源" width="90">
        <template #default="{ row }">
          <el-tag v-if="row.owner_id === null" size="small">系统</el-tag>
          <el-tag v-else size="small" type="info">我的</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="类型" prop="type" width="120">
        <template #default="{ row }">{{ typeLabel(row.type) }}</template>
      </el-table-column>
      <el-table-column label="描述" prop="description" min-width="200" show-overflow-tooltip />
      <el-table-column label="状态" width="80">
        <template #default="{ row }">
          <el-switch
            :model-value="row.enabled"
            :disabled="!canEdit(row)"
            @change="(v: boolean) => toggleEnabled(row, v)"
          />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <template v-if="canEdit(row)">
            <el-button size="small" @click="openEdit(row)">编辑</el-button>
            <el-button size="small" type="danger" @click="handleDelete(row)">删除</el-button>
          </template>
          <span v-else class="no-action">—</span>
        </template>
      </el-table-column>
    </el-table>

    <!-- Create / Edit drawer -->
    <el-drawer
      v-model="drawerVisible"
      :title="editingTemplate ? '编辑模板' : '新增模板'"
      size="640px"
      destroy-on-close
    >
      <el-form :model="form" label-width="80px" class="template-form">
        <el-form-item label="模板名称" required>
          <el-input v-model="form.name" placeholder="如：售前交流纪要" />
        </el-form-item>
        <el-form-item label="类型">
          <el-select v-model="form.type" style="width: 100%">
            <el-option label="通用" value="general" />
            <el-option label="售前交流" value="presales" />
            <el-option label="项目推进" value="project" />
            <el-option label="技术方案" value="technical" />
            <el-option label="招投标" value="bidding" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" placeholder="简述此模板的适用场景" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
        <el-form-item label="Prompt" required>
          <div class="prompt-hint">
            使用 <code>&#123;&#123;transcript_text&#125;&#125;</code> 作为转写文本占位符
          </div>
          <el-input
            v-model="form.prompt_text"
            type="textarea"
            :rows="18"
            placeholder="在此输入 Prompt 内容..."
            class="prompt-editor"
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="drawerVisible = false">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">保存</el-button>
      </template>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  listTemplates,
  createTemplate,
  updateTemplate,
  deleteTemplate,
  type Template,
} from '@/api/templates'
import { useAuthStore } from '@/stores/useAuthStore'

const authStore = useAuthStore()

const templates = ref<Template[]>([])
const loading = ref(false)
const drawerVisible = ref(false)
const saving = ref(false)
const editingTemplate = ref<Template | null>(null)

const form = ref({
  name: '',
  type: 'general',
  description: '',
  prompt_text: '',
  enabled: true,
})

async function load() {
  loading.value = true
  try {
    templates.value = await listTemplates()
  } finally {
    loading.value = false
  }
}

function openCreate() {
  editingTemplate.value = null
  form.value = { name: '', type: 'general', description: '', prompt_text: '', enabled: true }
  drawerVisible.value = true
}

function openEdit(t: Template) {
  editingTemplate.value = t
  form.value = {
    name: t.name,
    type: t.type,
    description: t.description ?? '',
    prompt_text: t.prompt_text,
    enabled: t.enabled,
  }
  drawerVisible.value = true
}

async function handleSave() {
  if (!form.value.name.trim() || !form.value.prompt_text.trim()) {
    ElMessage.warning('模板名称和 Prompt 不能为空')
    return
  }
  saving.value = true
  try {
    const payload = {
      ...form.value,
      description: form.value.description.trim() || null,
    }
    if (editingTemplate.value) {
      const updated = await updateTemplate(editingTemplate.value.id, payload)
      const idx = templates.value.findIndex(t => t.id === updated.id)
      if (idx >= 0) templates.value[idx] = updated
    } else {
      const created = await createTemplate(payload)
      templates.value.push(created)
    }
    drawerVisible.value = false
    ElMessage.success('保存成功')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    saving.value = false
  }
}

async function toggleEnabled(t: Template, enabled: boolean) {
  try {
    const updated = await updateTemplate(t.id, { enabled })
    const idx = templates.value.findIndex(item => item.id === updated.id)
    if (idx >= 0) templates.value[idx] = updated
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleDelete(t: Template) {
  await ElMessageBox.confirm(`确认删除模板「${t.name}」？`, '删除确认', {
    type: 'warning',
    confirmButtonText: '删除',
    cancelButtonText: '取消',
  })
  try {
    await deleteTemplate(t.id)
    templates.value = templates.value.filter(item => item.id !== t.id)
    ElMessage.success('已删除')
  } catch {
    ElMessage.error('删除失败')
  }
}

function canEdit(t: Template): boolean {
  if (authStore.isAdmin) return true
  return t.owner_id !== null && t.owner_id === authStore.user?.id
}

function typeLabel(type: string) {
  const map: Record<string, string> = {
    general: '通用',
    presales: '售前交流',
    project: '项目推进',
    technical: '技术方案',
    bidding: '招投标',
    other: '其他',
  }
  return map[type] ?? type
}

onMounted(load)
</script>

<style scoped>
.templates-view {
  padding: var(--space-6);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-5);
}

.page-title {
  font-size: var(--font-size-page-title);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.template-form {
  padding: var(--space-4) 0;
}

.prompt-hint {
  font-size: var(--font-size-label);
  color: var(--color-text-secondary);
  margin-bottom: var(--space-2);
  line-height: var(--line-height-base);
}

.prompt-hint code {
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 1px 4px;
  font-family: var(--font-family-en);
  color: var(--color-accent-brown);
}

.prompt-editor {
  font-family: var(--font-family-en);
  font-size: var(--font-size-label);
}

.no-action {
  color: var(--color-text-placeholder);
  font-size: var(--font-size-label);
}
</style>
