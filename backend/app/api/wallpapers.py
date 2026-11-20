"""
壁纸管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
from PIL import Image
import os
import io

from app.database import get_db
from app.models.wallpaper import Wallpaper
from app.services.wallpaper_service import WallpaperService
from app.schemas.wallpaper import (
    WallpaperResponse,
    WallpaperListResponse,
)

router = APIRouter(prefix="/wallpapers", tags=["壁纸管理"])

THUMBNAIL_DIR = os.path.abspath("data/thumbnails")
os.makedirs(THUMBNAIL_DIR, exist_ok=True)


@router.get("", response_model=WallpaperListResponse)
async def get_wallpapers(
    skip: int = Query(0, ge=0, description="跳过数量"),
    limit: int = Query(100, ge=1, le=500, description="返回数量"),
    db: AsyncSession = Depends(get_db),
):
    """获取壁纸列表"""
    service = WallpaperService(db)
    total, wallpapers = await service.get_all(skip, limit)
    return WallpaperListResponse(total=total, items=wallpapers)


@router.get("/current", response_model=WallpaperResponse)
async def get_current_wallpaper(db: AsyncSession = Depends(get_db)):
    """获取当前壁纸"""
    service = WallpaperService(db)
    wallpaper = await service.get_current()
    if not wallpaper:
        raise HTTPException(status_code=404, detail="当前没有设置壁纸")
    return wallpaper


@router.post("/download", response_model=WallpaperResponse)
async def download_wallpaper(
    quality: str = Query("uhd", description="图片质量: uhd 或 1080p"),
    set_as_wallpaper: bool = Query(False, description="是否同时设置为壁纸"),
    db: AsyncSession = Depends(get_db),
):
    """下载随机壁纸"""
    service = WallpaperService(db)
    
    try:
        if set_as_wallpaper:
            wallpaper = await service.download_and_set(quality)
        else:
            wallpaper = await service.download_random(quality)
        return wallpaper
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载壁纸失败: {str(e)}")


@router.post("/{wallpaper_id}/set")
async def set_wallpaper(
    wallpaper_id: int,
    db: AsyncSession = Depends(get_db),
):
    """设置为桌面壁纸"""
    service = WallpaperService(db)
    
    try:
        success = await service.set_as_wallpaper(wallpaper_id)
        if not success:
            raise HTTPException(status_code=500, detail="设置壁纸失败")
        return {"message": "壁纸设置成功", "wallpaper_id": wallpaper_id}
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"设置壁纸失败: {str(e)}")


@router.get("/{wallpaper_id}/image")
async def get_wallpaper_image(
    wallpaper_id: int,
    width: Optional[int] = Query(None, ge=100, le=3840, description="缩略图宽度，不传则返回原图"),
    db: AsyncSession = Depends(get_db),
):
    """获取壁纸图片文件，支持缩略图"""
    result = await db.execute(
        select(Wallpaper).where(Wallpaper.id == wallpaper_id)
    )
    wallpaper = result.scalar_one_or_none()
    if not wallpaper:
        raise HTTPException(status_code=404, detail="壁纸不存在")
    file_path = os.path.abspath(wallpaper.file_path)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="壁纸文件不存在")
    if width:
        thumb_name = f"{wallpaper.id}_{width}.jpg"
        thumb_path = os.path.join(THUMBNAIL_DIR, thumb_name)
        if not os.path.exists(thumb_path):
            img = Image.open(file_path)
            ratio = width / img.width
            height = int(img.height * ratio)
            img = img.resize((width, height), Image.LANCZOS)
            img.save(thumb_path, "JPEG", quality=80, optimize=True)
        return FileResponse(thumb_path, media_type="image/jpeg")
    return FileResponse(file_path, media_type="image/jpeg")


@router.delete("/{wallpaper_id}")
async def delete_wallpaper(
    wallpaper_id: int,
    db: AsyncSession = Depends(get_db),
):
    """删除壁纸"""
    service = WallpaperService(db)
    
    try:
        success = await service.delete(wallpaper_id)
        return {"message": "壁纸删除成功", "wallpaper_id": wallpaper_id}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"删除壁纸失败：{str(e)}")


@router.delete("/batch/all-except-current")
async def delete_all_except_current(
    db: AsyncSession = Depends(get_db),
):
    """一键删除除当前壁纸外的所有壁纸"""
    service = WallpaperService(db)
    
    try:
        deleted_count = await service.delete_all_except_current()
        return {"message": f"成功删除 {deleted_count} 张壁纸", "deleted_count": deleted_count}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"批量删除壁纸失败：{str(e)}")
