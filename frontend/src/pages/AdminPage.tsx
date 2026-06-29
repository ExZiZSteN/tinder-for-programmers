import { useState, useEffect } from 'react'
import { toast } from 'sonner'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { adminApi, type AdminStats, type AdminUser } from '@/api/admin'
import {
  Users,
  FolderKanban,
  Heart,
  Tag,
  Shield,
  Ban,
  Trash2,
  Search,
  RefreshCw,
} from 'lucide-react'

type Tab = 'dashboard' | 'users' | 'projects' | 'skills'

export default function AdminPage() {
  const [activeTab, setActiveTab] = useState<Tab>('dashboard')
  const [stats, setStats] = useState<AdminStats | null>(null)
  const [isLoading, setIsLoading] = useState(false)

  useEffect(() => {
    loadStats()
  }, [])

  const loadStats = async () => {
    try {
      setIsLoading(true)
      const data = await adminApi.getStats()
      setStats(data)
    } catch (error: any) {
      toast.error('Ошибка загрузки статистики')
    } finally {
      setIsLoading(false)
    }
  }

  const tabs = [
    { id: 'dashboard' as Tab, label: 'Dashboard', icon: Shield },
    { id: 'users' as Tab, label: 'Пользователи', icon: Users },
    { id: 'projects' as Tab, label: 'Проекты', icon: FolderKanban },
    { id: 'skills' as Tab, label: 'Навыки', icon: Tag },
  ]

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold flex items-center gap-3">
            <Shield className="h-8 w-8" />
            Админ-панель
          </h1>
          <p className="text-muted-foreground mt-1">
            Управление платформой
          </p>
        </div>
        <Button
          variant="outline"
          onClick={loadStats}
          disabled={isLoading}
        >
          <RefreshCw className={`h-4 w-4 mr-2 ${isLoading ? 'animate-spin' : ''}`} />
          Обновить
        </Button>
      </div>

      {/* Tabs */}
      <div className="flex gap-2 border-b">
        {tabs.map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`px-4 py-2 font-medium transition-colors ${
              activeTab === tab.id
                ? 'border-b-2 border-primary text-primary'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            <tab.icon className="h-4 w-4 inline mr-2" />
            {tab.label}
          </button>
        ))}
      </div>

      {/* Content */}
      {activeTab === 'dashboard' && <DashboardTab stats={stats} />}
      {activeTab === 'users' && <UsersTab />}
      {activeTab === 'projects' && <ProjectsTab />}
      {activeTab === 'skills' && <SkillsTab />}
    </div>
  )
}

// Dashboard Tab
function DashboardTab({ stats }: { stats: AdminStats | null }) {
  if (!stats) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  const statCards = [
    { label: 'Пользователи', value: stats.total_users, icon: Users, color: 'bg-blue-500' },
    { label: 'Проекты', value: stats.total_projects, icon: FolderKanban, color: 'bg-green-500' },
    { label: 'Матчи', value: stats.total_matches, icon: Heart, color: 'bg-pink-500' },
    { label: 'Навыки', value: stats.total_skills, icon: Tag, color: 'bg-purple-500' },
    { label: 'Забанены', value: stats.banned_users, icon: Ban, color: 'bg-red-500' },
    { label: 'Активные проекты', value: stats.active_projects, icon: FolderKanban, color: 'bg-emerald-500' },
  ]

  return (
    <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
      {statCards.map((stat) => (
        <div
          key={stat.label}
          className="rounded-lg border bg-card p-6 hover:shadow-lg transition-shadow"
        >
          <div className="flex items-center justify-between mb-4">
            <div className={`p-3 rounded-lg ${stat.color} text-white`}>
              <stat.icon className="h-6 w-6" />
            </div>
          </div>
          <h3 className="text-3xl font-bold mb-1">{stat.value}</h3>
          <p className="text-muted-foreground text-sm">{stat.label}</p>
        </div>
      ))}
    </div>
  )
}

// Users Tab
function UsersTab() {
  const [users, setUsers] = useState<AdminUser[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [search, setSearch] = useState('')
  const [filterRole, setFilterRole] = useState('')
  const [filterBanned, setFilterBanned] = useState('')

  useEffect(() => {
    loadUsers()
  }, [filterRole, filterBanned])

  const loadUsers = async () => {
    try {
      setIsLoading(true)
      const params: any = {}
      if (filterRole) params.role = filterRole
      if (filterBanned !== '') params.is_banned = filterBanned === 'true'
      
      const data = await adminApi.getUsers(params)
      setUsers(data.users)
    } catch (error: any) {
      toast.error('Ошибка загрузки пользователей')
    } finally {
      setIsLoading(false)
    }
  }

  const handleBan = async (userId: number, currentBanned: boolean) => {
    try {
      await adminApi.banUser(userId, !currentBanned)
      toast.success(currentBanned ? 'Пользователь разбанен' : 'Пользователь забанен')
      await loadUsers()
    } catch (error: any) {
      toast.error('Ошибка')
    }
  }

  const handleRoleChange = async (userId: number, currentRole: string) => {
    try {
      const newRole = currentRole === 'admin' ? 'user' : 'admin'
      await adminApi.changeRole(userId, newRole)
      toast.success(`Роль изменена на ${newRole}`)
      await loadUsers()
    } catch (error: any) {
      toast.error('Ошибка')
    }
  }

  const handleDelete = async (userId: number) => {
    if (!confirm('Удалить пользователя?')) return
    try {
      await adminApi.deleteUser(userId)
      toast.success('Пользователь удалён')
      await loadUsers()
    } catch (error: any) {
      toast.error('Ошибка')
    }
  }

  const filteredUsers = users.filter(u =>
    u.full_name.toLowerCase().includes(search.toLowerCase()) ||
    u.email.toLowerCase().includes(search.toLowerCase())
  )

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex gap-4">
        <div className="flex-1">
          <Input
            placeholder="Поиск по имени или email..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="max-w-md"
          />
        </div>
        <select
          value={filterRole}
          onChange={(e) => setFilterRole(e.target.value)}
          className="flex h-10 w-40 rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Все роли</option>
          <option value="user">Пользователи</option>
          <option value="admin">Админы</option>
        </select>
        <select
          value={filterBanned}
          onChange={(e) => setFilterBanned(e.target.value)}
          className="flex h-10 w-40 rounded-md border border-input bg-background px-3 py-2 text-sm"
        >
          <option value="">Все</option>
          <option value="false">Активные</option>
          <option value="true">Забанены</option>
        </select>
      </div>

      {/* Table */}
      <div className="rounded-lg border bg-card overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="text-left p-4 font-medium">Пользователь</th>
              <th className="text-left p-4 font-medium">Email</th>
              <th className="text-left p-4 font-medium">Роль</th>
              <th className="text-left p-4 font-medium">Статус</th>
              <th className="text-left p-4 font-medium">Действия</th>
            </tr>
          </thead>
          <tbody>
            {filteredUsers.map((user) => (
              <tr key={user.id} className="border-t hover:bg-muted/50">
                <td className="p-4">
                  <div className="font-medium">{user.full_name}</div>
                  <div className="text-xs text-muted-foreground">
                    ID: {user.id}
                  </div>
                </td>
                <td className="p-4 text-sm">{user.email}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    user.user_role === 'admin'
                      ? 'bg-purple-100 text-purple-700'
                      : 'bg-gray-100 text-gray-700'
                  }`}>
                    {user.user_role}
                  </span>
                </td>
                <td className="p-4">
                  {user.is_banned ? (
                    <span className="px-2 py-1 rounded text-xs font-medium bg-red-100 text-red-700">
                      Забанен
                    </span>
                  ) : user.is_active ? (
                    <span className="px-2 py-1 rounded text-xs font-medium bg-green-100 text-green-700">
                      Активен
                    </span>
                  ) : (
                    <span className="px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700">
                      Неактивен
                    </span>
                  )}
                </td>
                <td className="p-4">
                  <div className="flex gap-2">
                    <Button
                      size="sm"
                      variant="outline"
                      onClick={() => handleRoleChange(user.id, user.user_role)}
                    >
                      {user.user_role === 'admin' ? 'Снять админа' : 'Сделать админом'}
                    </Button>
                    <Button
                      size="sm"
                      variant={user.is_banned ? 'default' : 'destructive'}
                      onClick={() => handleBan(user.id, user.is_banned)}
                    >
                      {user.is_banned ? 'Разбанить' : 'Забанить'}
                    </Button>
                    <Button
                      size="sm"
                      variant="ghost"
                      onClick={() => handleDelete(user.id)}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Projects Tab
function ProjectsTab() {
  const [projects, setProjects] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)

  useEffect(() => {
    loadProjects()
  }, [])

  const loadProjects = async () => {
    try {
      setIsLoading(true)
      const data = await adminApi.getProjects()
      setProjects(data.projects)
    } catch (error: any) {
      toast.error('Ошибка загрузки проектов')
    } finally {
      setIsLoading(false)
    }
  }

  const handleDelete = async (projectId: number) => {
    if (!confirm('Удалить проект?')) return
    try {
      await adminApi.deleteProject(projectId)
      toast.success('Проект удалён')
      await loadProjects()
    } catch (error: any) {
      toast.error('Ошибка')
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
    <div className="space-y-4">
      <div className="rounded-lg border bg-card overflow-hidden">
        <table className="w-full">
          <thead className="bg-muted">
            <tr>
              <th className="text-left p-4 font-medium">Название</th>
              <th className="text-left p-4 font-medium">Владелец</th>
              <th className="text-left p-4 font-medium">Статус</th>
              <th className="text-left p-4 font-medium">Создан</th>
              <th className="text-left p-4 font-medium">Действия</th>
            </tr>
          </thead>
          <tbody>
            {projects.map((project) => (
              <tr key={project.id} className="border-t hover:bg-muted/50">
                <td className="p-4">
                  <div className="font-medium">{project.title}</div>
                  <div className="text-xs text-muted-foreground line-clamp-1">
                    {project.description}
                  </div>
                </td>
                <td className="p-4 text-sm">{project.owner?.full_name || 'N/A'}</td>
                <td className="p-4">
                  <span className={`px-2 py-1 rounded text-xs font-medium ${
                    project.status === 'open' ? 'bg-green-100 text-green-700' :
                    project.status === 'draft' ? 'bg-yellow-100 text-yellow-700' :
                    'bg-gray-100 text-gray-700'
                  }`}>
                    {project.status}
                  </span>
                </td>
                <td className="p-4 text-sm">
                  {new Date(project.created_at).toLocaleDateString('ru-RU')}
                </td>
                <td className="p-4">
                  <Button
                    size="sm"
                    variant="destructive"
                    onClick={() => handleDelete(project.id)}
                  >
                    <Trash2 className="h-4 w-4" />
                  </Button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}

// Skills Tab
function SkillsTab() {
  const [skills, setSkills] = useState<any[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [newSkillName, setNewSkillName] = useState('')
  const [search, setSearch] = useState('')

  useEffect(() => {
    loadSkills()
  }, [])

  const loadSkills = async () => {
    try {
      setIsLoading(true)
      const data = await adminApi.getSkills({ search })
      setSkills(data.skills)
    } catch (error: any) {
      toast.error('Ошибка загрузки навыков')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCreate = async () => {
    if (!newSkillName.trim()) return
    try {
      await adminApi.createSkill(newSkillName.trim())
      toast.success('Навык создан')
      setNewSkillName('')
      await loadSkills()
    } catch (error: any) {
      toast.error('Ошибка создания навыка')
    }
  }

  const handleDelete = async (skillId: number) => {
    if (!confirm('Удалить навык?')) return
    try {
      await adminApi.deleteSkill(skillId)
      toast.success('Навык удалён')
      await loadSkills()
    } catch (error: any) {
      toast.error('Ошибка')
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
    <div className="space-y-4">
      {/* Create skill */}
      <div className="flex gap-4">
        <Input
          placeholder="Название нового навыка..."
          value={newSkillName}
          onChange={(e) => setNewSkillName(e.target.value)}
          className="max-w-md"
        />
        <Button onClick={handleCreate}>Создать</Button>
      </div>

      {/* Search */}
      <Input
        placeholder="Поиск навыков..."
        value={search}
        onChange={(e) => setSearch(e.target.value)}
        className="max-w-md"
      />

      {/* Skills list */}
      <div className="grid gap-2">
        {skills.map((skill) => (
          <div
            key={skill.id}
            className="flex items-center justify-between p-4 rounded-lg border bg-card hover:shadow-sm"
          >
            <div>
              <span className="font-medium">{skill.name}</span>
              <span className="text-xs text-muted-foreground ml-2">
                ID: {skill.id}
              </span>
            </div>
            <Button
              size="sm"
              variant="destructive"
              onClick={() => handleDelete(skill.id)}
            >
              <Trash2 className="h-4 w-4" />
            </Button>
          </div>
        ))}
      </div>
    </div>
  )
}