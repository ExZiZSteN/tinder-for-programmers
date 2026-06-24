import { apiClient } from './client'
import type { User, UserCreate } from '@/types/user'

export interface LoginResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

export interface LoginRequest {
  email: string
  password: string
}

export const authApi = {
  login: async (data: LoginRequest): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/login', data)
    return response.data
  },

  register: async (data: UserCreate): Promise<{ user_id: number }> => {
    const response = await apiClient.post('/auth/register', data)
    return response.data
  },

  refresh: async (refreshToken: string): Promise<LoginResponse> => {
    const response = await apiClient.post('/auth/refresh', {
      refresh_token: refreshToken,
    })
    return response.data
  },

  logout: async (): Promise<void> => {
    await apiClient.post('/auth/logout')
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/me')
    return response.data
  },
}