import { apiClient } from './client'
import type { Match } from '@/types/match'

export const matchesApi = {
  // Получить список матчей
  list: async (): Promise<Match[]> => {
    const response = await apiClient.get('/matches')
    return response.data
  },

  // Получить матч по ID
  getById: async (matchId: number): Promise<Match> => {
    const response = await apiClient.get(`/matches/${matchId}`)
    return response.data
  },

  // Закрыть матч
  close: async (matchId: number): Promise<void> => {
    await apiClient.delete(`/matches/${matchId}`)
  },
}