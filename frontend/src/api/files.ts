import { apiClient } from "./client";
import type { FileDownloadResponse, FileUploadResponse } from "@/types/file";

export const filesApi = {
  uploadDirect: async (file: File): Promise<FileUploadResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    const response = await apiClient.post('/files/upload-direct', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
    return response.data
  },

  getDownloadUrl: async (fileId: number): Promise<FileDownloadResponse> => {
    const response = await apiClient.get(`/files/${fileId}`)
    return response.data
  },

}