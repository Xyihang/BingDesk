"""
应用配置管理
"""
from pydantic_settings import BaseSettings
from typing import Optional
import os


class Settings(BaseSettings):
    """应用配置"""
    
    # 基础配置
    APP_NAME: str = "BingDesk"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    
    # 服务配置
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # 数据库配置
    DATABASE_URL: str = "sqlite+aiosqlite:///./data/app.db"
    
    # 文件存储配置
    WALLPAPER_DIR: str = "data/wallpapers"
    LOG_DIR: str = "logs"
    
    # Bing API 配置
    BING_API_BASE: str = "https://bing.img.run"
    DEFAULT_QUALITY: str = "uhd"  # uhd, 1080p, 768p
    
    # AI 服务配置（从 .env 读取，避免密钥进入仓库）
    ZHIPU_API_KEY: Optional[str] = None
    
    # 定时任务配置
    AUTO_CHANGE_ENABLED: bool = False
    CHANGE_INTERVAL_MINUTES: int = 60  # 默认 1 小时切换一次
    
    # CORS 配置
    CORS_ORIGINS: list = [
        "http://localhost:3000",
        "http://localhost:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:5173",
    ]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# 全局配置实例
settings = Settings()


def get_settings() -> Settings:
    """获取配置实例"""
    return settings
