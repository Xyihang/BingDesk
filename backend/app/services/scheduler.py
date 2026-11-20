"""
定时任务调度器
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from loguru import logger
from app.database import async_session_maker
from app.services.wallpaper_service import WallpaperService


# 使用字典存储调度器实例，避免重复创建
_scheduler_instance = None


def get_scheduler():
    """获取调度器实例（单例模式）"""
    global _scheduler_instance
    if _scheduler_instance is None or not _scheduler_instance.running:
        _scheduler_instance = AsyncIOScheduler()
    return _scheduler_instance


async def auto_change_wallpaper():
    """自动更换壁纸任务"""
    logger.info("开始自动更换壁纸...")
    try:
        async with async_session_maker() as db:
            service = WallpaperService(db)
            wallpaper = await service.download_and_set()
            logger.info(f"自动更换壁纸成功: {wallpaper.id}")
    except Exception as e:
        logger.error(f"自动更换壁纸失败: {e}")


def start_scheduler(interval_minutes: int = 60):
    """启动调度器"""
    scheduler = get_scheduler()
    
    # 如果已经在运行，先停止
    if scheduler.running:
        logger.info("调度器已在运行，先停止再重新启动")
        scheduler.shutdown(wait=False)
        # 重新创建实例
        global _scheduler_instance
        _scheduler_instance = AsyncIOScheduler()
        scheduler = _scheduler_instance
    
    # 添加任务
    scheduler.add_job(
        auto_change_wallpaper,
        IntervalTrigger(minutes=interval_minutes),
        id="auto_wallpaper",
        replace_existing=True,
    )
    
    scheduler.start()
    logger.info(f"定时任务已启动，间隔: {interval_minutes} 分钟")


def stop_scheduler():
    """停止调度器"""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("定时任务已停止")


def update_interval(interval_minutes: int):
    """更新定时任务间隔"""
    scheduler = get_scheduler()
    if scheduler.running:
        scheduler.modify_job("auto_wallpaper", trigger=IntervalTrigger(minutes=interval_minutes))
        logger.info(f"定时任务间隔已更新: {interval_minutes} 分钟")


def is_scheduler_running() -> bool:
    """检查调度器是否运行"""
    scheduler = get_scheduler()
    return scheduler.running
