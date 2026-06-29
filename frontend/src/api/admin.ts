import { apiClient } from './client'
import type { User } from '@/types/user'

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

export const adminApi = {
  // Статистика
  getStats: async (): Promise<AdminStats> => {
    const response = await apiClient.get('/admin/stats')
    return response.data
  },

  // Список пользователей
  getUsers: async (params?: {
    offset?: number
    limit?: number
    search?: string
    role?: string
    is_banned?: boolean
  }): Promise<{ users: AdminUser[]; total: number }> => {
    const response = await apiClient.get('/admin/users', { params })
    return response.data
  },

  // Забанить/разбанить пользователя
  banUser: async (userId: number, banned: boolean): Promise<AdminUser> => {
    const response = await apiClient.post(`/admin/users/${userId}/ban`, {
      is_banned: banned,
    })
    return response.data
  },

  // Сменить роль
  changeRole: async (userId: number, role: 'user' | 'admin'): Promise<AdminUser> => {
    const response = await apiClient.patch(`/admin/users/${userId}/role`, {
      role,
    })
    return response.data
  },

  // Удалить пользователя
  deleteUser: async (userId: number): Promise<void> => {
    await apiClient.delete(`/admin/users/${userId}`)
  },

  // Список проектов (для модерации)
  getProjects: async (params?: {
    offset?: number
    limit?: number
    status?: string
  }): Promise<{ projects: any[]; total: number }> => {
    const response = await apiClient.get('/admin/projects', { params })
    return response.data
  },

  // Удалить проект
  deleteProject: async (projectId: number): Promise<void> => {
    await apiClient.delete(`/admin/projects/${projectId}`)
  },

  // Список навыков
  getSkills: async (params?: {
    offset?: number
    limit?: number
    search?: string
  }): Promise<{ skills: any[]; total: number }> => {
    const response = await apiClient.get('/admin/skills', { params })
    return response.data
  },

  // Создать навык
  createSkill: async (name: string): Promise<any> => {
    const response = await apiClient.post('/admin/skills', { name })
    return response.data
  },

  // Удалить навык
  deleteSkill: async (skillId: number): Promise<void> => {
    await apiClient.delete(`/admin/skills/${skillId}`)
  },
}