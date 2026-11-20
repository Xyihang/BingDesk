@echo off
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
) else if exist "%SCRIPT_DIR%cstest\backend" (
    set "BACKEND_DIR=%SCRIPT_DIR%cstest\backend"
    set "FRONTEND_DIR=%SCRIPT_DIR%cstest\frontend"
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

if not exist "%FRONTEND_DIR%\node_modules" (
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

exit /b 0