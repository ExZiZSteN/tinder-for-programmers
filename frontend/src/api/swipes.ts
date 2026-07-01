import { apiClient } from './client'
import type { Swipe, SwipeCreate } from '@/types/swipe'
import type { Project } from '@/types/project'

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

    getMySwipes: async (): Promise<Swipe[]> => {
    const response = await apiClient.get('/swipes/my')
    return response.data
  },

  // Ответить на свайп (approved/rejected)
  review: async (swipeId: number, status: 'approved' | 'rejected'): Promise<Swipe> => {
    const response = await apiClient.patch(`/swipes/${swipeId}/review`, {
      status,
    })
    return response.data
  },

  getFeed: async (params?: {limit?: number; offest?: number }): Promise<Project[]> => {
    const response = await apiClient.get('/feed', { params })
    return response.data
  },
}