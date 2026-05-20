<template>
  <div class="transcript-editor">
    <!-- ASR trigger panel -->
    <div class="asr-panel" v-if="audioFiles.length">
      <span class="asr-label">识别音频：</span>
      <el-select v-model="selectedAudioId" style="width: 240px" placeholder="选择音频文件">
        <el-option
          v-for="f in audioFiles"
          :key="f.id"
          :label="`${f.original_filename}（${f.status}）`"
          :value="f.id"
        />
      </el-select>
      <el-select v-model="selectedEngine" style="width: 160px" placeholder="识别引擎">
        <el-option label="本地 FunASR" value="local" />
        <el-option
          v-for="c in asrConfigs"
          :key="c.id"
          :label="c.name"
          :value="c.id"
        />
      </el-select>
      <el-button
        type="primary"
        :loading="asrRunning"
        :disabled="!selectedAudioId"
        @click="startAsr"
      >
        启动识别
      </el-button>
      <el-button :loading="applyingTerms" @click="handleApplyTerms">应用术语纠错</el-button>
      <span v-if="asrTask" :class="['status-badge', `badge-${asrTask.status}`]">
        {{ asrStatusLabel(asrTask.status) }}
        <span v-if="asrTask.status === 'running'"> {{ asrTask.progress }}%</span>
      </span>
    </div>
    <el-empty v-else description="请先上传音频文件" />

    <!-- Segment list -->
    <template v-if="segments.length">
      <div class="segment-toolbar">
        <span class="section-title">转写片段（{{ segments.length }} 段）</span>
        <el-button
          size="small"
          type="primary"
          :loading="savingAll"
          :disabled="dirtyIds.size === 0"
          @click="saveAllDirty"
        >
          保存全部修改（{{ dirtyIds.size }}）
        </el-button>
      </div>

      <div class="segment-list">
        <div
          v-for="seg in segments"
          :key="seg.id"
          class="segment-row"
          :class="{ 'is-editing': editingId === seg.id, 'is-dirty': dirtyIds.has(seg.id) }"
        >
          <div class="seg-meta">
            <span class="seg-time">{{ fmtMs(seg.start_ms) }}–{{ fmtMs(seg.end_ms) }}</span>
            <span v-if="resolvedSpeaker(seg)" class="seg-speaker-badge">
              {{ resolvedSpeaker(seg) }}
            </span>
          </div>
          <el-input
            v-model="seg._text"
            type="textarea"
            :autosize="{ minRows: 1, maxRows: 5 }"
            placeholder="暂无转写文本"
            class="seg-text"
            @focus="editingId = seg.id"
            @blur="editingId = null"
            @input="markDirty(seg)"
          />
        </div>
      </div>

      <!-- Merge & corrected text -->
      <div class="corrected-panel">
        <div class="corrected-toolbar">
          <span class="section-title">完整转写文本</span>
          <el-button size="small" @click="mergeSegments">从片段生成</el-button>
          <el-button size="small" type="primary" :loading="savingText" @click="saveCorrected">
            保存
          </el-button>
        </div>
        <el-input
          v-model="correctedText"
          type="textarea"
          :rows="8"
          placeholder="转写完整文本将显示在此处，也可直接编辑"
        />
      </div>
    </template>
    <el-empty v-else-if="audioFiles.length && !loading" description="暂无转写片段，请先启动识别" />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { listAudioFiles, type AudioFile } from '@/api/audio'
import { listSegments, updateSegment, saveCorrectedText, type TranscriptSegment } from '@/api/segments'
import { startAsrTask, getAsrTask, type AsrTask } from '@/api/asr'
import { listAsrConfigs, type AsrConfig } from '@/api/asr_configs'
import { applyTerms } from '@/api/terms'

const props = defineProps<{
  meetingId: string
  initialCorrectedText?: string | null
  speakerMap?: Record<string, string>
}>()
const emit = defineEmits<{
  (e: 'corrected-text-saved', text: string): void
  (e: 'segments-loaded', segments: TranscriptSegment[]): void
}>()

type EditableSeg = TranscriptSegment & { _text: string }

const loading = ref(false)
const audioFiles = ref<AudioFile[]>([])
const segments = ref<EditableSeg[]>([])
const correctedText = ref(props.initialCorrectedText ?? '')
const selectedAudioId = ref<string>('')
const selectedEngine = ref<string>('local')
const asrConfigs = ref<AsrConfig[]>([])
const editingId = ref<string | null>(null)
const dirtyIds = ref(new Set<string>())
const savingAll = ref(false)
const savingText = ref(false)
const asrTask = ref<AsrTask | null>(null)
const asrRunning = ref(false)
const applyingTerms = ref(false)
let pollTimer: ReturnType<typeof setTimeout> | null = null

function toEditable(s: TranscriptSegment): EditableSeg {
  return { ...s, _text: s.corrected_text ?? s.raw_text ?? '' }
}

function resolvedSpeaker(seg: EditableSeg): string {
  if (!seg.speaker_label) return ''
  return props.speakerMap?.[seg.speaker_label] || seg.speaker_label
}

async function load() {
  loading.value = true
  try {
    const [files, segs, cfgs] = await Promise.all([
      listAudioFiles(props.meetingId),
      listSegments(props.meetingId),
      listAsrConfigs().catch(() => [] as AsrConfig[]),
    ])
    audioFiles.value = files
    segments.value = segs.map(toEditable)
    asrConfigs.value = cfgs.filter(c => c.is_enabled && c.provider === 'remote')
    emit('segments-loaded', segs)
    if (files.length && !selectedAudioId.value) selectedAudioId.value = files[0].id
  } finally {
    loading.value = false
  }
}

function markDirty(seg: EditableSeg) {
  dirtyIds.value = new Set(dirtyIds.value).add(seg.id)
}

async function saveAllDirty() {
  const dirty = segments.value.filter(s => dirtyIds.value.has(s.id))
  if (!dirty.length) return
  savingAll.value = true
  let failed = 0
  await Promise.all(
    dirty.map(async (seg) => {
      try {
        const updated = await updateSegment(seg.id, { corrected_text: seg._text || null })
        Object.assign(seg, toEditable(updated))
        const next = new Set(dirtyIds.value)
        next.delete(seg.id)
        dirtyIds.value = next
      } catch {
        failed++
      }
    }),
  )
  savingAll.value = false
  if (failed) {
    ElMessage.error(`${failed} 个片段保存失败`)
  } else {
    ElMessage.success(`已保存 ${dirty.length} 个修改`)
  }
}

function mergeSegments() {
  correctedText.value = segments.value
    .map(s => {
      const text = s._text.trim()
      if (!text) return ''
      const speaker = resolvedSpeaker(s)
      return speaker
        ? `[${fmtMs(s.start_ms)}-${fmtMs(s.end_ms)} ${speaker}] ${text}`
        : `[${fmtMs(s.start_ms)}-${fmtMs(s.end_ms)}] ${text}`
    })
    .filter(Boolean)
    .join('\n')
}

async function saveCorrected() {
  savingText.value = true
  try {
    await saveCorrectedText(props.meetingId, correctedText.value)
    emit('corrected-text-saved', correctedText.value)
    ElMessage.success('完整文本已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingText.value = false
  }
}

async function handleApplyTerms() {
  applyingTerms.value = true
  try {
    const result = await applyTerms(props.meetingId)
    correctedText.value = result.corrected_text
    emit('corrected-text-saved', result.corrected_text)
    await load()
    ElMessage.success(`已完成纠错，更新 ${result.segments_updated} 个片段`)
  } catch {
    ElMessage.error('术语纠错失败')
  } finally {
    applyingTerms.value = false
  }
}

async function startAsr() {
  if (!selectedAudioId.value) return
  asrRunning.value = true
  try {
    const isRemote = selectedEngine.value !== 'local'
    asrTask.value = await startAsrTask(
      props.meetingId,
      selectedAudioId.value,
      isRemote ? 'remote' : 'local',
      isRemote ? selectedEngine.value : undefined,
    )
    pollAsrStatus()
  } catch {
    ElMessage.error('启动识别失败')
    asrRunning.value = false
  }
}

function pollAsrStatus() {
  if (pollTimer) clearTimeout(pollTimer)
  pollTimer = setTimeout(async () => {
    if (!asrTask.value) return
    try {
      asrTask.value = await getAsrTask(asrTask.value.id)
    } catch { /* ignore */ }
    if (asrTask.value?.status === 'running' || asrTask.value?.status === 'pending') {
      pollAsrStatus()
    } else {
      asrRunning.value = false
      if (asrTask.value?.status === 'done') {
        ElMessage.success('识别完成')
        await load()
      } else if (asrTask.value?.status === 'failed') {
        ElMessage.error(`识别失败：${asrTask.value.error_message ?? '未知错误'}`)
      }
    }
  }, 2000)
}

function asrStatusLabel(s: string) {
  const map: Record<string, string> = { pending: '排队中', running: '识别中', done: '已完成', failed: '失败' }
  return map[s] ?? s
}

function fmtMs(ms: number): string {
  const s = Math.floor(ms / 1000)
  const m = Math.floor(s / 60)
  const ss = s % 60
  return `${String(m).padStart(2, '0')}:${String(ss).padStart(2, '0')}`
}

watch(() => props.initialCorrectedText, (v) => { correctedText.value = v ?? '' })

onMounted(load)
</script>

<style scoped>
.transcript-editor {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-5);
}

.asr-panel {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-3);
  padding: var(--meeting-space-4);
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-md);
}

.asr-label {
  color: var(--meeting-text-secondary);
  font-size: var(--meeting-font-size-sm);
  white-space: nowrap;
}

.segment-toolbar {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-3);
}

.segment-list {
  display: flex;
  flex-direction: column;
}

.segment-row {
  display: flex;
  gap: var(--meeting-space-3);
  align-items: flex-start;
  padding: var(--meeting-space-4);
  padding-bottom: var(--meeting-space-4);
  border-bottom: 0.5px solid var(--meeting-border-light);
  transition: background var(--meeting-transition-fast),
              border-color var(--meeting-transition-fast);
}

.segment-row:last-child {
  border-bottom: none;
}

.segment-row.is-editing {
  border: 0.5px solid var(--meeting-color-primary);
  background: var(--meeting-bg-base);
  border-radius: var(--meeting-radius-md);
}

.segment-row.is-dirty {
  border-color: var(--meeting-color-warning-border);
}

.seg-meta {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-1);
  min-width: 88px;
  flex-shrink: 0;
  padding-top: 4px;
}

.seg-time {
  font-size: var(--meeting-font-size-xs);
  color: var(--meeting-text-tertiary);
  font-family: monospace;
  white-space: nowrap;
}

.seg-speaker-badge {
  display: inline-block;
  padding: 1px var(--meeting-space-2);
  background: var(--meeting-color-info-bg);
  color: var(--meeting-color-info);
  border-radius: var(--meeting-radius-sm);
  font-size: var(--meeting-font-size-sm);
  font-weight: var(--meeting-font-weight-medium);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 88px;
}

.seg-text {
  flex: 1;
}

.corrected-panel {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-3);
}

.corrected-toolbar {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-3);
}

.section-title {
  font-size: var(--meeting-font-size-base);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
  flex: 1;
}

/* ── ASR 状态徽章 ── */
.status-badge {
  display: inline-block;
  font-size: var(--meeting-font-size-xs);
  font-weight: var(--meeting-font-weight-medium);
  padding: 2px 8px;
  border-radius: 999px;
  white-space: nowrap;
}

.badge-pending,
.badge-uploaded {
  background: var(--meeting-color-info-bg);
  color: var(--meeting-color-info);
  border: 0.5px solid var(--meeting-color-info-border);
}

.badge-running,
.badge-processing {
  background: var(--meeting-color-warning-bg);
  color: var(--meeting-color-warning);
  border: 0.5px solid var(--meeting-color-warning-border);
}

.badge-done {
  background: var(--meeting-color-success-bg);
  color: var(--meeting-color-success);
  border: 0.5px solid var(--meeting-color-success-border);
}

.badge-failed {
  background: var(--meeting-color-danger-bg);
  color: var(--meeting-color-danger-dark);
  border: 0.5px solid var(--meeting-color-danger-border);
}
</style>
