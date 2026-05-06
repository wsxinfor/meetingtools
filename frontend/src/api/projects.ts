import http from './http'

export interface Project {
  id: string
  customer_id: string
  name: string
  stage: string | null
  budget: string | null
  notes: string | null
  created_at: string
  updated_at: string
}

export async function listProjects(customer_id?: string): Promise<Project[]> {
  const params = customer_id ? { customer_id } : {}
  const res = await http.get<{ code: number; data: Project[] }>('/projects', { params })
  return res.data.data
}
