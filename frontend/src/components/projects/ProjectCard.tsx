import { MapPin, DollarSign, Clock, Users } from 'lucide-react'
import type { Project } from '@/types/project'
import { cn } from '@/utils/cn'

interface ProjectCardProps {
    project: Project
}

export function ProjectCard({ project }: ProjectCardProps){
    const formatLabel = {
        remote: 'Удалённо',
        office: 'Офис',
        hybrid: 'Гибрид'
    }

    const paymentLabel = {
        volunteer: 'Волонтерство',
        paid: 'Оплата',
        equity: 'Доля'
    }

    const statusLabel = {
        draft: 'Черновик',
        open: 'Открыт',
        closed: 'Закрыт',
        completed: 'Завершён',
        archived: 'Заморожен',
    }

    const statusColor = {
        draft: 'bg-gray-100 text-gray-700',
        open: 'bg-green-100 text-green-700',
        closed: 'bg-red-100 text-red-700',
        completed: 'bg-blue-100 text-blue-700',
        archived: 'bg-gray-100 text-gray-700',
    }

  return (
    <div className="rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-semibold mb-1 truncate">
            {project.title}
          </h3>
          <p className="text-sm text-muted-foreground truncate">
            от {project.owner?.full_name || 'Неизвестный автор'}
          </p>
        </div>
        <span
          className={cn(
            'px-2 py-1 rounded text-xs font-medium shrink-0 ml-2',
            statusColor[project.status]
          )}
        >
          {statusLabel[project.status]}
        </span>
      </div>

      {/* Description */}
      <p className="text-sm text-muted-foreground mb-4 line-clamp-2">
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
            <span>{project.members.length}</span>
          </div>
        )}
      </div>

      {/* Skills */}
      {project.skills && project.skills.length > 0 && (
        <div className="flex flex-wrap gap-2">
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
        </div>
      )}
    </div>
  )
}