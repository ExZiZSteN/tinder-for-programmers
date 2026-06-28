export interface FileUploadResponse {
  id: number
  owner_id: number
  upload_url: string
  original_name: string
  expires_in: number
}

export interface FileDownloadResponse {
  id: number
  owner_id: number
  original_name: string
  mime_type: string
  size_bytes: number
  download_url: string
  created_at: string
}