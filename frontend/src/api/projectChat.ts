import { apiClient } from "./client";
import type { ProjectMessage, ProjectMessageSender } from "@/types/chat";

export const projectChatApi = {
    getMessages: async (
        projectId: number,
        beforeId?: number,
        limit: number = 50
    ): Promise<ProjectMessage[]> => {
        const params: Record<string, any> = { limit };
        if (beforeId) {
            params.before_id = beforeId
        }
        const response = await apiClient.get(`/projects/${projectId}/messages`, { params })
        return response.data
    },

    sendMessge: async (projectId: number, content: string): Promise<ProjectMessage> => {
        const response = await apiClient.post(`/projects/${projectId}/messages`, { content })
        return response.data
    },
}