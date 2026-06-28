import { apiClient } from './client'
import type { Swipe, SwipeCreate } from '@/types/swipe'

export const swipesApi = {
  // Создать свайп (лайк/дизлайк проекта)
  create: async (data: SwipeCreate): Promise<Swipe> => {
    const response = await apiClient.post('/swipes', data)
    return response.data
  },

  // Получить входящие свайпы (на которые нужно ответить)
  getInbox: async (): Promise<Swipe[]> => {
    const response = await apiClient.get('/swipes/inbox')
    return response.data
  },

  // Ответить на свайп (approved/rejected)
  review: async (swipeId: number, action: 'approved' | 'rejected'): Promise<Swipe> => {
    const response = await apiClient.patch(`/swipes/${swipeId}/review`, {
      action,
    })
    return response.data
  },
}