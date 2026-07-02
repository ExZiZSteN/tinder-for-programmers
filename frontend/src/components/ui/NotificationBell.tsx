import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Bell } from 'lucide-react'
import { Button } from '@/components/ui/button'
import { useNotifications } from '@/hooks/useNotifications'
import {
  Popover,
  PopoverContent,
  PopoverTrigger,
} from '@/components/ui/popover'
import { cn } from '@/utils/cn'

export function NotificationBell() {
    const { notifications, unreadCount, markAsRead, markAllAsRead } = useNotifications()
    const [isOpen, setIsOpen] = useState(false)
    const navigate = useNavigate()
    const safeNotifications = notifications || []
    const safeUnreadCount = unreadCount || 0

    const handleClickNotification = (notif: any) => {
      if (!notif.is_read) {
        markAsRead(notif.id)
      }
      const payload = notif.payload || {}
      // Переходим по payload, если есть
      if (payload?.match_id) {
        navigate(`/matches/${payload.match_id}/chat`)
        setIsOpen(false)
      } else if (payload?.project_id) {
        navigate(`/projects/${payload.project_id}`)
        setIsOpen(false)
      }
    }
  
    return (
      <Popover open={isOpen} onOpenChange={setIsOpen}>
        <PopoverTrigger asChild>
          <Button variant="ghost" size="icon" className="relative">
            <Bell className="h-5 w-5" />
            {safeUnreadCount > 0 && (
              <span className="absolute -top-1 -right-1 h-5 w-5 rounded-full bg-red-500 text-white text-xs flex items-center justify-center font-bold">
                {safeUnreadCount > 99 ? '99+' : safeUnreadCount}
              </span>
            )}
          </Button>
        </PopoverTrigger>
        <PopoverContent className="w-96 p-0" align="end">
          <div className="flex items-center justify-between p-4 border-b">
            <h3 className="font-semibold">Уведомления</h3>
            {safeUnreadCount > 0 && (
              <Button
                variant="ghost"
                size="sm"
                onClick={markAllAsRead}
                className="text-xs"
              >
                Прочитать все
              </Button>
            )}
          </div>
          <div className="max-h-96 overflow-y-auto">
            {safeNotifications.length === 0 ? (
              <div className="p-8 text-center text-muted-foreground">
                Нет уведомлений
              </div>
            ) : (
              <div className="divide-y">
                {safeNotifications.slice(0, 20).map((notif) => (
                  <div
                    key={notif.id}
                    className={cn(
                      'p-4 hover:bg-muted/50 cursor-pointer transition-colors',
                      !notif.is_read && 'bg-blue-50/50 dark:bg-blue-950/20'
                    )}
                    onClick={() => handleClickNotification(notif)}
                  >
                    <div className="flex items-start gap-3">
                      <div
                        className={cn(
                          'h-2 w-2 rounded-full mt-2 shrink-0',
                          notif.is_read ? 'bg-transparent' : 'bg-blue-500'
                        )}
                      />
                      <div className="flex-1 min-w-0">
                        <p className="font-medium text-sm">{notif.title}</p>
                        {notif.body && (
                          <p className="text-xs text-muted-foreground mt-1 line-clamp-2">
                            {notif.body}
                          </p>
                        )}
                        <p className="text-xs text-muted-foreground mt-2">
                          {new Date(notif.created_at).toLocaleString('ru-RU')}
                        </p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </PopoverContent>
      </Popover>
    )
}