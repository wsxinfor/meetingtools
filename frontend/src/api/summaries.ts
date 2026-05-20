import http from './http'

export interface Summary {
  id: string
  meeting_id: string
  template_id: string | null
  llm_config_id: string | null
  llm_model: string | null
  title: string | null
  content_md: string | null
  content_json: Record<string, unknown> | null
  version: number
  is_final: boolean
  created_at: string
}

export interface SummaryCreate {
  template_id: string
  source?: string
  llm_config_id?: string | null
}

export interface SummaryUpdate {
  title?: string
  content_md?: string
  is_final?: boolean
}

export async function generateSummary(meetingId: string, data: SummaryCreate): Promise<Summary> {
  const res = await http.post(`/meetings/${meetingId}/summaries`, data, { timeout: 0 })
  return res.data.data
}

export async function listSummaries(meetingId: string): Promise<Summary[]> {
  const res = await http.get(`/meetings/${meetingId}/summaries`)
  return res.data.data
}

export async function updateSummary(id: string, data: SummaryUpdate): Promise<Summary> {
  const res = await http.put(`/summaries/${id}`, data)
  return res.data.data
}
