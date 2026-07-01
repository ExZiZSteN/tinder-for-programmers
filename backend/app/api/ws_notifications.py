import logging
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import async_session
from app.core.security import decode_token
from app.core.ws_manager import notification_manager
from app.models.user import User


logger = logging.getLogger(__name__)


WS_CLOSE_UNAUTHORIZED = 4001
WS_CLOSE_INTERNAL = 1011


async def handle_notifications_ws(websocket: WebSocket):
    """
    Обработчик WebSocket-соединения для глобального канала уведомлений пользователя.
    Используется для отправки реалтайм-пушей (события мэтчей, системные алерты).
    """
    await websocket.accept()


    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
        return

    try:
        payload = decode_token(token)
    except ValueError:
        await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
        return

    if payload.get("type") != "access":
        await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
        return

    user_id = int(payload["sub"])

    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user or not user.is_active or user.is_banned:
            await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
            return

        await notification_manager.connect(user_id, websocket)

        try:
            while True:
                await websocket.receive_text()
                
        except WebSocketDisconnect:

            logger.info(f"User {user_id} disconnected from notification channel.")
        except Exception as e:

            logger.exception(f"Critical error in notification WS loop for user {user_id}: {e}")
            try:
                await websocket.close(code=WS_CLOSE_INTERNAL)
            except Exception:
                pass
        finally:

            notification_manager.disconnect(user_id)
