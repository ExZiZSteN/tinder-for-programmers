import { apiClient } from './client'
import type { User, UserCreate } from '@/types/user'
import type { LoginRequest, LoginResponse } from '@/types/auth'

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

  logout: async (refreshToken: string): Promise<void> => {
    await apiClient.post('/auth/logout', {
      refresh_token: refreshToken,
    })
  },

  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/users/me')
    return response.data
  },
}