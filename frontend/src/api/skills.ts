import { apiClient } from './client'
import type { Skill } from '@/types/project'

export const skillsApi = {
  list: async (params?: {q?: string; offset?: number; limit?: number}): Promise<Skill[]> => {
    const response = await apiClient.get('/skills', { params })
    return response.data
  },

  popular: async (): Promise<Skill[]> => {
    const response = await apiClient.get('/skills/popular')
    return response.data
  },

  create: async (name: string): Promise<Skill> => {
    const response = await apiClient.post('/skills', { params: { name }})
    return response.data
  },
}