export interface Project {
  id: number
  owner_id: number
  title: string
  description: string
  format: 'remote' | 'office' | 'hybrid'
  payment_type: 'volunteer' | 'paid' | 'equity'
  status: 'draft' | 'open' | 'closed' | 'completed' | 'archived'
  skills: Skill[]
  owner: ProjectOwner
  score?: number
  created_at: string
  updated_at: string
}

export interface ProjectOwner {
  id: number
  full_name: string
  avatar_url?: string
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
}

export interface ProjectUpdate {
  title?: string
  description?: string
  format?: 'remote' | 'office' | 'hybrid'
  payment_type?: 'volunteer' | 'paid' | 'equity'
  skill_ids?: number[]
}