import { useEffect, useState } from "react";
import { useParams, useNavigate, Link } from "react-router-dom";
import { toast } from "sonner";
import { Button } from "@/components/ui/button";
import { projectsApi } from "@/api/project";
import { useAuthStore } from "@/stores/authStore";
import type { Project } from "@/types/project";
import { AvatarImage } from "@/components/profile/AvatarImage";
import {
    ArrowLeft,
    MapPin,
    DollarSign,
    Clock,
    Users,
    Edit,
    Archive,
    UserPlus,
    CheckCircle,
} from 'lucide-react'
import { cn } from '@/utils/cn'
import { string } from "zod";

export default function ProjectDetailPage() {
    const { id } = useParams<{ id: string}> ()
    const navigate = useNavigate()
    const user = useAuthStore((state) => state.user)
    const [project, setProject] = useState<Project | null>(null)
    const [isLoading, setIsLoading] = useState(true)
    const [isApplying, setIsApplying] = useState(false)

    useEffect(() => {
        if (id) {
            loadProject(Number(id))
        }
    }, [id])

    const loadProject = async (projectId: number) => {
        try{
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

    const handleApply = async () => {
        if (!project || !user) return

        setIsApplying(true)
        try{
            // await projectsApi.apply(project.id)
            toast.success('Вы откликнулись на проект!')
            await loadProject(project.id)
        } catch (error: any) {
            toast.error(error.response?.data?.detail || 'Ошибка отклика')
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
        } catch (error: any){
            toast.error(error.response?.data?.detail || 'Ошибка архивации')
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
    const isMember = project?.members?.some(m => m.user_id === user?.id && m.is_active)

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
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div className="flex-1">
            <div className="flex items-center gap-3 mb-2">
              <h1 className="text-3xl font-bold">{project.title}</h1>
              <span className={cn('px-3 py-1 rounded-full text-sm font-medium', statusColor[project.status])}>
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
              <p className="text-lg font-medium">{project.owner?.full_name || 'Неизвестный автор'}</p>
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
            <p className="text-muted-foreground whitespace-pre-wrap">{project.description}</p>
          </div>

          <div className="grid gap-4 md:grid-cols-2">
            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
              <MapPin className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Формат работы</p>
                <p className="font-medium">{formatLabel[project.format] || project.format}</p>
              </div>
            </div>

            <div className="flex items-center gap-3 p-4 rounded-lg bg-muted/50">
              <DollarSign className="h-5 w-5 text-muted-foreground" />
              <div>
                <p className="text-sm text-muted-foreground">Тип оплаты</p>
                <p className="font-medium">{paymentLabel[project.payment_type] || project.payment_type}</p>
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
              Команда проекта ({project.members.length})
            </h2>
            <div className="space-y-3">
              {project.members.map((member) => (
                <div
                  key={member.user_id}
                  className="flex items-center justify-between p-3 rounded-lg bg-muted/50"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    {/* Аватар участника */}
                    <div className="h-10 w-10 shrink-0 overflow-hidden rounded-full bg-primary/20">
                      <AvatarImage
                        fileId={member.user?.avatar_file_id}
                        fallback={member.user?.full_name?.[0]?.toUpperCase() || '?'}
                        className="text-sm"
                      />
                    </div>
                    <div className="min-w-0">
                      {/* Имя участника */}
                      <p className="font-medium truncate">
                        {member.user?.full_name || `Пользователь #${member.user_id}`}
                      </p>
                      <p className="text-sm text-muted-foreground capitalize">
                        {member.role}
                      </p>
                    </div>
                  </div>

                  {/* Статус и дата */}
                  <div className="flex items-center gap-2 shrink-0 ml-4">
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
                      <span className="text-xs text-muted-foreground hidden sm:inline">
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
            <Button size="lg" disabled>
              <CheckCircle className="h-4 w-4 mr-2" />
              Вы участник проекта
            </Button>
          ) : project.status === 'open' ? (
            <Button
              size="lg"
              onClick={handleApply}
              disabled={isApplying}
            >
              <UserPlus className="h-4 w-4 mr-2" />
              {isApplying ? 'Отправка...' : 'Откликнуться на проект'}
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