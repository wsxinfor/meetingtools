<template>
  <div class="record-page">
    <!-- 步骤条 -->
    <div class="step-bar">
      <div
        v-for="(step, idx) in steps"
        :key="idx"
        class="step-item"
        :class="stepClass(idx)"
      >
        <span class="step-icon">{{ stepIcon(idx) }}</span>
        <span class="step-label">{{ step.label }}</span>
      </div>
    </div>

    <div class="record-card">

      <!-- ── 就绪 / 申请权限 ── -->
      <template v-if="isIdlePhase">
        <div class="mic-stage">
          <button
            class="mic-btn mic-btn--idle"
            :class="{ 'is-requesting': store.state === 'requesting' }"
            :disabled="store.state === 'requesting'"
            @click="store.startRecording()"
          >
            <span class="mic-dot" />
          </button>
          <p class="mic-hint">
            {{ store.state === 'requesting' ? '正在获取麦克风权限…' : '点击开始录音' }}
          </p>
        </div>

        <div class="pre-select">
          <div class="field-label">关联会议（可选）</div>
          <el-radio-group v-model="saveMode" class="mode-radios">
            <el-radio value="existing">已有会议</el-radio>
            <el-radio value="new">新建会议</el-radio>
          </el-radio-group>
          <el-select
            v-if="saveMode === 'existing'"
            v-model="selectedMeetingId"
            placeholder="请选择会议"
            filterable
            clearable
            style="width: 100%"
            :loading="loadingMeetings"
          >
            <el-option v-for="m in meetings" :key="m.id" :label="m.title" :value="m.id" />
          </el-select>
          <template v-else>
            <el-input v-model="newTitle" placeholder="请输入会议标题" />
            <div class="field-label">参会人</div>
            <div class="participant-input">
              <el-tag
                v-for="(p, i) in newParticipants"
                :key="i"
                closable
                @close="removeParticipant(i)"
                class="participant-tag"
              >{{ p }}</el-tag>
              <el-input
                v-if="partInputVisible"
                ref="partInputRef"
                v-model="partInputValue"
                size="small"
                style="width: 120px"
                @keyup.enter="addParticipant"
                @blur="addParticipant"
              />
              <el-button v-else size="small" @click="showPartInput">+ 添加</el-button>
            </div>
          </template>
        </div>
      </template>

      <!-- ── 录音中 / 已暂停 ── -->
      <template v-else-if="isActivePhase">
        <div class="timer" :class="{ 'is-paused': store.state === 'paused' }">
          {{ formattedDuration }}
        </div>

        <div class="rec-status-label">
          {{ store.state === 'paused' ? '已暂停' : '录音中' }}
        </div>

        <div class="waveform" :class="{ 'is-running': store.state === 'recording' }">
          <span v-for="i in 16" :key="i" :class="`wave-bar bar-${i}`" />
        </div>

        <button class="mic-btn mic-btn--recording recording-active" @click="store.stopRecording()">
          <svg viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
            <rect x="6" y="6" width="12" height="12" rx="2"/>
          </svg>
        </button>

        <div class="rec-controls">
          <button
            v-if="store.state === 'recording'"
            class="ctrl-btn"
            @click="store.pauseRecording()"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
              <rect x="5" y="4" width="4" height="16" rx="1"/>
              <rect x="15" y="4" width="4" height="16" rx="1"/>
            </svg>
            暂停
          </button>
          <button
            v-else
            class="ctrl-btn resume"
            @click="store.resumeRecording()"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="14" height="14">
              <path d="M8 5v14l11-7z"/>
            </svg>
            继续
          </button>
          <button class="ctrl-btn cancel" @click="store.resetRecorder()">
            取消录音
          </button>
        </div>
      </template>

      <!-- ── 已录制，等待保存 ── -->
      <template v-else-if="store.state === 'stopped'">
        <div class="done-header">
          <span class="done-check">✓</span>
          <span class="done-meta">录音完成 · {{ formattedDuration }} · {{ fileSize }}</span>
        </div>

        <audio
          v-if="store.blobUrl"
          :src="store.blobUrl"
          controls
          preload="metadata"
          class="audio-player"
        />

        <div class="save-section">
          <div class="field-label">保存方式</div>
          <el-radio-group v-model="saveMode" class="mode-radios">
            <el-radio value="existing">关联到已有会议</el-radio>
            <el-radio value="new">新建会议</el-radio>
          </el-radio-group>
          <el-select
            v-if="saveMode === 'existing'"
            v-model="selectedMeetingId"
            placeholder="请选择会议"
            filterable
            clearable
            style="width: 100%"
            :loading="loadingMeetings"
          >
            <el-option v-for="m in meetings" :key="m.id" :label="m.title" :value="m.id" />
          </el-select>
          <template v-else>
            <el-input v-model="newTitle" placeholder="请输入会议标题" />
            <div class="field-label">参会人</div>
            <div class="participant-input">
              <el-tag
                v-for="(p, i) in newParticipants"
                :key="i"
                closable
                @close="removeParticipant(i)"
                class="participant-tag"
              >{{ p }}</el-tag>
              <el-input
                v-if="partInputVisible"
                ref="partInputRef"
                v-model="partInputValue"
                size="small"
                style="width: 120px"
                @keyup.enter="addParticipant"
                @blur="addParticipant"
              />
              <el-button v-else size="small" @click="showPartInput">+ 添加</el-button>
            </div>
          </template>
        </div>

        <div class="save-actions">
          <el-button
            type="primary"
            :loading="uploading"
            :disabled="!canUpload"
            @click="upload"
          >
            上传保存
          </el-button>
          <el-button @click="store.downloadRecording()">
            下载到本地
          </el-button>
          <el-button @click="store.resetRecorder()">
            重新录制
          </el-button>
        </div>
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useRecorderStore } from '@/stores/useRecorderStore'
import { listMeetings, createMeeting, type Meeting } from '@/api/meetings'
import { uploadAudio } from '@/api/audio'

const store = useRecorderStore()
const router = useRouter()

const saveMode = ref<'existing' | 'new'>('existing')
const selectedMeetingId = ref('')
const newTitle = ref('')
const meetings = ref<Meeting[]>([])
const loadingMeetings = ref(false)
const uploading = ref(false)
const newParticipants = ref<string[]>([])
const partInputVisible = ref(false)
const partInputValue = ref('')
const partInputRef = ref<HTMLInputElement>()

const steps = [
  { label: '录音' },
  { label: '转录' },
  { label: '选模板' },
  { label: '生成报告' },
]

const currentStep = computed(() => {
  if (isIdlePhase.value) return 0
  if (isActivePhase.value) return 0
  return 1
})

function stepClass(idx: number) {
  if (idx < currentStep.value) return 'step-done'
  if (idx === currentStep.value) return 'step-active'
  return 'step-pending'
}

function stepIcon(idx: number) {
  if (idx < currentStep.value) return '✓'
  return String(idx + 1)
}

const isIdlePhase = computed(() =>
  store.state === 'idle' || store.state === 'requesting'
)
const isActivePhase = computed(() =>
  store.state === 'recording' || store.state === 'paused'
)

const formattedDuration = computed(() => {
  const t = store.durationSec
  const h = Math.floor(t / 3600)
  const m = Math.floor((t % 3600) / 60)
  const s = t % 60
  const mm = String(m).padStart(2, '0')
  const ss = String(s).padStart(2, '0')
  return h > 0 ? `${String(h).padStart(2, '0')}:${mm}:${ss}` : `${mm}:${ss}`
})

const fileSize = computed(() => {
  if (!store.blob) return ''
  const b = store.blob.size
  return b < 1024 * 1024
    ? `${(b / 1024).toFixed(1)} KB`
    : `${(b / 1024 / 1024).toFixed(1)} MB`
})

const canUpload = computed(() =>
  saveMode.value === 'existing' ? !!selectedMeetingId.value : newTitle.value.trim().length > 0
)

function removeParticipant(i: number) {
  newParticipants.value.splice(i, 1)
}

function showPartInput() {
  partInputVisible.value = true
  nextTick(() => partInputRef.value?.focus())
}

function addParticipant() {
  const v = partInputValue.value.trim()
  if (v && !newParticipants.value.includes(v)) {
    newParticipants.value.push(v)
  }
  partInputVisible.value = false
  partInputValue.value = ''
}

async function fetchMeetings() {
  loadingMeetings.value = true
  try {
    const res = await listMeetings({ page: 1, page_size: 100 })
    meetings.value = res.items
  } finally {
    loadingMeetings.value = false
  }
}

async function upload() {
  if (!store.blob || !canUpload.value) return
  uploading.value = true
  try {
    let meetingId = selectedMeetingId.value
    if (saveMode.value === 'new') {
      const created = await createMeeting({
        title: newTitle.value.trim(),
        participants: newParticipants.value.length ? newParticipants.value : undefined,
      })
      meetingId = created.id
    }
    const ext = store.blob.type.includes('ogg') ? 'ogg' : 'webm'
    const file = new File([store.blob], `recording.${ext}`, { type: store.blob.type })
    await uploadAudio(meetingId, file)
    ElMessage.success('录音已上传')
    newParticipants.value = []
    store.resetRecorder()
    router.push(`/meetings/${meetingId}`)
  } catch {
    ElMessage.error('上传失败，请重试')
  } finally {
    uploading.value = false
  }
}

onMounted(fetchMeetings)
</script>

<style scoped>
/* ── 页面容器 ── */
.record-page {
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-6);
  min-height: 100%;
}

/* ── 步骤条 ── */
.step-bar {
  display: flex;
  gap: var(--meeting-space-2);
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-light);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-3) var(--meeting-space-4);
}

.step-item {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-2);
  padding: var(--meeting-space-2) var(--meeting-space-3);
  border-radius: var(--meeting-radius-md);
  font-size: var(--meeting-font-size-sm);
  flex: 1;
  justify-content: center;
}

.step-done {
  background: var(--meeting-color-success-bg);
  color: var(--meeting-color-success);
  font-weight: var(--meeting-font-weight-medium);
}

.step-active {
  background: var(--meeting-color-primary-bg);
  color: var(--meeting-color-primary);
  font-weight: var(--meeting-font-weight-medium);
}

.step-pending {
  background: var(--meeting-bg-subtle);
  color: var(--meeting-text-tertiary);
}

.step-icon {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 18px;
  height: 18px;
  border-radius: 50%;
  font-size: var(--meeting-font-size-xs);
  line-height: 1;
}

.step-done .step-icon {
  background: var(--meeting-color-success);
  color: var(--meeting-bg-surface);
}

.step-active .step-icon {
  background: var(--meeting-color-primary);
  color: var(--meeting-text-on-primary);
}

/* ── 主卡片 ── */
.record-card {
  width: 100%;
  max-width: 520px;
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-lg);
  padding: var(--meeting-space-6);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--meeting-space-5);
  align-self: center;
}

/* ── 麦克风区 ── */
.mic-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--meeting-space-4);
  padding: var(--meeting-space-8) 0 var(--meeting-space-4);
}

/* 录音按钮 — 待录音态 */
.mic-btn {
  width: 52px;
  height: 52px;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
  border: 2px solid var(--meeting-color-danger);
  background: transparent;
  transition: background var(--meeting-transition-base),
              transform var(--meeting-transition-fast);
}

.mic-btn--idle {
  border: 2px solid var(--meeting-color-danger);
  background: transparent;
}

.mic-btn--idle:hover:not(:disabled) {
  background: var(--meeting-color-danger-bg);
  transform: translateY(-1px);
}

.mic-btn--idle:active:not(:disabled) {
  transform: translateY(0);
}

.mic-btn--idle.is-requesting {
  opacity: 0.6;
  cursor: not-allowed;
}

.mic-dot {
  width: 16px;
  height: 16px;
  border-radius: 50%;
  background: var(--meeting-color-danger);
}

/* 录音按钮 — 录音中态 */
.mic-btn--recording {
  background: var(--meeting-color-danger);
  border-color: var(--meeting-color-danger);
  color: var(--meeting-text-on-primary);
}

.mic-btn--recording:hover {
  background: var(--meeting-color-danger-dark);
  transform: translateY(-1px);
}

.mic-btn--recording:active {
  transform: translateY(0);
}

.mic-hint {
  font-size: var(--meeting-font-size-base);
  color: var(--meeting-text-secondary);
  margin: 0;
}

/* ── 录音中：计时器 ── */
.timer {
  font-size: var(--meeting-font-size-2xl);
  font-variant-numeric: tabular-nums;
  letter-spacing: 2px;
  color: var(--meeting-text-primary);
  font-weight: var(--meeting-font-weight-medium);
  line-height: 1;
}

.timer.is-paused {
  color: var(--meeting-text-tertiary);
}

.rec-status-label {
  font-size: var(--meeting-font-size-xs);
  color: var(--meeting-text-tertiary);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-top: calc(var(--meeting-space-2) * -1);
}

/* ── 波形 — 16 bars ── */
.waveform {
  display: flex;
  align-items: center;
  gap: 3px;
  height: 36px;
}

.wave-bar {
  display: inline-block;
  width: 3px;
  border-radius: 2px;
  background: var(--meeting-color-primary-light);
  height: 6px;
  transform-origin: center;
  animation-play-state: paused;
  animation-fill-mode: both;
  animation-timing-function: ease-in-out;
  animation-iteration-count: infinite;
}

.waveform.is-running .wave-bar {
  animation-play-state: running;
}

/* 16 bars with staggered delays (0–0.7s) and heights 6–28px */
.bar-1  { animation-name: wbar1;  animation-duration: 0.80s; animation-delay: 0.00s; }
.bar-2  { animation-name: wbar2;  animation-duration: 0.75s; animation-delay: 0.05s; }
.bar-3  { animation-name: wbar3;  animation-duration: 0.85s; animation-delay: 0.10s; }
.bar-4  { animation-name: wbar4;  animation-duration: 0.70s; animation-delay: 0.15s; }
.bar-5  { animation-name: wbar5;  animation-duration: 0.80s; animation-delay: 0.20s; }
.bar-6  { animation-name: wbar6;  animation-duration: 0.75s; animation-delay: 0.25s; }
.bar-7  { animation-name: wbar7;  animation-duration: 0.85s; animation-delay: 0.30s; }
.bar-8  { animation-name: wbar8;  animation-duration: 0.70s; animation-delay: 0.35s; }
.bar-9  { animation-name: wbar9;  animation-duration: 0.80s; animation-delay: 0.40s; }
.bar-10 { animation-name: wbar10; animation-duration: 0.75s; animation-delay: 0.45s; }
.bar-11 { animation-name: wbar11; animation-duration: 0.85s; animation-delay: 0.50s; }
.bar-12 { animation-name: wbar12; animation-duration: 0.70s; animation-delay: 0.55s; }
.bar-13 { animation-name: wbar13; animation-duration: 0.80s; animation-delay: 0.60s; }
.bar-14 { animation-name: wbar14; animation-duration: 0.75s; animation-delay: 0.65s; }
.bar-15 { animation-name: wbar15; animation-duration: 0.85s; animation-delay: 0.68s; }
.bar-16 { animation-name: wbar16; animation-duration: 0.70s; animation-delay: 0.70s; }

@keyframes wbar1  { 0%,100% { height: 8px  } 50% { height: 26px } }
@keyframes wbar2  { 0%,100% { height: 12px } 50% { height: 28px } }
@keyframes wbar3  { 0%,100% { height: 6px  } 50% { height: 22px } }
@keyframes wbar4  { 0%,100% { height: 10px } 50% { height: 28px } }
@keyframes wbar5  { 0%,100% { height: 8px  } 50% { height: 18px } }
@keyframes wbar6  { 0%,100% { height: 14px } 50% { height: 26px } }
@keyframes wbar7  { 0%,100% { height: 6px  } 50% { height: 24px } }
@keyframes wbar8  { 0%,100% { height: 10px } 50% { height: 28px } }
@keyframes wbar9  { 0%,100% { height: 8px  } 50% { height: 20px } }
@keyframes wbar10 { 0%,100% { height: 12px } 50% { height: 26px } }
@keyframes wbar11 { 0%,100% { height: 6px  } 50% { height: 22px } }
@keyframes wbar12 { 0%,100% { height: 10px } 50% { height: 28px } }
@keyframes wbar13 { 0%,100% { height: 8px  } 50% { height: 18px } }
@keyframes wbar14 { 0%,100% { height: 14px } 50% { height: 24px } }
@keyframes wbar15 { 0%,100% { height: 6px  } 50% { height: 20px } }
@keyframes wbar16 { 0%,100% { height: 10px } 50% { height: 26px } }

/* ── 录音辅助控制 ── */
.rec-controls {
  display: flex;
  gap: var(--meeting-space-4);
}

.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--meeting-space-1);
  background: none;
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-sm);
  padding: var(--meeting-space-2) var(--meeting-space-4);
  font-size: var(--meeting-font-size-base);
  font-family: inherit;
  color: var(--meeting-text-secondary);
  cursor: pointer;
  transition: background var(--meeting-transition-fast),
              color var(--meeting-transition-fast);
}

.ctrl-btn:hover {
  background: var(--meeting-bg-base);
  color: var(--meeting-text-primary);
}

.ctrl-btn.resume {
  color: var(--meeting-color-primary);
  border-color: var(--meeting-color-primary);
}

.ctrl-btn.resume:hover {
  background: var(--meeting-color-primary-bg);
}

.ctrl-btn.cancel:hover {
  color: var(--meeting-color-danger);
  border-color: var(--meeting-color-danger);
}

/* ── 录前：会议预选 ── */
.pre-select {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-3);
}

.field-label {
  font-size: var(--meeting-font-size-xs);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-tertiary);
  text-transform: uppercase;
  letter-spacing: 0.06em;
}

.mode-radios {
  display: flex;
  gap: var(--meeting-space-4);
}

/* ── 录制完成 ── */
.done-header {
  display: flex;
  align-items: center;
  gap: var(--meeting-space-2);
  width: 100%;
  padding: var(--meeting-space-3) var(--meeting-space-4);
  background: var(--meeting-color-success-bg);
  border: 0.5px solid var(--meeting-color-success-border);
  border-radius: var(--meeting-radius-md);
}

.done-check {
  color: var(--meeting-color-success);
  font-size: var(--meeting-font-size-lg);
}

.done-meta {
  font-size: var(--meeting-font-size-base);
  color: var(--meeting-text-secondary);
}

.audio-player {
  width: 100%;
  height: 40px;
  outline: none;
}

/* ── 保存区 ── */
.save-section {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--meeting-space-3);
  padding-top: var(--meeting-space-3);
  border-top: 0.5px solid var(--meeting-border-light);
}

.save-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--meeting-space-3);
  width: 100%;
}

.participant-input {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  gap: var(--meeting-space-1);
}

.participant-tag {
  margin-right: var(--meeting-space-1);
  margin-bottom: var(--meeting-space-1);
  border-radius: var(--meeting-radius-sm);
}
</style>
