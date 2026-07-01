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
  Inbox as InboxIcon,
  Send,
} from 'lucide-react'

type TabType = 'incoming' | 'my'

export default function InboxPage() {
  const [activeTab, setActiveTab] = useState<TabType>('incoming')
  const [incomingSwipes, setIncomingSwipes] = useState<Swipe[]>([])
  const [mySwipes, setMySwipes] = useState<Swipe[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()

  useEffect(() => {
    loadAll()
  }, [])

  const loadAll = async () => {
    try {
      setIsLoading(true)
      const [incoming, my] = await Promise.all([
        swipesApi.getInbox(),
        swipesApi.getMySwipes(),
      ])
      setIncomingSwipes(incoming)
      setMySwipes(my)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки')
    } finally {
      setIsLoading(false)
    }
  }

  const handleReview = async (swipeId: number, action: 'approved' | 'rejected') => {
    try {
      await swipesApi.review(swipeId, action)
      toast.success(action === 'approved' ? '✅ Заявка одобрена!' : 'Заявка отклонена')
      setIncomingSwipes((prev) => prev.filter((s) => s.id !== swipeId))
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обработки')
    }
  }

  const currentSwipes = activeTab === 'incoming' ? incomingSwipes : mySwipes

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
            <InboxIcon className="h-8 w-8" />
            Заявки
          </h1>
          <p className="text-muted-foreground mt-1">
            Входящие отклики и ваши отклики на проекты
          </p>
        </div>
      </div>

      {/* Вкладки */}
      <div className="flex gap-2 border-b">
        <button
          onClick={() => setActiveTab('incoming')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'incoming'
              ? 'text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <InboxIcon className="h-4 w-4 inline mr-2" />
          Входящие
          {incomingSwipes.length > 0 && (
            <span className="ml-2 px-2 py-0.5 text-xs bg-primary text-primary-foreground rounded-full">
              {incomingSwipes.length}
            </span>
          )}
          {activeTab === 'incoming' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>

        <button
          onClick={() => setActiveTab('my')}
          className={`px-4 py-2 font-medium transition-colors relative ${
            activeTab === 'my'
              ? 'text-primary'
              : 'text-muted-foreground hover:text-foreground'
          }`}
        >
          <Send className="h-4 w-4 inline mr-2" />
          Мои отклики
          {mySwipes.length > 0 && (
            <span className="ml-2 px-2 py-0.5 text-xs bg-muted text-foreground rounded-full">
              {mySwipes.length}
            </span>
          )}
          {activeTab === 'my' && (
            <div className="absolute bottom-0 left-0 right-0 h-0.5 bg-primary" />
          )}
        </button>
      </div>

      {/* Контент */}
      {currentSwipes.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 text-center rounded-lg border bg-card p-12">
          <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
            <Sparkles className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">
            {activeTab === 'incoming' ? 'Нет входящих заявок' : 'У вас нет отправленных откликов'}
          </h3>
          <p className="text-muted-foreground mb-6 max-w-md">
            {activeTab === 'incoming'
              ? 'Когда кто-то откликнется на ваш проект, заявка появится здесь'
              : 'Откликайтесь на интересные проекты в ленте'}
          </p>
          <Button onClick={() => navigate(activeTab === 'incoming' ? '/projects' : '/feed')}>
            <FolderKanban className="h-4 w-4 mr-2" />
            {activeTab === 'incoming' ? 'Мои проекты' : 'Перейти в ленту'}
          </Button>
        </div>
      ) : (
        <div className="grid gap-4">
          {currentSwipes.map((swipe) => (
            <SwipeCard
              key={swipe.id}
              swipe={swipe}
              isMySwipe={activeTab === 'my'}
              onReview={handleReview}
              navigate={navigate}
            />
          ))}
        </div>
      )}
    </div>
  )
}

// Отдельный компонент карточки свайпа
interface SwipeCardProps {
  swipe: Swipe
  isMySwipe: boolean
  onReview: (swipeId: number, action: 'approved' | 'rejected') => void
  navigate: (path: string) => void
}

function SwipeCard({ swipe, isMySwipe, onReview, navigate }: SwipeCardProps) {
  // Для "Входящих" — показываем разработчика и его проект
  // Для "Мои отклики" — показываем владельца проекта
  const otherUser = isMySwipe ? swipe.project?.owner : swipe.user
  const projectTitle = swipe.project?.title

  return (
    <div className="rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start gap-4">
        <div className="h-14 w-14 rounded-full overflow-hidden bg-primary/20 shrink-0">
          <AvatarImage
            fileId={otherUser?.avatar_file_id}
            fallback={otherUser?.full_name?.[0]?.toUpperCase() || '?'}
            className="text-xl"
          />
        </div>

        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold truncate">
            {otherUser?.full_name || 'Неизвестный пользователь'}
          </h3>
          <p className="text-sm text-muted-foreground">
            {isMySwipe ? (
              <>Отклик на проект: <span className="font-medium text-foreground">{projectTitle}</span></>
            ) : (
              <>Откликнулся на проект: <span className="font-medium text-foreground">{projectTitle}</span></>
            )}
          </p>

          {swipe.message && (
            <div className="mt-3 p-3 rounded-lg bg-muted/50">
              <p className="text-sm text-muted-foreground">
                <span className="font-medium text-foreground">Сообщение:</span> {swipe.message}
              </p>
            </div>
          )}

          <div className="flex items-center gap-4 text-xs text-muted-foreground mt-3">
            <div className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              <span>{new Date(swipe.created_at).toLocaleDateString('ru-RU')}</span>
            </div>
            <StatusBadge status={swipe.status} />
          </div>
        </div>
      </div>

      {/* Действия */}
      <div className="flex gap-3 mt-4 pt-4 border-t">
        {/* Кнопка Чат — доступна обоим, если есть match_id */}
        {swipe.match_id && (
          <Button
            size="sm"
            variant="outline"
            onClick={() => navigate(`/matches/${swipe.match_id}/chat`)}
            className="flex-1"
          >
            <MessageCircle className="h-4 w-4 mr-2" />
            Чат
          </Button>
        )}

        {/* Для "Входящих" — кнопки Одобрить/Отклонить (только для pending) */}
        {!isMySwipe && swipe.status === 'pending' && (
          <>
            <Button
              size="sm"
              onClick={() => onReview(swipe.id, 'approved')}
              className="flex-1 bg-green-600 hover:bg-green-700"
            >
              <Check className="h-4 w-4 mr-2" />
              Одобрить
            </Button>
            <Button
              size="sm"
              variant="outline"
              onClick={() => onReview(swipe.id, 'rejected')}
              className="flex-1 text-destructive hover:text-destructive hover:bg-destructive/10"
            >
              <X className="h-4 w-4 mr-2" />
              Отклонить
            </Button>
          </>
        )}

        {/* Для "Моих откликов" — только статус */}
        {isMySwipe && (
          <div className="flex-1 flex items-center justify-end">
            <StatusBadge status={swipe.status} large />
          </div>
        )}
      </div>
    </div>
  )
}

// Компонент бейджа статуса
function StatusBadge({ status, large = false }: { status: string; large?: boolean }) {
  const config: Record<string, { label: string; className: string }> = {
    pending: {
      label: 'На рассмотрении',
      className: 'bg-amber-100 text-amber-800',
    },
    approved: {
      label: 'Одобрено',
      className: 'bg-green-100 text-green-800',
    },
    rejected: {
      label: 'Отклонено',
      className: 'bg-red-100 text-red-800',
    },
    withdrawn: {
      label: 'Отозвано',
      className: 'bg-gray-100 text-gray-800',
    },
  }

  const { label, className } = config[status] || config.pending

  return (
    <span className={`px-2 py-1 rounded-full font-medium ${className} ${large ? 'text-sm' : 'text-xs'}`}>
      {label}
    </span>
  )
}