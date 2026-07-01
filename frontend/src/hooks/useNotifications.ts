import { useEffect, useRef, useState, useCallback } from 'react'
import { notificationsApi } from '@/api/notifications'
import type { Notification } from '@/types/notification'
import { useAuthStore } from '@/stores/authStore'
import { toast } from 'sonner'

const WS_URL = import.meta.env.VITE_WS_URL || 'ws://localhost:8000'

export const useNotifications = () => {

  const [notifications, setNotifications] = useState<Notification[]>([])
  const [unreadCount, setUnreadCount] = useState<number>(0)
  const [isConnected, setIsConnected] = useState<boolean>(false)
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<ReturnType<typeof setTimeout> | null>(null)
  const reconnectDelayRef = useRef<number>(1000)

  const token = useAuthStore((state) => state.token)
  const isAuthenticated = useAuthStore((state) => state.isAuthenticated)

  const loadNotifications = useCallback(async () => {
    if (!isAuthenticated) return
    try {
      const data = await notificationsApi.list()

      setNotifications(data?.items || [])
      setUnreadCount(data?.unread_count || 0)
    } catch (error) {
      console.error('Ошибка загрузки уведомлений:', error)
      setNotifications([])
      setUnreadCount(0)
    }
  }, [isAuthenticated])

  const connectWS = useCallback(() => {
    if (wsRef.current || !token || !isAuthenticated) return

    const ws = new WebSocket(`${WS_URL}/ws/notifications?token=${token}`)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket уведомлений подключён')
      setIsConnected(true)
      reconnectDelayRef.current = 1000
    }

    ws.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data)
        if (data.type === 'notification') {
          setNotifications((prev) => {
            const safePrev = prev || []
            const exists = safePrev.some((n) => n.id === data.id)
            if (exists) return safePrev
            return [data, ...safePrev]
          })
          setUnreadCount((prev) => (prev || 0) + 1)

          toast(data.title, {
            description: data.body || '',
            duration: 5000,
          })
        }
      } catch (err) {
        console.error('Ошибка парсинга уведомления:', err)
      }
    }

    ws.onclose = (event) => {
      setIsConnected(false)
      wsRef.current = null
      console.warn(`WebSocket уведомлений закрыт (код: ${event.code})`)

      if (event.code !== 4001) {
        reconnectTimeoutRef.current = setTimeout(() => {
          reconnectDelayRef.current = Math.min(reconnectDelayRef.current * 2, 30000)
          connectWS()
        }, reconnectDelayRef.current)
      }
    }

    ws.onerror = (error) => {
      console.error('Ошибка WebSocket уведомлений:', error)
      ws.close()
    }
  }, [token, isAuthenticated])

  const markAsRead = useCallback(async (id: number) => {
    try {
      const updated = await notificationsApi.markAsRead(id)
      setNotifications((prev) => {
        const safePrev = prev || []
        return safePrev.map((n) => (n.id === id ? { ...n, ...updated } : n))
      })
      setUnreadCount((prev) => Math.max(0, (prev || 0) - 1))
    } catch (error) {
      console.error('Ошибка отметки уведомления:', error)
    }
  }, [])

  const markAllAsRead = useCallback(async () => {
    try {
      const safeNotifications = notifications || []
      const unread = safeNotifications.filter((n) => !n.is_read)
      
      if (unread.length === 0) return
      
      await Promise.all(unread.map((n) => notificationsApi.markAsRead(n.id)))
      
      setNotifications((prev) => {
        const safePrev = prev || []
        return safePrev.map((n) => ({ ...n, is_read: true }))
      })
      setUnreadCount(0)
    } catch (error) {
      console.error('Ошибка отметки всех уведомлений:', error)
    }
  }, [notifications])

  useEffect(() => {
    if (isAuthenticated) {
      loadNotifications()
      connectWS()
    }

    return () => {
      if (wsRef.current) {
        wsRef.current.close()
      }
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current)
      }
    }
  }, [isAuthenticated, loadNotifications, connectWS])

  return {
    notifications,
    unreadCount,
    isConnected,
    markAsRead,
    markAllAsRead,
    refresh: loadNotifications,
  }
}