export interface Project {
  id: number
  owner_id: number
  title: string
  description: string
  format: 'remote' | 'office' | 'hybrid'
  payment_type: 'volunteer' | 'paid' | 'equity'
  status: 'draft' | 'open' | 'closed' | 'completed' | 'archived'
  skills: Skill[]
  members?: ProjectMember[]
  owner?: ProjectOwner
  score?: number
  created_at: string
  updated_at: string
}

export interface ProjectOwner {
  id: number
  full_name: string
  avatar_url?: string
}

export interface ProjectMember {
  id: number
  role: string
  joined_at?: string
  is_active: boolean
}
export interface Skill {
  id: number
  name: string
}

export interface ProjectCreate {
  title: string
  description: string
  format: 'remote' | 'office' | 'hybrid'
  payment_type: 'volunteer' | 'paid' | 'equity'
  skill_ids: number[]
  status?: 'draft' | 'open' | 'closed' | 'archived'
}

export interface ProjectUpdate {
  title?: string
  description?: string
  format?: 'remote' | 'office' | 'hybrid'
  payment_type?: 'volunteer' | 'paid' | 'equity'
  status?: 'draft' | 'open' | 'closed' | 'completed' | 'archived'
  skill_ids?: number[]
}