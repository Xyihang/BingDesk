# Bing 壁纸管理系统 - 安装脚本
# 需要以管理员权限运行

param(
    [switch]$SkipFrontend,
    [switch]$SkipBackend
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bing 壁纸管理系统 - 安装向导" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# 检查 Python
Write-Host "[1/5] 检查 Python 环境..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ 找到 Python: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 未找到 Python，请先安装 Python 3.10+" -ForegroundColor Red
    exit 1
}

# 检查 Node.js
Write-Host "[2/5] 检查 Node.js 环境..." -ForegroundColor Yellow
try {
    $nodeVersion = node --version 2>&1
    Write-Host "  ✓ 找到 Node.js: $nodeVersion" -ForegroundColor Green
} catch {
    Write-Host "  ✗ 未找到 Node.js，请先安装 Node.js 18+" -ForegroundColor Red
    exit 1
}

# 安装后端依赖
if (-not $SkipBackend) {
    Write-Host "[3/5] 安装后端依赖..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\backend"
    
    if (-not (Test-Path "venv")) {
        Write-Host "  创建 Python 虚拟环境..." -ForegroundColor Gray
        python -m venv venv
    }
    
    Write-Host "  激活虚拟环境并安装依赖..." -ForegroundColor Gray
    & ".\venv\Scripts\Activate.ps1"
    pip install -r requirements.txt -q
    Write-Host "  ✓ 后端依赖安装完成" -ForegroundColor Green
}

# 安装前端依赖
if (-not $SkipFrontend) {
    Write-Host "[4/5] 安装前端依赖..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\frontend"
    
    Write-Host "  安装 npm 依赖..." -ForegroundColor Gray
    npm install --silent
    Write-Host "  ✓ 前端依赖安装完成" -ForegroundColor Green
}

# 创建数据目录
Write-Host "[5/5] 初始化数据目录..." -ForegroundColor Yellow
$DataDir = "$ProjectRoot\backend\data"
$WallpaperDir = "$DataDir\wallpapers"
$LogDir = "$ProjectRoot\backend\logs"

if (-not (Test-Path $DataDir)) {
    New-Item -ItemType Directory -Path $DataDir -Force | Out-Null
}
if (-not (Test-Path $WallpaperDir)) {
    New-Item -ItemType Directory -Path $WallpaperDir -Force | Out-Null
}
if (-not (Test-Path $LogDir)) {
    New-Item -ItemType Directory -Path $LogDir -Force | Out-Null
}
Write-Host "  ✓ 数据目录创建完成" -ForegroundColor Green

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  安装完成！" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "启动方式：" -ForegroundColor Yellow
Write-Host "  后端: cd backend && python -c `"import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000)`"" -ForegroundColor White
Write-Host "  前端: cd frontend && npm run dev" -ForegroundColor White
Write-Host ""
Write-Host "访问地址：" -ForegroundColor Yellow
Write-Host "  前端: http://localhost:5173" -ForegroundColor White
Write-Host "  后端: http://localhost:8000" -ForegroundColor White
Write-Host "  API文档: http://localhost:8000/docs" -ForegroundColor White
Write-Host ""
