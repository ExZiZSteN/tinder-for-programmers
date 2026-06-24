export interface Swipe {
  id: number
  user_id: number
  project_id: number
  message?: string
  status: 'pending' | 'approved' | 'rejected' | 'withdrawn'
  created_at: string
  reviewed_at?: string
  user?: SwipeUser
  project?: SwipeProject
}

export interface SwipeUser {
  id: number
  full_name: string
  avatar_url?: string
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