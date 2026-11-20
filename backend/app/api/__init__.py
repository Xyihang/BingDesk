"""
API 路由初始化
"""
from fastapi import APIRouter
from app.api.wallpapers import router as wallpapers_router
from app.api.settings import router as settings_router
from app.api.system import router as system_router
from app.api.tarot import router as tarot_router
from app.api.auth import router as auth_router

api_router = APIRouter()

api_router.include_router(wallpapers_router, prefix="/api")
api_router.include_router(settings_router, prefix="/api")
api_router.include_router(system_router, prefix="/api")
api_router.include_router(tarot_router, prefix="/api")
api_router.include_router(auth_router, prefix="/api")
