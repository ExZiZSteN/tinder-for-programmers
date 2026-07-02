export interface Notification {
  id: number
  user_id: number
  type: 'match' | 'swipe_approved' | 'swipe_rejected' | 'system'
  title: string
  body: string | null
  payload?: Record<string, any>
  is_read: boolean
  read_at: string | null
  created_at: string
  related_project_id?: number
  related_user_id?: number
}

export interface NotificationListResponse {
  notifications: Notification[]
  unread_count: number
}