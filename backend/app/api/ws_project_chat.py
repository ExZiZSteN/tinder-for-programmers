import logging
from fastapi import WebSocket, WebSocketDisconnect
from sqlalchemy import select
from app.core.database import async_session
from app.core.security import decode_token
from app.core.ws_manager import project_chat_manager
from app.core.exceptions import NotFoundException, ForbiddenException
from app.models.user import User
from app.schemas.project_message import WSProjectMessageIn
from app.services.project_chat import ProjectChatService

logger = logging.getLogger(__name__)

WS_CLOSE_UNAUTHORIZED = 4001
WS_CLOSE_FORBIDDEN = 4003
WS_CLOSE_NOT_FOUND = 4004
WS_CLOSE_INTERNAL = 1011


async def handle_project_chat_ws(websocket: WebSocket, project_id: int):
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

        service = ProjectChatService(db)

        try:
            await service._verify_participant(user, project_id)
        except NotFoundException:
            await websocket.close(code=WS_CLOSE_NOT_FOUND)
            return
        except ForbiddenException:
            await websocket.close(code=WS_CLOSE_FORBIDDEN)
            return

        await project_chat_manager.connect(project_id, user_id, websocket)

        try:
            while True:
                raw = await websocket.receive_text()

                try:
                    msg_in = WSProjectMessageIn.model_validate_json(raw)
                except Exception:
                    await websocket.send_json({"type": "error", "detail": "Invalid message format"})
                    continue

                if msg_in.type != "message":
                    await websocket.send_json({"type": "error", "detail": "Unknown message type"})
                    continue

                out = await service.save_message(project_id, user_id, msg_in.content)

                # Отправляем всем участникам проекта (включая отправителя)
                await project_chat_manager.broadcast(project_id, out.model_dump(mode="json"))

        except WebSocketDisconnect:
            logger.info(f"User {user_id} disconnected from project chat {project_id}")
        except Exception as e:
            logger.exception(f"Error in WebSocket project chat for project {project_id}: {e}")
            try:
                await websocket.close(code=WS_CLOSE_INTERNAL)
            except Exception:
                pass
        finally:
            project_chat_manager.disconnect(project_id, user_id)