import { apiClient } from './client'

export interface Message {
  id: number
  match_id: number
  sender_id: number
  content: string
  created_at: string
}

export const chatApi = {
  // Получить историю сообщений матча
  getMessages: async (
    matchId: number,
    offset: number = 0,
    limit: number = 50
  ): Promise<Message[]> => {
    const response = await apiClient.get(`/matches/${matchId}/messages`, {
      params: { offset, limit },
    })
    return response.data
  },

  // ⚠️ Отправка сообщений пока не реализована на backend
  // Нужно добавить POST /matches/{match_id}/messages
  sendMessage: async (matchId: number, content: string): Promise<Message> => {
    const response = await apiClient.post(`/matches/${matchId}/messages`, {
      content,
    })
    return response.data
  },
}