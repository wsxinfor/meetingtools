import http from './http'

export interface AsrTask {
  id: string
  meeting_id: string
  audio_file_id: string
  engine: string
  status: string
  progress: number
  error_message: string | null
  started_at: string | null
  finished_at: string | null
  created_at: string
}

export async function startAsrTask(
  meetingId: string,
  audioFileId: string,
  engine = 'mock',
): Promise<AsrTask> {
  const res = await http.post(`/meetings/${meetingId}/asr-tasks`, {
    audio_file_id: audioFileId,
    engine,
  })
  return res.data.data
}

export async function getAsrTask(taskId: string): Promise<AsrTask> {
  const res = await http.get(`/asr-tasks/${taskId}`)
  return res.data.data
}
