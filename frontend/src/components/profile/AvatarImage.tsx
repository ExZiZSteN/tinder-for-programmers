import { useEffect, useState } from 'react'
import { filesApi } from '@/api/files'
import { cn } from '@/utils/cn'

interface AvatarImageProps {
  fileId?: number
  fallback?: string  // Буква для аватара-заглушки
  className?: string
}

export function AvatarImage({ fileId, fallback, className }: AvatarImageProps) {
  const [url, setUrl] = useState<string>('')
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!fileId) {
      setUrl('')
      return
    }

    let cancelled = false
    setLoading(true)

    filesApi
      .getDownloadUrl(fileId)
      .then((downloadUrl) => {
        if (!cancelled) {
          setUrl(downloadUrl)
        }
      })
      .catch((err) => {
        console.error('Ошибка загрузки URL аватара:', err)
      })
      .finally(() => {
        if (!cancelled) setLoading(false)
      })

    return () => {
      cancelled = true
    }
  }, [fileId])

  // Заглушка, если нет fileId или URL ещё не загружен
  if (!fileId || (!url && !loading)) {
    return (
      <div
        className={cn(
          'flex h-full w-full items-center justify-center bg-muted text-3xl font-bold text-muted-foreground',
          className
        )}
      >
        {fallback || '?'}
      </div>
    )
  }

  if (loading) {
    return (
      <div
        className={cn(
          'flex h-full w-full items-center justify-center bg-muted',
          className
        )}
      >
        <div className="h-6 w-6 animate-spin rounded-full border-2 border-primary border-t-transparent" />
      </div>
    )
  }

  return (
    <img
      src={url}
      alt="Avatar"
      className={cn('h-full w-full object-cover', className)}
    />
  )
}