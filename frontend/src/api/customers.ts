import http from './http'

export interface Customer {
  id: string
  name: string
  industry: string | null
  contact_info: Record<string, unknown> | null
  notes: string | null
  created_at: string
  updated_at: string
}

export interface CustomerCreate {
  name: string
  industry?: string
  notes?: string
}

export interface CustomerUpdate {
  name?: string
  industry?: string
  notes?: string
}

export async function listCustomers(): Promise<Customer[]> {
  const res = await http.get<{ code: number; data: Customer[] }>('/customers')
  return res.data.data
}

export async function createCustomer(data: CustomerCreate): Promise<Customer> {
  const res = await http.post<{ code: number; data: Customer }>('/customers', data)
  return res.data.data
}

export async function getCustomer(id: string): Promise<Customer> {
  const res = await http.get<{ code: number; data: Customer }>(`/customers/${id}`)
  return res.data.data
}

export async function updateCustomer(id: string, data: CustomerUpdate): Promise<Customer> {
  const res = await http.put<{ code: number; data: Customer }>(`/customers/${id}`, data)
  return res.data.data
}

export async function deleteCustomer(id: string): Promise<void> {
  await http.delete(`/customers/${id}`)
}
