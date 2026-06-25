from sqlalchemy import select
from app.core.database import async_session
from app.core.security import decode_token
from app.core.ws_manager import notification_manager
from app.models.user import User


async def handle_notifications_ws(websocket):
    await websocket.accept()

    token = websocket.query_params.get("token")
    if not token:
        await websocket.close(code=4001)
        return

    try:
        payload = decode_token(token)
    except ValueError:
        await websocket.close(code=4001)
        return

    if payload.get("type") != "access":
        await websocket.close(code=4001)
        return

    user_id = int(payload["sub"])

    async with async_session() as db:
        result = await db.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user or not user.is_active or user.is_banned:
            await websocket.close(code=4001)
            return

        await notification_manager.connect(user_id, websocket)

        try:
            while True:
                await websocket.receive_text()
        except Exception:
            pass
        finally:
            notification_manager.disconnect(user_id)
