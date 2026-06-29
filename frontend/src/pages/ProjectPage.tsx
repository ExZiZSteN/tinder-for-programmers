import { useEffect, useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { ProjectCard } from '@/components/projects/ProjectCard'
import { projectsApi } from '@/api/project'
import { useAuthStore } from '@/stores/authStore'
import type { Project } from '@/types/project'
import { FolderKanban, Plus, Archive, Edit, Trash2 } from 'lucide-react'

export default function ProjectsPage() {
  const [projects, setProjects] = useState<Project[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const user = useAuthStore((state) => state.user)
  const navigate = useNavigate()

  useEffect(() => {
    loadMyProjects()
  }, [])

  const loadMyProjects = async () => {
    try {
      setIsLoading(true)
      const data = await projectsApi.getMyProjects()
      setProjects(data)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки проектов')
    } finally {
      setIsLoading(false)
    }
  }

  const handleArchive = async (projectId: number) => {
    if (!confirm('Архивировать проект?')) return
    
    try {
      await projectsApi.delete(projectId)
      await loadMyProjects()
      toast.success('Проект архивирован')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка архивации')
    }
  }

  const handleRestore = async (projectId: number) => {
    try {
      await projectsApi.restore(projectId)
      await loadMyProjects()
      toast.success('Проект восстановлен')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка восстановления')
    }
  }

  if (isLoading) {
    return (
      <div className='flex items-center justify-center h-96'>
        <div className='h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin' />
      </div>
    )
  }

  return (
    <div className='max-w-7xl mx-auto space-y-6'>
      {/* Header */}
      <div className='flex items-center justify-between'>
        <div>
          <h1 className='text-3xl font-bold flex items-center gap-3'>
            <FolderKanban className='h-8 w-8' />
            Мои проекты
          </h1>
          <p className='text-muted-foreground mt-1'>
            Проекты, в которых вы участвуете
          </p>
        </div>
        <Button 
          size='lg' 
          onClick={() => navigate('/projects/create')}
        >
          <Plus className='h-4 w-4 mr-2' />
          Создать проект
        </Button>
      </div>

      {/* Projects List */}
      {projects.length === 0 ? (
        <div className='flex flex-col items-center justify-center h-96 text-center rounded-lg border bg-card p-12'>
          <FolderKanban className='h-16 w-16 text-muted-foreground mb-4' />
          <h3 className='text-xl font-semibold mb-2'>У вас пока нет проектов</h3>
          <p className='text-muted-foreground mb-6 max-w-md'>
            Создайте свой первый проект или откликнитесь на чужой в ленте
          </p>
          <div className='flex gap-3'>
            <Button onClick={() => navigate('/projects/create')}>
              <Plus className='h-4 w-4 mr-2' />
              Создать проект
            </Button>
            <Button variant='outline' onClick={() => navigate('/feed')}>
              Перейти в ленту
            </Button>
          </div>
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
  {projects.map((project) => (
    <div key={project.id} className="relative group">
      <Link to={`/projects/${project.id}`}>
        <ProjectCard
          project={project}
          isOwner={project.owner_id === user?.id}
        />
      </Link>
      
      {/* Иконки действий — на месте статуса */}
      {project.owner_id === user?.id && (
        <div className="absolute top-2 right-2 flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity duration-200">
            {project.status === 'archived' ? (
              <button
                onClick={(e) => {
                  e.preventDefault()
                  e.stopPropagation()
                  handleRestore(project.id)
                }}
                className="p-1.5 rounded-md bg-card hover:bg-muted shadow-sm transition-colors"
                title="Восстановить"
              >
                <Archive className="h-4 w-4" />
              </button>
            ) : (
              <>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    navigate(`/projects/${project.id}/edit`)
                  }}
                  className="p-1.5 rounded-md bg-card hover:bg-muted shadow-sm transition-colors"
                  title="Редактировать"
                >
                  <Edit className="h-4 w-4" />
                </button>
                <button
                  onClick={(e) => {
                    e.preventDefault()
                    e.stopPropagation()
                    handleArchive(project.id)
                  }}
                  className="p-1.5 rounded-md bg-card hover:bg-destructive/10 hover:text-destructive shadow-sm transition-colors"
                  title="Архивировать"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </>
                )}
            </div>
            )}
          </div>
        ))}
      </div>
      )}
    </div>
  )
}