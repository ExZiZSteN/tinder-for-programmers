import { apiClient } from './client'
import type { UserUpdate, User, PublicUserResponse } from '@/types/user'


export const usersApi = {
  // Получить свой профиль
  getMe: async (): Promise<User> => {
    const response = await apiClient.get('/users/me')
    return response.data
  },

  // Обновить профиль
  updateMe: async (data: UserUpdate): Promise<User> => {
    const response = await apiClient.patch('/users/me', data)
    return response.data
  },

  // Заменить навыки
  updateSkills: async (skillIds: number[]): Promise<User> => {
    const response = await apiClient.put('/users/me/skills', {
      skill_ids: skillIds,
    })
    return response.data
  },

  // Публичный профиль другого пользователя
  getUserById: async (userId: number): Promise<PublicUserResponse> => {
    const response = await apiClient.get(`/users/${userId}`)
    return response.data
  },

  // Установить аватар
  setAvatar: async (fileId: number): Promise<User> => {
    const response = await apiClient.post('/users/me/avatar', null, {
      params: { file_id: fileId },
    })
    return response.data
  },

  // Удалить аватар
  removeAvatar: async (): Promise<User> => {
    const response = await apiClient.delete('/users/me/avatar')
    return response.data
  },

  // Установить резюме
  setResume: async (fileId: number): Promise<User> => {
    const response = await apiClient.post('/users/me/resume', null, {
      params: { file_id: fileId },
    })
    return response.data
  },

  // Удалить резюме
  removeResume: async (): Promise<User> => {
    const response = await apiClient.delete('/users/me/resume')
    return response.data
  },
}