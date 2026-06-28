import { apiClient } from './client'
import type { Project } from '@/types/project'

export const feedApi = {
  getFeed: async (offset?: number, limit?: number): Promise<Project[]> => {
    const response = await apiClient.get('/feed', { params: { offset, limit } })
    return response.data
  },
}