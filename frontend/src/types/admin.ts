export interface AdminStats {
  total_users: number
  total_projects: number
  total_matches: number
  total_skills: number
  banned_users: number
  active_projects: number
}

export interface AdminUser {
  id: number
  email: string
  full_name: string
  user_role: 'user' | 'admin'
  is_active: boolean
  is_banned: boolean
  created_at: string
  last_login_at?: string
}
