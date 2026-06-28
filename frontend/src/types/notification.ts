export interface Notification {
  id: number
  user_id: number
  type: 'match' | 'swipe_approved' | 'swipe_rejected' | 'system'
  title: string
  message: string
  is_read: boolean
  created_at: string
  // Опционально: связанные сущности, если бэкенд их возвращает
  related_project_id?: number
  related_user_id?: number
}

export interface NotificationListResponse {
  items: Notification[]
  unread_count: number
}