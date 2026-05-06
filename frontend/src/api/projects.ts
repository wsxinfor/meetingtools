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

export interface ProjectCreate {
  customer_id: string
  name: string
  stage?: string
  budget?: string
  notes?: string
}

export interface ProjectUpdate {
  customer_id?: string
  name?: string
  stage?: string
  budget?: string
  notes?: string
}

export async function listProjects(customer_id?: string): Promise<Project[]> {
  const params = customer_id ? { customer_id } : {}
  const res = await http.get<{ code: number; data: Project[] }>('/projects', { params })
  return res.data.data
}

export async function createProject(data: ProjectCreate): Promise<Project> {
  const res = await http.post<{ code: number; data: Project }>('/projects', data)
  return res.data.data
}

export async function getProject(id: string): Promise<Project> {
  const res = await http.get<{ code: number; data: Project }>(`/projects/${id}`)
  return res.data.data
}

export async function updateProject(id: string, data: ProjectUpdate): Promise<Project> {
  const res = await http.put<{ code: number; data: Project }>(`/projects/${id}`, data)
  return res.data.data
}

export async function deleteProject(id: string): Promise<void> {
  await http.delete(`/projects/${id}`)
}
