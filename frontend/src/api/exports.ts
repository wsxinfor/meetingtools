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
