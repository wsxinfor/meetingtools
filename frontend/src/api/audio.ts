import http from './http'

export interface AudioFile {
  id: string
  meeting_id: string
  original_filename: string
  file_size: number | null
  duration_seconds: number | null
  sample_rate: number | null
  channels: number | null
  status: string
  created_at: string
}

export async function uploadAudio(meetingId: string, file: File): Promise<AudioFile> {
  const form = new FormData()
  form.append('file', file)
  const res = await http.post<{ code: number; data: AudioFile }>(
    `/meetings/${meetingId}/audio`,
    form,
    { headers: { 'Content-Type': 'multipart/form-data' } },
  )
  return res.data.data
}

export async function listAudioFiles(meetingId: string): Promise<AudioFile[]> {
  const res = await http.get<{ code: number; data: AudioFile[] }>(
    `/meetings/${meetingId}/audio-files`,
  )
  return res.data.data
}

export async function downloadAudioFile(audioFileId: string): Promise<Blob> {
  const res = await http.get(`/audio-files/${audioFileId}/download`, {
    responseType: 'blob',
  })
  return res.data
}
