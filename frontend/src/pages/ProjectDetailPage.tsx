import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { projectsApi } from '@/api/project'
import { swipesApi } from '@/api/swipes'
import { useAuthStore } from '@/stores/authStore'
import type { Project } from '@/types/project'
import { AvatarImage } from '@/components/profile/AvatarImage'
import {
  ArrowLeft,
  MapPin,
  DollarSign,
  Users,
  Edit,
  Archive,
  UserPlus,
  CheckCircle,
  Trash2,
  Shield,
  MessageCircle,
} from 'lucide-react'
import { cn } from '@/utils/cn'

const roleLabels: Record<string, string> = {
  owner: 'Владелец',
  developer: 'Разработчик',
  teamlead: 'Тимлид',
  member: 'Участник',
}

export default function ProjectDetailPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const [project, setProject] = useState<Project | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [isApplying, setIsApplying] = useState(false)
  const [managingMemberId, setManagingMemberId] = useState<number | null>(null)

  useEffect(() => {
    if (id) {
      loadProject(Number(id))
    }
  }, [id])

  const loadProject = async (projectId: number) => {
    try {
      setIsLoading(true)
      const data = await projectsApi.getById(projectId)
      setProject(data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки проекта')
      navigate('/projects')
    } finally {
      setIsLoading(false)
    }
  }

  // Отклик через swipesApi, а не projectsApi
  const handleApply = async () => {
    if (!project || !user) return

    setIsApplying(true)
    try {
      await swipesApi.create({ project_id: project.id })
      toast.success('Заявка отправлена владельцу проекта')
    } catch (error: any) {
      const detail = error.response?.data?.detail
      const message = Array.isArray(detail)
        ? detail.map((d: any) => d.msg).join(', ')
        : typeof detail === 'string'
        ? detail
        : 'Ошибка отправки заявки'
      toast.error(message)
    } finally {
      setIsApplying(false)
    }
  }

  const handleArchive = async () => {
    if (!project || !confirm('Архивировать проект?')) return

    try {
      await projectsApi.delete(project.id)
      toast.success('Проект архивирован')
      navigate('/projects')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка архивации')
    }
  }

  const handleUpdateRole = async (userId: number, newRole: string) => {
    if (!project) return

    try {
      await projectsApi.updateMemberRole(project.id, userId, newRole)
      toast.success('Роль изменена')
      await loadProject(project.id)
      setManagingMemberId(null)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка изменения роли')
    }
  }

  const handleRemoveMember = async (userId: number) => {
    if (!project || !confirm('Исключить участника из проекта?')) return

    try {
      await projectsApi.removeMember(project.id, userId)
      toast.success('Участник исключён')
      await loadProject(project.id)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка исключения')
    }
  }

  const formatLabel: Record<string, string> = {
    remote: 'Удалённо',
    office: 'Офис',
    hybrid: 'Гибрид',
  }

  const paymentLabel: Record<string, string> = {
    volunteer: 'Волонтёрство',
    paid: 'Оплата',
    equity: 'Доля в проекте',
  }

  const statusLabel: Record<string, string> = {
    draft: 'Черновик',
    open: 'Открыт для набора',
    closed: 'Набор закрыт',
    completed: 'Завершён',
    archived: 'В архиве',
  }

  const statusColor: Record<string, string> = {
    draft: 'bg-yellow-100 text-yellow-800',
    open: 'bg-green-100 text-green-700',
    closed: 'bg-red-100 text-red-700',
    completed: 'bg-blue-100 text-blue-700',
    archived: 'bg-gray-100 text-gray-700',
  }

  const isOwner = project?.owner_id === user?.id
  const isMember = project?.members?.some(
    (m) => m.user_id === user?.id && m.is_active
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  if (!project) {
    return (
      <div className="flex items-center justify-center h-96">
        <p className="text-muted-foreground">Проект не найден</p>
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
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-bold">{project.title}</h1>
            <span
              className={cn(
                'px-3 py-1 rounded-full text-sm font-medium',
                statusColor[project.status]
              )}
            >
              {statusLabel[project.status]}
            </span>
          </div>
          <p className="text-muted-foreground">
            Создан {new Date(project.created_at).toLocaleDateString('ru-RU')}
          </p>
        </div>
      </div>

      {/* Owner Info */}
      <div className="rounded-lg border bg-card p-6">
        <h2 className="text-lg font-semibold mb-4">Владелец проекта</h2>
        <div className="flex items-center gap-4">
          <div className="h-16 w-16 rounded-full overflow-hidden bg-primary/20">
            <AvatarImage
              fileId={project.owner?.avatar_file_id}
              fallback={project.owner?.full_name?.[0]?.toUpperCase() || '?'}
              className="text-2xl"
            />
          </div>
          <div>
            <p className="text-lg font-medium">
              {project.owner?.full_name || 'Неизвестный автор'}
            </p>
            {isOwner && (
              <p className="text-sm text-muted-foreground">Это ваш проект</p>
            )}
          </div>
        </div>
      </div>

      {/* Project Info */}
      <div className="rounded-lg border bg-card p-6 space-y-6">
        <div>
          <h2 className="text-lg font-semibold mb-3">Описание</h2>
          <p className="text-muted-foreground whitespace-pre-wrap">
            {project.description}
          </p>
        </div>

        <div className="grid gap-4 md:grid-cols-2">
          <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
            <MapPin className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Формат работы</p>
              <p className="font-medium">
                {formatLabel[project.format] || project.format}
              </p>
            </div>
          </div>

          <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
            <DollarSign className="h-5 w-5 text-muted-foreground" />
            <div>
              <p className="text-sm text-muted-foreground">Тип оплаты</p>
              <p className="font-medium">
                {paymentLabel[project.payment_type] || project.payment_type}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Skills */}
      {project.skills && project.skills.length > 0 && (
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Требуемые навыки</h2>
          <div className="flex flex-wrap gap-2">
            {project.skills.map((skill) => (
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

      {/* Team Members */}
      {project.members && project.members.length > 0 && (
      <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
              <Users className="h-5 w-5" />
              Команда проекта ({project.members.filter((m) => m.is_active).length})
          </h2>
          <div className="space-y-3">
            {project.members.filter((m) => m.is_active)
                .map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/50 hover:bg-muted transition-colors cursor-pointer"
                  onClick={() => 
                    navigate(
                      member.user_id === user?.id
                      ? `/profile`
                      : `/users/${member.user_id}`
                    )
                  }
                >
                  <div className="flex items-center gap-3">
                    {/* Аватар участника */}
                    <div className="h-10 w-10 rounded-full overflow-hidden bg-primary/20 shrink-0">
                      <AvatarImage
                        fileId={member.user?.avatar_file_id}
                        fallback={member.user?.full_name?.[0]?.toUpperCase() || '?'}
                        className="text-sm"
                      />
                    </div>
                    <div>
                      {/* Имя участника */}
                      <p className="font-medium">
                        {member.user?.full_name || `Пользователь #${member.user_id}`}
                      </p>
                      <p className="text-sm text-muted-foreground capitalize">
                        {roleLabels[member.role] || member.role}
                      </p>
                    </div>
                  </div>
              
                  {/* Управление участниками (только для владельца) */}
                  {isOwner && member.user_id !== project.owner_id && (
                    <div className="flex items-center gap-2">
                      {managingMemberId === member.user_id ? (
                        <div className="flex items-center gap-2">
                          <select
                            value={member.role}
                            onChange={(e) =>
                              handleUpdateRole(member.user_id, e.target.value)
                            }
                            className="px-2 py-1 rounded border text-sm"
                          >
                            <option value="developer">Разработчик</option>
                            <option value="teamlead">Тимлид</option>
                            <option value="member">Участник</option>
                          </select>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setManagingMemberId(null)}
                          >
                            Отмена
                          </Button>
                        </div>
                      ) : (
                        <div className="flex items-center gap-1">
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => setManagingMemberId(member.user_id)}
                            title="Изменить роль"
                          >
                            <Shield className="h-4 w-4" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            onClick={() => handleRemoveMember(member.user_id)}
                            title="Исключить"
                            className="text-destructive hover:text-destructive hover:bg-destructive/10"
                          >
                            <Trash2 className="h-4 w-4" />
                          </Button>
                        </div>
                      )}
                    </div>
                  )}

                  {/* Статус */}
                  <div className="flex items-center gap-2">
                    {member.is_active ? (
                      <span className="px-2 py-1 rounded-full bg-green-100 text-green-700 text-xs font-medium">
                        Активен
                      </span>
                    ) : (
                      <span className="px-2 py-1 rounded-full bg-gray-100 text-gray-700 text-xs font-medium">
                        Покинул
                      </span>
                    )}
                    {member.joined_at && (
                      <span className="text-xs text-muted-foreground">
                        с {new Date(member.joined_at).toLocaleDateString('ru-RU')}
                      </span>
                    )}
                  </div>
                </div>
              ))}
          </div>
        </div>
      )}

      {/* Actions */}
      <div className="flex gap-3 sticky bottom-6">
        {isOwner ? (
          <>
          <Button
            size="lg"
            onClick={() => navigate(`/projects/${project.id}/chat`)}
          >
            <MessageCircle className='h-4 w-4 mr-2' />
            Чат проекта
          </Button>
            <Button
              size="lg"
              onClick={() => navigate(`/projects/${project.id}/edit`)}
            >
              <Edit className="h-4 w-4 mr-2" />
              Редактировать
            </Button>
            {project.status !== 'archived' && (
              <Button
                size="lg"
                variant="destructive"
                onClick={handleArchive}
              >
                <Archive className="h-4 w-4 mr-2" />
                Архивировать
              </Button>
            )}
          </>
        ) : isMember ? (
          <>
          <Button
            size="lg"
            onClick={() => navigate(`/projects/${project.id}/chat`)}
          >
            <MessageCircle className='h-4 w-4 mr-2' />
            Чат проекта
          </Button>
          <Button size="lg" disabled>
            <CheckCircle className="h-4 w-4 mr-2" />
            Вы участник проекта
          </Button>
          </> 
        ) : project.status === 'open' ? (
          <Button
            size="lg"
            onClick={handleApply}
            disabled={isApplying}
          >
            <UserPlus className="h-4 w-4 mr-2" />
            {isApplying ? 'Отправка...' : 'Откликнуться'}
          </Button>
        ) : (
          <Button size="lg" disabled>
            Проект не открыт для набора
          </Button>
        )}
      </div>
    </div>
  )
}