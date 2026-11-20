# BingDesk

<p align="center">
  <img src="https://img.shields.io/badge/React-18-61DAFB?logo=react&logoColor=white" alt="React">
  <img src="https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/TypeScript-5.6-3178C6?logo=typescript&logoColor=white" alt="TypeScript">
  <img src="https://img.shields.io/badge/Ant%20Design-5-1677FF?logo=antdesign&logoColor=white" alt="Ant Design">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

<p align="center">
  必应桌面壁纸管理系统，附带本地 Web 仪表盘与 AI 塔罗牌占卜模块。
  <br>
  <a href="README.md">English</a>
</p>

> **说明**：本版本已移除前端页面访问验证（网格验证码与 U 盘检测），后端 API 本身也没有鉴权，请仅在可信的本地环境中运行。

## 功能特性

### 壁纸管理
- 下载必应每日壁纸，支持 UHD / FHD / HD 三种质量
- 一键将任意壁纸设为 Windows 桌面背景
- 按自定义间隔自动轮换壁纸
- 壁纸历史列表：预览、分辨率、日期、设为壁纸、删除
- 一键清理，自动保留当前正在使用的壁纸

### 仪表盘
- 壁纸数量与自动切换状态一目了然
- 一键「下载并设置新壁纸」
- 系统信息：版本、数据库大小、当前壁纸、下次切换时间

### AI 塔罗占卜
- 月度运势（1-12 个月）、每日塔罗、凯尔特十字三种牌阵
- 支持输入具体问题进行占卜
- 基于智谱 GLM 的 AI 解读，未配置密钥时使用本地备用解读
- 占卜历史记录，可恢复查看与删除

### 系统设置
- 下载质量与自动切换间隔
- 定时任务启动 / 停止 / 重启
- Windows 开机自启开关
- 生成 BAT / PowerShell 一键启动脚本
- 密码管理接口（后端保留，供后续扩展）

## 技术栈

| 层级 | 技术 |
|---|---|
| 前端 | React 18、TypeScript、Vite 5、Ant Design 5、Zustand、React Router 6 |
| 后端 | FastAPI、SQLAlchemy 2、SQLite（aiosqlite）、APScheduler、httpx、loguru |
| 桌面集成 | pywin32、Pillow（仅 Windows） |

## 系统要求

- Windows 10 / 11
- Python 3.10+
- Node.js 18+

## 快速开始

```powershell
# 1. 安装依赖
.\scripts\install.ps1

# 2. 启动前后端
.\scripts\start.ps1

# 仅启动后端 / 仅启动前端
.\scripts\start.ps1 -Backend
.\scripts\start.ps1 -Frontend
```

手动安装：

```powershell
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --port 8000

cd frontend
npm install
npm run dev
```

| 服务 | 地址 |
|---|---|
| 前端界面 | http://localhost:5173 |
| 后端 API | http://localhost:8000 |
| Swagger 文档 | http://localhost:8000/docs |

## 配置说明

在 `backend/.env`（已被 Git 忽略）中配置 AI 模块：

```dotenv
ZHIPU_API_KEY=your_api_key_here
```

未配置密钥时，塔罗占卜仍可正常使用，只是采用内置的备用解读。

壁纸相关配置保存在 `settings` 表中，可在设置页面修改：

| 配置项 | 说明 |
|---|---|
| `download_quality` | `uhd` / `fhd` / `hd` |
| `change_interval` | 自动切换间隔（分钟） |
| `auto_start` | 开机自启 |

开机自启与服务停止操作需要管理员权限。

## 项目结构

```
bingdesk/
├── backend/
│   ├── app/
│   │   ├── api/          # 壁纸、设置、系统、塔罗、auth 接口
│   │   ├── models/       # SQLAlchemy 模型
│   │   ├── schemas/      # Pydantic 模式
│   │   ├── services/     # Bing、壁纸、定时任务、塔罗、AI
│   │   ├── utils/        # 开机自启、壁纸设置
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/Layout/
│   │   ├── pages/        # 仪表盘、壁纸、塔罗、设置
│   │   ├── services/     # Axios API 封装
│   │   ├── stores/       # Zustand 状态
│   │   ├── styles/       # 设计令牌与布局样式
│   │   └── types/
│   └── package.json
├── scripts/              # install.ps1、start.ps1、setup-autostart.ps1
└── README.md
```

## API 一览

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/wallpapers` | 壁纸列表 |
| `GET` | `/api/wallpapers/current` | 当前壁纸 |
| `POST` | `/api/wallpapers/download` | 下载新壁纸 |
| `POST` | `/api/wallpapers/{id}/set` | 设为桌面壁纸 |
| `GET` | `/api/wallpapers/{id}/image` | 壁纸预览图 |
| `DELETE` | `/api/wallpapers/{id}` | 删除壁纸 |
| `DELETE` | `/api/wallpapers/batch/all-except-current` | 批量清理 |
| `GET` | `/api/system/status` | 系统状态 |
| `POST` | `/api/system/scheduler/start` | 启动自动切换 |
| `POST` | `/api/system/scheduler/stop` | 停止自动切换 |
| `POST` | `/api/system/autostart` | 切换开机自启 |
| `POST` | `/api/tarot/reading` | 月度运势占卜 |
| `GET` | `/api/tarot/daily` | 每日塔罗 |
| `GET` | `/api/tarot/celtic-cross` | 凯尔特十字 |
| `GET` | `/api/tarot/history` | 占卜历史 |
| `GET` | `/api/settings` | 设置列表 |
| `PUT` | `/api/settings/{key}` | 更新设置 |

## 开发说明

```powershell
# 前端类型检查与构建
cd frontend
npm run build

# 后端热重载
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## 许可证

[MIT](LICENSE)

## 致谢

- 必应壁纸 API：[bing.img.run](https://bing.img.run/)
- 智谱 AI：[bigmodel.cn](https://bigmodel.cn/)
- [Ant Design](https://ant.design/)、[FastAPI](https://fastapi.tiangolo.com/)、[React](https://react.dev/)
