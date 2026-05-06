<template>
  <div class="record-page">
    <div class="record-card">

      <!-- ── 就绪 / 申请权限 ── -->
      <template v-if="isIdlePhase">
        <h2 class="card-title">开始录音</h2>

        <div class="pre-select">
          <div class="field-label">关联会议（可选，录音结束后也可更改）</div>
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
          <el-input v-else v-model="newTitle" placeholder="请输入会议标题" />
        </div>

        <div class="mic-stage">
          <button
            class="mic-btn"
            :class="{ 'is-requesting': store.state === 'requesting' }"
            :disabled="store.state === 'requesting'"
            @click="store.startRecording()"
          >
            <svg viewBox="0 0 24 24" fill="currentColor" width="40" height="40">
              <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm6.5 9a1 1 0 0 1 1 1 7.5 7.5 0 0 1-6.5 7.43V20h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-1.57A7.5 7.5 0 0 1 4.5 11a1 1 0 1 1 2 0 5.5 5.5 0 0 0 11 0 1 1 0 0 1 1-1z"/>
            </svg>
          </button>
          <p class="mic-hint">
            {{ store.state === 'requesting' ? '正在获取麦克风权限…' : '点击开始录音' }}
          </p>
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
          <span v-for="i in 7" :key="i" :class="`wave-bar bar-${i}`" />
        </div>

        <button class="stop-btn" @click="store.stopRecording()">
          <svg viewBox="0 0 24 24" fill="currentColor" width="36" height="36">
            <rect x="4" y="4" width="16" height="16" rx="3"/>
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
          <span class="done-meta">录音完成 &nbsp;·&nbsp; {{ formattedDuration }} &nbsp;·&nbsp; {{ fileSize }}</span>
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
          <el-input v-else v-model="newTitle" placeholder="请输入会议标题" />
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
import { ref, computed, onMounted } from 'vue'
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
      const created = await createMeeting({ title: newTitle.value.trim() })
      meetingId = created.id
    }
    const ext = store.blob.type.includes('ogg') ? 'ogg' : 'webm'
    const file = new File([store.blob], `recording.${ext}`, { type: store.blob.type })
    await uploadAudio(meetingId, file)
    ElMessage.success('录音已上传')
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
  justify-content: center;
  padding: var(--space-6);
  min-height: 100%;
}

/* ── 主卡片 ── */
.record-card {
  width: 100%;
  max-width: 520px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-xl);
  padding: var(--space-6);
  box-shadow: var(--shadow-card);
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-5);
  align-self: flex-start;
  margin-top: var(--space-6);
}

.card-title {
  align-self: flex-start;
  font-size: var(--font-size-section-title);
  font-weight: var(--font-weight-medium);
  color: var(--color-text-primary);
  margin: 0;
}

/* ── 录前：会议预选 ── */
.pre-select {
  width: 100%;
  display: flex;
  flex-direction: column;
  gap: var(--space-3);
}

.field-label {
  font-size: var(--font-size-label);
  color: var(--color-text-secondary);
}

.mode-radios {
  display: flex;
  gap: var(--space-4);
}

/* ── 麦克风区 ── */
.mic-stage {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-4);
  padding: var(--space-5) 0;
}

.mic-btn {
  width: 96px;
  height: 96px;
  border-radius: 50%;
  border: none;
  background: var(--color-primary);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background 0.2s, transform 0.15s;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.12);
  outline: none;
}

.mic-btn:hover:not(:disabled) {
  background: var(--color-primary-hover);
  transform: scale(1.04);
}

.mic-btn:active:not(:disabled) {
  background: var(--color-primary-pressed);
  transform: scale(0.97);
}

.mic-btn.is-requesting {
  opacity: 0.6;
  cursor: not-allowed;
}

.mic-hint {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
  margin: 0;
}

/* ── 录音中：计时器 ── */
.timer {
  font-size: var(--font-size-display);
  font-variant-numeric: tabular-nums;
  letter-spacing: 2px;
  color: var(--color-text-primary);
  font-weight: var(--font-weight-medium);
  line-height: 1;
}

.timer.is-paused {
  color: var(--color-text-placeholder);
}

.rec-status-label {
  font-size: var(--font-size-label);
  color: var(--color-text-placeholder);
  letter-spacing: 1px;
  text-transform: uppercase;
  margin-top: calc(var(--space-2) * -1);
}

/* ── 波形 ── */
.waveform {
  display: flex;
  align-items: center;
  gap: 5px;
  height: 48px;
}

.wave-bar {
  display: inline-block;
  width: 4px;
  border-radius: 2px;
  background: var(--color-primary);
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

/* 7 根各有自己的动画，宽度和频率略有差异，形成自然感 */
.bar-1 { animation-name: bar1; animation-duration: 0.75s; animation-delay: 0.00s; width: 3px; }
.bar-2 { animation-name: bar2; animation-duration: 0.90s; animation-delay: 0.12s; width: 4px; }
.bar-3 { animation-name: bar3; animation-duration: 0.65s; animation-delay: 0.05s; width: 4px; }
.bar-4 { animation-name: bar4; animation-duration: 0.80s; animation-delay: 0.20s; width: 5px; }
.bar-5 { animation-name: bar5; animation-duration: 0.65s; animation-delay: 0.08s; width: 4px; }
.bar-6 { animation-name: bar6; animation-duration: 0.90s; animation-delay: 0.15s; width: 4px; }
.bar-7 { animation-name: bar7; animation-duration: 0.75s; animation-delay: 0.03s; width: 3px; }

@keyframes bar1 { 0%,100% { height: 6px  } 50% { height: 26px } }
@keyframes bar2 { 0%,100% { height: 10px } 50% { height: 38px } }
@keyframes bar3 { 0%,100% { height: 6px  } 50% { height: 34px } }
@keyframes bar4 { 0%,100% { height: 8px  } 50% { height: 44px } }
@keyframes bar5 { 0%,100% { height: 6px  } 50% { height: 34px } }
@keyframes bar6 { 0%,100% { height: 10px } 50% { height: 38px } }
@keyframes bar7 { 0%,100% { height: 6px  } 50% { height: 26px } }

/* ── 停止按钮 ── */
.stop-btn {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  border: none;
  background: var(--color-error);
  color: #fff;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  outline: none;
  animation: stop-pulse 1.6s ease-out infinite;
  transition: background 0.2s, transform 0.15s;
}

.stop-btn:hover {
  background: #7a3030;
  transform: scale(1.04);
}

.stop-btn:active {
  transform: scale(0.96);
}

@keyframes stop-pulse {
  0%   { box-shadow: 0 0 0 0   rgba(139, 58, 58, 0.45); }
  70%  { box-shadow: 0 0 0 8px rgba(139, 58, 58, 0);    }
  100% { box-shadow: 0 0 0 0   rgba(139, 58, 58, 0);    }
}

/* ── 录音辅助控制 ── */
.rec-controls {
  display: flex;
  gap: var(--space-4);
}

.ctrl-btn {
  display: inline-flex;
  align-items: center;
  gap: var(--space-1);
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: var(--space-2) var(--space-4);
  font-size: var(--font-size-body);
  font-family: inherit;
  color: var(--color-text-secondary);
  cursor: pointer;
  transition: background 0.15s, color 0.15s;
}

.ctrl-btn:hover {
  background: var(--color-bg-page);
  color: var(--color-text-primary);
}

.ctrl-btn.resume {
  color: var(--color-primary);
  border-color: var(--color-primary);
}

.ctrl-btn.resume:hover {
  background: rgba(92, 138, 120, 0.06);
}

.ctrl-btn.cancel:hover {
  color: var(--color-error);
  border-color: var(--color-error);
}

/* ── 录制完成 ── */
.done-header {
  display: flex;
  align-items: center;
  gap: var(--space-2);
  width: 100%;
  padding: var(--space-3) var(--space-4);
  background: rgba(74, 122, 90, 0.07);
  border: 1px solid rgba(74, 122, 90, 0.2);
  border-radius: var(--radius-md);
}

.done-check {
  color: var(--color-success);
  font-size: var(--font-size-card-title);
}

.done-meta {
  font-size: var(--font-size-body);
  color: var(--color-text-secondary);
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
  gap: var(--space-3);
  padding-top: var(--space-3);
  border-top: 1px solid var(--color-border);
}

.save-actions {
  display: flex;
  flex-wrap: wrap;
  gap: var(--space-3);
  width: 100%;
}
</style>
