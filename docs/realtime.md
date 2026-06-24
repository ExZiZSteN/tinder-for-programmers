# Realtime — WebSocket

##  Назначение

Realtime-коммуникации используются для:
- Чата между участниками матча
- Доставки уведомлений в реальном времени

##  WebSocket Endpoints

### Chat

```
ws://localhost:8000/ws/chat/{match_id}?token=<jwt>
```

**Аутентификация:** через query-параметр `token` (JWT)

**Проверки при подключении:**
1. JWT валиден
2. Пользователь — участник матча (user_id в match)
3. Матч в статусе `active`

### Notifications

```
ws://localhost:8000/ws/notifications?token=<jwt>
```

Доставляет уведомления пользователю в реальном времени.

##  Архитектура

```
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Client A                       Client B                   │
│      │                               │                      │
│      │ WebSocket                     │ WebSocket            │
│      └──────────────┬────────────────┘                      │
│                     ▼                                       │
│        ┌──────────────────────────┐                        │
│        │ FastAPI WebSocket Handler│                        │
│        └──────────────┬───────────┘                        │
│                       ▼                                     │
│        ┌──────────────────────────┐                        │
│        │ ConnectionManager        │                        │
│        │ match_id → {user_id→ws}  │                        │
│        └──────────────┬───────────┘                        │
│                       ▼                                     │
│        ┌──────────────────────────┐                        │
│        │ Redis Pub/Sub            │                        │
│        │ channel: chat:{match_id} │                        │
│        └──────────────────────────┘                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Зачем Redis Pub/Sub:**
- Поддержка нескольких инстансов backend (horizontal scaling)
- Сообщение от Client A на инстансе 1 должно дойти до Client B на инстансе 2

##  Протокол чата

### Отправка сообщения

```json
// Client → Server
{
  "type": "message",
  "content": "Привет!"
}
```

### Получение сообщения

```json
// Server → Client
{
  "type": "message",
  "id": 42,
  "match_id": 7,
  "sender_id": 3,
  "sender_name": "John Doe",
  "content": "Привет!",
  "created_at": "2026-06-24T10:15:30Z"
}
```

### Системные сообщения

```json
{
  "type": "system",
  "event": "user_joined",
  "user_id": 3
}
```

## 🔔 Протокол уведомлений

```json
// Server → Client
{
  "type": "new_swipe",
  "payload": {
    "swipe_id": 42,
    "developer_name": "John Doe",
    "project_title": "My Project"
  },
  "created_at": "2026-06-24T10:15:30Z"
}
```

**Типы уведомлений:**
- `new_swipe` — новый отклик на проект
- `swipe_approved` — отклик одобрен
- `swipe_rejected` — отклик отклонён
- `match_created` — создан матч
- `new_message` — новое сообщение в чате

##  Frontend-клиент

### React-хук для чата

```typescript
// hooks/useChat.ts
export const useChat = (matchId: number) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    const ws = new WebSocket(
      `${WS_URL}/ws/chat/${matchId}?token=${getToken()}`
    );
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'message') {
        setMessages(prev => [...prev, msg]);
      }
    };
    
    return () => ws.close();
  }, [matchId]);
  
  const sendMessage = (content: string) => {
    // Optimistic update
    const tempMsg = {
      id: Date.now(),
      content,
      sender_id: currentUser.id,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMsg]);
    
    wsRef.current?.send(JSON.stringify({
      type: 'message',
      content
    }));
  };
  
  return { messages, sendMessage };
};
```

### React-хук для уведомлений

```typescript
// hooks/useNotifications.ts
export const useNotifications = () => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const queryClient = useQueryClient();
  
  useEffect(() => {
    const ws = new WebSocket(
      `${WS_URL}/ws/notifications?token=${getToken()}`
    );
    
    ws.onmessage = (event) => {
      const notif = JSON.parse(event.data);
      setNotifications(prev => [notif, ...prev]);
      
      // Показать toast
      toast.info(notif.payload.title);
      
      // Обновить счётчик непрочитанных
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    };
    
    return () => ws.close();
  }, []);
  
  return notifications;
};
```

##  Безопасность

- Все WS-соединения требуют JWT
- Проверка прав на уровне handler'а (участник матча)
- Rate limiting: 30 сообщений/сек на соединение
- Валидация содержимого (1..4000 символов)

##  Troubleshooting

**Проблема:** сообщение не доходит до другого клиента  
**Решение:** проверить, что оба клиента подключены к одному Redis

**Проблема:** WS отключается  
**Решение:** реализовать reconnect с exponential backoff на клиенте

**Проблема:** дубликаты сообщений  
**Решение:** использовать `id` сообщения для дедупликации на клиенте