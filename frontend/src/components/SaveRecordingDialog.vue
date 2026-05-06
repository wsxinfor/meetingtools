<template>
  <el-dialog
    v-model="visible"
    title="保存录音"
    width="480px"
    :close-on-click-modal="false"
    :close-on-press-escape="false"
    :show-close="false"
  >
    <div class="dialog-body">
      <audio v-if="store.blobUrl" :src="store.blobUrl" controls class="audio-preview" />

      <el-radio-group v-model="mode" class="mode-group">
        <el-radio value="existing">关联到已有会议</el-radio>
        <el-radio value="new">新建会议并上传</el-radio>
      </el-radio-group>

      <div v-if="mode === 'existing'" class="field-row">
        <el-select
          v-model="selectedMeetingId"
          placeholder="请选择会议"
          filterable
          style="width: 100%"
          :loading="loadingMeetings"
        >
          <el-option
            v-for="m in meetings"
            :key="m.id"
            :label="m.title"
            :value="m.id"
          />
        </el-select>
      </div>

      <div v-else class="field-row">
        <el-input v-model="newTitle" placeholder="请输入会议标题" />
      </div>
    </div>

    <template #footer>
      <el-button @click="discard">丢弃录音</el-button>
      <el-button type="primary" :loading="uploading" :disabled="!canUpload" @click="upload">
        上传录音
      </el-button>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useRecorderStore } from '@/stores/useRecorderStore'
import { listMeetings, createMeeting, type Meeting } from '@/api/meetings'
import { uploadAudio } from '@/api/audio'

const store = useRecorderStore()
const router = useRouter()

const visible = computed(() => store.state === 'stopped')
const mode = ref<'existing' | 'new'>('existing')
const selectedMeetingId = ref('')
const newTitle = ref('')
const meetings = ref<Meeting[]>([])
const loadingMeetings = ref(false)
const uploading = ref(false)

const canUpload = computed(() => {
  if (mode.value === 'existing') return !!selectedMeetingId.value
  return newTitle.value.trim().length > 0
})

watch(visible, async (open) => {
  if (!open) return
  mode.value = 'existing'
  selectedMeetingId.value = ''
  newTitle.value = ''
  loadingMeetings.value = true
  try {
    const res = await listMeetings({ page: 1, page_size: 50 })
    meetings.value = res.items
  } finally {
    loadingMeetings.value = false
  }
})

function discard() {
  store.resetRecorder()
}

async function upload() {
  if (!store.blob || !canUpload.value) return
  uploading.value = true
  try {
    let meetingId = selectedMeetingId.value
    if (mode.value === 'new') {
      const created = await createMeeting({ title: newTitle.value.trim() })
      meetingId = created.id
    }
    const file = new File([store.blob], 'recording.webm', { type: store.blob.type || 'audio/webm' })
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
</script>

<style scoped>
.dialog-body {
  display: flex;
  flex-direction: column;
  gap: var(--space-4);
}

.audio-preview {
  width: 100%;
  height: 40px;
}

.mode-group {
  display: flex;
  gap: var(--space-5);
}

.field-row {
  width: 100%;
}
</style>
