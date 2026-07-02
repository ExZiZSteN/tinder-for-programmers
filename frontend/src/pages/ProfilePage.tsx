import { useEffect, useState, useRef } from 'react'
import { useForm } from 'react-hook-form'
import { zodResolver } from '@hookform/resolvers/zod'
import { z } from 'zod'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { usersApi } from '@/api/user'
import { skillsApi } from '@/api/skills'
import { filesApi } from '@/api/files'
import { useAuthStore } from '@/stores/authStore'
import type { User } from '@/types/user'
import type { Skill } from '@/types/project'
import { AvatarImage } from '@/components/profile/AvatarImage'

const profileSchema = z.object({
  full_name: z.string().min(2, 'Имя должно содержать минимум 2 символа').max(150, 'Имя слишком длинное'),
  bio: z.string().max(500, 'Биография слишком длинная').optional().or(z.literal('')),
  github_url: z.string().url('Некорректный URL').optional().or(z.literal('')),
  linkedin_url: z.string().url('Некорректный URL').optional().or(z.literal('')),
  portfolio_url: z.string().url('Некорректный URL').optional().or(z.literal('')),
  experience_years: z.number().min(0, 'Опыт не может быть отрицательным').max(50, 'Некорректное значение').optional(),
})

type ProfileFormData = z.infer<typeof profileSchema>

export default function ProfilePage() {
  const [user, setUser] = useState<User | null>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [skills, setSkills] = useState<Skill[]>([])
  const [isUploadingAvatar, setIsUploadingAvatar] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)
  const setUserInStore = useAuthStore((state) => state.setUser)

  const {
    register,
    handleSubmit,
    reset,
    formState: { errors, isSubmitting },
  } = useForm<ProfileFormData>({
    resolver: zodResolver(profileSchema),
  })

  // Загрузка профиля
  useEffect(() => {
    loadProfile()
  }, [])

  const loadProfile = async () => {
    try {
      const userData = await usersApi.getMe()
      setUser(userData)
      setSkills(userData.skills || [])

      useAuthStore.getState().setUser(userData)

      reset({
        full_name: userData.full_name,
        bio: userData.bio || '',
        github_url: userData.github_url || '',
        linkedin_url: userData.linkedin_url || '',
        portfolio_url: userData.portfolio_url || '',
        experience_years: userData.experience_years || 0,
      })
    } catch (error) {
      toast.error('Ошибка загрузки профиля')
    } finally {
      setIsLoading(false)
    }
  }

  const onSubmit = async (data: ProfileFormData) => {
    try {
      // 1. Обновляем профиль
      await usersApi.updateMe(data)
      
      // 2. Обновляем навыки
      const skillIds = skills.map(s => s.id)
      await usersApi.updateSkills(skillIds)
      
      // 3. Перезагружаем профиль
      await loadProfile()
      
      toast.success('Профиль обновлён')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка обновления профиля')
    }
  }

  const handleAvatarClick = () => {
    console.log('Click')
    fileInputRef.current?.click()
  }

  const handleAvatarChange = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    console.log('Файл выбран: ', file)
    if (!file) {
        console.log('Файл не выбран', file) 
        return
    }

    if (file.size > 5 * 1024 * 1024) {
      toast.error('Файл слишком большой (максимум 5MB)')
      return
    }

    if (!file.type.startsWith('image/')) {
      toast.error('Можно загружать только изображения')
      return
    }

    setIsUploadingAvatar(true)
    try {
        console.log("Загрузка файла")
        const uploadResponse = await filesApi.uploadDirect(file)
        console.log("Файл загружен")
        console.log("Установка аватара")
        await usersApi.setAvatar(uploadResponse.id)
        console.log("Автар установлен")
        await loadProfile()
        toast.success('Аватар обновлён')
    } catch (error: any) {
      toast.error(error.response?.data?.detail || 'Ошибка загрузки аватара')
    } finally {
      setIsUploadingAvatar(false)
      if (fileInputRef.current) {
        fileInputRef.current.value = ''
      }
    }
  }

  const handleRemoveAvatar = async () => {
    try {
      await usersApi.removeAvatar()
      await loadProfile()
      toast.success('Аватар удалён')
    } catch (error: any) {
      toast.error('Ошибка удаления аватара')
    }
  }

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
        <p className="text-muted-foreground">Ошибка загрузки профиля</p>
      </div>
    )
  }

  return (
    <div className="max-w-4xl mx-auto space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold">Профиль</h1>
        <p className="text-muted-foreground mt-1">Управляйте информацией о себе</p>
      </div>

      <form onSubmit={handleSubmit(onSubmit)} className="space-y-8">
        {/* Аватар */}
        <div className="rounded-lg border bg-card p-6">
          <h2 className="text-lg font-semibold mb-4">Аватар</h2>
          <div className="flex items-center gap-4">
            <div className="h-24 w-24 rounded-full bg-muted flex items-center justify-center overflow-hidden">
              <AvatarImage
                fileId={user.avatar_file_id}
                fallback={user.full_name?.[0]?.toUpperCase() || '?'}
              />
            </div>

            <div className="flex flex-col gap-2">
              <input
                ref={fileInputRef}
                type="file"
                accept="image/*"
                onChange={handleAvatarChange}
                className="hidden"
                id="avatar-upload"
              />
              <label htmlFor="avatar-upload">
                <Button
                  type="button"
                  size="sm"
                  onClick={handleAvatarClick}
                  disabled={isUploadingAvatar}
                >
                  {isUploadingAvatar ? 'Загрузка...' : 'Загрузить аватар'}
                </Button>
              </label>
              {user.avatar_file_id && (
                <Button
                  type="button"
                  size="sm"
                  variant="destructive"
                  onClick={handleRemoveAvatar}
                  disabled={isUploadingAvatar}
                >
                  Удалить
                </Button>
              )}
            </div>
          </div>
        </div>

        {/* Основная информация */}
        <div className="rounded-lg border bg-card p-6 space-y-6">
          <h2 className="text-lg font-semibold">Основная информация</h2>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="full_name">Имя *</Label>
              <Input
                id="full_name"
                {...register('full_name')}
                error={errors.full_name?.message}
              />
            </div>

            <div>
              <Label htmlFor="experience_years">Опыт работы (лет)</Label>
              <Input
                id="experience_years"
                type="number"
                min="0"
                max="50"
                {...register('experience_years', { valueAsNumber: true })}
                error={errors.experience_years?.message}
              />
            </div>
          </div>

          <div>
            <Label htmlFor="bio">О себе</Label>
            <textarea
              id="bio"
              rows={4}
              className="flex min-h-[80px] w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50"
              {...register('bio')}
            />
            {errors.bio?.message && (
              <p className="mt-1 text-sm text-destructive">{errors.bio.message}</p>
            )}
          </div>
        </div>

        {/* Ссылки */}
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h2 className="text-lg font-semibold">Ссылки</h2>

          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <Label htmlFor="github_url">GitHub</Label>
              <Input
                id="github_url"
                placeholder="https://github.com/username"
                {...register('github_url')}
                error={errors.github_url?.message}
              />
            </div>

            <div>
              <Label htmlFor="linkedin_url">LinkedIn</Label>
              <Input
                id="linkedin_url"
                placeholder="https://linkedin.com/in/username"
                {...register('linkedin_url')}
                error={errors.linkedin_url?.message}
              />
            </div>

            <div className="md:col-span-2">
              <Label htmlFor="portfolio_url">Портфолио</Label>
              <Input
                id="portfolio_url"
                placeholder="https://your-portfolio.com"
                {...register('portfolio_url')}
                error={errors.portfolio_url?.message}
              />
            </div>
          </div>
        </div>

        {/* Навыки */}
        <div className="rounded-lg border bg-card p-6 space-y-4">
          <h2 className="text-lg font-semibold">Навыки</h2>
          <SkillSelector
            selectedSkills={skills}
            onSkillsChange={setSkills}
          />
        </div>

        {/* Кнопки */}
        <div className="flex gap-3">
          <Button type="submit" size="lg" isLoading={isSubmitting}>
            Сохранить изменения
          </Button>
          <Button type="button" variant="outline" size="lg" onClick={() => reset()}>
            Отменить
          </Button>
        </div>
      </form>
    </div>
  )
}

// Компонент выбора навыков
function SkillSelector({ selectedSkills, onSkillsChange }: { selectedSkills: Skill[]; onSkillsChange: (skills: Skill[]) => void }) {
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
        setSearchResults(results.filter(s => !selectedSkills.find(ss => ss.id === s.id)))
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
    const name = searchQuery.trim()
    if (!name) return

    try {
      setIsSearching(true)
      const newSkill = await skillsApi.create(name)
      handleAddSkill(newSkill)
      toast.success(`Навык "${name}" создан`)
    } catch (error: any) {
      console.error('Ошибка создания навыка:', error)

      // Достаём сообщение об ошибке
      const detail = error.response?.data?.detail
      const message = typeof detail === 'string' 
        ? detail 
        : `Не удалось создать навык "${name}"`

      toast.error(message)
    } finally {
      setIsSearching(false)
    }
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap gap-2">
        {selectedSkills.map((skill) => (
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
          onChange={(e) => setSearchQuery(e.target.value)}
        />
      </div>

      {searchResults.length > 0 && (
        <div className="rounded-lg border bg-card p-2 max-h-48 overflow-y-auto">
          {searchResults.map((skill) => (
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

      {searchQuery.length >= 2 && searchResults.length === 0 && !isSearching && (
        <Button
          type="button"
          size="sm"
          variant="outline"
          onClick={handleCreateSkill}
          disabled={isSearching}
          className="w-full"
        >
          + Создать навык "{searchQuery}"
        </Button>
      )}
    </div>
  )
}