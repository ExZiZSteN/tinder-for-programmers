export interface Match {
  id: number
  user_id: number
  project_id: number
  swipe_id: number
  status: 'active' | 'completed' | 'closed'
  created_at: string
  closed_at?: string
  project?: MatchProject
  user?: MatchUser
}

export interface MatchProject {
  id: number
  title: string
  description: string
  owner: {
    id: number
    full_name: string
    avatar_file_id?: number
  }
}

export interface MatchUser {
  id: number
  full_name: string
  avatar_file_id?: number
  experience_years?: number
}