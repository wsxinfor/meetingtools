<template>
  <div class="meeting-detail" v-loading="loading">
    <el-page-header @back="$router.push('/meetings')" :content="meeting?.title ?? '会议详情'" />

    <el-tabs v-model="activeTab" class="detail-tabs">
      <!-- Tab 1: 基础信息 -->
      <el-tab-pane label="基础信息" name="info">
        <template v-if="meeting">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="会议标题">
              <template v-if="editing">
                <el-input v-model="editForm.title" />
              </template>
              <template v-else>{{ meeting.title }}</template>
            </el-descriptions-item>

            <el-descriptions-item label="会议类型">
              <template v-if="editing">
                <el-select v-model="editForm.meeting_type" clearable style="width: 100%">
                  <el-option label="售前交流" value="presales" />
                  <el-option label="项目推进" value="project" />
                  <el-option label="技术方案" value="technical" />
                  <el-option label="招投标沟通" value="bidding" />
                  <el-option label="其他" value="other" />
                </el-select>
              </template>
              <template v-else>{{ meeting.meeting_type ?? '-' }}</template>
            </el-descriptions-item>

            <el-descriptions-item label="会议时间">
              <template v-if="editing">
                <el-date-picker v-model="editForm.meeting_time" type="datetime" style="width: 100%" />
              </template>
              <template v-else>
                {{ meeting.meeting_time ? formatDate(meeting.meeting_time) : '-' }}
              </template>
            </el-descriptions-item>

            <el-descriptions-item label="状态">
              <span :class="['status-badge', `badge-${meeting.status}`]">
                {{ statusLabel(meeting.status) }}
              </span>
            </el-descriptions-item>

            <el-descriptions-item label="参会人" :span="2">
              <template v-if="editing">
                <el-tag
                  v-for="(p, i) in editForm.participants"
                  :key="i"
                  closable
                  class="participant-tag"
                  @close="removeEditParticipant(i)"
                >
                  {{ p }}
                </el-tag>
                <el-input
                  v-if="editInputVisible"
                  ref="editInputRef"
                  v-model="editInputValue"
                  size="small"
                  style="width: 120px"
                  @keyup.enter="addEditParticipant"
                  @blur="addEditParticipant"
                />
                <el-button v-else size="small" @click="showEditInput">+ 添加</el-button>
              </template>
              <template v-else>
                <el-tag v-for="(p, i) in meeting.participants" :key="i" class="participant-tag">
                  {{ p }}
                </el-tag>
                <span v-if="!meeting.participants?.length">-</span>
              </template>
            </el-descriptions-item>

            <el-descriptions-item label="创建时间">
              {{ formatDate(meeting.created_at) }}
            </el-descriptions-item>

            <el-descriptions-item label="更新时间">
              {{ formatDate(meeting.updated_at) }}
            </el-descriptions-item>
          </el-descriptions>

          <div class="actions">
            <template v-if="editing">
              <el-button type="primary" :loading="saving" @click="saveEdit">保存</el-button>
              <el-button @click="cancelEdit">取消</el-button>
            </template>
            <template v-else>
              <el-button @click="startEdit">编辑基础信息</el-button>
            </template>
          </div>
        </template>
      </el-tab-pane>

      <!-- Tab 2: 音频 -->
      <el-tab-pane label="音频" name="audio">
        <AudioUploader :meeting-id="meetingId" />
      </el-tab-pane>

      <!-- Tab 3: 转写编辑 -->
      <el-tab-pane label="转写编辑" name="transcript">
        <div v-if="meeting">
          <div class="transcript-export-bar">
            <el-button size="small" @click="exportTranscriptFile('md')">导出 Markdown</el-button>
            <el-button size="small" @click="exportTranscriptFile('docx')">导出 Word</el-button>
          </div>

          <!-- 发言人映射 -->
          <div v-if="speakerLabels.length" class="speaker-map-panel">
            <div class="speaker-map-title">发言人映射</div>
            <div class="speaker-map-hint">
              将识别到的发言人统一关联到参会人，保存后导出文档自动替换
            </div>
            <div class="speaker-map-rows">
              <div v-for="label in speakerLabels" :key="label" class="speaker-map-row">
                <span class="speaker-label-tag">{{ label }}</span>
                <span class="speaker-arrow">→</span>
                <el-select
                  v-model="speakerMapDraft[label]"
                  placeholder="选择参会人"
                  size="small"
                  style="width: 200px"
                  clearable
                  filterable
                  allow-create
                >
                  <el-option
                    v-for="p in (meeting.participants ?? [])"
                    :key="p"
                    :label="p"
                    :value="p"
                  />
                </el-select>
              </div>
            </div>
            <el-button
              type="primary"
              size="small"
              :loading="savingMap"
              @click="saveSpeakerMap"
              style="margin-top: var(--meeting-space-3)"
            >保存映射</el-button>
          </div>

          <TranscriptEditor
            :meeting-id="meetingId"
            :initial-corrected-text="meeting.corrected_text"
            :speaker-map="meeting.speaker_map ?? {}"
            @corrected-text-saved="onCorrectedTextSaved"
            @segments-loaded="onSegmentsLoaded"
          />
        </div>
      </el-tab-pane>

      <!-- Tab 4: 会议纪要 -->
      <el-tab-pane label="会议纪要" name="summary">
        <SummaryPanel v-if="meeting" :meeting-id="meetingId" />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import { getMeeting, updateMeeting, updateSpeakerMap, type MeetingDetail } from '@/api/meetings'
import { exportTranscript, downloadExportFile } from '@/api/exports'
import type { TranscriptSegment } from '@/api/segments'
import AudioUploader from '@/components/AudioUploader.vue'
import TranscriptEditor from '@/components/TranscriptEditor.vue'
import SummaryPanel from '@/components/SummaryPanel.vue'

const route = useRoute()
const meetingId = route.params.id as string
const meeting = ref<MeetingDetail | null>(null)
const loading = ref(false)
const activeTab = ref('info')
const editing = ref(false)
const saving = ref(false)

const editForm = ref({
  title: '',
  meeting_type: '',
  meeting_time: null as Date | null,
  participants: [] as string[],
})

const editInputVisible = ref(false)
const editInputValue = ref('')
const editInputRef = ref<InstanceType<typeof import('element-plus')['ElInput']> | null>(null)

const segments = ref<TranscriptSegment[]>([])
const speakerMapDraft = ref<Record<string, string>>({})
const savingMap = ref(false)

const speakerLabels = computed(() => {
  const labels = new Set<string>()
  for (const seg of segments.value) {
    if (seg.speaker_label) labels.add(seg.speaker_label)
  }
  return [...labels].sort()
})

function onSegmentsLoaded(segs: TranscriptSegment[]) {
  segments.value = segs
  const existing = meeting.value?.speaker_map ?? {}
  const draft: Record<string, string> = {}
  for (const seg of segs) {
    if (seg.speaker_label && !(seg.speaker_label in draft)) {
      draft[seg.speaker_label] = existing[seg.speaker_label] ?? ''
    }
  }
  speakerMapDraft.value = draft
}

async function saveSpeakerMap() {
  savingMap.value = true
  try {
    const updated = await updateSpeakerMap(meetingId, speakerMapDraft.value)
    if (meeting.value) meeting.value.speaker_map = updated.speaker_map
    ElMessage.success('发言人映射已保存')
  } catch {
    ElMessage.error('保存失败')
  } finally {
    savingMap.value = false
  }
}

async function fetchMeeting() {
  loading.value = true
  try {
    meeting.value = await getMeeting(meetingId)
  } finally {
    loading.value = false
  }
}

function startEdit() {
  if (!meeting.value) return
  editForm.value = {
    title: meeting.value.title,
    meeting_type: meeting.value.meeting_type ?? '',
    meeting_time: meeting.value.meeting_time ? new Date(meeting.value.meeting_time) : null,
    participants: [...(meeting.value.participants ?? [])],
  }
  editing.value = true
}

function removeEditParticipant(idx: number) {
  editForm.value.participants.splice(idx, 1)
}

function showEditInput() {
  editInputVisible.value = true
  nextTick(() => editInputRef.value?.focus())
}

function addEditParticipant() {
  const val = editInputValue.value.trim()
  if (val && !editForm.value.participants.includes(val)) {
    editForm.value.participants.push(val)
  }
  editInputVisible.value = false
  editInputValue.value = ''
}

function cancelEdit() {
  editing.value = false
}

async function saveEdit() {
  saving.value = true
  try {
    meeting.value = await updateMeeting(meetingId, {
      title: editForm.value.title,
      meeting_type: editForm.value.meeting_type || undefined,
      meeting_time: editForm.value.meeting_time?.toISOString() ?? null,
      participants: editForm.value.participants,
    })
    editing.value = false
    ElMessage.success('已保存')
  } finally {
    saving.value = false
  }
}

function onCorrectedTextSaved(text: string) {
  if (meeting.value) meeting.value.corrected_text = text
}

async function exportTranscriptFile(format: 'md' | 'docx') {
  try {
    const record = await exportTranscript(meetingId, format)
    const ext = format === 'docx' ? '.docx' : '.md'
    const filename = `${meeting.value?.title ?? 'transcript'}${ext}`
    await downloadExportFile(record.id, filename)
  } catch {
    ElMessage.error('导出失败')
  }
}

function formatDate(d: string) {
  return new Date(d).toLocaleString('zh-CN', { hour12: false })
}

function statusLabel(s: string) {
  const map: Record<string, string> = {
    draft: '草稿', uploaded: '已上传', processing: '处理中', done: '已完成', failed: '失败',
  }
  return map[s] ?? s
}

onMounted(fetchMeeting)
</script>

<style scoped>
.meeting-detail {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-5);
}

.detail-tabs {
  margin-top: var(--meeting-space-2);
}

.actions {
  display: flex;
  gap: var(--meeting-space-2);
  margin-top: var(--meeting-space-4);
}

.transcript-export-bar {
  display: flex;
  gap: var(--meeting-space-2);
  margin-bottom: var(--meeting-space-3);
}

.speaker-map-panel {
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-md);
  padding: var(--meeting-space-4);
  margin-bottom: var(--meeting-space-4);
}

.speaker-map-title {
  font-size: var(--meeting-font-size-base);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
  margin-bottom: var(--meeting-space-1);
}

.speaker-map-hint {
  font-size: var(--meeting-font-size-sm);
  color: var(--meeting-text-tertiary);
  margin-bottom: var(--meeting-space-3);
}

.speaker-map-rows {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-2);
}

.speaker-map-row {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-3);
}

.speaker-label-tag {
  display: inline-block;
  min-width: 60px;
  padding: 2px var(--meeting-space-2);
  background: var(--meeting-color-info-bg);
  color: var(--meeting-color-info);
  border-radius: var(--meeting-radius-sm);
  font-size: var(--meeting-font-size-sm);
  font-weight: var(--meeting-font-weight-medium);
  text-align: center;
}

.speaker-arrow {
  color: var(--meeting-text-tertiary);
  font-size: var(--meeting-font-size-sm);
}

.participant-tag {
  margin-right: 6px;
  border-radius: var(--meeting-radius-sm);
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

.badge-draft,
.badge-uploaded {
  background: var(--meeting-color-info-bg);
  color: var(--meeting-color-info);
  border: 0.5px solid var(--meeting-color-info-border);
}

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
