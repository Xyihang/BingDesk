"""
服务层初始化
"""
from app.services.bing_service import bing_service, BingService
from app.services.wallpaper_service import WallpaperService
from app.services.scheduler import (
    get_scheduler,
    start_scheduler,
    stop_scheduler,
    update_interval,
    is_scheduler_running,
)

__all__ = [
    "bing_service",
    "BingService",
    "WallpaperService",
    "get_scheduler",
    "start_scheduler",
    "stop_scheduler",
    "update_interval",
    "is_scheduler_running",
]
