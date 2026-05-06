import { defineStore } from 'pinia'
import { ref } from 'vue'
import { ElMessage } from 'element-plus'

export type RecordState = 'idle' | 'requesting' | 'recording' | 'paused' | 'stopped'

export const useRecorderStore = defineStore('recorder', () => {
  const state = ref<RecordState>('idle')
  const durationSec = ref(0)
  const blob = ref<Blob | null>(null)
  const blobUrl = ref<string | null>(null)
  const errorMsg = ref<string | null>(null)

  let mediaRecorder: MediaRecorder | null = null
  let stream: MediaStream | null = null
  let chunks: BlobPart[] = []
  let timer: ReturnType<typeof setInterval> | null = null

  async function startRecording() {
    if (state.value !== 'idle') return
    state.value = 'requesting'
    errorMsg.value = null

    try {
      stream = await navigator.mediaDevices.getUserMedia({ audio: true })
    } catch {
      state.value = 'idle'
      errorMsg.value = '麦克风权限被拒绝'
      ElMessage.error('无法访问麦克风，请检查浏览器权限')
      return
    }

    chunks = []
    durationSec.value = 0

    const mimeType = MediaRecorder.isTypeSupported('audio/webm;codecs=opus')
      ? 'audio/webm;codecs=opus'
      : 'audio/webm'

    mediaRecorder = new MediaRecorder(stream, { mimeType })
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) chunks.push(e.data)
    }
    mediaRecorder.onstop = () => {
      const recorded = new Blob(chunks, { type: mimeType })
      blob.value = recorded
      blobUrl.value = URL.createObjectURL(recorded)
      state.value = 'stopped'
    }

    mediaRecorder.start(250)
    state.value = 'recording'

    timer = setInterval(() => {
      durationSec.value += 1
    }, 1000)
  }

  function stopRecording() {
    if (state.value !== 'recording' && state.value !== 'paused') return
    _clearTimer()
    stream?.getTracks().forEach((t) => t.stop())
    mediaRecorder?.stop()
    // state transitions to 'stopped' in onstop handler
  }

  function pauseRecording() {
    if (state.value !== 'recording') return
    _clearTimer()
    mediaRecorder?.pause()
    state.value = 'paused'
  }

  function resumeRecording() {
    if (state.value !== 'paused') return
    mediaRecorder?.resume()
    state.value = 'recording'
    timer = setInterval(() => {
      durationSec.value += 1
    }, 1000)
  }

  function downloadRecording() {
    if (!blobUrl.value || !blob.value) return
    const ext = blob.value.type.includes('ogg') ? 'ogg' : 'webm'
    const ts = new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-')
    const a = document.createElement('a')
    a.href = blobUrl.value
    a.download = `recording-${ts}.${ext}`
    a.click()
  }

  function resetRecorder() {
    _clearTimer()
    stream?.getTracks().forEach((t) => t.stop())
    if (blobUrl.value) URL.revokeObjectURL(blobUrl.value)
    blob.value = null
    blobUrl.value = null
    durationSec.value = 0
    errorMsg.value = null
    mediaRecorder = null
    stream = null
    chunks = []
    state.value = 'idle'
  }

  function _clearTimer() {
    if (timer) { clearInterval(timer); timer = null }
  }

  return {
    state, durationSec, blob, blobUrl, errorMsg,
    startRecording, stopRecording, pauseRecording, resumeRecording,
    downloadRecording, resetRecorder,
  }
})
