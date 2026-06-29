export interface Swipe {
  id: number
  user_id: number
  project_id: number
  message?: string
  status: 'pending' | 'approved' | 'rejected' | 'withdrawn' | 'liked' | 'disliked'
  created_at: string
  reviewed_at?: string
  user?: SwipeUser
  project?: SwipeProject
}

export interface SwipeUser {
  id: number
  full_name: string
  avatar_url?: string
  avatar_file_id?: number
  experience_years?: number
  skills: { id: number; name: string }[]
}

export interface SwipeProject {
  id: number
  title: string
}

export interface SwipeCreate {
  project_id: number
  message?: string
}