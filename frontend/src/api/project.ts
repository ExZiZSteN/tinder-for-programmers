import { apiClient } from './client'
import type { Project, ProjectCreate, ProjectUpdate } from '@/types/project'

export const projectsApi = {
    list: async (params? : {
        offset?: number
        limit?: number
        status?: string
        format?: string
        payment_type?: string
        skill_ids?: number[]
    }): Promise<Project[]> => {
        const response = await apiClient.get('/projects', { params })
        return response.data
    },

    getMyProjects: async (): Promise<Project[]> => {
        const response = await apiClient.get('/projects/my')
        return response.data
    },

    getById: async (id: number): Promise<Project> => {
        const response = await apiClient.get(`/projects/${id}`)
        return response.data
    },

    create: async (data: ProjectCreate): Promise<Project> => {
        const response = await apiClient.post('/projects', data)
        return response.data
    },

    update: async (id: number, data: ProjectUpdate): Promise<Project> => {
        const response = await apiClient.patch(`/projects/${id}`, data)
        return response.data
    },

    delete: async (id: number): Promise<void> => {
        await apiClient.delete(`/projects/${id}`)
    },

    restore: async (id: number): Promise<Project> => {
        const response = await apiClient.post(`/projects/${id}/restore`)
        return response.data
    },
    
    updateMemberRole: async (
        projectId: number,
        userId: number,
        role: string
    ): Promise<void> => {
        await apiClient.patch(`/projects/${projectId}/members/${userId}`, { role })
    },

    removeMember: async (projectId: number, userId: number): Promise<void> => {
        await apiClient.delete(`/projects/${projectId}/members/${userId}`)
    },
}