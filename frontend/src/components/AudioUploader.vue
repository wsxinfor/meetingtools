<template>
  <div class="audio-uploader">
    <div class="uploader-header">
      <span class="section-title">音频文件</span>
      <el-upload
        :before-upload="handleUpload"
        :show-file-list="false"
        accept=".mp3,.wav,.m4a,.aac"
        :disabled="uploading"
      >
        <el-button :loading="uploading" size="small">上传音频</el-button>
      </el-upload>
    </div>

    <el-empty v-if="!files.length && !uploading" description="暂无音频，请上传" :image-size="60" />

    <el-table v-else :data="files" size="small" class="audio-table">
      <el-table-column label="文件名" prop="original_filename" min-width="200" />
      <el-table-column label="大小" width="100">
        <template #default="{ row }">
          {{ row.file_size ? formatSize(row.file_size) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="时长" width="90">
        <template #default="{ row }">
          {{ row.duration_seconds ? formatDuration(row.duration_seconds) : '-' }}
        </template>
      </el-table-column>
      <el-table-column label="状态" width="90">
        <template #default="{ row }">
          <el-tag size="small" :type="statusType(row.status)">{{ statusLabel(row.status) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="80" align="center">
        <template #default="{ row }">
          <el-button size="small" link type="primary" @click="handleDownload(row)">下载</el-button>
        </template>
      </el-table-column>
    </el-table>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { uploadAudio, listAudioFiles, downloadAudioFile, type AudioFile } from '@/api/audio'

const props = defineProps<{ meetingId: string }>()

const files = ref<AudioFile[]>([])
const uploading = ref(false)

async function fetchFiles() {
  files.value = await listAudioFiles(props.meetingId)
}

async function handleUpload(file: File): Promise<false> {
  uploading.value = true
  try {
    const result = await uploadAudio(props.meetingId, file)
    files.value.push(result)
    ElMessage.success('上传成功')
  } catch {
    ElMessage.error('上传失败，请检查文件格式或大小')
  } finally {
    uploading.value = false
  }
  return false
}

function formatSize(bytes: number): string {
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`
}

function formatDuration(s: number): string {
  const m = Math.floor(s / 60)
  const sec = Math.floor(s % 60)
  return `${m}:${String(sec).padStart(2, '0')}`
}

function statusLabel(s: string): string {
  const map: Record<string, string> = {
    uploaded: '已上传',
    preprocessed: '已预处理',
    failed: '失败',
  }
  return map[s] ?? s
}

function statusType(s: string): 'success' | 'danger' | '' {
  if (s === 'preprocessed') return 'success'
  if (s === 'failed') return 'danger'
  return ''
}

async function handleDownload(file: AudioFile) {
  try {
    const blob = await downloadAudioFile(file.id)
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = file.original_filename
    a.click()
    URL.revokeObjectURL(url)
  } catch {
    ElMessage.error('下载失败')
  }
}

onMounted(fetchFiles)
</script>

<style scoped>
.audio-uploader {
  margin-top: var(--meeting-space-6);
}

.uploader-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--meeting-space-3);
}

.section-title {
  font-size: var(--meeting-font-size-md);
  font-weight: var(--meeting-font-weight-medium);
  color: var(--meeting-text-primary);
}

.audio-table {
  margin-top: var(--meeting-space-3);
  border-radius: var(--meeting-radius-lg);
  overflow: hidden;
}
</style>
