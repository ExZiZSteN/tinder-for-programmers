export interface Message {
  id: number
  match_id: number
  sender_id: number
  content: string
  is_read: boolean 
  read_at: string | null
  created_at: string
}

export interface ProjectMessageSender {
  id: number
  full_name: string
  avatar_file_id?: number
}

export interface ProjectMessage {
  id: number
  project_id: number
  sender_id: number
  content: string
  created_at: string
  sender?: ProjectMessageSender
}