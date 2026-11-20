"""
工具函数初始化
"""
from app.utils.wallpaper_setter import set_wallpaper, get_wallpaper
from app.utils.auto_start import (
    enable_autostart,
    disable_autostart,
    is_autostart_enabled,
    get_autostart_scripts,
)

__all__ = [
    "set_wallpaper",
    "get_wallpaper",
    "enable_autostart",
    "disable_autostart",
    "is_autostart_enabled",
    "get_autostart_scripts",
]
