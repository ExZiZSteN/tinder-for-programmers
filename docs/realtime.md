# Модуль Realtime-коммуникаций (WebSockets)

## Назначение подсистемы

Постоянные двусторонние WebSocket-соединения используются для решения двух ключевых задач:

1. **Интерактивные чаты** — мгновенный обмен сообщениями между участниками подтвержденных матчей.
2. **Push-уведомления** — доставка системных уведомлений клиенту в режиме реального времени.

---

# WebSocket-эндпоинты

## 1. Комната чата

```text
ws://localhost:8000/api/v1/ws/chat/{match_id}?token=<jwt_access_token>
```

### Аутентификация

Используется **JWT Access Token**, передаваемый через query-параметр `token`.

### Проверки при подключении

- Проверка валидности и срока действия JWT.
- Проверка, что пользователь является участником матча (`developer` или `project owner`).
- Проверка, что матч находится в статусе **active**.

---

## 2. Поток персональных уведомлений

```text
ws://localhost:8000/api/v1/ws/notifications?token=<jwt_access_token>
```

---

# Архитектура

```text
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│   Client A                       Client B                   │
│      │                              │                       │
│      │ WebSocket                    │ WebSocket             │
│      └──────────────┬───────────────┘                       │
│                     ▼                                       │
│        ┌──────────────────────────┐                         │
│        │ FastAPI WebSocket Handler│                         │
│        └──────────────┬───────────┘                         │
│                       ▼                                     │
│        ┌──────────────────────────┐                         │
│        │ ConnectionManager        │                         │
│        │ match_id → {user_id→ws}  │                         │
│        └──────────────┬───────────┘                         │
│                       ▼                                     │
│        ┌──────────────────────────┐                         │
│        │ Redis Pub/Sub            │                         │
│        │ channel: chat:{match_id} │                         │
│        └──────────────────────────┘                         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Назначение Redis Pub/Sub

Redis Pub/Sub обеспечивает **горизонтальное масштабирование** приложения.

Если backend работает на нескольких инстансах за балансировщиком нагрузки, Redis выступает общей шиной сообщений и гарантирует доставку данных между пользователями независимо от того, к какому экземпляру FastAPI они подключены.

---

# Протокол обмена сообщениями (JSON)

## Модуль "Чат"

### Отправка сообщения (Client → Server)

```json
{
  "type": "message",
  "content": "Привет! Готов обсудить архитектуру вашего RAG-пайплайна."
}
```

### Получение сообщения (Server → Client)

```json
{
  "type": "message",
  "id": 42,
  "match_id": 7,
  "sender_id": 3,
  "sender_name": "John Doe",
  "content": "Привет! Готов обсудить архитектуру вашего RAG-пайплайна.",
  "created_at": "2026-06-24T10:15:30Z"
}
```

### Системное событие (Server → Client)

```json
{
  "type": "system",
  "event": "user_joined",
  "user_id": 3
}
```

---

## Модуль "Уведомления"

### Получение уведомления (Server → Client)

```json
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
```

### Поддерживаемые события

| Событие | Описание |
|----------|----------|
| `new_swipe` | Новый отклик на проект |
| `swipe_approved` | Отклик одобрен |
| `swipe_rejected` | Отклик отклонён |
| `match_created` | Создан новый матч |
| `new_message` | Получено новое сообщение |

---

# Клиентская интеграция (React Hooks)

## useChat

Файл:

```text
src/hooks/useChat.ts
```

```tsx
import { useState, useEffect, useRef } from "react";
import { Message } from "@/types";

export const useChat = (
  matchId: number,
  currentUser: { id: number },
  getToken: () => string
) => {
  const [messages, setMessages] = useState<Message[]>([]);
  const wsRef = useRef<WebSocket | null>(null);

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/chat/${matchId}?token=${getToken()}`
    );

    wsRef.current = ws;

    ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);

      if (msg.type === "message") {
        setMessages((prev) => [...prev, msg]);
      }
    };

    return () => ws.close();
  }, [matchId, getToken]);

  const sendMessage = (content: string) => {
    if (!content.trim()) return;

    // Optimistic Update
    const tempMsg: Message = {
      id: Date.now(),
      match_id: matchId,
      content,
      sender_id: currentUser.id,
      created_at: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, tempMsg]);

    wsRef.current?.send(
      JSON.stringify({
        type: "message",
        content: content.trim(),
      })
    );
  };

  return {
    messages,
    sendMessage,
  };
};
```

---

## useNotifications

Файл:

```text
src/hooks/useNotifications.ts
```

```tsx
import { useState, useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";
import { Notification } from "@/types";

export const useNotifications = (
  getToken: () => string
) => {
  const [notifications, setNotifications] = useState<Notification[]>([]);
  const queryClient = useQueryClient();

  useEffect(() => {
    const ws = new WebSocket(
      `ws://localhost:8000/api/v1/ws/notifications?token=${getToken()}`
    );

    ws.onmessage = (event) => {
      const notif = JSON.parse(event.data);

      setNotifications((prev) => [notif, ...prev]);

      // Toast
      toast.info(
        notif.payload.title || "Новое системное уведомление"
      );

      // Обновление кэша
      queryClient.invalidateQueries({
        queryKey: ["notifications"],
      });
    };

    return () => ws.close();
  }, [queryClient, getToken]);

  return notifications;
};
```

---

# Безопасность и ограничения

## Защита соединений

- Анонимные подключения запрещены.
- JWT валидируется во время WebSocket Handshake.

## Rate Limiting

- Максимум **30 сообщений в секунду** на одно соединение.
- При превышении лимита соединение закрывается сервером.

## Ограничение размера сообщения

Перед публикацией в Redis сообщение проходит проверку:

- минимум **1 символ**;
- максимум **4000 символов**.

---

# Troubleshooting

## Сообщения не доходят до второго участника

**Причина**

FastAPI-инстансы используют разные Redis.

**Решение**

Убедитесь, что все экземпляры backend используют одинаковый:

```env
REDIS_URL
```

---

## Периодически обрывается WebSocket

**Причина**

Нестабильная сеть или мобильное соединение.

**Решение**

Реализовать автоматическое переподключение (**Reconnection**) с использованием алгоритма **Exponential Backoff**.

---

## Сообщения отображаются дважды

**Причина**

Одновременно отображается оптимистично добавленное сообщение и подтверждение от сервера.

**Решение**

При рендеринге списка выполнять дедупликацию сообщений по уникальному `id`.
**Проблема**: Дублирование сообщений на экране при отправке.

Решение: Реализуйте сверку уникальных id сообщений при рендере списка на клиенте для дедупликации оптимистичных и серверных ответов.
