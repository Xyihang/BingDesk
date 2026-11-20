"""
系统管理 API
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from loguru import logger
import os

from app.database import get_db
from app.models.wallpaper import Wallpaper
from app.models.settings import Setting
from app.utils.auto_start import enable_autostart, disable_autostart, is_autostart_enabled
from app.services.scheduler import start_scheduler, stop_scheduler, is_scheduler_running
from app.schemas.settings import SystemStatus
from app.config import settings as app_settings

router = APIRouter(prefix="/system", tags=["系统管理"])


@router.get("/status", response_model=SystemStatus)
async def get_system_status(db: AsyncSession = Depends(get_db)):
    """获取系统状态"""
    result = await db.execute(select(Setting).where(Setting.key == "auto_change_enabled"))
    auto_change_setting = result.scalar_one_or_none()
    auto_change_enabled = auto_change_setting.value == "true" if auto_change_setting else False
    
    result = await db.execute(select(Setting).where(Setting.key == "change_interval"))
    interval_setting = result.scalar_one_or_none()
    interval = int(interval_setting.value) if interval_setting else 60
    
    result = await db.execute(select(Wallpaper).where(Wallpaper.is_current == True))
    current_wallpaper = result.scalar_one_or_none()
    
    result = await db.execute(select(Wallpaper))
    wallpaper_count = len(result.scalars().all())
    
    db_path = Path("data/app.db")
    db_size = f"{db_path.stat().st_size / 1024 / 1024:.2f} MB" if db_path.exists() else "0 MB"
    
    from datetime import datetime
    next_change = None
    if auto_change_enabled and is_scheduler_running():
        from datetime import timedelta
        next_change = datetime.now() + timedelta(minutes=interval)
    
    return SystemStatus(
        app_name=app_settings.APP_NAME,
        version=app_settings.APP_VERSION,
        is_running=is_scheduler_running(),
        auto_start=is_autostart_enabled(),
        current_wallpaper=current_wallpaper.file_path if current_wallpaper else None,
        next_change_time=next_change,
        database_size=db_size,
        wallpaper_count=wallpaper_count,
    )


@router.get("/autostart/scripts")
async def get_autostart_scripts():
    """获取开机自启脚本内容（BAT 和 PowerShell），使用系统默认 Python"""
    from app.utils.auto_start import get_startup_folder
    
    backend_path = Path(__file__).parent.parent.parent
    frontend_path = backend_path.parent / "frontend"
    startup_folder = get_startup_folder()
    
    bat_script = f"""@echo off
chcp 65001 >nul
setlocal enabledelayedexpansion

set "BACKEND_DIR={backend_path}"
set "FRONTEND_DIR={frontend_path}"

python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 未安装或未添加到 PATH
    exit /b 1
)

node --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Node.js 未安装或未添加到 PATH
    exit /b 1
)

cd /d "%BACKEND_DIR%"
start "" python -m uvicorn app.main:app --host 0.0.0.0 --port 8000

timeout /t 3 /nobreak >nul

cd /d "%FRONTEND_DIR%"
start "" npm run dev

exit"""

    ps_script = f"""# Bing 壁纸管理系统 - 一键启动

$BackendDir = "{backend_path}"
$FrontendDir = "{frontend_path}"

$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {{
    Write-Host "[ERROR] Python 未安装或未添加到 PATH" -ForegroundColor Red
    exit 1
}}

$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCmd) {{
    Write-Host "[ERROR] Node.js 未安装或未添加到 PATH" -ForegroundColor Red
    exit 1
}}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bing 壁纸管理系统 - 一键启动" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "正在启动后端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$BackendDir'; python -m uvicorn app.main:app --host 0.0.0.0 --port 8000"

Write-Host "等待后端启动（5 秒）..." -ForegroundColor Cyan
Start-Sleep -Seconds 5

Write-Host "正在启动前端服务..." -ForegroundColor Yellow
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd '$FrontendDir'; npm run dev"

Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  服务启动完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Cyan
Write-Host "  前端：http://localhost:5173" -ForegroundColor White
Write-Host "  后端：http://localhost:8000" -ForegroundColor White
Write-Host "  API 文档：http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
Write-Host "按任意键退出此窗口（不影响已启动的服务）" -ForegroundColor Yellow
pause >nul"""

    bat_hidden_script = f"""@echo off
set "BACKEND_DIR={backend_path}"
set "FRONTEND_DIR={frontend_path}"

powershell -WindowStyle Hidden -Command "Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory '{backend_path}' -WindowStyle Hidden"

ping -n 4 127.0.0.1 >nul

powershell -WindowStyle Hidden -Command "Start-Process -FilePath 'cmd' -ArgumentList '/c','npm run dev' -WorkingDirectory '{frontend_path}' -WindowStyle Hidden"

exit"""

    ps_hidden_script = f"""$BackendDir = "{backend_path}"
$FrontendDir = "{frontend_path}"

Start-Process -FilePath 'python' -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory $BackendDir -WindowStyle Hidden

Start-Sleep -Seconds 3

Start-Process -FilePath 'cmd' -ArgumentList '/c','npm run dev' -WorkingDirectory $FrontendDir -WindowStyle Hidden

Write-Host "前后端服务已在后台静默启动" -ForegroundColor Green
Write-Host "前端：http://localhost:5173  后端：http://localhost:8000" -ForegroundColor Cyan"""

    return {
        "bat": bat_script,
        "powershell": ps_script,
        "bat_hidden": bat_hidden_script,
        "powershell_hidden": ps_hidden_script,
        "startup_folder": str(startup_folder),
        "backend_path": str(backend_path),
        "frontend_path": str(frontend_path)
    }


@router.post("/autostart")
async def set_autostart(
    enabled: bool = Query(..., description="是否启用开机自启"),
    db: AsyncSession = Depends(get_db),
):
    """设置开机自启（同步数据库和系统设置）"""
    from app.models.settings import Setting
    from sqlalchemy import select
    
    if enabled:
        success = enable_autostart()
        if not success:
            raise HTTPException(status_code=500, detail="启用开机自启失败")
    else:
        success = disable_autostart()
        if not success:
            raise HTTPException(status_code=500, detail="禁用开机自启失败")
    
    # 同步更新数据库配置
    try:
        result = await db.execute(select(Setting).where(Setting.key == "auto_start"))
        setting = result.scalar_one_or_none()
        
        if not setting:
            setting = Setting(key="auto_start", value=str(enabled).lower(), description="开机自启")
            db.add(setting)
        else:
            setting.value = str(enabled).lower()
        
        await db.commit()
        logger.info(f"数据库配置已同步：auto_start = {enabled}")
    except Exception as e:
        logger.error(f"同步数据库配置失败：{e}")
        # 不抛出异常，避免影响主流程
    
    return {"message": f"开机自启已{'启用' if enabled else '禁用'}", "enabled": enabled}


@router.get("/autostart")
async def get_autostart_status():
    """获取开机自启状态"""
    enabled = is_autostart_enabled()
    return {"enabled": enabled}


@router.post("/scheduler/start")
async def start_auto_change(
    interval: int = Query(60, ge=1, le=1440, description="切换间隔（分钟）"),
    db: AsyncSession = Depends(get_db),
):
    """启动自动切换"""
    result = await db.execute(select(Setting).where(Setting.key == "auto_change_enabled"))
    setting = result.scalar_one_or_none()
    
    if not setting:
        setting = Setting(key="auto_change_enabled", value="true")
        db.add(setting)
    else:
        setting.value = "true"
    
    result = await db.execute(select(Setting).where(Setting.key == "change_interval"))
    interval_setting = result.scalar_one_or_none()
    
    if not interval_setting:
        interval_setting = Setting(key="change_interval", value=str(interval))
        db.add(interval_setting)
    else:
        interval_setting.value = str(interval)
    
    await db.commit()
    
    start_scheduler(interval)
    
    return {"message": "自动切换已启动", "interval": interval}


@router.post("/scheduler/stop")
async def stop_auto_change(db: AsyncSession = Depends(get_db)):
    """停止自动切换"""
    result = await db.execute(select(Setting).where(Setting.key == "auto_change_enabled"))
    setting = result.scalar_one_or_none()
    
    if setting:
        setting.value = "false"
        await db.commit()
    
    stop_scheduler()
    
    return {"message": "自动切换已停止"}


@router.get("/logs")
async def get_logs(
    lines: int = Query(100, ge=1, le=1000, description="返回行数"),
):
    """获取系统日志"""
    log_dir = Path("logs")
    if not log_dir.exists():
        return {"logs": [], "message": "日志目录不存在"}
    
    log_files = sorted(log_dir.glob("*.log"), reverse=True)
    if not log_files:
        return {"logs": [], "message": "没有日志文件"}
    
    latest_log = log_files[0]
    
    try:
        with open(latest_log, "r", encoding="utf-8") as f:
            all_lines = f.readlines()
            log_lines = all_lines[-lines:]
        
        return {"logs": [line.strip() for line in log_lines], "file": str(latest_log)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"读取日志失败: {str(e)}")


@router.post("/services/stop")
async def stop_services():
    """停止前后端服务"""
    import subprocess
    import platform
    import os
    import asyncio
    
    try:
        stopped_processes = []
        processes_to_kill = []
        current_pid = os.getpid()
        
        if platform.system() == "Windows":
            result = subprocess.run(
                ["tasklist"],
                capture_output=True,
                text=True,
                check=False,
                creationflags=subprocess.CREATE_NO_WINDOW
            )
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if 'python.exe' in line or 'node.exe' in line:
                        parts = line.split()
                        if len(parts) >= 2:
                            try:
                                pid = int(parts[1])
                                process_name = parts[0]
                                
                                if 'python.exe' in process_name or 'node.exe' in process_name:
                                    processes_to_kill.append((process_name, pid))
                                    if pid != current_pid:
                                        kill_result = subprocess.run(
                                            ["taskkill", "/F", "/PID", str(pid)],
                                            capture_output=True,
                                            text=True,
                                            check=False,
                                            creationflags=subprocess.CREATE_NO_WINDOW
                                        )
                                        if kill_result.returncode == 0:
                                            stopped_processes.append(f"{process_name} (PID: {pid})")
                                            logger.info(f"已停止进程: {process_name} (PID: {pid})")
                            except (ValueError, subprocess.SubprocessError) as e:
                                logger.warning(f"处理进程失败: {e}")
                                continue
        
        async def kill_current_process():
            await asyncio.sleep(0.5)
            try:
                subprocess.run(
                    ["taskkill", "/F", "/PID", str(current_pid)],
                    capture_output=True,
                    text=True,
                    check=False,
                    creationflags=subprocess.CREATE_NO_WINDOW
                )
                logger.info(f"已停止当前进程: PID {current_pid}")
            except Exception as e:
                logger.error(f"停止当前进程失败: {e}")
        
        if processes_to_kill:
            for process_name, pid in processes_to_kill:
                if pid == current_pid:
                    stopped_processes.append(f"{process_name} (PID: {pid}) - 将在响应后停止")
                    asyncio.create_task(kill_current_process())
                    break
            
            return {
                "success": True,
                "message": f"已停止 {len(stopped_processes)} 个进程",
                "processes": stopped_processes
            }
        else:
            return {
                "success": True,
                "message": "未找到运行中的前后端服务",
                "processes": []
            }
            
    except Exception as e:
        logger.error(f"停止服务失败: {e}")
        raise HTTPException(status_code=500, detail=f"停止服务失败: {str(e)}")
