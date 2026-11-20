"""
认证 API - 密码验证与修改 + U盘密钥检测
"""
import asyncio
import ctypes
import hashlib
import hmac
import os
import sys
from pathlib import Path

from fastapi import APIRouter, Depends
from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Literal, Optional

from app.database import get_db
from app.models.settings import Setting

router = APIRouter(prefix="/auth", tags=["认证"])


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def _verify_password(password: str, stored_hash: str) -> bool:
    return hmac.compare_digest(_hash_password(password), stored_hash)


async def _get_setting(db: AsyncSession, key: str) -> str | None:
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    return setting.value if setting else None


async def _set_setting(db: AsyncSession, key: str, value: str):
    result = await db.execute(select(Setting).where(Setting.key == key))
    setting = result.scalar_one_or_none()
    if setting:
        setting.value = value
    else:
        db.add(Setting(key=key, value=value))
    await db.commit()


class VerifyRequest(BaseModel):
    password: str
    type: Literal["app", "grid"]


class VerifyResponse(BaseModel):
    valid: bool


class ChangePasswordRequest(BaseModel):
    current_password: str
    new_password: str
    type: Literal["app", "grid"]


class ChangePasswordResponse(BaseModel):
    success: bool
    message: str


@router.post("/verify", response_model=VerifyResponse)
async def verify_password(req: VerifyRequest, db: AsyncSession = Depends(get_db)):
    if req.type == "app":
        stored = await _get_setting(db, "app_password")
        if stored and _verify_password(req.password, stored):
            return VerifyResponse(valid=True)
        return VerifyResponse(valid=False)

    stored = await _get_setting(db, "grid_password")
    if stored and _verify_password(req.password, stored):
        return VerifyResponse(valid=True)

    admin_stored = await _get_setting(db, "app_password")
    if admin_stored and _verify_password(req.password, admin_stored):
        return VerifyResponse(valid=True)

    return VerifyResponse(valid=False)


@router.put("/password", response_model=ChangePasswordResponse)
async def change_password(req: ChangePasswordRequest, db: AsyncSession = Depends(get_db)):
    if len(req.new_password) < 4:
        return ChangePasswordResponse(success=False, message="新密码长度不能少于4位")

    if req.current_password == req.new_password:
        return ChangePasswordResponse(success=False, message="新密码不能与当前密码相同")

    key = "app_password" if req.type == "app" else "grid_password"
    stored = await _get_setting(db, key)

    if not stored or not _verify_password(req.current_password, stored):
        return ChangePasswordResponse(success=False, message="当前密码错误")

    new_hash = _hash_password(req.new_password)
    await _set_setting(db, key, new_hash)

    return ChangePasswordResponse(success=True, message="密码修改成功")


DEFAULT_USB_KEY_FILE = ".cstest_auth"


class USBCheckResponse(BaseModel):
    found: bool
    drive: Optional[str] = None
    message: str


def _get_removable_drives_ctypes() -> list[str]:
    """使用 Windows API (ctypes) 直接检测可移动驱动器，不依赖 PowerShell"""
    if sys.platform != "win32":
        return []
    
    DRIVE_REMOVABLE = 2
    kernel32 = ctypes.windll.kernel32
    GetDriveTypeW = kernel32.GetDriveTypeW
    
    removable_drives = []
    for letter in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        drive_path = f"{letter}:\\"
        try:
            drive_type = GetDriveTypeW(drive_path)
            if drive_type == DRIVE_REMOVABLE:
                removable_drives.append(f"{letter}:")
                logger.debug(f"检测到可移动驱动器: {letter}:")
        except Exception as e:
            logger.debug(f"检测驱动器 {letter}: 时出错: {e}")
            continue
    
    return removable_drives


async def _get_removable_drives() -> list[str]:
    """异步包装 ctypes 调用"""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, _get_removable_drives_ctypes)


async def _find_key_on_drives(drives: list[str], key_file: str) -> Optional[str]:
    for drive in drives:
        try:
            key_path = Path(f"{drive}\\") / key_file
            if key_path.exists() and key_path.is_file():
                return drive
        except Exception:
            continue
    return None


@router.post("/check-usb", response_model=USBCheckResponse)
async def check_usb_key(
    db: AsyncSession = Depends(get_db),
):
    key_file = await _get_setting(db, "usb_key_filename")
    if not key_file:
        key_file = DEFAULT_USB_KEY_FILE

    drives = await _get_removable_drives()
    if not drives:
        return USBCheckResponse(found=False, message="未检测到可移动驱动器，请插入U盘后重试")

    found_drive = await _find_key_on_drives(drives, key_file)
    if found_drive:
        logger.info(f"U盘密钥验证通过，驱动器: {found_drive}")
        return USBCheckResponse(found=True, drive=found_drive, message="U盘密钥验证通过")

    return USBCheckResponse(found=False, message=f"未在可移动驱动器中找到密钥文件 '{key_file}'")
