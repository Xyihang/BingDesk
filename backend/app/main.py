"""
Bing 壁纸管理系统 - 主入口
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from pathlib import Path
import sys

from app.config import settings
from app.database import init_db, close_db, AsyncSessionLocal
from app.api import api_router
from app.models.wallpaper import Wallpaper
from sqlalchemy import select


def setup_logging():
    """配置日志"""
    log_dir = Path(settings.LOG_DIR)
    log_dir.mkdir(parents=True, exist_ok=True)
    
    logger.remove()
    
    logger.add(
        sys.stdout,
        level="DEBUG" if settings.DEBUG else "INFO",
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    )
    
    logger.add(
        f"{log_dir}/app_{{time:YYYY-MM-DD}}.log",
        rotation="00:00",
        retention="7 days",
        level="DEBUG",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        encoding="utf-8",
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理"""
    import asyncio
    
    setup_logging()
    logger.info(f"启动 {settings.APP_NAME} v{settings.APP_VERSION}")
    
    await init_db()
    logger.info("数据库初始化完成")
    
    # 延迟20秒后下载壁纸（等待系统完全启动）
    async def delayed_wallpaper_download():
        await asyncio.sleep(20)
        try:
            from app.services.wallpaper_service import WallpaperService
            
            async with AsyncSessionLocal() as db:
                wallpaper_service = WallpaperService(db)
                logger.info("延迟20秒后自动下载壁纸...")
                wallpaper = await wallpaper_service.download_and_set("uhd")
                logger.info(f"启动壁纸下载完成: {wallpaper.id}")
        except Exception as e:
            logger.error(f"启动时下载壁纸失败: {e}")
    
    # 启动后台任务下载壁纸
    asyncio.create_task(delayed_wallpaper_download())
    
    # 根据数据库设置自动启动调度器（仅在调度器未运行时启动）
    try:
        from app.services.scheduler import start_scheduler, is_scheduler_running
        from app.models.settings import Setting
        
        async with AsyncSessionLocal() as db:
            # 获取自动切换设置
            result = await db.execute(select(Setting).where(Setting.key == "auto_change_enabled"))
            auto_change_setting = result.scalar_one_or_none()
            
            if auto_change_setting and auto_change_setting.value == "true":
                # 检查调度器是否已在运行（防止重复启动）
                if is_scheduler_running():
                    logger.info("调度器已在运行，跳过启动")
                else:
                    # 获取切换间隔
                    result = await db.execute(select(Setting).where(Setting.key == "change_interval"))
                    interval_setting = result.scalar_one_or_none()
                    interval = int(interval_setting.value) if interval_setting else 60
                    
                    start_scheduler(interval)
                    logger.info(f"根据设置自动启动调度器，间隔：{interval} 分钟")
    except Exception as e:
        logger.error(f"自动启动调度器失败：{e}")
    
    yield
    
    await close_db()
    logger.info("应用关闭")


def create_app() -> FastAPI:
    """创建 FastAPI 应用"""
    app = FastAPI(
        title=settings.APP_NAME,
        version=settings.APP_VERSION,
        description="Bing 壁纸与课程表管理系统",
        lifespan=lifespan,
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(api_router)
    
    @app.get("/")
    async def root():
        return {
            "name": settings.APP_NAME,
            "version": settings.APP_VERSION,
            "docs": "/docs",
            "status": "running",
        }
    
    @app.get("/health")
    async def health():
        return {"status": "healthy"}
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
    )
