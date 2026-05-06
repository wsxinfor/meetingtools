<template>
  <div class="recorder-wrap">
    <el-tooltip :content="tooltipText" placement="left">
      <button
        class="recorder-btn"
        :class="btnClass"
        :disabled="store.state === 'requesting'"
        @click="handleClick"
        aria-label="录音"
      >
        <svg v-if="store.state !== 'recording'" viewBox="0 0 24 24" fill="currentColor" width="22" height="22">
          <path d="M12 1a4 4 0 0 1 4 4v6a4 4 0 0 1-8 0V5a4 4 0 0 1 4-4zm6.5 9a1 1 0 0 1 1 1 7.5 7.5 0 0 1-6.5 7.43V20h2a1 1 0 1 1 0 2H9a1 1 0 1 1 0-2h2v-1.57A7.5 7.5 0 0 1 4.5 11a1 1 0 1 1 2 0 5.5 5.5 0 0 0 11 0 1 1 0 0 1 1-1z"/>
        </svg>
        <svg v-else viewBox="0 0 24 24" fill="currentColor" width="20" height="20">
          <rect x="4" y="4" width="16" height="16" rx="2"/>
        </svg>
      </button>
    </el-tooltip>
    <span v-if="store.state === 'recording'" class="recorder-timer">{{ formattedDuration }}</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRecorderStore } from '@/stores/useRecorderStore'

const store = useRecorderStore()

const tooltipText = computed(() => {
  if (store.state === 'requesting') return '正在获取麦克风权限...'
  if (store.state === 'recording') return '点击停止录音'
  return '开始录音'
})

const btnClass = computed(() => ({
  'recorder-btn--recording': store.state === 'recording',
  'recorder-btn--requesting': store.state === 'requesting',
}))

const formattedDuration = computed(() => {
  const m = Math.floor(store.durationSec / 60)
  const s = store.durationSec % 60
  return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`
})

function handleClick() {
  if (store.state === 'idle') store.startRecording()
  else if (store.state === 'recording') store.stopRecording()
}
</script>

<style scoped>
.recorder-wrap {
  position: fixed;
  bottom: 28px;
  right: 28px;
  z-index: 1000;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
}

.recorder-btn {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  border: 2px solid var(--meeting-color-danger);
  background: transparent;
  color: var(--meeting-color-danger);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: background var(--meeting-transition-base),
              transform var(--meeting-transition-fast);
  outline: none;
}

.recorder-btn:hover:not(:disabled) {
  background: var(--meeting-color-danger-bg);
  transform: translateY(-1px);
}

.recorder-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.recorder-btn--recording {
  background: var(--meeting-color-danger) !important;
  border-color: var(--meeting-color-danger) !important;
  color: var(--meeting-text-on-primary) !important;
  animation: recording-pulse 1.2s ease-in-out infinite;
}

.recorder-btn--requesting {
  background: var(--meeting-bg-subtle) !important;
  border-color: var(--meeting-text-tertiary) !important;
  color: var(--meeting-text-tertiary) !important;
}

.recorder-timer {
  font-size: var(--meeting-font-size-xs);
  color: var(--meeting-color-danger);
  font-variant-numeric: tabular-nums;
  background: var(--meeting-bg-surface);
  border: 0.5px solid var(--meeting-border-base);
  border-radius: var(--meeting-radius-sm);
  padding: 1px 6px;
  line-height: 1.5;
}
</style>
