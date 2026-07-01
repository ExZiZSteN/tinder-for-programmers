import { useState, useEffect, useRef } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { useChat } from '@/hooks/useChat'
import { useAuthStore } from '@/stores/authStore'
import { ArrowLeft } from 'lucide-react'
import { Button } from '@/components/ui/button'

export default function ChatPage() {
  const { matchId } = useParams<{ matchId: string }>()
  const navigate = useNavigate()
  const user = useAuthStore((state) => state.user)
  const [inputText, setInputText] = useState('')

  const currentUserId = user?.id || 0
  const parsedMatchId = Number(matchId)

  const {
    messages,
    sendMessage,
    isLoadingHistory,
    isConnected,
    loadMoreMessages,
    hasMore,
  } = useChat(parsedMatchId)

  const messagesEndRef = useRef<HTMLDivElement | null>(null)

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  const handleSend = (e: React.FormEvent) => {
    e.preventDefault()
    if (!inputText.trim()) return
    sendMessage(inputText)
    setInputText('')
  }

  if (isLoadingHistory) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="h-8 w-8 border-4 border-primary border-t-transparent rounded-full animate-spin" />
      </div>
    )
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      <header className="flex items-center justify-between px-6 py-4 bg-card border-b shadow-sm z-10">
        <div className="flex items-center gap-3">
          <Button variant="ghost" size="icon" onClick={() => navigate(-1)}>
            <ArrowLeft className="h-5 w-5" />
          </Button>
          <h2 className="text-lg font-semibold">Диалог #{matchId}</h2>
        </div>

        <div className="flex items-center gap-2 bg-muted px-3 py-1.5 rounded-full">
          <span
            className={`w-2 h-2 rounded-full ${
              isConnected ? 'bg-green-500' : 'bg-amber-500 animate-pulse'
            }`}
          />
          <span className="text-xs font-medium text-muted-foreground">
            {isConnected ? 'В сети' : 'Подключение...'}
          </span>
        </div>
      </header>

      <div className="flex-1 overflow-y-auto p-6 space-y-4">
        {hasMore && (
          <div className="text-center pb-2">
            <Button
              type="button"
              variant="outline"
              size="sm"
              onClick={loadMoreMessages}
            >
              Показать более старые сообщения
            </Button>
          </div>
        )}

        {messages.map((msg) => {
          const isMe = msg.sender_id === currentUserId
          return (
            <div
              key={msg.id}
              className={`flex ${isMe ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-xs md:max-w-md px-4 py-2.5 rounded-2xl shadow-sm ${
                  isMe
                    ? 'bg-primary text-primary-foreground rounded-br-none'
                    : 'bg-card text-foreground rounded-bl-none border'
                }`}
              >
                <p className="text-sm whitespace-pre-wrap break-words">{msg.content}</p>
                <span
                  className={`block text-[10px] text-right mt-1 font-light ${
                    isMe ? 'text-primary-foreground/70' : 'text-muted-foreground'
                  }`}
                >
                  {new Date(msg.created_at).toLocaleTimeString([], {
                    hour: '2-digit',
                    minute: '2-digit',
                  })}
                </span>
              </div>
            </div>
          )
        })}

        <div ref={messagesEndRef} />
      </div>

      <footer className="p-4 bg-card border-t">
        <form onSubmit={handleSend} className="flex gap-3 max-w-4xl mx-auto">
          <input
            type="text"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            placeholder={isConnected ? 'Напишите сообщение...' : 'Соединение разорвано...'}
            disabled={!isConnected}
            maxLength={4000}
            className="flex-1 px-4 py-3 bg-background border rounded-xl focus:outline-none focus:ring-2 focus:ring-ring disabled:bg-muted disabled:cursor-not-allowed text-sm shadow-sm"
          />
          <Button type="submit" disabled={!inputText.trim() || !isConnected}>
            Отправить
          </Button>
        </form>
      </footer>
    </div>
  )
}