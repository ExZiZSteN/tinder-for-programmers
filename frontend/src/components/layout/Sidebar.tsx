import { NavLink, useNavigate } from 'react-router-dom'
import { useAuthStore } from '@/stores/authStore'
import { useUIStore } from '@/stores/uiStore'
import { cn } from '@/utils/cn'
import { authApi } from '@/api/auth'
import {
  Heart,
  MessageCircle,
  User,
  FolderKanban,
  LogOut,
  Menu,
} from 'lucide-react'
import { AvatarImage } from '../profile/AvatarImage'

const navItems = [
  { to: '/feed', label: 'Лента', icon: Heart },
  { to: '/matches', label: 'Матчи', icon: MessageCircle },
  { to: '/projects', label: 'Проекты', icon: FolderKanban },
  { to: '/profile', label: 'Профиль', icon: User },
]


export function Sidebar() {
  const { sidebarOpen, toggleSidebar } = useUIStore()
  const user = useAuthStore((state) => state.user)
  const logout = useAuthStore((state) => state.logout)
  const navigate = useNavigate()
  const handleLogout = async () => {
    const refreshToken = useAuthStore.getState().refreshToken
    try {
      if (refreshToken) {
        await authApi.logout(refreshToken)
      }
    } catch (error) {
      console.error('Ошибка при logout:', error)
    } finally {
      logout()
      navigate('/login')
    }
    }
  return (
    <aside
      className={cn(
        'fixed left-0 top-0 z-40 h-screen bg-card border-r border-border transition-all duration-300',
        sidebarOpen ? 'w-64' : 'w-20'
      )}
    >
      <div className="flex h-16 items-center justify-between px-4 border-b border-border">
        {sidebarOpen && (
          <h1 className="text-xl font-bold text-primary">TFP</h1>
        )}
        <button
          onClick={toggleSidebar}
          className="p-2 rounded-lg hover:bg-muted transition-colors"
        >
          <Menu className="h-5 w-5" />
        </button>
      </div>
      
      <nav className="flex flex-col gap-2 p-4">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                'flex items-center gap-3 px-3 py-2 rounded-lg transition-colors',
                isActive
                  ? 'bg-primary text-primary-foreground'
                  : 'hover:bg-muted'
              )
            }
          >
            <item.icon className="h-5 w-5 shrink-0" />
            {sidebarOpen && <span>{item.label}</span>}
          </NavLink>
        ))}
      </nav>

      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-border">
        {sidebarOpen && user && (
          <div className="mb-3 flex itmes-center gap-3 rounded-lg bg-sidebar-accent/50  px-3 py-2">
            <div className="h-9 w-9 shrink-0 overflow-hidden rounded-full bg-primary/20">
              <AvatarImage
                fileId={user.avatar_file_id}
                fallback={user.full_name?.[0]?.toUpperCase() || '?'}
                className='text-sm'
                />
              </div>
              <div className='min-w-0 flex-1 flex flex-col gap-0.5'>
                <p className="text-sm font-medium truncate">{user.full_name}</p>
                <p className="text-xs text-muted-foreground truncate">{user.email}</p>
              </div>
          </div>
        )}
        <button
          onClick={handleLogout}
          className="flex items-center gap-3 px-3 py-2 rounded-lg hover:bg-destructive/10 text-destructive transition-colors w-full"
        >
          <LogOut className="h-5 w-5 shrink-0" />
          {sidebarOpen && <span>Выйти</span>}
        </button>
      </div>
    </aside>
  )
}