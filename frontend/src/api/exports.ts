import http from './http'

export interface ExportRecord {
  id: string
  meeting_id: string
  summary_id: string | null
  export_type: string
  file_format: string
  file_path: string
  created_at: string
}

export async function exportTranscript(
  meetingId: string,
  format: 'md' | 'docx',
): Promise<ExportRecord> {
  const res = await http.post(`/meetings/${meetingId}/export-transcript`, { format })
  return res.data.data
}

export async function exportSummary(
  summaryId: string,
  format: 'md' | 'docx',
): Promise<ExportRecord> {
  const res = await http.post(`/summaries/${summaryId}/export`, { format })
  return res.data.data
}

export function getDownloadUrl(exportId: string): string {
  return `${http.defaults.baseURL}/export-records/${exportId}/download`
}

export async function downloadExportFile(exportId: string, filename: string): Promise<void> {
  const res = await http.get(`/export-records/${exportId}/download`, {
    responseType: 'blob',
  })
  const blob: Blob = res.data
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  a.click()
  URL.revokeObjectURL(url)
}
