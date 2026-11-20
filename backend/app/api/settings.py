"""
配置管理 API
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from app.database import get_db
from app.models.settings import Setting
from app.schemas.settings import (
    SettingCreate,
    SettingUpdate,
    SettingResponse,
    SettingListResponse,
)

router = APIRouter(prefix="/settings", tags=["配置管理"])


@router.get("", response_model=SettingListResponse)
async def get_settings(db: AsyncSession = Depends(get_db)):
    """获取所有配置"""
    result = await db.execute(select(Setting))
    settings = result.scalars().all()
    return SettingListResponse(total=len(settings), items=settings)


@router.get("/{key}", response_model=SettingResponse)
async def get_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
):
    """获取单个配置"""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    
    if not setting:
        raise HTTPException(status_code=404, detail=f"配置不存在: {key}")
    
    return setting


@router.put("/{key}", response_model=SettingResponse)
async def update_setting(
    key: str,
    data: SettingUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新配置"""
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    
    if not setting:
        setting = Setting(key=key, value=data.value)
        db.add(setting)
    else:
        setting.value = data.value
    
    await db.commit()
    await db.refresh(setting)
    
    return setting


@router.post("/batch")
async def batch_update_settings(
    settings: List[SettingCreate],
    db: AsyncSession = Depends(get_db),
):
    """批量更新配置"""
    for setting_data in settings:
        result = await db.execute(select(Setting).where(Setting.key == setting_data.key))
        setting = result.scalar_one_or_none()
        
        if not setting:
            setting = Setting(
                key=setting_data.key,
                value=setting_data.value,
                description=setting_data.description,
            )
            db.add(setting)
        else:
            setting.value = setting_data.value
            if setting_data.description:
                setting.description = setting_data.description
    
    await db.commit()
    
    return {"message": f"成功更新 {len(settings)} 个配置"}


@router.post("/init")
async def init_default_settings(db: AsyncSession = Depends(get_db)):
    """初始化默认配置"""
    default_settings = [
        Setting(key="auto_change_enabled", value="false", description="是否自动切换壁纸"),
        Setting(key="change_interval", value="60", description="切换间隔（分钟）"),
        Setting(key="download_quality", value="uhd", description="下载质量"),
        Setting(key="auto_start", value="false", description="开机自启"),
        Setting(key="server_port", value="8000", description="服务端口"),
    ]
    
    for setting in default_settings:
        result = await db.execute(select(Setting).where(Setting.key == setting.key))
        existing = result.scalar_one_or_none()
        
        if not existing:
            db.add(setting)
    
    await db.commit()
    
    return {"message": "默认配置初始化完成"}
