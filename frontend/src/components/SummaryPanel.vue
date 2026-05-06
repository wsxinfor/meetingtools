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
          <el-tag v-if="s.is_final" type="success" size="small">已定稿</el-tag>
          <span class="summary-meta">{{ s.llm_model }} · {{ fmtDate(s.created_at) }}</span>
        </div>
      </div>

      <!-- Active summary editor -->
      <template v-if="activeSummary">
        <div class="summary-editor-area">
          <div class="editor-toolbar">
            <span class="section-title">{{ activeSummary.title ?? '纪要内容' }}</span>
            <el-button size="small" @click="handleExport(activeSummary.id, 'md')">
              导出 Markdown
            </el-button>
            <el-button size="small" @click="handleExport(activeSummary.id, 'docx')">
              导出 Word
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
          <el-input
            v-model="editingContent"
            type="textarea"
            :rows="20"
            placeholder="纪要内容（Markdown格式）"
          />
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
import { exportSummary, getDownloadUrl } from '@/api/exports'

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
    const msg = (e as { response?: { data?: { detail?: string } } })?.response?.data?.detail
    ElMessage.error(msg ?? '生成失败，请检查LLM配置')
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
    const url = getDownloadUrl(record.id)
    const a = document.createElement('a')
    a.href = url
    a.download = ''
    a.click()
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
  gap: var(--space-4);
}

.generate-bar {
  display: flex;
  align-items: center;
  gap: var(--space-3);
  padding: var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  flex-wrap: wrap;
}

.summary-list {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.summary-card {
  padding: var(--space-3) var(--space-4);
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 0.15s;
}

.summary-card:hover {
  border-color: var(--color-primary);
}

.summary-card.is-active {
  border-color: var(--color-primary);
  background: #f0f7f4;
}

.summary-card-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
}

.summary-title {
  flex: 1;
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}

.summary-meta {
  font-size: var(--font-size-label);
  color: var(--color-text-secondary);
}

.summary-editor-area {
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
  margin-top: var(--space-1);
}

.editor-toolbar {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  flex-wrap: wrap;
}

.section-title {
  flex: 1;
  font-size: var(--font-size-body);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
}
</style>
