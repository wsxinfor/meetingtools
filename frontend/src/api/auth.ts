import http from './http'

export interface UserInfo {
  id: string
  username: string
  role: string
  is_active: boolean
  created_at: string
}

export interface TokenResponse {
  access_token: string
  token_type: string
  user: UserInfo
}

export async function login(username: string, password: string): Promise<TokenResponse> {
  const res = await http.post<{ code: number; data: TokenResponse }>('/auth/login', {
    username,
    password,
  })
  return res.data.data
}
