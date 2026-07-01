import { apiClient } from './client'
import type { Message } from '@/types/chat'

export const chatApi = {

  getMessages: async (
    matchId: number,
    beforeId?: number, 
    limit: number = 50
  ): Promise<Message[]> => {
    const params: Record<string, any> = { limit }
    if (beforeId) {
      params.before_id = beforeId
    }

    const response = await apiClient.get(`/chat/${matchId}/history`, {
      params,
    })
    return response.data
  },

  sendMessage: async (matchId: number, content: string): Promise<Message> => {
    const response = await apiClient.post(`/chat/${matchId}/messages`, {
      content,
    })
    return response.data
  },

  markAsRead: async (matchId: number): Promise<{ read_count: number }> => {
    const response = await apiClient.post(`/chat/${matchId}/read`)
    return response.data
  },
}

