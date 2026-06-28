export interface User {
  id: number
  email: string
  full_name: string
  bio?: string
  github_url?: string
  linkedin_url?: string
  portfolio_url?: string
  experience_years?: number
  avatar_file_id?: number
  resume_file_id?: number
  skills: {id: number; name: string}[]
  user_role: 'user' | 'admin'
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface UserCreate {
  email: string
  password: string
  full_name: string
}

export interface UserUpdate {
  full_name?: string
  bio?: string
  github_url?: string
  linkedin_url?: string
  portfolio_url?: string
  experience_years?: number
}
export interface PublicUserResponse {
  id: number
  full_name: string
  bio?: string
  github_url?: string
  linkedin_url?: string
  portfolio_url?: string
  experience_years?: number
  avatar_url?: string
  skills: { id: number; name: string }[]
}