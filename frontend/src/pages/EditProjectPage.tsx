import { useState, useEffect } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { projectsApi } from '@/api/project'
import { skillsApi } from '@/api/skills'
import type { Project, Skill } from '@/types/project'
import { ArrowLeft, Save, Trash2 } from 'lucide-react'

const projectSchema = z.object({
  title: z
    .string()
    .min(1, 'Название обязательно')
    .max(200, 'Название слишком длинное'),
  description: z
    .string()
    .min(1, 'Описание обязательно')
    .max(5000, 'Описание слишком длинное'),
  format: z.enum(['remote', 'office', 'hybrid']),
  payment_type: z.enum(['volunteer', 'paid', 'equity']),
  status: z.enum(['draft', 'open', 'closed', 'archived', 'completed']),
})

type ProjectFormData = z.infer<typeof projectSchema>

export default function EditProjectPage() {
  const { id } = useParams<{ id: string }>()
  const navigate = useNavigate()
  const [skills, setSkills] = useState<Skill[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isLoading, setIsLoading] = useState(true)
  const [project, setProject] = useState<Project | null>(null)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
  })

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
      setSkills(data.skills || [])
      reset({
        title: data.title,
        description: data.description,
        format: data.format,
        payment_type: data.payment_type,
        status: data.status,
      })
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки проекта')
      navigate('/projects')
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmit = async (data: ProjectFormData) => {
    if (!id) return
    
    setIsSubmitting(true)
    try {
      await projectsApi.update(Number(id), {
        title: data.title,
        description: data.description,
        format: data.format,
        payment_type: data.payment_type,
        status: data.status,
        skill_ids: skills.map(s => s.id),
      })
      
      toast.success('Проект обновлён')
      navigate(`/projects`)
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обновления проекта')
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleArchive = async () => {
    if (!id || !confirm('Архивировать проект?')) return
    
    try {
      await projectsApi.delete(Number(id))
      toast.success('Проект архивирован')
      navigate('/projects')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка архивации')
    }
  }

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
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <Button
            variant="ghost"
            size="icon"
            onClick={() => navigate(-1)}
          >
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <div>
            <h1 className="text-3xl font-bold">Редактировать проект</h1>
            <p className="text-muted-foreground mt-1">
              {project.title}
            </p>
          </div>
        </div>
        <Button
          variant="destructive"
          onClick={handleArchive}
          className="flex items-center gap-2"
        >
          <Trash2 className="h-4 w-4" />
          Архивировать
        </Button>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Основная информация */}
        <div className="rounded-lg border bg-card p-6 space-y-6">
          <h2 className="text-lg font-semibold">Основная информация</h2>

          <div>
            <Label htmlFor="title">Название проекта *</Label>
            <Input
              id="title"
              placeholder="Например: Мобильное приложение для доставки"
              {...register('title')}
              error={errors.title?.message}
            />
          </div>

          <div>
            <Label htmlFor="description">Описание *</Label>
            <textarea
              id="description"
              rows={6}
              placeholder="Опишите идею проекта, цели, задачи и чего вы ожидаете от участников..."
              className="flex min-h-[120px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              {...register('description')}
            />
            {errors.description?.message && (
              <p className="mt-1 text-sm text-destructive">{errors.description.message}</p>
            )}
            <p className="mt-1 text-xs text-muted-foreground">
              Максимум 5000 символов
            </p>
          </div>
        </div>

        {/* Параметры */}
        <div className="rounded-lg border bg-card p-6 space-y-6">
          <h2 className="text-lg font-semibold">Параметры проекта</h2>

          <div className="grid gap-4 md:grid-cols-3">
            <div>
              <Label htmlFor="format">Формат работы</Label>
              <select
                id="format"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                {...register('format')}
              >
                <option value="remote">Удалённо</option>
                <option value="office">Офис</option>
                <option value="hybrid">Гибрид</option>
              </select>
            </div>

            <div>
              <Label htmlFor="payment_type">Тип оплаты</Label>
              <select
                id="payment_type"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                {...register('payment_type')}
              >
                <option value="volunteer">Волонтёрство</option>
                <option value="paid">Оплата</option>
                <option value="equity">Доля в проекте</option>
              </select>
            </div>

            <div>
              <Label htmlFor="status">Статус</Label>
              <select
                id="status"
                className="flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring"
                {...register('status')}
              >
                <option value="draft">Черновик</option>
                <option value="open">Открыт</option>
                <option value="closed">Закрыт</option>
                <option value="completed">Завершен</option>
                <option value="archived">В архиве</option>
              </select>
            </div>
          </div>
        </div>

        {/* Навыки */}
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h2 className="text-lg font-semibold">Требуемые навыки</h2>
          <p className="text-sm text-muted-foreground">
            Выберите навыки, которые нужны для проекта
          </p>
          <SkillSelector
            selectedSkills={skills}
            onSkillsChange={setSkills}
          />
        </div>

        {/* Кнопки */}
        <div className="flex gap-3 sticky bottom-6">
          <Button
            type="submit"
            size="lg"
            disabled={isSubmitting}
          >
            <Save className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Сохранение...' : 'Сохранить изменения'}
          </Button>
          <Button
            type="button"
            size="lg"
            variant="outline"
            onClick={() => navigate(-1)}
          >
            Отмена
          </Button>
        </div>
      </form>
    </div>
  )
}

// Компонент выбора навыков
function SkillSelector({
  selectedSkills,
  onSkillsChange,
}: {
  selectedSkills: Skill[]
  onSkillsChange: (skills: Skill[]) => void
}) {
  const [searchQuery, setSearchQuery] = useState('')
  const [searchResults, setSearchResults] = useState<Skill[]>([])
  const [isSearching, setIsSearching] = useState(false)

  useEffect(() => {
    const timer = setTimeout(async () => {
      if (searchQuery.length < 2) {
        setSearchResults([])
        return
      }

      setIsSearching(true)
      try {
        const results = await skillsApi.list({ q: searchQuery, limit: 10 })
        setSearchResults(
          results.filter(s => !selectedSkills.find(ss => ss.id === s.id))
        )
      } catch (error) {
        console.error('Ошибка поиска навыков:', error)
      } finally {
        setIsSearching(false)
      }
    }, 300)

    return () => clearTimeout(timer)
  }, [searchQuery, selectedSkills])

  const handleAddSkill = (skill: Skill) => {
    onSkillsChange([...selectedSkills, skill])
    setSearchQuery('')
    setSearchResults([])
  }

  const handleRemoveSkill = (skillId: number) => {
    onSkillsChange(selectedSkills.filter(s => s.id !== skillId))
  }

  const handleCreateSkill = async () => {
    if (!searchQuery.trim()) return

    try {
      const newSkill = await skillsApi.create(searchQuery.trim())
      handleAddSkill(newSkill)
    } catch (error: any) {
      console.error('Ошибка создания навыка:', error)
      toast.error(error.response?.data?.detail || 'Не удалось создать навык')
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {selectedSkills.map(skill => (
          <div
            key={skill.id}
            className="inline-flex items-center gap-1 rounded-full bg-primary/10 px-3 py-1 text-sm"
          >
            <span>{skill.name}</span>
            <button
              type="button"
              onClick={() => handleRemoveSkill(skill.id)}
              className="rounded-full p-0.5 hover:bg-primary/20 transition-colors"
            >
              ×
            </button>
          </div>
        ))}
      </div>

      <div className="relative">
        <Input
          placeholder="Поиск навыков..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
        />
      </div>

      {searchResults.length > 0 && (
        <div className="rounded-lg border bg-card p-2 max-h-48 overflow-y-auto">
          {searchResults.map(skill => (
            <button
              key={skill.id}
              type="button"
              onClick={() => handleAddSkill(skill)}
              className="w-full text-left px-3 py-2 rounded-md hover:bg-muted transition-colors"
            >
              + {skill.name}
            </button>
          ))}
        </div>
      )}

      {searchQuery.length >= 2 &&
        searchResults.length === 0 &&
        !isSearching && (
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={handleCreateSkill}
            className="w-full"
          >
            + Создать навык "{searchQuery}"
          </Button>
        )}
    </div>
  )
}