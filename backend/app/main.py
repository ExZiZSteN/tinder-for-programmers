from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import text

from app.core.logging import setup_logging
from app.api.router import api_router
from app.api.ws_chat import handle_chat_ws
from app.api.ws_notifications import handle_notifications_ws
from app.core.config import settings
from app.core.database import engine
from app.core.minio_client import init_minio_bucket
from app.models.base import Base  # noqa: F401 - ensures all models are loaded


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.create_all)
    await init_minio_bucket()
    yield
    await engine.dispose()

setup_logging()

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
)

app.include_router(api_router, prefix="/api")

@app.websocket("/ws/chat/{match_id}")
async def chat_websocket(websocket: WebSocket, match_id: int):
    await handle_chat_ws(websocket, match_id)

@app.websocket("/ws/notifications")
async def notifications_websocket(websocket: WebSocket):
    await handle_notifications_ws(websocket)

@app.get("/")
async def root():
    return {"message" : "Tinder for Programmers API"}