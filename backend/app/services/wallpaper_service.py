"""
壁纸服务
"""
import os
import uuid
from datetime import date
from typing import Optional, List
from pathlib import Path
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update
from loguru import logger

from app.models.wallpaper import Wallpaper
from app.services.bing_service import bing_service
from app.config import settings


class WallpaperService:
    """壁纸管理服务"""
    
    def __init__(self, db: AsyncSession):
        self.db = db
        self.wallpaper_dir = Path(settings.WALLPAPER_DIR)
        self.wallpaper_dir.mkdir(parents=True, exist_ok=True)
    
    async def get_all(self, skip: int = 0, limit: int = 100) -> tuple[int, List[Wallpaper]]:
        """获取所有壁纸"""
        result = await self.db.execute(
            select(Wallpaper).order_by(Wallpaper.created_at.desc()).offset(skip).limit(limit)
        )
        wallpapers = result.scalars().all()
        
        count_result = await self.db.execute(select(Wallpaper))
        total = len(count_result.scalars().all())
        
        return total, wallpapers
    
    async def get_by_id(self, wallpaper_id: int) -> Optional[Wallpaper]:
        """根据 ID 获取壁纸"""
        result = await self.db.execute(
            select(Wallpaper).where(Wallpaper.id == wallpaper_id)
        )
        return result.scalar_one_or_none()
    
    async def get_current(self) -> Optional[Wallpaper]:
        """获取当前壁纸"""
        result = await self.db.execute(
            select(Wallpaper).where(Wallpaper.is_current == True)
        )
        return result.scalar_one_or_none()
    
    async def download_random(self, quality: str = "uhd") -> Wallpaper:
        """下载随机壁纸"""
        try:
            if quality == "uhd":
                image_url = await bing_service.get_random_uhd_url()
            else:
                image_url = await bing_service.get_random_1080p_url()
            
            file_name = f"{date.today().strftime('%Y%m%d')}_{uuid.uuid4().hex[:8]}.jpg"
            file_path = self.wallpaper_dir / file_name
            
            await bing_service.download_image(image_url, str(file_path))
            
            wallpaper = Wallpaper(
                file_path=str(file_path),
                source_url=image_url,
                resolution="3840x2160" if quality == "uhd" else "1920x1080",
                download_date=date.today(),
                is_current=False,
            )
            
            self.db.add(wallpaper)
            await self.db.commit()
            await self.db.refresh(wallpaper)
            
            logger.info(f"壁纸下载成功: {wallpaper.id}")
            return wallpaper
            
        except Exception as e:
            logger.error(f"下载壁纸失败: {e}")
            raise
    
    async def set_as_wallpaper(self, wallpaper_id: int) -> bool:
        """设置为桌面壁纸"""
        from app.utils.wallpaper_setter import set_wallpaper
        
        wallpaper = await self.get_by_id(wallpaper_id)
        if not wallpaper:
            raise ValueError(f"壁纸不存在: {wallpaper_id}")
        
        if not os.path.exists(wallpaper.file_path):
            raise FileNotFoundError(f"壁纸文件不存在: {wallpaper.file_path}")
        
        await self.db.execute(
            update(Wallpaper).values(is_current=False)
        )
        
        wallpaper.is_current = True
        await self.db.commit()
        
        success = set_wallpaper(wallpaper.file_path)
        
        if success:
            logger.info(f"壁纸设置成功: {wallpaper.file_path}")
        else:
            logger.error(f"壁纸设置失败: {wallpaper.file_path}")
        
        return success
    
    async def delete(self, wallpaper_id: int) -> bool:
        """删除壁纸"""
        wallpaper = await self.get_by_id(wallpaper_id)
        if not wallpaper:
            raise ValueError(f"壁纸不存在：{wallpaper_id}")
        
        if wallpaper.is_current:
            raise ValueError("不能删除当前使用的壁纸")
        
        if os.path.exists(wallpaper.file_path):
            os.remove(wallpaper.file_path)
        
        await self.db.delete(wallpaper)
        await self.db.commit()
        
        logger.info(f"壁纸删除成功：{wallpaper_id}")
        return True
    
    async def delete_all_except_current(self) -> int:
        """一键删除除当前壁纸外的所有壁纸"""
        result = await self.db.execute(
            select(Wallpaper).where(Wallpaper.is_current == False)
        )
        wallpapers_to_delete = result.scalars().all()
        
        deleted_count = 0
        for wallpaper in wallpapers_to_delete:
            try:
                if os.path.exists(wallpaper.file_path):
                    os.remove(wallpaper.file_path)
                await self.db.delete(wallpaper)
                deleted_count += 1
            except Exception as e:
                logger.error(f"删除壁纸 {wallpaper.id} 失败：{e}")
                continue
        
        await self.db.commit()
        
        logger.info(f"批量删除壁纸完成：共删除 {deleted_count} 张")
        return deleted_count
    
    async def download_and_set(self, quality: str = "uhd") -> Wallpaper:
        """下载并设置为壁纸"""
        wallpaper = await self.download_random(quality)
        await self.set_as_wallpaper(wallpaper.id)
        return wallpaper
