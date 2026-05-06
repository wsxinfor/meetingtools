import http from './http'

export interface HealthResponse {
  code: number
  data: { status: string; database: string }
  msg: string
}

export async function checkHealth(): Promise<HealthResponse> {
  const res = await http.get<HealthResponse>('/health')
  return res.data
}
