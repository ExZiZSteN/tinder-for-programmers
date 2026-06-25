from fastapi import WebSocket


class ConnectionManager:
    def __init__(self):
        self._connections: dict[int, dict[int, WebSocket]] = {}

    async def connect(self, match_id: int, user_id: int, ws: WebSocket) -> None:
        self._connections.setdefault(match_id, {})[user_id] = ws

    def disconnect(self, match_id: int, user_id: int) -> None:
        self._connections.get(match_id, {}).pop(user_id, None)
        if not self._connections.get(match_id):
            self._connections.pop(match_id, None)

    async def broadcast(self, match_id: int, data: dict, exclude_user_id: int | None = None) -> None:
        for uid, ws in self._connections.get(match_id, {}).items():
            if uid == exclude_user_id:
                continue
            try:
                await ws.send_json(data)
            except Exception:
                pass

    def get_active_users(self, match_id: int) -> set[int]:
        return set(self._connections.get(match_id, {}).keys())


class NotificationManager:
    def __init__(self):
        self._connections: dict[int, WebSocket] = {}

    async def connect(self, user_id: int, ws: WebSocket) -> None:
        self._connections[user_id] = ws

    def disconnect(self, user_id: int) -> None:
        self._connections.pop(user_id, None)

    async def send_to_user(self, user_id: int, data: dict) -> None:
        ws = self._connections.get(user_id)
        if ws is None:
            return
        try:
            await ws.send_json(data)
        except Exception:
            self.disconnect(user_id)


ws_manager = ConnectionManager()
notification_manager = NotificationManager()
