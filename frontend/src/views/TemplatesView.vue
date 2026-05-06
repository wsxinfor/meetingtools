<template>
  <div class="templates-view">
    <div class="page-header">
      <el-button type="primary" class="btn-new-template" @click="openCreate">新增模板</el-button>
    </div>

    <div class="template-grid" v-loading="loading">
      <div
        v-for="t in templates"
        :key="t.id"
        class="template-card"
      >
        <div class="template-card-name">{{ t.name }}</div>
        <div class="template-card-desc">{{ t.description || '无描述' }}</div>
        <div class="template-card-footer">
          <span class="template-card-time">{{ formatDate(t.updated_at) }}</span>
          <div class="template-card-actions">
            <el-switch
              :model-value="t.enabled"
              :disabled="!canEdit(t)"
              size="small"
              @change="(v: boolean) => toggleEnabled(t, v)"
            />
            <template v-if="canEdit(t)">
              <el-button size="small" link @click="openEdit(t)">编辑</el-button>
              <el-button size="small" link type="danger" @click="handleDelete(t)">删除</el-button>
            </template>
          </div>
        </div>
      </div>
    </div>

    <el-empty v-if="!loading && !templates.length" description="暂无模板，点击右上角新增" />

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
            :rows="16"
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

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

onMounted(load)
</script>

<style scoped>
.templates-view {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-4);
}

.page-header {
  display: flex;
  align-items: center;
  justify-content: flex-end;
}

.btn-new-template {
  border-radius: var(--meeting-radius-md);
  padding: 7px 16px;
  font-weight: var(--meeting-font-weight-medium);
}

/* ── 模板卡片网格 ── */
.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: var(--meeting-space-4);
}

.template-card {
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-4) var(--meeting-space-5);
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-2);
  transition: border-color var(--meeting-transition-fast);
}

.template-card:hover {
  border-color: var(--meeting-border-focus);
}

.template-card-name {
  font-size: var(--meeting-font-size-base);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
}

.template-card-desc {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-tertiary);
  line-height: var(--meeting-line-height-base);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-card-footer {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: var(--meeting-space-2);
  padding-top: var(--meeting-space-2);
  border-top: 0.5px solid var(--meeting-border-light);
}

.template-card-time {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-tertiary);
}

.template-card-actions {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-2);
}

/* ── 模板表单 ── */
.template-form {
  padding: var(--meeting-space-4) 0;
}

.prompt-hint {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-secondary);
  margin-bottom: var(--meeting-space-2);
  line-height: var(--meeting-line-height-base);
}

.prompt-hint code {
  background: var(--meeting-bg-subtle);
  border: 0.5px solid var(--meeting-border-light);
  border-radius: var(--meeting-radius-sm);
  padding: 1px 4px;
  font-family: monospace;
  color: var(--meeting-color-accent);
}

.prompt-editor :deep(textarea) {
  font-family: monospace;
  font-size: var(--meeting-font-size-base);
}
</style>
