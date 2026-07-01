from fastapi import APIRouter
from app.api.auth import router as auth_router
from app.api.chat import router as chat_router
from app.api.feed import router as feed_router
from app.api.files import router as files_router
from app.api.matches import router as matches_router
from app.api.notifications import router as notifications_router
from app.api.projects import router as projects_router
from app.api.swipes import router as swipes_router
from app.api.users import router as users_router
from app.api.skills import router as skills_router
from app.api.admin import router as admin_router
from app.api.project_chat import router as project_chat_router

api_router = APIRouter()
api_router.include_router(auth_router, prefix="/auth")
api_router.include_router(chat_router, prefix="/chat")
api_router.include_router(feed_router, prefix="/feed")
api_router.include_router(files_router, prefix="/files")
api_router.include_router(matches_router, prefix="/matches")
api_router.include_router(notifications_router, prefix="/notifications")
api_router.include_router(projects_router, prefix="/projects")
api_router.include_router(swipes_router, prefix="/swipes")
api_router.include_router(users_router, prefix="/users")
api_router.include_router(skills_router, prefix="/skills")
api_router.include_router(admin_router, prefix='/admin')
api_router.include_router(project_chat_router, prefix='/projects')