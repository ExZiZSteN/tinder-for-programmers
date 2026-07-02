import { apiClient } from './client'
import type { Notification, NotificationListResponse } from '@/types/notification'

export const notificationsApi = {
  // Получить список уведомлений
  list: async (): Promise<NotificationListResponse> => {
    const response = await apiClient.get('/notifications')
    return response.data
  },

  // Отметить уведомление как прочитанное
  markAsRead: async (notificationId: number): Promise<Notification> => {
    const response = await apiClient.patch(`/notifications/${notificationId}/read`)
    return response.data
  },
}