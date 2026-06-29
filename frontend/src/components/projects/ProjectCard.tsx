import { MapPin, DollarSign, Clock, Users } from 'lucide-react'
import type { Project } from '@/types/project'
import { cn } from '@/utils/cn'

interface ProjectCardProps {
  project: Project
  isOwner?: boolean
}

export function ProjectCard({ project, isOwner = false }: ProjectCardProps) {
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

  const statusLabel: Record<string, string> = {
    draft: 'Черновик',
    open: 'Открыт',
    closed: 'Закрыт',
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

  const activeMembersCount = project.members?.filter(m => m.is_active).length

  return (
    <div className="rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow flex flex-col h-full group/card">
      {/* Header */}
      <div className="flex items-start justify-between gap-2 mb-4">
        <div className="flex-1 min-w-0">
          <h3
            className="text-lg font-semibold leading-tight break-words"
            title={project.title}
          >
            {project.title}
          </h3>
          <p className="text-sm text-muted-foreground truncate mt-1">
            от {project.owner?.full_name || 'Неизвестный автор'}
          </p>
        </div>
        {/* Статус исчезает при наведении (только если isOwner) */}
        {isOwner ? (
          <span
            className={cn(
              'px-2 py-1 rounded text-xs font-medium shrink-0 transition-opacity duration-200',
              'group-hover:opacity-0',  // Скрываем при наведении
              statusColor[project.status]
            )}
          >
            {statusLabel[project.status]}
          </span>
        ) : (
          <span
            className={cn(
              'px-2 py-1 rounded text-xs font-medium shrink-0',
              statusColor[project.status]
            )}
          >
            {statusLabel[project.status]}
          </span>
        )}
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2 flex-1">
        {project.description}
      </p>

      {/* Meta */}
      <div className="flex flex-wrap gap-3 mb-4 text-sm">
        <div className="flex items-center gap-1 text-muted-foreground">
          <MapPin className="h-4 w-4" />
          <span>{formatLabel[project.format] || project.format}</span>
        </div>
        <div className="flex items-center gap-1 text-muted-foreground">
          <DollarSign className="h-4 w-4" />
          <span>{paymentLabel[project.payment_type] || project.payment_type}</span>
        </div>
        <div className="flex items-center gap-1 text-muted-foreground">
          <Clock className="h-4 w-4" />
          <span>{new Date(project.created_at).toLocaleDateString('ru-RU')}</span>
        </div>
        {project.members && project.members.length > 0 && (
          <div className="flex items-center gap-1 text-muted-foreground">
            <Users className="h-4 w-4" />
            <span>{activeMembersCount}</span>
          </div>
        )}
      </div>

      {/* Skills + Owner badge */}
      <div className="flex flex-wrap items-center gap-2">
        {project.skills && project.skills.length > 0 && (
          <>
            {project.skills.slice(0, 5).map((skill) => (
              <span
                key={skill.id}
                className="px-2 py-1 rounded-full bg-primary/10 text-primary text-xs"
              >
                {skill.name}
              </span>
            ))}
            {project.skills.length > 5 && (
              <span className="px-2 py-1 text-xs text-muted-foreground">
                +{project.skills.length - 5}
              </span>
            )}
          </>
        )}
        {isOwner && (
          <span className="ml-auto px-2 py-1 rounded-full bg-secondary text-secondary-foreground text-xs font-medium shrink-0">
            Владелец
          </span>
        )}
      </div>
    </div>
  )
}