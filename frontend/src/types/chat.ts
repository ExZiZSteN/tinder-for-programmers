export interface Message {
  id: number
  match_id: number
  sender_id: number
  content: string
  is_read: boolean 
  read_at: string | null
  created_at: string
}
