"""
Windows 开机自启管理 - 使用任务计划程序
"""
import os
import sys
import subprocess
from pathlib import Path
from loguru import logger

try:
    import winreg
except ImportError:
    winreg = None

TASK_NAME = "BingWallpaperManager"


def get_startup_folder() -> Path:
    """获取 Windows 启动文件夹路径"""
    return Path(os.environ.get("APPDATA", "")) / "Microsoft" / "Windows" / "Start Menu" / "Programs" / "Startup"


def get_app_path() -> str:
    """获取应用程序路径（backend 目录）"""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def find_python_executable() -> str:
    """
    查找可用的 Python 可执行文件
    优先级：虚拟环境 > 系统 Python > py 启动器
    """
    backend_path = get_app_path()
    
    # 1. 尝试虚拟环境
    venv_python = Path(backend_path) / "venv" / "Scripts" / "python.exe"
    if venv_python.exists():
        logger.info(f"使用虚拟环境 Python: {venv_python}")
        return str(venv_python)
    
    # 2. 尝试系统 Python (python.exe)
    try:
        result = subprocess.run(
            ["where", "python"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            python_path = result.stdout.strip().split('\n')[0]
            logger.info(f"使用系统 Python: {python_path}")
            return python_path
    except Exception:
        pass
    
    # 3. 尝试 py 启动器
    try:
        result = subprocess.run(
            ["where", "py"],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            py_path = result.stdout.strip().split('\n')[0]
            logger.info(f"使用 py 启动器：{py_path}")
            return py_path
    except Exception:
        pass
    
    # 4. 回退到虚拟环境路径（即使不存在）
    logger.warning(f"未找到可用的 Python，使用默认路径：{venv_python}")
    return str(venv_python)


def create_startup_script() -> str:
    """
    创建隐藏启动脚本（无窗口静默启动前后端）
    返回脚本路径
    """
    backend_path = get_app_path()
    project_root = str(Path(backend_path).parent)
    frontend_path = str(Path(backend_path).parent / "frontend")

    script_path = Path(project_root) / "BingWallpaperManager.bat"

    if script_path.exists():
        try:
            script_path.unlink()
            logger.info(f"已删除旧启动脚本：{script_path}")
        except Exception as e:
            logger.warning(f"删除旧脚本失败：{e}")

    script_content = f'''@echo off
setlocal enabledelayedexpansion

REM Bing 壁纸管理系统 - 开机自启脚本
REM 兼容低版本 Windows，使用系统 Python，完全隐藏窗口

set "LOG_FILE=%~dp0BingWallpaperManager_startup.log"
set "ERROR_LOG=%~dp0BingWallpaperManager_error.log"

echo [%date% %time%] 开始启动服务 >> "%LOG_FILE%"

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 自动检测项目结构
if exist "%SCRIPT_DIR%backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
) else if exist "%SCRIPT_DIR%cstest\\backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%cstest\\backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%cstest\\frontend"
) else (
    echo [%date% %time%] ERROR: 无法找到项目目录 >> "%ERROR_LOG%"
    exit /b 1
)

echo [%date% %time%] 后端目录：%BACKEND_DIR% >> "%LOG_FILE%"
echo [%date% %time%] 前端目录：%FRONTEND_DIR% >> "%LOG_FILE%"

REM 检查 Python（系统环境）
set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=python"

if "!PYTHON_CMD!"=="" (
    py --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py"
)

if "!PYTHON_CMD!"=="" (
    echo [%date% %time%] ERROR: 未找到 Python >> "%ERROR_LOG%"
    exit /b 1
)

for /f "tokens=*" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set PYTHON_VER=%%i
echo [%date% %time%] Python 版本：%PYTHON_VER% >> "%LOG_FILE%"

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: 未找到 Node.js >> "%ERROR_LOG%"
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
echo [%date% %time%] Node.js 版本：%NODE_VER% >> "%LOG_FILE%"

REM 检查依赖是否已安装
!PYTHON_CMD! -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] 警告：FastAPI 未安装，尝试安装... >> "%LOG_FILE%"
    cd /d "%BACKEND_DIR%"
    if exist requirements.txt (
        !PYTHON_CMD! -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
    )
)

if not exist "%FRONTEND_DIR%\\node_modules" (
    echo [%date% %time%] 警告：node_modules 不存在，尝试安装... >> "%LOG_FILE%"
    cd /d "%FRONTEND_DIR%"
    call npm install >> "%LOG_FILE%" 2>&1
)

REM 启动后端服务（完全隐藏窗口）
echo [%date% %time%] 启动后端服务... >> "%LOG_FILE%"
cd /d "%BACKEND_DIR%"
powershell -WindowStyle Hidden -Command "Start-Process !PYTHON_CMD! -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -WindowStyle Hidden"
echo [%date% %time%] 后端服务已启动 >> "%LOG_FILE%"

REM 等待后端启动
timeout /t 5 /nobreak >nul

REM 启动前端服务（完全隐藏窗口）
echo [%date% %time%] 启动前端服务... >> "%LOG_FILE%"
cd /d "%FRONTEND_DIR%"
powershell -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c','npm run dev' -WorkingDirectory '%FRONTEND_DIR%' -WindowStyle Hidden"
echo [%date% %time%] 前端服务已启动 >> "%LOG_FILE%"

echo [%date% %time%] 服务启动完成 >> "%LOG_FILE%"
echo [%date% %time%] 前端：http://localhost:5173 >> "%LOG_FILE%"
echo [%date% %time%] 后端：http://localhost:8000 >> "%LOG_FILE%"

exit /b 0'''

    with open(script_path, "w", encoding="utf-8") as f:
        f.write(script_content)

    logger.info(f"启动脚本已创建：{script_path}")
    return str(script_path)


def check_admin_privileges() -> bool:
    """
    检查是否具有管理员权限
    任务计划程序需要管理员权限
    """
    try:
        import ctypes
        try:
            return ctypes.windll.shell32.IsUserAnAdmin() != 0
        except Exception:
            return False
    except Exception:
        return False


def create_scheduled_task(script_path: str) -> bool:
    """
    创建 Windows 任务计划程序任务
    使用 schtasks 命令
    """
    try:
        backend_path = get_app_path()
        
        # 构建 schtasks 命令
        # /CREATE: 创建任务
        # /TN: 任务名称
        # /TR: 任务运行程序
        # /SC: 计划类型 (ONSTART=开机启动)
        # /RL: 运行级别 (HIGHEST=最高权限)
        # /F: 强制创建（覆盖已存在的任务）
        cmd = [
            "schtasks",
            "/CREATE",
            "/TN", TASK_NAME,
            "/TR", f'"{script_path}"',
            "/SC", "ONSTART",
            "/RL", "HIGHEST",
            "/F"
        ]
        
        logger.info(f"创建任务计划：{' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            logger.info(f"任务计划创建成功：{TASK_NAME}")
            return True
        else:
            logger.error(f"任务计划创建失败：{result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"创建任务计划异常：{e}")
        return False


def delete_scheduled_task() -> bool:
    """
    删除 Windows 任务计划程序任务
    """
    try:
        cmd = [
            "schtasks",
            "/DELETE",
            "/TN", TASK_NAME,
            "/F"
        ]
        
        logger.info(f"删除任务计划：{' '.join(cmd)}")
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        if result.returncode == 0:
            logger.info(f"任务计划已删除：{TASK_NAME}")
            return True
        else:
            # 任务不存在也算成功
            if "ERROR: The specified task name does not exist" in result.stderr:
                logger.info(f"任务计划不存在，无需删除：{TASK_NAME}")
                return True
            logger.error(f"删除任务计划失败：{result.stderr}")
            return False
            
    except Exception as e:
        logger.error(f"删除任务计划异常：{e}")
        return False


def is_scheduled_task_exists() -> bool:
    """
    检查任务计划是否存在
    """
    try:
        cmd = [
            "schtasks",
            "/QUERY",
            "/TN", TASK_NAME
        ]
        
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )
        
        return result.returncode == 0
            
    except Exception:
        return False


def enable_autostart() -> bool:
    """
    启用开机自启
    将 BAT 脚本放在项目根目录，创建快捷方式到 Startup 文件夹
    """
    try:
        if winreg is None:
            logger.error("winreg 模块不可用")
            return False

        backend_path = get_app_path()
        project_root = str(Path(backend_path).parent)
        frontend_path = str(Path(backend_path).parent / "frontend")

        startup_folder = get_startup_folder()
        
        bat_path = Path(project_root) / "BingWallpaperManager.bat"
        shortcut_path = startup_folder / "BingWallpaperManager.lnk"

        if not bat_path.exists():
            bat_content = f'''@echo off
setlocal enabledelayedexpansion

REM Bing 壁纸管理系统 - 开机自启脚本
REM 兼容低版本 Windows，使用系统 Python，完全隐藏窗口

set "LOG_FILE=%~dp0BingWallpaperManager_startup.log"
set "ERROR_LOG=%~dp0BingWallpaperManager_error.log"

echo [%date% %time%] 开始启动服务 >> "%LOG_FILE%"

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 自动检测项目结构
if exist "%SCRIPT_DIR%backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
) else if exist "%SCRIPT_DIR%cstest\\backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%cstest\\backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%cstest\\frontend"
) else (
    echo [%date% %time%] ERROR: 无法找到项目目录 >> "%ERROR_LOG%"
    exit /b 1
)

echo [%date% %time%] 后端目录：%BACKEND_DIR% >> "%LOG_FILE%"
echo [%date% %time%] 前端目录：%FRONTEND_DIR% >> "%LOG_FILE%"

REM 检查 Python（系统环境）
set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=python"

if "!PYTHON_CMD!"=="" (
    py --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py"
)

if "!PYTHON_CMD!"=="" (
    echo [%date% %time%] ERROR: 未找到 Python >> "%ERROR_LOG%"
    exit /b 1
)

for /f "tokens=*" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set PYTHON_VER=%%i
echo [%date% %time%] Python 版本：%PYTHON_VER% >> "%LOG_FILE%"

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: 未找到 Node.js >> "%ERROR_LOG%"
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
echo [%date% %time%] Node.js 版本：%NODE_VER% >> "%LOG_FILE%"

REM 检查依赖是否已安装
!PYTHON_CMD! -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] 警告：FastAPI 未安装，尝试安装... >> "%LOG_FILE%"
    cd /d "%BACKEND_DIR%"
    if exist requirements.txt (
        !PYTHON_CMD! -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
    )
)

if not exist "%FRONTEND_DIR%\\node_modules" (
    echo [%date% %time%] 警告：node_modules 不存在，尝试安装... >> "%LOG_FILE%"
    cd /d "%FRONTEND_DIR%"
    call npm install >> "%LOG_FILE%" 2>&1
)

REM 启动后端服务（完全隐藏窗口）
echo [%date% %time%] 启动后端服务... >> "%LOG_FILE%"
cd /d "%BACKEND_DIR%"
powershell -WindowStyle Hidden -Command "Start-Process !PYTHON_CMD! -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -WindowStyle Hidden"
echo [%date% %time%] 后端服务已启动 >> "%LOG_FILE%"

REM 等待后端启动
timeout /t 5 /nobreak >nul

REM 启动前端服务（完全隐藏窗口）
echo [%date% %time%] 启动前端服务... >> "%LOG_FILE%"
cd /d "%FRONTEND_DIR%"
powershell -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c','npm run dev' -WorkingDirectory '%FRONTEND_DIR%' -WindowStyle Hidden"
echo [%date% %time%] 前端服务已启动 >> "%LOG_FILE%"

echo [%date% %time%] 服务启动完成 >> "%LOG_FILE%"
echo [%date% %time%] 前端：http://localhost:5173 >> "%LOG_FILE%"
echo [%date% %time%] 后端：http://localhost:8000 >> "%LOG_FILE%"

exit /b 0'''

            with open(bat_path, "w", encoding="utf-8") as f:
                f.write(bat_content)
            logger.info(f"启动脚本已创建：{bat_path}")
        else:
            logger.info(f"启动脚本已存在：{bat_path}")

        vbs_path = Path(project_root) / "BingWallpaperManager.vbs"
        if vbs_path.exists():
            vbs_path.unlink()
            logger.info(f"已删除旧的 VBS 包装器：{vbs_path}")

        shortcut_ps = f'''
$WshShell = New-Object -ComObject WScript.Shell
$Shortcut = $WshShell.CreateShortcut("{shortcut_path}")
$Shortcut.TargetPath = "{bat_path}"
$Shortcut.WorkingDirectory = "{project_root}"
$Shortcut.WindowStyle = 7
$Shortcut.Description = "Bing Wallpaper Manager Autostart"
$Shortcut.Save()
'''
        result = subprocess.run(
            ["powershell", "-Command", shortcut_ps],
            capture_output=True,
            text=True,
            check=False,
            creationflags=subprocess.CREATE_NO_WINDOW
        )

        if result.returncode == 0:
            logger.info(f"快捷方式已创建：{shortcut_path}")
        else:
            logger.error(f"创建快捷方式失败：{result.stderr}")
            return False

        delete_scheduled_task()

        old_bat = startup_folder / "BingWallpaperManager.bat"
        if old_bat.exists():
            old_bat.unlink()
            logger.info(f"已删除旧的 BAT 文件：{old_bat}")

        logger.info("开机自启已启用（快捷方式模式）")
        return True

    except Exception as e:
        logger.error(f"启用开机自启失败：{e}")
        return False


def disable_autostart() -> bool:
    """
    禁用开机自启
    
    Returns:
        bool: 是否成功
    """
    try:
        if winreg is None:
            logger.error("winreg 模块不可用")
            return False
        
        delete_scheduled_task()
        
        startup_folder = get_startup_folder()
        backend_path = get_app_path()
        project_root = str(Path(backend_path).parent)
        
        shortcut_path = startup_folder / "BingWallpaperManager.lnk"
        if shortcut_path.exists():
            shortcut_path.unlink()
            logger.info(f"已删除快捷方式：{shortcut_path}")
        
        bat_path = Path(project_root) / "BingWallpaperManager.bat"
        if bat_path.exists():
            bat_path.unlink()
            logger.info(f"已删除 BAT 启动脚本：{bat_path}")
        
        vbs_path = Path(project_root) / "BingWallpaperManager.vbs"
        if vbs_path.exists():
            vbs_path.unlink()
            logger.info(f"已删除 VBS 包装器：{vbs_path}")
        
        old_bat = startup_folder / "BingWallpaperManager.bat"
        if old_bat.exists():
            old_bat.unlink()
            logger.info(f"已删除旧的 BAT 文件：{old_bat}")
        
        for name in ["start.bat", "start_hidden.bat"]:
            old_path = Path(backend_path) / "scripts" / name
            if old_path.exists():
                try:
                    old_path.unlink()
                    logger.info(f"已删除旧脚本：{old_path}")
                except Exception:
                    pass
        
        vbs_path = startup_folder / "BingWallpaperManager.vbs"
        if vbs_path.exists():
            vbs_path.unlink()
            logger.info(f"已删除旧 VBS 启动脚本：{vbs_path}")
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_SET_VALUE,
            )
            try:
                winreg.DeleteValue(key, "BingWallpaperManager")
                logger.info("已删除旧注册表项")
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
        except Exception:
            pass
        
        logger.info("开机自启已完全禁用")
        return True
        
    except Exception as e:
        logger.error(f"禁用开机自启失败: {e}")
        return False


def get_autostart_scripts() -> dict:
    """
    生成开机自启脚本内容（BAT 和 PowerShell），不写入文件，仅返回文本

    Returns:
        dict: {"bat": str, "powershell": str}
    """
    backend_path = get_app_path()
    frontend_path = str(Path(backend_path).parent / "frontend")

    bat_content = f'''@echo off
setlocal enabledelayedexpansion

REM Bing 壁纸管理系统 - 开机自启脚本
REM 兼容低版本 Windows，使用系统 Python，完全隐藏窗口

set "LOG_FILE=%~dp0BingWallpaperManager_startup.log"
set "ERROR_LOG=%~dp0BingWallpaperManager_error.log"

echo [%date% %time%] 开始启动服务 >> "%LOG_FILE%"

REM 获取脚本所在目录
set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

REM 自动检测项目结构
if exist "%SCRIPT_DIR%backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%frontend"
) else if exist "%SCRIPT_DIR%cstest\\backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%cstest\\backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%cstest\\frontend"
) else (
    echo [%date% %time%] ERROR: 无法找到项目目录 >> "%ERROR_LOG%"
    exit /b 1
)

echo [%date% %time%] 后端目录：%BACKEND_DIR% >> "%LOG_FILE%"
echo [%date% %time%] 前端目录：%FRONTEND_DIR% >> "%LOG_FILE%"

REM 检查 Python（系统环境）
set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 set "PYTHON_CMD=python"

if "!PYTHON_CMD!"=="" (
    py --version >nul 2>&1
    if not errorlevel 1 set "PYTHON_CMD=py"
)

if "!PYTHON_CMD!"=="" (
    echo [%date% %time%] ERROR: 未找到 Python >> "%ERROR_LOG%"
    exit /b 1
)

for /f "tokens=*" %%i in ('!PYTHON_CMD! --version 2^>^&1') do set PYTHON_VER=%%i
echo [%date% %time%] Python 版本：%PYTHON_VER% >> "%LOG_FILE%"

REM 检查 Node.js
node --version >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] ERROR: 未找到 Node.js >> "%ERROR_LOG%"
    exit /b 1
)

for /f "tokens=*" %%i in ('node --version 2^>^&1') do set NODE_VER=%%i
echo [%date% %time%] Node.js 版本：%NODE_VER% >> "%LOG_FILE%"

REM 检查依赖是否已安装
!PYTHON_CMD! -c "import fastapi" >nul 2>&1
if errorlevel 1 (
    echo [%date% %time%] 警告：FastAPI 未安装，尝试安装... >> "%LOG_FILE%"
    cd /d "%BACKEND_DIR%"
    if exist requirements.txt (
        !PYTHON_CMD! -m pip install -r requirements.txt >> "%LOG_FILE%" 2>&1
    )
)

if not exist "%FRONTEND_DIR%\\node_modules" (
    echo [%date% %time%] 警告：node_modules 不存在，尝试安装... >> "%LOG_FILE%"
    cd /d "%FRONTEND_DIR%"
    call npm install >> "%LOG_FILE%" 2>&1
)

REM 启动后端服务（完全隐藏窗口）
echo [%date% %time%] 启动后端服务... >> "%LOG_FILE%"
cd /d "%BACKEND_DIR%"
powershell -WindowStyle Hidden -Command "Start-Process !PYTHON_CMD! -ArgumentList '-m','uvicorn','app.main:app','--host','0.0.0.0','--port','8000' -WorkingDirectory '%BACKEND_DIR%' -WindowStyle Hidden"
echo [%date% %time%] 后端服务已启动 >> "%LOG_FILE%"

REM 等待后端启动
timeout /t 5 /nobreak >nul

REM 启动前端服务（完全隐藏窗口）
echo [%date% %time%] 启动前端服务... >> "%LOG_FILE%"
cd /d "%FRONTEND_DIR%"
powershell -WindowStyle Hidden -Command "Start-Process cmd -ArgumentList '/c','npm run dev' -WorkingDirectory '%FRONTEND_DIR%' -WindowStyle Hidden"
echo [%date% %time%] 前端服务已启动 >> "%LOG_FILE%"

echo [%date% %time%] 服务启动完成 >> "%LOG_FILE%"
echo [%date% %time%] 前端：http://localhost:5173 >> "%LOG_FILE%"
echo [%date% %time%] 后端：http://localhost:8000 >> "%LOG_FILE%"

exit /b 0'''

    ps_content = f'''$BackendDir = "{backend_path}"
$FrontendDir = "{frontend_path}"

$PythonCmd = Get-Command python -ErrorAction SilentlyContinue
if (-not $PythonCmd) {{
    $PythonCmd = Get-Command py -ErrorAction SilentlyContinue
}}

if (-not $PythonCmd) {{
    exit 1
}}

$NodeCmd = Get-Command node -ErrorAction SilentlyContinue
if (-not $NodeCmd) {{
    exit 1
}}

Start-Process -FilePath $PythonCmd.Name -ArgumentList "-m","uvicorn","app.main:app","--host","0.0.0.0","--port","8000" -WorkingDirectory $BackendDir -WindowStyle Hidden

Start-Sleep -Seconds 5

Start-Process -FilePath "cmd" -ArgumentList "/c","npm run dev" -WorkingDirectory $FrontendDir -WindowStyle Hidden'''

    return {
        "bat": bat_content.strip(),
        "powershell": ps_content.strip(),
    }


def is_autostart_enabled() -> bool:
    """
    检查是否已启用开机自启
    
    Returns:
        bool: 是否已启用
    """
    try:
        if winreg is None:
            return False
        
        if is_scheduled_task_exists():
            logger.info("检测到任务计划程序已启用")
            return True
        
        startup_folder = get_startup_folder()
        backend_path = get_app_path()
        project_root = str(Path(backend_path).parent)
        
        bat_path = Path(project_root) / "BingWallpaperManager.bat"
        shortcut_path = startup_folder / "BingWallpaperManager.lnk"
        
        if shortcut_path.exists() and bat_path.exists():
            logger.info("检测到快捷方式和 BAT 脚本已启用")
            return True
        
        bat_path_in_startup = startup_folder / "BingWallpaperManager.bat"
        if bat_path_in_startup.exists():
            logger.info("检测到 BAT 启动文件夹方式已启用")
            return True
        
        vbs_path = startup_folder / "BingWallpaperManager.vbs"
        if vbs_path.exists():
            logger.info("检测到旧 VBS 启动文件夹方式已启用")
            return True
        
        try:
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                r"Software\Microsoft\Windows\CurrentVersion\Run",
                0,
                winreg.KEY_READ,
            )
            
            try:
                value, _ = winreg.QueryValueEx(key, "BingWallpaperManager")
                winreg.CloseKey(key)
                logger.info("检测到注册表方式已启用")
                return bool(value)
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
        except Exception:
            return False
            
    except Exception as e:
        logger.error(f"检查开机自启状态失败: {e}")
        return False
