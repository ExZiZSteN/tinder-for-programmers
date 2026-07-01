import logging
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    def __init__(self):

        self._connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, match_id: int, user_id: int, ws: WebSocket) -> None:
        """Подключает пользователя к чат-комнате мэтча."""

        old_ws = self._connections.get(match_id, {}).get(user_id)
        if old_ws:
            try:
                await old_ws.close(code=4000)
            except Exception:
                pass

        self._connections.setdefault(match_id, {})[user_id] = ws
        logger.info(f"User {user_id} connected to match chat {match_id}")

    def disconnect(self, match_id: int, user_id: int) -> None:
        """Отключает пользователя от чат-комнаты и удаляет пустые комнаты."""
        if match_id in self._connections:
            self._connections[match_id].pop(user_id, None)

            if not self._connections[match_id]:
                self._connections.pop(match_id, None)
        logger.info(f"User {user_id} disconnected from match chat {match_id}")

    async def broadcast(self, match_id: int, data: dict, exclude_user_id: int | None = None) -> None:
        """Отправляет сообщение всем участникам чата мэтча (кроме отправителя)."""
        match_room = self._connections.get(match_id, {})
        

        for uid, ws in list(match_room.items()):
            if uid == exclude_user_id:
                continue
            try:
                await ws.send_json(data)
            except Exception as e:
                logger.warning(f"Failed to send WS message to user {uid} in match {match_id}: {e}")
                self.disconnect(match_id, uid)

    async def broadcast_to_all(self, data: dict) -> None:
        """
        Рассылает сообщение абсолютно всем активным чат-соединениям на сервере.
        Полезно для системных уведомлений о перезагрузке бэкенда.
        """

        for match_id, match_room in list(self._connections.items()):
            for uid, ws in list(match_room.items()):
                try:
                    await ws.send_json(data)
                except Exception:
                    self.disconnect(match_id, uid)

    def get_active_users(self, match_id: int) -> set[int]:
        """Возвращает ID пользователей, которые сейчас онлайн в конкретном чате."""
        return set(self._connections.get(match_id, {}).keys())


class NotificationManager:
    def __init__(self):

        self._connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        """Подключает пользователя к его персональному каналу уведомлений."""

        old_ws = self._connections.get(user_id)
        if old_ws:
            try:
                await old_ws.close(code=4000)
            except Exception:
                pass

        self._connections[user_id] = ws
        logger.info(f"User {user_id} connected to global notifications")

    def disconnect(self, user_id: int) -> None:
        """Отключает пользователя от канала уведомлений."""
        self._connections.pop(user_id, None)
        logger.info(f"User {user_id} disconnected from global notifications")

    async def send_to_user(self, user_id: int, data: dict) -> None:
        """Отправляет персональное уведомление (например, событие нового мэтча)."""
        ws = self._connections.get(user_id)
        if ws is None:
            return
        try:
            await ws.send_json(data)
        except Exception as e:
            logger.warning(f"Failed to send notification to user {user_id}: {e}")
            self.disconnect(user_id)


ws_manager = ConnectionManager()
notification_manager = NotificationManager()
