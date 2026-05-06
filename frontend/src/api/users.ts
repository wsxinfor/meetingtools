import http from './http'
import type { UserInfo } from './auth'

export type { UserInfo }

export interface UserCreate {
  username: string
  password: string
  role: string
}

export interface UserUpdate {
  password?: string
  role?: string
  is_active?: boolean
}

export async function listUsers(): Promise<UserInfo[]> {
  const res = await http.get<{ code: number; data: UserInfo[] }>('/users')
  return res.data.data
}

export async function createUser(data: UserCreate): Promise<UserInfo> {
  const res = await http.post<{ code: number; data: UserInfo }>('/users', data)
  return res.data.data
}

export async function updateUser(id: string, data: UserUpdate): Promise<UserInfo> {
  const res = await http.put<{ code: number; data: UserInfo }>(`/users/${id}`, data)
  return res.data.data
}

export async function deleteUser(id: string): Promise<void> {
  await http.delete(`/users/${id}`)
}
