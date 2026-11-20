"""
Pydantic 模式 - 壁纸
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class WallpaperBase(BaseModel):
    """壁纸基础模式"""
    file_path: str = Field(..., description="文件路径")
    source_url: Optional[str] = Field(None, description="来源 URL")
    resolution: Optional[str] = Field(None, description="分辨率")
    bing_date: Optional[date] = Field(None, description="Bing 原始日期")


class WallpaperCreate(WallpaperBase):
    """创建壁纸模式"""
    is_current: bool = False


class WallpaperUpdate(BaseModel):
    """更新壁纸模式"""
    is_current: Optional[bool] = None


class WallpaperResponse(WallpaperBase):
    """壁纸响应模式"""
    id: int
    download_date: date
    is_current: bool
    created_at: datetime
    
    class Config:
        from_attributes = True


class WallpaperListResponse(BaseModel):
    """壁纸列表响应"""
    total: int
    items: list[WallpaperResponse]


class WallpaperInfo(BaseModel):
    """Bing 壁纸信息"""
    url: str
    copyright: str
    copyright_link: str
    end_date: str
    full_start_date: str
