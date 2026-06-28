import axios from 'axios'

import { useAuthStore } from '@/stores/authStore'

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

// Response interceptor - обработка ошибок
apiClient.interceptors.response.use(
    (repsonse) => repsonse,
    async (error) => {
        if (error.response?.status == 401){
            // Токен истек или недействителен
            useAuthStore.getState().logout()
            window.location.href = '/login'
        }
        return Promise.reject(error)
    }
)