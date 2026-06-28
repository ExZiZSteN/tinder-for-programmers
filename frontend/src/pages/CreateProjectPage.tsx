import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { projectsApi } from '@/api/project'
import { skillsApi } from '@/api/skills'
import type { Skill } from '@/types/project'
import { ArrowLeft, FolderPlus, Save } from 'lucide-react'
import { useEffect } from 'react'

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
})

type ProjectFormData = z.infer<typeof projectSchema>

export default function CreateProjectPage() {
  const navigate = useNavigate()
  const [skills, setSkills] = useState<Skill[]>([])
  const [isSubmitting, setIsSubmitting] = useState(false)

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectFormData>({
    resolver: zodResolver(projectSchema),
    defaultValues: {
      format: 'remote',
      payment_type: 'volunteer',
    },
  })

  const onSubmit = async (data: ProjectFormData, isDraft: boolean = false) => {
    setIsSubmitting(true)
    try {
      const project = await projectsApi.create({
        title: data.title,
        description: data.description,
        format: data.format,
        payment_type: data.payment_type,
        skill_ids: skills.map(s => s.id),
        status: isDraft ? 'draft' : 'open',
      })
      
      toast.success(isDraft ? 'Черновик сохранён' : 'Проект создан!')
      navigate(`/projects/${project.id}`)
    } catch (error: any) {
      console.error('Ошибка создания проекта:', error)
      toast.error(error.response?.data?.detail || 'Ошибка создания проекта')
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div className="flex items-center gap-4">
        <Button
          variant="ghost"
          size="icon"
          onClick={() => navigate(-1)}
        >
          <ArrowLeft className="h-5 w-5" />
        </Button>
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <FolderPlus className="h-8 w-8" />
            Создать проект
          </h1>
          <p className="text-muted-foreground mt-1">
            Заполните информацию о вашем проекте
          </p>
        </div>
      </div>

      <form className="space-y-8">
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

          <div className="grid gap-4 md:grid-cols-2">
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
            type="button"
            size="lg"
            onClick={handleSubmit((data) => onSubmit(data, true))}
            disabled={isSubmitting}
            variant="outline"
          >
            <Save className="h-4 w-4 mr-2" />
            Сохранить черновик
          </Button>
          <Button
            type="button"
            size="lg"
            onClick={handleSubmit((data) => onSubmit(data, false))}
            disabled={isSubmitting}
          >
            <FolderPlus className="h-4 w-4 mr-2" />
            {isSubmitting ? 'Создание...' : 'Опубликовать проект'}
          </Button>
          <Button
            type="button"
            size="lg"
            variant="ghost"
            onClick={() => navigate(-1)}
          >
            Отмена
          </Button>
        </div>
      </form>
    </div>
  )
}

// Компонент выбора навыков (тот же, что в ProfilePage)
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
      if (searchQuery.length < 1) {
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