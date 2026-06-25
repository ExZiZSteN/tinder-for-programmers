from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.feed import router as feed_router
from app.api.matches import router as matches_router
from app.api.notifications import router as notifications_router
from app.api.projects import router as projects_router
from app.api.swipes import router as swipes_router
from app.api.users import router as users_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(feed_router, prefix="/feed")
api_router.include_router(matches_router, prefix="/matches")
api_router.include_router(notifications_router, prefix="/notifications")
api_router.include_router(projects_router, prefix="/projects")
api_router.include_router(swipes_router, prefix="/swipes")
api_router.include_router(users_router, prefix="/users")