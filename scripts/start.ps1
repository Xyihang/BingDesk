# Bing 壁纸管理系统 - 启动脚本

param(
    [switch]$Frontend,
    [switch]$Backend,
    [switch]$All
)

$ProjectRoot = $PSScriptRoot | Split-Path -Parent

if ($All -or (-not $Frontend -and -not $Backend)) {
    $Frontend = $true
    $Backend = $true
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bing 壁纸管理系统 - 启动服务" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

if ($Backend) {
    Write-Host "启动后端服务..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\backend"
    
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "python -c `"import uvicorn; uvicorn.run('app.main:app', host='0.0.0.0', port=8000)`""
    )
    
    Write-Host "  ✓ 后端服务已启动 (http://localhost:8000)" -ForegroundColor Green
}

if ($Frontend) {
    Write-Host "启动前端服务..." -ForegroundColor Yellow
    Set-Location "$ProjectRoot\frontend"
    
    Start-Process powershell -ArgumentList @(
        "-NoExit",
        "-Command",
        "npm run dev"
    )
    
    Write-Host "  ✓ 前端服务已启动 (http://localhost:5173)" -ForegroundColor Green
}

Write-Host ""
Write-Host "服务已启动，请访问 http://localhost:5173" -ForegroundColor Cyan
Write-Host ""
