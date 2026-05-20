<template>
  <div class="summary-panel">
    <!-- Generate bar -->
    <div class="generate-bar">
      <el-select
        v-model="selectedTemplateId"
        placeholder="选择模板"
        style="width: 200px"
        clearable
      >
        <el-option
          v-for="t in templates"
          :key="t.id"
          :label="t.name"
          :value="t.id"
        />
      </el-select>
      <el-select
        v-model="selectedConfigId"
        placeholder="LLM配置（默认）"
        style="width: 200px"
        clearable
      >
        <el-option
          v-for="c in llmConfigs"
          :key="c.id"
          :label="`${c.name}${c.is_default ? '（默认）' : ''}`"
          :value="c.id"
        />
      </el-select>
      <el-button
        type="primary"
        :loading="generating"
        :disabled="!selectedTemplateId"
        @click="handleGenerate"
      >
        生成纪要
      </el-button>
    </div>

    <!-- Generating state -->
    <div v-if="generating" class="generating-state">
      <div class="generating-spinner" />
      <span class="generating-text">正在生成纪要…</span>
    </div>

    <!-- Summary list -->
    <div v-if="summaries.length" class="summary-list">
      <div
        v-for="s in summaries"
        :key="s.id"
        class="summary-card"
        :class="{ 'is-active': activeSummaryId === s.id }"
        @click="activeSummaryId = s.id"
      >
        <div class="summary-card-header">
          <span class="summary-title">{{ s.title ?? '未命名纪要' }}</span>
          <span v-if="s.is_final" :class="['status-badge', 'badge-done']">已定稿</span>
          <span class="summary-meta">{{ s.llm_model }} · {{ fmtDate(s.created_at) }}</span>
        </div>
      </div>

      <!-- Active summary editor -->
      <template v-if="activeSummary">
        <div class="summary-editor-area">
          <div class="summary-content-card">
            <div class="editor-toolbar">
              <span class="section-title">{{ activeSummary.title ?? '纪要内容' }}</span>
              <div class="editor-actions">
                <el-button size="small" type="primary" @click="handleExport(activeSummary.id, 'docx')">
                  下载 Word
                </el-button>
                <el-button size="small" @click="handleExport(activeSummary.id, 'md')">
                  下载 Markdown
                </el-button>
                <el-button
                  size="small"
                  link
                  @click="handleGenerate"
                >
                  重新生成
                </el-button>
                <el-button
                  size="small"
                  :type="activeSummary.is_final ? '' : 'success'"
                  @click="toggleFinal"
                >
                  {{ activeSummary.is_final ? '取消定稿' : '标记定稿' }}
                </el-button>
                <el-button size="small" type="primary" :loading="savingSummary" @click="saveSummaryContent">
                  保存
                </el-button>
              </div>
            </div>
            <el-input
              v-model="editingContent"
              type="textarea"
              :rows="20"
              placeholder="纪要内容（Markdown格式）"
              class="summary-textarea"
            />
          </div>
        </div>
      </template>
    </div>
    <el-empty v-else-if="!generating" description="暂无纪要，选择模板后点击生成" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { listTemplates, type Template } from '@/api/templates'
import { listLlmConfigs, type LlmConfig } from '@/api/llm_configs'
import { generateSummary, listSummaries, updateSummary, type Summary } from '@/api/summaries'
import { exportSummary, downloadExportFile } from '@/api/exports'

const props = defineProps<{ meetingId: string }>()

const templates = ref<Template[]>([])
const llmConfigs = ref<LlmConfig[]>([])
const summaries = ref<Summary[]>([])
const selectedTemplateId = ref<string>('')
const selectedConfigId = ref<string>('')
const generating = ref(false)
const savingSummary = ref(false)
const activeSummaryId = ref<string | null>(null)
const editingContent = ref('')

const activeSummary = computed(() =>
  summaries.value.find(s => s.id === activeSummaryId.value) ?? null,
)

watch(activeSummary, s => {
  editingContent.value = s?.content_md ?? ''
})

async function load() {
  const [tpls, cfgs, sums] = await Promise.all([
    listTemplates(),
    listLlmConfigs(),
    listSummaries(props.meetingId),
  ])
  templates.value = tpls.filter(t => t.enabled)
  llmConfigs.value = cfgs.filter(c => c.is_enabled)
  summaries.value = sums
  if (sums.length && !activeSummaryId.value) activeSummaryId.value = sums[0].id
}

async function handleGenerate() {
  if (!selectedTemplateId.value) return
  generating.value = true
  try {
    const summary = await generateSummary(props.meetingId, {
      template_id: selectedTemplateId.value,
      llm_config_id: selectedConfigId.value || null,
      source: 'corrected_text',
    })
    summaries.value.unshift(summary)
    activeSummaryId.value = summary.id
    ElMessage.success('纪要生成成功')
  } catch (e: unknown) {
    const axiosErr = e as { code?: string; message?: string; response?: { data?: { detail?: string } } }
    let msg: string
    if (axiosErr.code === 'ECONNABORTED' || axiosErr.message?.includes('timeout')) {
      msg = '生成超时，LLM 响应时间较长，请稍后重试'
    } else {
      msg = axiosErr.response?.data?.detail ?? '生成失败，请检查LLM配置'
    }
    ElMessage.error(msg)
  } finally {
    generating.value = false
  }
}

async function saveSummaryContent() {
  if (!activeSummary.value) return
  savingSummary.value = true
  try {
    const updated = await updateSummary(activeSummary.value.id, {
      content_md: editingContent.value,
    })
    const idx = summaries.value.findIndex(s => s.id === updated.id)
    if (idx >= 0) summaries.value[idx] = updated
    ElMessage.success('已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingSummary.value = false
  }
}

async function toggleFinal() {
  if (!activeSummary.value) return
  try {
    const updated = await updateSummary(activeSummary.value.id, {
      is_final: !activeSummary.value.is_final,
    })
    const idx = summaries.value.findIndex(s => s.id === updated.id)
    if (idx >= 0) summaries.value[idx] = updated
  } catch {
    ElMessage.error('操作失败')
  }
}

async function handleExport(summaryId: string, format: 'md' | 'docx') {
  try {
    const record = await exportSummary(summaryId, format)
    const ext = format === 'docx' ? '.docx' : '.md'
    const filename = `${activeSummary.value?.title ?? 'summary'}${ext}`
    await downloadExportFile(record.id, filename)
  } catch {
    ElMessage.error('导出失败')
  }
}

function fmtDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

onMounted(load)
</script>

<style scoped>
.summary-panel {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-4);
}

.generate-bar {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-3);
  padding: var(--meeting-space-4);
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-md);
  flex-wrap: wrap;
}

/* ── 生成中状态 ── */
.generating-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--meeting-space-4);
  padding: var(--meeting-space-10) 0;
}

.generating-spinner {
  width: 32px;
  height: 32px;
  border: 2px solid var(--meeting-color-primary-bg);
  border-top-color: var(--meeting-color-primary);
  border-radius: 50%;
  animation: spin 600ms linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.generating-text {
  font-size: var(--meeting-font-size-base);
  color: var(--meeting-text-secondary);
}

/* ── 纪要列表 ── */
.summary-list {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-3);
}

.summary-card {
  padding: var(--meeting-space-3) var(--meeting-space-4);
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  cursor: pointer;
  transition: border-color var(--meeting-transition-fast),
              background var(--meeting-transition-fast);
}

.summary-card:hover {
  border-color: var(--meeting-border-focus);
  background: var(--meeting-bg-base);
}

.summary-card.is-active {
  border-color: var(--meeting-color-primary);
  background: var(--meeting-color-primary-bg);
}

.summary-card-header {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-2);
}

.summary-title {
  flex: 1;
  font-size: var(--meeting-font-size-base);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
}

.summary-meta {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-tertiary);
}

/* ── 纪要编辑区 ── */
.summary-editor-area {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-3);
  margin-top: var(--meeting-space-1);
}

.summary-content-card {
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-8) var(--meeting-space-10);
  max-width: 780px;
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-2);
  flex-wrap: wrap;
  margin-bottom: var(--meeting-space-4);
}

.editor-actions {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-2);
  margin-left: auto;
}

.section-title {
  font-size: var(--meeting-font-size-md);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
}

.summary-textarea :deep(textarea) {
  font-family: monospace;
  font-size: var(--meeting-font-size-base);
  line-height: var(--meeting-line-height-loose);
}

/* ── 状态徽章 ── */
.status-badge {
  display: inline-block;
  font-size: var(--meeting-font-size-xs);
  font-weight: var(--meeting-font-weight-medium);
  padding: 2px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.badge-done {
  background: var(--meeting-color-success-bg);
  color: var(--meeting-color-success);
  border: 0.5px solid var(--meeting-color-success-border);
}
</style>
