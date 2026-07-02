from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text

from app.core.logging import setup_logging
from app.api.router import api_router
from app.api.ws_chat import handle_chat_ws
from app.api.ws_notifications import handle_notifications_ws
from app.api.ws_project_chat import handle_project_chat_ws
from app.core.config import settings
from app.core.database import engine
from app.core.redis import init_redis, close_redis
from app.core.minio_client import init_minio_bucket
from app.models.base import Base  # noqa: F401 - ensures all models are loaded


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        # await conn.run_sync(Base.metadata.create_all)
        await init_minio_bucket()
    
    await init_redis()

    await create_default_admin()
    yield
    await close_redis()
    await engine.dispose()

setup_logging()

async def create_default_admin():
    from app.core.database import async_session
    from app.models.user import User
    from app.core.security import hash_password
    from sqlalchemy import select
    
    async with async_session() as db:
        result = await db.execute(select(User).where(User.user_role == 'admin'))
        admin = result.scalar_one_or_none()
        
        if not admin:
            admin = User(
                email='admin@admin.com',
                full_name='Администратор',
                password_hash=hash_password('admin123'),
                user_role='admin',
                is_active=True,
            )
            db.add(admin)
            await db.commit()
            print("Админ создан: admin@example.com / admin123")

app = FastAPI(
    title="Tinder for Programmers",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
    max_age=600,
)

app.include_router(api_router, prefix="/api")

@app.websocket("/ws/chat/{match_id}")
async def chat_websocket(websocket: WebSocket, match_id: int):
    await handle_chat_ws(websocket, match_id)

@app.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    await handle_notifications_ws(websocket)

@app.websocket("/ws/project/{project_id}")
async def project_chat_websocket(websocket: WebSocket, project_id: int):
    await handle_project_chat_ws(websocket, project_id)

@app.get("/")
async def root():
    return {"message" : "Tinder for Programmers API"}