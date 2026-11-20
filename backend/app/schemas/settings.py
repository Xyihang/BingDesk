"""
Pydantic 模式 - 配置
"""
from pydantic import BaseModel, Field
from typing import Optional, Union
from datetime import datetime


class SettingBase(BaseModel):
    """配置基础模式"""
    key: str = Field(..., min_length=1, max_length=50, description="配置键")
    value: str = Field(..., description="配置值")
    description: Optional[str] = Field(None, max_length=200, description="配置描述")


class SettingCreate(SettingBase):
    """创建配置模式"""
    pass


class SettingUpdate(BaseModel):
    """更新配置模式"""
    value: str = Field(..., description="配置值")


class SettingResponse(SettingBase):
    """配置响应模式"""
    id: int
    updated_at: datetime
    
    class Config:
        from_attributes = True


class SettingListResponse(BaseModel):
    """配置列表响应"""
    total: int
    items: list[SettingResponse]


class SystemStatus(BaseModel):
    """系统状态响应"""
    app_name: str
    version: str
    is_running: bool
    auto_start: bool
    current_wallpaper: Optional[str]
    next_change_time: Optional[datetime]
    database_size: str
    wallpaper_count: int
