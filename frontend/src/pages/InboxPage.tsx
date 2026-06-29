import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { swipesApi } from '@/api/swipes'
import { AvatarImage } from '@/components/profile/AvatarImage'
import type { Swipe } from '@/types/swipe'
import {
  ArrowLeft,
  Check,
  X,
  MessageCircle,
  Sparkles,
  Calendar,
  FolderKanban,
} from 'lucide-react'

export default function InboxPage() {
  const [swipes, setSwipes] = useState<Swipe[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadInbox()
  }, [])

  const loadInbox = async () => {
    try {
      setIsLoading(true)
      const data = await swipesApi.getInbox()
      setSwipes(data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки заявок')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReview = async (swipeId: number, action: 'approved' | 'rejected') => {
    try {
      await swipesApi.review(swipeId, action)
      toast.success(action === 'approved' ? 'Заявка одобрена — создан матч!' : 'Заявка отклонена')
      setSwipes((prev) => prev.filter((s) => s.id !== swipeId))
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обработки заявки')
    }
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <MessageCircle className="h-8 w-8" />
            Входящие заявки
          </h1>
          <p className="text-muted-foreground mt-1">
            Отклики на ваши проекты
          </p>
        </div>
      </div>

      {/* Swipes List */}
      {swipes.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 text-center rounded-lg border bg-card p-12">
          <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
            <Sparkles className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Нет новых заявок</h3>
          <p className="text-muted-foreground mb-6 max-w-md">
            Когда кто-то откликнется на ваш проект, заявка появится здесь
          </p>
          <Button onClick={() => navigate('/projects')}>
            <FolderKanban className="h-4 w-4 mr-2" />
            Мои проекты
          </Button>
        </div>
      ) : (
        <div className="grid gap-4">
          {swipes.map((swipe) => (
            <div
              key={swipe.id}
              className="rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow"
            >
              <div className="flex items-start gap-4">
                {/* Аватар пользователя */}
                <div className="h-14 w-14 rounded-full overflow-hidden bg-primary/20 shrink-0">
                  <AvatarImage
                    fileId={swipe.user?.avatar_file_id}
                    fallback={swipe.user?.full_name?.[0]?.toUpperCase() || '?'}
                    className="text-xl"
                  />
                </div>

                {/* Информация */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-start justify-between gap-2 mb-1">
                    <div className="min-w-0">
                      <h3 className="text-lg font-semibold truncate">
                        {swipe.user?.full_name || 'Неизвестный пользователь'}
                      </h3>
                      <p className="text-sm text-muted-foreground">
                        Откликнулся на проект:{' '}
                        <span className="font-medium text-foreground">
                          {swipe.project?.title || 'Неизвестный проект'}
                        </span>
                      </p>
                    </div>
                  </div>

                  {/* Сообщение */}
                  {swipe.message && (
                    <div className="mt-3 p-3 rounded-lg bg-muted/50">
                      <p className="text-sm text-muted-foreground">
                        <span className="font-medium text-foreground">Сообщение:</span> {swipe.message}
                      </p>
                    </div>
                  )}

                  {/* Мета */}
                  <div className="flex items-center gap-4 text-xs text-muted-foreground mt-3">
                    <div className="flex items-center gap-1">
                      <Calendar className="h-3.5 w-3.5" />
                      <span>
                        {new Date(swipe.created_at).toLocaleDateString('ru-RU')}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              {/* Действия */}
              <div className="flex gap-3 mt-4 pt-4 border-t">
                <Button
                  size="sm"
                  onClick={() => handleReview(swipe.id, 'approved')}
                  className="flex-1 bg-green-600 hover:bg-green-700"
                >
                  <Check className="h-4 w-4 mr-2" />
                  Одобрить
                </Button>
                <Button
                  size="sm"
                  variant="outline"
                  onClick={() => handleReview(swipe.id, 'rejected')}
                  className="flex-1 text-destructive hover:text-destructive hover:bg-destructive/10"
                >
                  <X className="h-4 w-4 mr-2" />
                  Отклонить
                </Button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}