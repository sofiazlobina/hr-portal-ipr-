import { apiClient } from './client'
import type { User } from '../types/hr'

export async function login(email: string, password: string) {
  const body = new URLSearchParams({ username: email, password })
  const { data: token } = await apiClient.post<{ access_token: string; token_type: string }>('/auth/login', body)
  const { data: user } = await apiClient.get<User>('/auth/me', {
    headers: { Authorization: `Bearer ${token.access_token}` },
  })
  return { accessToken: token.access_token, user }
}
