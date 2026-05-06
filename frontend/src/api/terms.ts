import http from './http'

export interface Term {
  id: string
  category: string
  wrong_text: string
  correct_text: string
  aliases: string[] | null
  enabled: boolean
  created_at: string
}

export interface TermCreate {
  category?: string
  wrong_text: string
  correct_text: string
  aliases?: string[] | null
  enabled?: boolean
}

export interface TermUpdate {
  category?: string
  wrong_text?: string
  correct_text?: string
  aliases?: string[] | null
  enabled?: boolean
}

export async function listTerms(): Promise<Term[]> {
  const res = await http.get('/terms')
  return res.data.data
}

export async function createTerm(data: TermCreate): Promise<Term> {
  const res = await http.post('/terms', data)
  return res.data.data
}

export async function updateTerm(id: string, data: TermUpdate): Promise<Term> {
  const res = await http.put(`/terms/${id}`, data)
  return res.data.data
}

export async function deleteTerm(id: string): Promise<void> {
  await http.delete(`/terms/${id}`)
}

export async function applyTerms(
  meetingId: string,
): Promise<{ corrected_text: string; segments_updated: number }> {
  const res = await http.post(`/meetings/${meetingId}/apply-terms`)
  return res.data.data
}
