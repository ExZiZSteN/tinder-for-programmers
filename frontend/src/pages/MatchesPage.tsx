import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { matchesApi } from '@/api/matches'
import { useAuthStore } from '@/stores/authStore'
import { AvatarImage } from '@/components/profile/AvatarImage'
import type { Match } from '@/types/match'
import {
  MessageCircle,
  ArrowLeft,
  Sparkles,
  Calendar,
  XCircle,
  FolderKanban,
} from 'lucide-react'
import { cn } from '@/utils/cn'

export default function MatchesPage() {
  const [matches, setMatches] = useState<Match[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)

  useEffect(() => {
    loadMatches()
  }, [])

  const loadMatches = async () => {
    try {
      setIsLoading(true)
      const data = await matchesApi.list()
      setMatches(data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки матчей')
    } finally {
      setIsLoading(false)
    }
  }

  const handleClose = async (matchId: number) => {
    if (!confirm('Закрыть матч?')) return

    try {
      await matchesApi.close(matchId)
      toast.success('Матч закрыт')
      setMatches((prev) => prev.filter((m) => m.id !== matchId))
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка закрытия матча')
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
            Мои мэтчи
          </h1>
          <p className="text-muted-foreground mt-1">
            Проекты, которые приняли вашу заявку
          </p>
        </div>
      </div>

      {/* Matches List */}
      {matches.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-96 text-center rounded-lg border bg-card p-12">
          <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center mb-6">
            <Sparkles className="h-12 w-12 text-muted-foreground" />
          </div>
          <h3 className="text-xl font-semibold mb-2">Пока нет матчей</h3>
          <p className="text-muted-foreground mb-6 max-w-md">
            Откликайтесь на проекты в ленте. Когда владелец одобрит вашу заявку, матч появится здесь.
          </p>
          <Button onClick={() => navigate('/feed')}>
            Перейти в ленту
          </Button>
        </div>
      ) : (
        <div className="grid gap-4">
          {matches.map((match) => (
            <MatchCard
              key={match.id}
              match={match}
              currentUserId={user?.id}
              onViewProject={() => navigate(`/projects/${match.project_id}`)}
              onClose={() => handleClose(match.id)}
            />
          ))}
        </div>
      )}
    </div>
  )
}

function MatchCard({
  match,
  currentUserId,
  onViewProject,
  onClose,
}: {
  match: Match
  currentUserId?: number
  onViewProject: () => void
  onClose: () => void
}) {
  // Определяем: пользователь — владелец проекта или участник
  const isOwner = match.project?.owner?.id === currentUserId
  const personName = isOwner
    ? match.user?.full_name
    : match.project?.owner?.full_name
  const personAvatarFileId = isOwner
    ? match.user?.avatar_file_id
    : match.project?.owner?.avatar_file_id
  const projectTitle = match.project?.title || 'Проект'

  return (
    <div className="rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
      <div className="flex items-start gap-4">
        {/* Аватар */}
        <div className="h-14 w-14 rounded-full overflow-hidden bg-primary/20 shrink-0">
          <AvatarImage
            fileId={personAvatarFileId}
            fallback={personName?.[0]?.toUpperCase() || '?'}
            className="text-xl"
          />
        </div>

        {/* Информация */}
        <div className="flex-1 min-w-0">
          <div className="flex items-start justify-between gap-2 mb-1">
            <div className="min-w-0">
              <h3 className="text-lg font-semibold truncate">{projectTitle}</h3>
              <p className="text-sm text-muted-foreground">
                {isOwner ? 'Участник: ' : 'Владелец: '}
                {personName || 'Неизвестный пользователь'}
              </p>
            </div>

            {/* Статус */}
            <span
              className={cn(
                'px-2 py-1 rounded-full text-xs font-medium shrink-0',
                match.status === 'active'
                  ? 'bg-green-100 text-green-700'
                  : match.status === 'completed'
                  ? 'bg-blue-100 text-blue-700'
                  : 'bg-gray-100 text-gray-700'
              )}
            >
              {match.status === 'active'
                ? 'Активен'
                : match.status === 'completed'
                ? 'Завершён'
                : 'Закрыт'}
            </span>
          </div>

          {/* Описание проекта */}
          {match.project?.description && (
            <p className="text-sm text-muted-foreground line-clamp-2 mb-3">
              {match.project.description}
            </p>
          )}

          {/* Мета */}
          <div className="flex items-center gap-4 text-xs text-muted-foreground">
            <div className="flex items-center gap-1">
              <Calendar className="h-3.5 w-3.5" />
              <span>
                {new Date(match.created_at).toLocaleDateString('ru-RU')}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Действия */}
      <div className="flex gap-3 mt-4 pt-4 border-t">
        <Button
          size="sm"
          variant="outline"
          onClick={onViewProject}
          className="flex-1"
        >
          <FolderKanban className="h-4 w-4 mr-2" />
          Открыть проект
        </Button>
        {match.status === 'active' && (
          <Button
            size="sm"
            variant="ghost"
            onClick={onClose}
            className="text-destructive hover:text-destructive hover:bg-destructive/10"
          >
            <XCircle className="h-4 w-4 mr-2" />
            Закрыть
          </Button>
        )}
      </div>
    </div>
  )
}