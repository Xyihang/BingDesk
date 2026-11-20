"""
Pydantic 模式初始化
"""
from app.schemas.course import (
    CourseBase,
    CourseCreate,
    CourseUpdate,
    CourseResponse,
    CourseListResponse,
)
from app.schemas.wallpaper import (
    WallpaperBase,
    WallpaperCreate,
    WallpaperUpdate,
    WallpaperResponse,
    WallpaperListResponse,
    WallpaperInfo,
)
from app.schemas.settings import (
    SettingBase,
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingListResponse,
    SystemStatus,
)

__all__ = [
    "CourseBase",
    "CourseCreate",
    "CourseUpdate",
    "CourseResponse",
    "CourseListResponse",
    "WallpaperBase",
    "WallpaperCreate",
    "WallpaperUpdate",
    "WallpaperResponse",
    "WallpaperListResponse",
    "WallpaperInfo",
    "SettingBase",
    "SettingCreate",
    "SettingUpdate",
    "SettingResponse",
    "SettingListResponse",
    "SystemStatus",
]
