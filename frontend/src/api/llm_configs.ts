import http from './http'

export interface LlmConfig {
  id: string
  name: string
  provider: string
  base_url: string
  api_key: string
  model_name: string
  is_default: boolean
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface LlmConfigCreate {
  name: string
  provider?: string
  base_url: string
  api_key?: string
  model_name: string
  is_default?: boolean
  is_enabled?: boolean
}

export interface LlmConfigUpdate {
  name?: string
  provider?: string
  base_url?: string
  api_key?: string
  model_name?: string
  is_default?: boolean
  is_enabled?: boolean
}

export interface TestResult {
  success: boolean
  latency_ms?: number
  sample_output?: string
  error?: string
}

export async function listLlmConfigs(): Promise<LlmConfig[]> {
  const res = await http.get('/llm-configs')
  return res.data.data
}

export async function createLlmConfig(data: LlmConfigCreate): Promise<LlmConfig> {
  const res = await http.post('/llm-configs', data)
  return res.data.data
}

export async function updateLlmConfig(id: string, data: LlmConfigUpdate): Promise<LlmConfig> {
  const res = await http.put(`/llm-configs/${id}`, data)
  return res.data.data
}

export async function deleteLlmConfig(id: string): Promise<void> {
  await http.delete(`/llm-configs/${id}`)
}

export async function setDefaultLlmConfig(id: string): Promise<LlmConfig> {
  const res = await http.put(`/llm-configs/${id}/set-default`)
  return res.data.data
}

export async function testLlmConfig(id: string): Promise<TestResult> {
  const res = await http.post(`/llm-configs/${id}/test`)
  return res.data.data
}
