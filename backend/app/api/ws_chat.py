import logging
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select

from app.core.database import async_session
from app.core.security import decode_token
from app.core.ws_manager import ws_manager
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.user import User
from app.schemas.message import WSMessageIn
from app.services.chat import ChatService


logger = logging.getLogger(__name__)


WS_CLOSE_UNAUTHORIZED = 4001
WS_CLOSE_FORBIDDEN = 4003 
WS_CLOSE_NOT_FOUND = 4004 
WS_CLOSE_INTERNAL = 1011


async def handle_chat_ws(websocket: WebSocket, match_id: int):
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

        service = ChatService(db)

        try:
            await service._verify_participant(user, match_id)
        except NotFoundException:
            await websocket.close(code=WS_CLOSE_NOT_FOUND)
            return
        except ForbiddenException:
            await websocket.close(code=WS_CLOSE_FORBIDDEN)
            return

        await ws_manager.connect(match_id, user_id, websocket)

        try:
            while True:
                raw = await websocket.receive_text()

                try:
                    msg_in = WSMessageIn.model_validate_json(raw)
                except Exception:
                    await websocket.send_json({"type": "error", "detail": "Invalid message format"})
                    continue

                if msg_in.type != "message":
                    await websocket.send_json({"type": "error", "detail": "Unknown message type"})
                    continue

                out = await service.save_message(match_id, user_id, msg_in.content)

                await websocket.send_json(out.model_dump(mode="json"))
                await ws_manager.broadcast(match_id, out.model_dump(mode="json"), exclude_user_id=user_id)

        except WebSocketDisconnect:
            logger.info(f"User {user_id} disconnected from match chat {match_id}")
        except Exception as e:
            logger.exception(f"Error in WebSocket chat for match {match_id}: {e}")
            try:
                await websocket.close(code=WS_CLOSE_INTERNAL)
            except Exception:
                pass
        finally:
            ws_manager.disconnect(match_id, user_id)