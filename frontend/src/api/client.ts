import axios from 'axios'

import { useAuthStore } from '@/stores/authStore'
import { authApi } from './auth'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'
export const apiClient = axios.create({
    baseURL: API_URL,
    headers: {
        'Content-Type' : 'application/json',
    },
})

// Request interceptor - добавляем токен
apiClient.interceptors.request.use(
    (config) => {
        const token = useAuthStore.getState().token
        if (token) {
            config.headers.Authorization = `Bearer ${token}`
        }
        return config
    },
    (error) => Promise.reject(error)
)


let isRefreshing = false
let failedQueue: Array<{
    resolve: (value: string) => void
    reject: (reason?: any) => void
}> = []

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error)
    } else {
      prom.resolve(token!)
    }
  })
  failedQueue = []
}
// Response interceptor - обработка ошибок
apiClient.interceptors.response.use(
    (response) => response,
    async (error) => {
        const originalRequest = error.config
        if (error.response?.status == 401 && !originalRequest._retry){
            if (isRefreshing){
                return new Promise((resolve, reject) => {
                    failedQueue.push({ resolve, reject })
                }).then((token) => {
                    originalRequest.headers.Authorization = `Bearer ${token}`
                    return apiClient(originalRequest)
                })
            }

            originalRequest._retry = true
            isRefreshing = true

            const refreshToken = useAuthStore.getState().refreshToken

            if (!refreshToken){
                useAuthStore.getState().logout()
                if (window.location.pathname !== '/login') {
                    window.location.href = '/login'
                }
                return Promise.reject(error)
            }

            try{
                const {access_token, refresh_token: new_refresh_token} =
                await authApi.refresh(refreshToken)

                const user = useAuthStore.getState().user
                if (user) {
                    useAuthStore.getState().setAuth(user, access_token, new_refresh_token)
                }

                processQueue(null, access_token)

                originalRequest.headers.Authorization = `Bearer ${access_token}`
                return apiClient(originalRequest)
            } catch (refreshError){
                processQueue(refreshError, null)
                useAuthStore.getState().logout()
                if (window.location.pathname !== '/login'){
                    window.location.href = '/login'
                }
                return Promise.reject(refreshToken)
            } finally {
                isRefreshing = false
            }
        }
        return Promise.reject(error)
    }
)