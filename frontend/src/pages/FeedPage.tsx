import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { swipesApi } from '@/api/swipes'
import { useAuthStore } from '@/stores/authStore'
import type { Project } from '@/types/project'
import { AvatarImage } from '@/components/profile/AvatarImage'
import {
  Heart,
  X,
  MapPin,
  DollarSign,
  Users,
  MessageCircle,
  RefreshCw,
  Sparkles,
  Send,
} from 'lucide-react'
import { cn } from '@/utils/cn'

export default function FeedPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [currentIndex, setCurrentIndex] = useState(0)
  const [isLoading, setIsLoading] = useState(true)
  const [isSwiping, setIsSwiping] = useState(false)
  const [swipeDirection, setSwipeDirection] = useState<'left' | 'right' | null>(null)
  const [message, setMessage] = useState('')
  const [showMessageInput, setShowMessageInput] = useState(false)
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)

  useEffect(() => {
    loadFeed()
  }, [])

  const loadFeed = async () => {
    try {
      setIsLoading(true)
      const data = await swipesApi.getFeed({ limit: 20 })
      // Фильтруем свои проекты
      const filtered = data.filter((p) => p.owner_id !== user?.id)
      setProjects(filtered)
      setCurrentIndex(0)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки ленты')
    } finally {
      setIsLoading(false)
    }
  }

  // Лайк = отправить заявку на участие
  const handleLike = async () => {
    if (currentIndex >= projects.length || isSwiping) return

    const project = projects[currentIndex]
    setIsSwiping(true)
    setSwipeDirection('right')

    try {
      await swipesApi.create({
        project_id: project.id,
        message: message.trim() || undefined,
      })

      toast.success('Заявка отправлена владельцу проекта')
      setMessage('')
      setShowMessageInput(false)

      setTimeout(() => {
        setCurrentIndex((prev) => prev + 1)
        setSwipeDirection(null)
        setIsSwiping(false)
      }, 300)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка отправки заявки')
      setIsSwiping(false)
      setSwipeDirection(null)
    }
  }

  // Дизлайк = просто пропустить проект
  const handleDislike = () => {
    if (currentIndex >= projects.length || isSwiping) return

    setSwipeDirection('left')
    setTimeout(() => {
      setCurrentIndex((prev) => prev + 1)
      setSwipeDirection(null)
      setMessage('')
      setShowMessageInput(false)
    }, 300)
  }

  const formatLabel: Record<string, string> = {
    remote: 'Удалённо',
    office: 'Офис',
    hybrid: 'Гибрид',
  }

  const paymentLabel: Record<string, string> = {
    volunteer: 'Волонтёрство',
    paid: 'Оплата',
    equity: 'Доля',
  }

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (currentIndex >= projects.length) {
    return (
      <div className="flex flex-col items-center justify-center h-[70vh] text-center">
        <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
          <Sparkles className="h-12 w-12 text-muted-foreground" />
        </div>
        <h3 className="text-2xl font-semibold mb-2">Проекты закончились</h3>
        <p className="text-muted-foreground mb-8 max-w-md">
          Вы просмотрели все доступные проекты. Загляните позже или обновите ленту.
        </p>
        <div className="flex gap-3">
          <Button onClick={loadFeed} size="lg">
            <RefreshCw className="h-4 w-4 mr-2" />
            Обновить ленту
          </Button>
          <Button variant="outline" size="lg" onClick={() => navigate('/matches')}>
            <MessageCircle className="h-4 w-4 mr-2" />
            Мои матчи
          </Button>
        </div>
      </div>
    )
  }

  const currentProject = projects[currentIndex]
  const currentProjectMembers = projects[currentIndex].members?.filter(m => m.is_active).length

  return (
    <div className="max-w-2xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Лента проектов</h1>
          <p className="text-muted-foreground mt-1">
            Откликайтесь на проекты, которые вам интересны
          </p>
        </div>
        <Button variant="outline" onClick={() => navigate('/matches')}>
          <MessageCircle className="h-4 w-4 mr-2" />
          Матчи
        </Button>
      </div>

      {/* Project Card */}
      <div
        className={cn(
          'relative transition-all duration-300',
          swipeDirection === 'left' && 'translate-x-[-120%] rotate-[-15deg] opacity-0',
          swipeDirection === 'right' && 'translate-x-[120%] rotate-[15deg] opacity-0'
        )}
      >
        <div className="rounded-lg border bg-card shadow-lg overflow-hidden">
          {/* Header с владельцем */}
          <div className="p-6 border-b bg-muted/30">
            <div className="flex items-center gap-4">
              <div className="h-14 w-14 rounded-full overflow-hidden bg-primary/20 shrink-0">
                <AvatarImage
                  fileId={currentProject.owner?.avatar_file_id}
                  fallback={currentProject.owner?.full_name?.[0]?.toUpperCase() || '?'}
                  className="text-xl"
                />
              </div>
              <div className="min-w-0 flex-1">
                <p className="font-semibold truncate">
                  {currentProject.owner?.full_name || 'Неизвестный автор'}
                </p>
                <p className="text-sm text-muted-foreground">
                  Владелец проекта
                </p>
              </div>
            </div>
          </div>

          {/* Контент */}
          <div className="p-6 space-y-6">
            <h2 className="text-2xl font-bold leading-tight">
              {currentProject.title}
            </h2>

            <p className="text-muted-foreground leading-relaxed">
              {currentProject.description}
            </p>

            {/* Мета-информация */}
            <div className="grid gap-3 sm:grid-cols-2">
              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <MapPin className="h-5 w-5 text-muted-foreground shrink-0" />
                <div className="min-w-0">
                  <p className="text-xs text-muted-foreground">Формат</p>
                  <p className="font-medium text-sm">
                    {formatLabel[currentProject.format] || currentProject.format}
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-3 p-3 rounded-lg bg-muted/50">
                <DollarSign className="h-5 w-5 text-muted-foreground shrink-0" />
                <div className="min-w-0">
                  <p className="text-xs text-muted-foreground">Оплата</p>
                  <p className="font-medium text-sm">
                    {paymentLabel[currentProject.payment_type] || currentProject.payment_type}
                  </p>
                </div>
              </div>
            </div>

            {/* Навыки */}
            {currentProject.skills && currentProject.skills.length > 0 && (
              <div>
                <p className="text-sm font-medium mb-2">Требуемые навыки:</p>
                <div className="flex flex-wrap gap-2">
                  {currentProject.skills.map((skill) => (
                    <span
                      key={skill.id}
                      className="px-3 py-1 rounded-full bg-primary/10 text-primary text-sm"
                    >
                      {skill.name}
                    </span>
                  ))}
                </div>
              </div>
            )}

            {/* Команда */}
            {currentProject.members && currentProject.members.length > 0 && (
              <div className="flex items-center gap-2 text-sm text-muted-foreground">
                <Users className="h-4 w-4" />
                <span>В команде уже {currentProjectMembers} человек</span>
              </div>
            )}

            {/* Сообщение к заявке */}
            {showMessageInput && (
              <div className="space-y-2">
                <label className="text-sm font-medium">
                  Сообщение владельцу (необязательно):
                </label>
                <textarea
                  value={message}
                  onChange={(e) => setMessage(e.target.value)}
                  placeholder="Расскажите о себе, почему хотите присоединиться..."
                  className="w-full min-h-[100px] rounded-lg border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                  rows={4}
                />
              </div>
            )}
          </div>
        </div>

        {/* Swipe Buttons */}
        <div className="flex justify-center gap-6 mt-6">
          <Button
            size="icon"
            variant="outline"
            onClick={handleDislike}
            disabled={isSwiping}
            className="h-16 w-16 rounded-full border-2 border-destructive/30 hover:border-destructive hover:bg-destructive/10 transition-all"
            title="Пропустить"
          >
            <X className="h-8 w-8 text-destructive" />
          </Button>

          <Button
            size="icon"
            onClick={() => {
              if (!showMessageInput) {
                setShowMessageInput(true)
              } else {
                handleLike()
              }
            }}
            disabled={isSwiping}
            className={cn(
              'h-16 w-16 rounded-full border-2 transition-all',
              showMessageInput
                ? 'border-green-500 bg-green-500 text-white hover:bg-green-600'
                : 'border-green-500/30 hover:border-green-500 hover:bg-green-500/10 bg-transparent text-green-500 hover:text-green-500'
            )}
            title={showMessageInput ? 'Отправить заявку' : 'Добавить сообщение'}
          >
            {showMessageInput ? (
              <Send className="h-8 w-8" />
            ) : (
              <Heart className="h-8 w-8" />
            )}
          </Button>
        </div>
      </div>

      {/* Progress */}
      <div className="text-center text-sm text-muted-foreground">
        Проект {currentIndex + 1} из {projects.length}
      </div>
    </div>
  )
}