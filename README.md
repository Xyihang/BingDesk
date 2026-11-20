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
  A Bing daily wallpaper manager for Windows with a local web dashboard and an AI tarot reading module.
  <br>
  <a href="README.zh-CN.md">简体中文</a>
</p>

> **Note:** Page-level access verification (grid captcha and USB key check) has been removed from the frontend. The API itself has no authentication, so run BingDesk only on a trusted local machine.

## Features

### Wallpaper management
- Downloads Bing's daily wallpapers in UHD / FHD / HD
- Applies any wallpaper to the Windows desktop with one click
- Rotates wallpapers automatically on an interval you configure
- Lists history with preview, resolution, date, set and delete actions
- Bulk cleanup that keeps the wallpaper currently in use

### Dashboard
- Wallpaper count and scheduler status at a glance
- One-click "download and set" action
- System information: app version, database size, current wallpaper, next switch time

### AI tarot reading
- Monthly spread (1-12 months), daily card and Celtic Cross
- Optional question input
- AI interpretation through Zhipu GLM, with a local fallback when no API key is configured
- Reading history with restore and delete

### Settings
- Download quality and auto-change interval
- Scheduler start / stop / restart
- Windows autostart toggle
- Generated BAT / PowerShell startup scripts
- Optional password management endpoints (kept on the backend for future use)

## Tech stack

| Layer | Technology |
|---|---|
| Frontend | React 18, TypeScript, Vite 5, Ant Design 5, Zustand, React Router 6 |
| Backend | FastAPI, SQLAlchemy 2, SQLite (aiosqlite), APScheduler, httpx, loguru |
| Desktop integration | pywin32, Pillow (Windows only) |

## Requirements

- Windows 10 / 11
- Python 3.10+
- Node.js 18+

## Getting started

```powershell
# 1. Install dependencies
.\scripts\install.ps1

# 2. Start backend and frontend
.\scripts\start.ps1

# Backend only / frontend only
.\scripts\start.ps1 -Backend
.\scripts\start.ps1 -Frontend
```

Manual setup:

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

| Service | URL |
|---|---|
| Web UI | http://localhost:5173 |
| API | http://localhost:8000 |
| Swagger docs | http://localhost:8000/docs |

## Configuration

Create `backend/.env` (ignored by Git) to configure the AI module:

```dotenv
ZHIPU_API_KEY=your_api_key_here
```

Without a key, tarot readings still work but use the built-in fallback interpretation.

Wallpaper preferences are stored in the `settings` table and edited from the Settings page:

| Key | Description |
|---|---|
| `download_quality` | `uhd` / `fhd` / `hd` |
| `change_interval` | Auto-change interval in minutes |
| `auto_start` | Run at Windows startup |

Autostart and service shutdown require administrator privileges.

## Project structure

```
bingdesk/
├── backend/
│   ├── app/
│   │   ├── api/          # wallpapers, settings, system, tarot, auth
│   │   ├── models/       # SQLAlchemy models
│   │   ├── schemas/      # Pydantic schemas
│   │   ├── services/     # Bing, wallpaper, scheduler, tarot, AI
│   │   ├── utils/        # autostart, wallpaper setter
│   │   ├── config.py
│   │   ├── database.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── components/Layout/
│   │   ├── pages/        # Dashboard, Wallpapers, Tarot, Settings
│   │   ├── services/     # Axios API clients
│   │   ├── stores/       # Zustand store
│   │   ├── styles/       # Design tokens and layout styles
│   │   └── types/
│   └── package.json
├── scripts/              # install.ps1, start.ps1, setup-autostart.ps1
└── README.md
```

## API overview

| Method | Path | Description |
|---|---|---|
| `GET` | `/api/wallpapers` | List wallpapers |
| `GET` | `/api/wallpapers/current` | Current wallpaper |
| `POST` | `/api/wallpapers/download` | Download a new wallpaper |
| `POST` | `/api/wallpapers/{id}/set` | Set as desktop wallpaper |
| `GET` | `/api/wallpapers/{id}/image` | Wallpaper preview |
| `DELETE` | `/api/wallpapers/{id}` | Delete a wallpaper |
| `DELETE` | `/api/wallpapers/batch/all-except-current` | Bulk delete |
| `GET` | `/api/system/status` | System status |
| `POST` | `/api/system/scheduler/start` | Start auto-change |
| `POST` | `/api/system/scheduler/stop` | Stop auto-change |
| `POST` | `/api/system/autostart` | Toggle Windows autostart |
| `POST` | `/api/tarot/reading` | Monthly reading |
| `GET` | `/api/tarot/daily` | Daily card |
| `GET` | `/api/tarot/celtic-cross` | Celtic Cross |
| `GET` | `/api/tarot/history` | Reading history |
| `GET` | `/api/settings` | List settings |
| `PUT` | `/api/settings/{key}` | Update a setting |

## Development

```powershell
# Type-check and build the frontend
cd frontend
npm run build

# Backend with hot reload
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

## License

[MIT](LICENSE)

## Acknowledgements

- Bing wallpaper API: [bing.img.run](https://bing.img.run/)
- Zhipu AI: [bigmodel.cn](https://bigmodel.cn/)
- [Ant Design](https://ant.design/), [FastAPI](https://fastapi.tiangolo.com/), [React](https://react.dev/)
