import http from './http'

export interface AsrConfig {
  id: string
  name: string
  provider: string
  base_url: string
  api_key: string
  enable_diarization: boolean
  enable_filler_removal: boolean
  is_default: boolean
  is_enabled: boolean
  created_at: string
  updated_at: string
}

export interface AsrConfigCreate {
  name: string
  provider?: string
  base_url?: string
  api_key?: string
  enable_diarization?: boolean
  enable_filler_removal?: boolean
  is_default?: boolean
  is_enabled?: boolean
}

export interface AsrConfigUpdate {
  name?: string
  provider?: string
  base_url?: string
  api_key?: string
  enable_diarization?: boolean
  enable_filler_removal?: boolean
  is_default?: boolean
  is_enabled?: boolean
}

export interface AsrTestResult {
  success: boolean
  error?: string
  message?: string
}

export async function listAsrConfigs(): Promise<AsrConfig[]> {
  const res = await http.get('/asr-configs')
  return res.data.data
}

export async function createAsrConfig(data: AsrConfigCreate): Promise<AsrConfig> {
  const res = await http.post('/asr-configs', data)
  return res.data.data
}

export async function updateAsrConfig(id: string, data: AsrConfigUpdate): Promise<AsrConfig> {
  const res = await http.put(`/asr-configs/${id}`, data)
  return res.data.data
}

export async function deleteAsrConfig(id: string): Promise<void> {
  await http.delete(`/asr-configs/${id}`)
}

export async function setDefaultAsrConfig(id: string): Promise<AsrConfig> {
  const res = await http.put(`/asr-configs/${id}/set-default`)
  return res.data.data
}

export async function testAsrConfig(id: string): Promise<AsrTestResult> {
  const res = await http.post(`/asr-configs/${id}/test`, null, { timeout: 15000 })
  return res.data.data
}
