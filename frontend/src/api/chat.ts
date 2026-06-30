import { apiClient } from './client'

export interface Message {
  id: number
  match_id: number
  sender_id: number
  content: string
  is_read: boolean 
  read_at: string | null
  created_at: string
}

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


    const response = await apiClient.get(`/api/chat/${matchId}/history`, {
      params,
    })
    return response.data
  },


  sendMessage: async (matchId: number, content: string): Promise<Message> => {
    const response = await apiClient.post(`/api/chat/${matchId}/messages`, {
      content,
    })
    return response.data
  },
}
