import json
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from app.core.database import async_session
from app.core.security import decode_token
from app.core.ws_manager import ws_manager
from app.models.match import Match
from app.models.user import User
from app.schemas.message import WSMessageIn, WSMessageOut
from app.services.chat import ChatService


WS_CLOSE_UNAUTHORIZED = 4001    #неавторизован
WS_CLOSE_FORBIDDEN = 4003       #нет доступа
WS_CLOSE_NOT_FOUND = 4004       #не найдено
WS_CLOSE_INTERNAL = 1011        #внутрення ошибка


async def handle_chat_ws(websocket, match_id: int):
    await websocket.accept()

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
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
        result = await db.execute(
            select(Match).options(
                selectinload(Match.project)
                ).where(Match.id == match_id)
            )
        match = result.scalar_one_or_none()
        if not match:
            await websocket.close(code=WS_CLOSE_NOT_FOUND)
            return

        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active or user.is_banned:
            await websocket.close(code=WS_CLOSE_UNAUTHORIZED)
            return

        if match.user_id != user_id and match.project.owner_id != user_id:
            await websocket.close(code=WS_CLOSE_FORBIDDEN)
            return

        service = ChatService(db)
        await ws_manager.connect(match_id, user_id, websocket)

        try:
            while True:
                raw = await websocket.receive_text()
                try:
                    data = json.loads(raw)
                    msg_in = WSMessageIn(**data)
                except (json.JSONDecodeError, ValueError):
                    await websocket.send_json({"type": "error", "detail": "Invalid message format"})
                    continue

                if msg_in.type != "message":
                    await websocket.send_json({"type": "error", "detail": "Unknown message type"})
                    continue

                out = await service.save_message(match_id, user_id, msg_in.content)

                await websocket.send_json(out.model_dump(mode="json"))
                await ws_manager.broadcast(match_id, out.model_dump(mode="json"), exclude_user_id=user_id)

        except Exception:
            pass
        finally:
            ws_manager.disconnect(match_id, user_id)
