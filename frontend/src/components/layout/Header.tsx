import { useAuthStore } from '@/stores/authStore'

export function Header() {
  const user = useAuthStore((state) => state.user)

  return (
    <header className="fixed top-0 right-0 left-0 h-16 bg-card border-b border-border flex items-center justify-between px-6 z-30">
      <div className="flex-1" />
      <div className="flex items-center gap-4">
        {user && (
          <div className="text-right">
            <p className="text-sm font-medium">{user.full_name}</p>
            <p className="text-xs text-muted-foreground">{user.email}</p>
          </div>
        )}
      </div>
    </header>
  )
}