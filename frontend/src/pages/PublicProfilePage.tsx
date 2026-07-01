import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { apiClient } from '@/api/client'
import { useAuthStore } from '@/stores/authStore'
import { AvatarImage } from '@/components/profile/AvatarImage'
import {
  ArrowLeft,
  Globe,
  Calendar,
  Briefcase,
  MessageCircle,
} from 'lucide-react'

interface PublicUser {
  id: number
  full_name: string
  bio?: string
  github_url?: string
  linkedin_url?: string
  portfolio_url?: string
  experience_years: number
  avatar_file_id?: number
  created_at: string
  skills?: { id: number; name: string }[]
}

export default function PublicProfilePage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const currentUser = useAuthStore((state) => state.user)
  const [user, setUser] = useState<PublicUser | null>(null)
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    const loadUser = async () => {
      try {
        setIsLoading(true)
        const response = await apiClient.get(`/users/${id}/public`)
        setUser(response.data)
      } catch (error: any) {
        toast.error(error.response?.data?.detail || 'Ошибка загрузки профиля')
        navigate('/feed')
      } finally {
        setIsLoading(false)
      }
    }
    if (id) loadUser()
  }, [id, navigate])

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!user) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Пользователь не найден</p>
      </div>
    )
  }

  const isMe = currentUser?.id === user.id

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <h1 className="text-3xl font-bold">Профиль</h1>
      </div>

      {/* Основная информация */}
      <div className="rounded-lg border bg-card p-6">
        <div className="flex items-start gap-6">
          <div className="h-24 w-24 rounded-full overflow-hidden bg-primary/20 shrink-0">
            <AvatarImage
              fileId={user.avatar_file_id}
              fallback={user.full_name?.[0]?.toUpperCase() || '?'}
              className="text-3xl"
            />
          </div>

          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h2 className="text-2xl font-bold">{user.full_name}</h2>
              {isMe && (
                <span className="px-2 py-0.5 text-xs bg-primary/10 text-primary rounded-full">
                  Это вы
                </span>
              )}
            </div>

            {user.bio && (
              <p className="text-muted-foreground whitespace-pre-wrap mb-4">
                {user.bio}
              </p>
            )}

            <div className="flex flex-wrap gap-4 text-sm text-muted-foreground">
              <div className="flex items-center gap-1">
                <Briefcase className="h-4 w-4" />
                <span>Опыт: {user.experience_years} лет</span>
              </div>
              <div className="flex items-center gap-1">
                <Calendar className="h-4 w-4" />
                <span>С нами с {new Date(user.created_at).toLocaleDateString('ru-RU')}</span>
              </div>
            </div>
          </div>

          {/* Кнопка написать (если это не свой профиль) */}
          {!isMe && (
            <Button
              variant="outline"
              onClick={() => {
                toast.info('Функция личных сообщений в разработке')
              }}
            >
              <MessageCircle className="h-4 w-4 mr-2" />
              Написать
            </Button>
          )}
        </div>
      </div>

      {/* Навыки */}
      {user.skills && user.skills.length > 0 && (
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">Навыки</h3>
          <div className="flex flex-wrap gap-2">
            {user.skills.map((skill) => (
              <span
                key={skill.id}
                className="px-3 py-1.5 rounded-full bg-primary/10 text-primary text-sm font-medium"
              >
                {skill.name}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Социальные ссылки */}
      {(user.github_url || user.linkedin_url || user.portfolio_url) && (
        <div className="rounded-lg border bg-card p-6">
          <h3 className="text-lg font-semibold mb-4">Контакты</h3>
          <div className="flex flex-wrap gap-3">
            {user.github_url && (
              <a
                href={user.github_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
              >

                <span className="text-sm">GitHub</span>
              </a>
            )}
            {user.linkedin_url && (
              <a
                href={user.linkedin_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
              >

                <span className="text-sm">LinkedIn</span>
              </a>
            )}
            {user.portfolio_url && (
              <a
                href={user.portfolio_url}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 px-4 py-2 rounded-lg bg-muted hover:bg-muted/80 transition-colors"
              >
                <Globe className="h-4 w-4" />
                <span className="text-sm">Портфолио</span>
              </a>
            )}
          </div>
        </div>
      )}
    </div>
  )
}