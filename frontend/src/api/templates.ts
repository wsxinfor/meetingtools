import http from './http'

export interface Template {
  id: string
  name: string
  type: string
  description: string | null
  prompt_text: string
  output_schema: Record<string, unknown> | null
  enabled: boolean
  owner_id: string | null
  created_at: string
  updated_at: string
}

export interface TemplateCreate {
  name: string
  type?: string
  description?: string | null
  prompt_text: string
  enabled?: boolean
}

export interface TemplateUpdate {
  name?: string
  type?: string
  description?: string | null
  prompt_text?: string
  enabled?: boolean
}

export async function listTemplates(): Promise<Template[]> {
  const res = await http.get('/templates')
  return res.data.data
}

export async function getTemplate(id: string): Promise<Template> {
  const res = await http.get(`/templates/${id}`)
  return res.data.data
}

export async function createTemplate(data: TemplateCreate): Promise<Template> {
  const res = await http.post('/templates', data)
  return res.data.data
}

export async function updateTemplate(id: string, data: TemplateUpdate): Promise<Template> {
  const res = await http.put(`/templates/${id}`, data)
  return res.data.data
}

export async function deleteTemplate(id: string): Promise<void> {
  await http.delete(`/templates/${id}`)
}
