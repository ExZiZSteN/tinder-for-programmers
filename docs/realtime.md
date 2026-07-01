#  Модуль Realtime-коммуникаций (WebSockets)

##  Назначение подсистемы
Постоянные двухсторонние WebSocket-соединения используются в приложении для решения двух ключевых задач:
1. **Интерактивные чаты:** Мгновенный обмен текстовыми сообщениями между участниками подтвержденных матчей.
2. **Push-уведомления:** Доставка системных нотификаций и алертов на клиент в режиме реального времени.

---

## 🔌 Эндпоинты WebSocket

### 1. Комната чата матча
```text
ws://localhost:8000/api/v1/ws/chat/{match_id}?token=<jwt_access_token>

Аутентификация: Строго через query-параметр token.

Валидация при подключении:

Проверка валидности и срока действия JWT-токена.

Верификация прав доступа: текущий user_id должен являться непосредственным участником матча (user_id разработчика или owner_id проекта).

Проверка статуса матча: соединение разрешено только при статусе active.


2. Поток персональных уведомлений
ws://localhost:8000/api/v1/ws/notifications?token=<jwt_access_token>



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
Протоколы обмена данными (JSON)
Модуль: Чат
Отправка сообщения (Client → Server)
JSON
{
  "type": "message",
  "content": "Привет! Готов обсудить архитектуру вашего RAG-пайплайна."
}

##  Получение сообщения (Server → Client)
JSON
{
  "type": "message",
  "id": 42,
  "match_id": 7,
  "sender_id": 3,
  "sender_name": "John Doe",
  "content": "Привет! Готов обсудить архитектуру вашего RAG-пайплайна.",
  "created_at": "2026-06-24T10:15:30Z"
}

##  Системное событие (Server → Client)
JSON
{
  "type": "system",
  "event": "user_joined",
  "user_id": 3
}

##  Модуль: Уведомления (Server → Client)
JSON
{
  "type": "new_swipe",
  "payload": {
    "swipe_id": 42,
    "title": "Новый отклик!",
    "developer_name": "John Doe",
    "project_title": "My Project"
  },
  "created_at": "2026-06-24T10:15:30Z"
}

##  Типы поддерживаемых событий:
new_swipe — Поступил новый отклик на ваш проект (для Тимлида).

swipe_approved — Ваш отклик на проект был одобрен (для Разработчика).

swipe_rejected — Ваш отклик на проект был отклонен.

match_created — Зафиксировано успешное взаимное совпадение.

new_message — Получено новое сообщение в одном из active чатов.

Клиентская интеграция (React-хуки)
**1. Хук управления чатом (src/hooks/useChat.ts)**
TypeScript
import { useState, useEffect, useRef } from 'react';
import { Message } from '@/types';

export const useChat = (matchId: number, currentUser: { id: number }, getToken: () => string) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);
  
  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/chat/${matchId}?token=${getToken()}`
    );
    wsRef.current = ws;
    
    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      if (msg.type === 'message') {
        setMessages(prev => [...prev, msg]);
      }
    };
    
    return () => ws.close();
  }, [matchId, getToken]);
  
  const sendMessage = (content: string) => {
    if (!content.trim()) return;

    // Оптимистичное обновление интерфейса (Optimistic Update)
    const tempMsg: Message = {
      id: Date.now(),
      match_id: matchId,
      content,
      sender_id: currentUser.id,
      created_at: new Date().toISOString()
    };
    setMessages(prev => [...prev, tempMsg]);
    
    wsRef.current?.send(JSON.stringify({
      type: 'message',
      content: content.trim()
    }));
  };
  
  return { messages, sendMessage };
};

**2. Хук подписки на уведомления** (src/hooks/useNotifications.ts)
TypeScript
import { useState, useEffect } from 'react';
import { useQueryClient } from '@tanstack/react-query';
import { toast } from 'sonner';
import { Notification } from '@/types';

export const useNotifications = (getToken: () => string) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const queryClient = useQueryClient();
  
  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/notifications?token=${getToken()}`
    );
    
    ws.onmessage = (event) => {
      const notif = JSON.parse(event.data);
      setNotifications(prev => [notif, ...prev]);
      
      // Вызов всплывающего уведомления через Sonner Toast
      toast.info(notif.payload.title || "Новое системное уведомление");
      
      // Инвалидация кэша TanStack Query для синхронизации счетчиков непрочитанного
      queryClient.invalidateQueries({ queryKey: ['notifications'] });
    };
    
    return () => ws.close();
  }, [queryClient, getToken]);
  
  return notifications;
}

##  Безопасность и Лимиты
**Защита токенов**: Запрещено принимать анонимные соединения. Токен валидируется строго в момент хэндшейка.

**Ограничение флуда (Rate Limiting)**: На уровне сервера установлено ограничение в 30 сообщений в секунду на одно открытое соединение. При превышении лимита сокет принудительно закрывается.

**Валидация размера пакета**: Текст сообщения на бэкенде проверяется на длину (минимум 1 символ, максимум 4000 символов) перед ретрансляцией в Redis.

##  Решение типовых проблем (Troubleshooting)
Проблема: Сообщения отправляются, но не доходят до второго участника чата.

**Решение**: Проверьте конфигурацию пула Redis в .env. Все инстансы FastAPI должны слушать одну и ту же БД Redis (REDIS_URL).

**Проблема**: Периодические обрывы соединений сокетов на мобильных устройствах или при плохой сети.

**Решение**: На стороне фронтенда логику подключения в хуках необходимо расширить механизмом автоматического переподключения (Reconnection) с использованием алгоритма экспоненциальной задержки (Exponential Backoff).

**Проблема**: Дублирование сообщений на экране при отправке.

Решение: Реализуйте сверку уникальных id сообщений при рендере списка на клиенте для дедупликации оптимистичных и серверных ответов.
