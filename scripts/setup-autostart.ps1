# Bing 壁纸管理系统 - 开机自启配置脚本
# 需要以管理员权限运行

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("enable", "disable")]
    [string]$Action
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot | Split-Path -Parent
$AppName = "BingWallpaperManager"

function Enable-Autostart {
    Write-Host "正在配置开机自启..." -ForegroundColor Yellow
    
    $PythonExe = "$ProjectRoot\backend\venv\Scripts\python.exe"
    $MainScript = "$ProjectRoot\backend\app\main.py"
    
    if (-not (Test-Path $PythonExe)) {
        Write-Host "  ✗ 未找到 Python 虚拟环境，请先运行 install.ps1" -ForegroundColor Red
        exit 1
    }
    
    $Command = "`"$PythonExe`" `"$MainScript`""
    
    try {
        $Key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey(
            "Software\Microsoft\Windows\CurrentVersion\Run",
            $true
        )
        $Key.SetValue($AppName, $Command)
        $Key.Close()
        
        Write-Host "  ✓ 开机自启已启用" -ForegroundColor Green
        Write-Host "  命令: $Command" -ForegroundColor Gray
    } catch {
        Write-Host "  ✗ 配置失败: $_" -ForegroundColor Red
        exit 1
    }
}

function Disable-Autostart {
    Write-Host "正在取消开机自启..." -ForegroundColor Yellow
    
    try {
        $Key = [Microsoft.Win32.Registry]::CurrentUser.OpenSubKey(
            "Software\Microsoft\Windows\CurrentVersion\Run",
            $true
        )
        $Key.DeleteValue($AppName, $false)
        $Key.Close()
        
        Write-Host "  ✓ 开机自启已禁用" -ForegroundColor Green
    } catch [System.Management.Automation.ItemNotFoundException] {
        Write-Host "  ℹ 开机自启未配置" -ForegroundColor Yellow
    } catch {
        Write-Host "  ✗ 取消失败: $_" -ForegroundColor Red
        exit 1
    }
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Bing 壁纸管理系统 - 开机自启配置" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

switch ($Action) {
    "enable" { Enable-Autostart }
    "disable" { Disable-Autostart }
}

Write-Host ""
