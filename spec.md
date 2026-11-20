# Bing 壁纸与课程表管理系统 - 架构设计文档

## 一、技术栈选型

### 1.1 前端技术栈
- **框架**: React 18 + TypeScript
- **构建工具**: Vite 5.x
- **UI 组件库**: Ant Design 5.x（支持自定义主题）
- **状态管理**: Zustand（轻量级状态管理）
- **HTTP 客户端**: Axios
- **样式方案**: Tailwind CSS + CSS Modules
- **图表库**: Recharts（用于课程表可视化）
- **主题色**: 浅蓝色系 (#1890ff, #e6f7ff, #bae7ff)

### 1.2 后端技术栈
- **语言**: Python 3.10+
- **Web 框架**: FastAPI（轻量、高性能、自动 API 文档）
- **数据库**: SQLite（嵌入式、零配置）
- **ORM**: SQLAlchemy 2.x（异步支持）
- **HTTP 客户端**: httpx（异步请求）
- **壁纸设置**: `wallpaper` Python 库或 ctypes 调用 Windows API
- **任务调度**: APScheduler（定时任务）
- **日志**: loguru（结构化日志）

### 1.3 系统架构
```
┌─────────────────────────────────────────────────────────┐
│                     用户层                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  Web 管理页  │  │  命令行工具  │  │  系统托盘   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                            ↓ HTTP/REST API
┌─────────────────────────────────────────────────────────┐
│                   应用服务层 (Python FastAPI)            │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │ 壁纸服务    │  │ 课程表服务  │  │ 配置服务    │     │
│  │ - 下载      │  │ - CRUD      │  │ - 读写      │     │
│  │ - 切换      │  │ - 查询      │  │ - 校验      │     │
│  │ - 定时      │  │ - 导出      │  │ - 备份      │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   数据持久层                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐     │
│  │  SQLite     │  │  文件系统   │  │  注册表     │     │
│  │  数据库     │  │  图片存储   │  │  自启配置   │     │
│  └─────────────┘  └─────────────┘  └─────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## 二、目录结构

```
cstest/
├── backend/                      # Python 后端
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI 入口
│   │   ├── config.py            # 配置管理
│   │   ├── database.py          # 数据库连接
│   │   ├── models/              # 数据模型
│   │   │   ├── __init__.py
│   │   │   ├── course.py        # 课程表模型
│   │   │   ├── wallpaper.py     # 壁纸模型
│   │   │   └── settings.py      # 配置模型
│   │   ├── schemas/             # Pydantic 模式
│   │   │   ├── __init__.py
│   │   │   ├── course.py
│   │   │   ├── wallpaper.py
│   │   │   └── settings.py
│   │   ├── api/                 # API 路由
│   │   │   ├── __init__.py
│   │   │   ├── courses.py
│   │   │   ├── wallpapers.py
│   │   │   ├── settings.py
│   │   │   └── system.py        # 系统接口（自启等）
│   │   ├── services/            # 业务逻辑
│   │   │   ├── __init__.py
│   │   │   ├── bing_service.py  # Bing API 服务
│   │   │   ├── wallpaper_service.py
│   │   │   ├── course_service.py
│   │   │   └── scheduler.py     # 定时任务
│   │   └── utils/               # 工具函数
│   │       ├── __init__.py
│   │       ├── wallpaper_setter.py
│   │       └── auto_start.py
│   ├── tests/                   # 测试
│   ├── logs/                    # 日志目录
│   ├── data/                    # 数据目录
│   │   ├── wallpapers/          # 下载的壁纸
│   │   └── app.db              # SQLite 数据库
│   ├── requirements.txt
│   └── run.ps1                  # 启动脚本
├── frontend/                     # React 前端
│   ├── src/
│   │   ├── main.tsx
│   │   ├── App.tsx
│   │   ├── components/          # 组件
│   │   │   ├── Layout/
│   │   │   ├── CourseTable/
│   │   │   ├── WallpaperGallery/
│   │   │   ├── Settings/
│   │   │   └── common/
│   │   ├── pages/               # 页面
│   │   ├── stores/              # Zustand stores
│   │   ├── services/            # API 服务
│   │   ├── types/               # TypeScript 类型
│   │   ├── utils/               # 工具函数
│   │   └── styles/              # 样式文件
│   ├── public/
│   ├── index.html
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── postcss.config.js
├── scripts/                      # 部署脚本
│   ├── install.ps1              # 安装脚本
│   ├── setup-autostart.ps1      # 自启配置
│   └── uninstall.ps1            # 卸载脚本
├── docs/                         # 文档
│   ├── API.md                   # API 文档
│   └── DEPLOYMENT.md            # 部署文档
├── part.md                       # Bing API 说明
└── README.md                     # 项目说明
```

## 三、数据库设计

### 3.1 课程表 (courses)
```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name VARCHAR(100) NOT NULL,
    teacher VARCHAR(50),
    classroom VARCHAR(50),
    day_of_week INTEGER NOT NULL,  -- 1-7 (周一到周日)
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    week_start INTEGER,            -- 起始周
    week_end INTEGER,              -- 结束周
    color VARCHAR(20),             -- 显示颜色
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.2 壁纸记录 (wallpapers)
```sql
CREATE TABLE wallpapers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    file_path VARCHAR(500) NOT NULL,
    source_url VARCHAR(500),
    resolution VARCHAR(20),        -- e.g., '3840x2160'
    download_date DATE NOT NULL,
    is_current BOOLEAN DEFAULT 0,
    bing_date DATE,                -- Bing 原始日期
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### 3.3 应用配置 (settings)
```sql
CREATE TABLE settings (
    key VARCHAR(50) PRIMARY KEY,
    value TEXT NOT NULL,
    description VARCHAR(200),
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

预设配置项：
- `auto_change_enabled`: 是否自动切换壁纸 (true/false)
- `change_interval`: 切换间隔（分钟）
- `download_quality`: 下载质量 (uhd/1080p/768p)
- `auto_start`: 开机自启 (true/false)
- `server_port`: 后端服务端口 (默认 8000)
- `download_path`: 壁纸下载路径

## 四、API 接口设计

### 4.1 壁纸管理 API
```
GET    /api/wallpapers              # 获取壁纸列表
GET    /api/wallpapers/current      # 获取当前壁纸
POST   /api/wallpapers/download     # 下载新壁纸（随机 4K）
PUT    /api/wallpapers/:id/set      # 设置为壁纸
DELETE /api/wallpapers/:id          # 删除壁纸
GET    /api/wallpapers/bing/info    # 获取 Bing 今日图片信息
```

### 4.2 课程表 API
```
GET    /api/courses                 # 获取所有课程
GET    /api/courses/:id             # 获取单门课程
GET    /api/courses/today           # 获取今日课程
GET    /api/courses/week/:week      # 获取指定周次课程
POST   /api/courses                 # 创建课程
PUT    /api/courses/:id             # 更新课程
DELETE /api/courses/:id            # 删除课程
DELETE /api/courses/batch          # 批量删除课程
POST   /api/courses/import          # 导入课程表
POST   /api/courses/export          # 导出课程表
```

### 4.3 配置管理 API
```
GET    /api/settings                # 获取所有配置
GET    /api/settings/:key           # 获取单个配置
PUT    /api/settings/:key           # 更新配置
POST   /api/settings/batch          # 批量更新配置
```

### 4.4 系统管理 API
```
GET    /api/system/status           # 获取系统状态
POST   /api/system/autostart        # 设置开机自启
GET    /api/system/autostart        # 查询自启状态
POST   /api/system/service/start   # 启动服务
POST   /api/system/service/stop    # 停止服务
GET    /api/system/logs             # 获取系统日志
```

## 五、核心功能实现方案

### 5.1 Bing 图片下载
```python
# 使用 bing.img.run 的 API
API_BASE = "https://bing.img.run"
RAND_UHD_URL = f"{API_BASE}/rand_uhd.php"  # 随机 4K

# 下载流程：
# 1. 发送 HEAD 请求获取真实图片 URL（会 302 跳转）
# 2. 发送 GET 请求下载图片
# 3. 保存到本地 data/wallpapers/ 目录
# 4. 记录到数据库
```

### 5.2 壁纸设置（Windows）
```python
# 方案 1：使用 wallpaper 库
import wallpaper
wallpaper.set("C:\\path\\to\\image.jpg")

# 方案 2： ctypes 调用 Windows API
import ctypes
SPI_SETDESKWALLPAPER = 20
ctypes.windll.user32.SystemParametersInfoW(
    SPI_SETDESKWALLPAPER, 0, path, 3
)
```

### 5.3 定时任务调度
```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# 定时下载并切换壁纸
scheduler.add_job(
    download_and_set_wallpaper,
    'interval',
    minutes=config.change_interval,
    id='auto_wallpaper'
)

scheduler.start()
```

### 5.4 开机自启（Windows 任务计划程序）
```powershell
# 创建任务计划
$action = New-ScheduledTaskAction -Execute "python" `
    -Argument "app/main.py" `
    -WorkingDirectory "C:\path\to\backend"

$trigger = New-ScheduledTaskTrigger -AtLogon

$principal = New-ScheduledTaskPrincipal -UserId "USER" `
    -LogonType S4U `
    -RunLevel Highest

Register-ScheduledTask -TaskName "BingWallpaper" `
    -Action $action `
    -Trigger $trigger `
    -Principal $principal
```

## 六、前端设计方案

### 6.1 色彩系统
```css
:root {
  /* 主色调 - 浅蓝色系 */
  --primary-color: #1890ff;
  --primary-light: #40a9ff;
  --primary-dark: #096dd9;
  
  /* 背景色 */
  --bg-light: #e6f7ff;
  --bg-white: #ffffff;
  --bg-dark: #f0f5ff;
  
  /* 边框色 */
  --border-color: #bae7ff;
  --border-light: #e6f7ff;
  
  /* 文字色 */
  --text-primary: #0c1929;
  --text-secondary: #597ef7;
  --text-disabled: #bfbfbf;
  
  /* 功能色 */
  --success: #52c41a;
  --warning: #faad14;
  --error: #ff4d4f;
}
```

### 6.2 页面布局
```
┌─────────────────────────────────────────────────────────┐
│  Header (Logo + 导航 + 系统状态)                         │
├──────────┬──────────────────────────────────────────────┤
│          │                                              │
│ Sidebar  │           Main Content Area                  │
│          │           (路由页面)                          │
│ - 壁纸   │                                              │
│ - 课程表 │                                              │
│ - 设置   │                                              │
│          │                                              │
└──────────┴──────────────────────────────────────────────┘
```

### 6.3 核心组件
1. **WallpaperGallery**: 壁纸画廊（网格布局 + 懒加载 + 预览）
2. **CourseTable**: 课程表（周视图 + 日视图 + 月视图）
3. **SettingsPanel**: 设置面板（表单 + 开关 + 滑块）
4. **Dashboard**: 仪表盘（今日课程 + 当前壁纸 + 快捷操作）

### 6.4 动画效果
```css
/* 页面切换动画 */
.page-transition {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

/* 卡片悬停效果 */
.card {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 24px rgba(24, 144, 255, 0.12);
}
```

## 七、错误处理与日志

### 7.1 后端错误处理
```python
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request, exc):
    return JSONResponse(
        status_code=400,
        content={"error": "validation_error", "details": exc.errors()}
    )

@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Unhandled exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "internal_server_error"}
    )
```

### 7.2 日志配置
```python
from loguru import logger

logger.add(
    "logs/app_{time:YYYY-MM-DD}.log",
    rotation="00:00",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level} | {name} | {message}"
)
```

### 7.3 前端错误边界
```tsx
class ErrorBoundary extends React.Component {
  state = { hasError: false, error: null };
  
  static getDerivedStateFromError(error) {
    return { hasError: true, error };
  }
  
  render() {
    if (this.state.hasError) {
      return <ErrorPage error={this.state.error} />;
    }
    return this.props.children;
  }
}
```

## 八、性能优化

### 8.1 后端优化
- 数据库连接池（SQLite 不需要，但预留扩展性）
- 图片下载使用异步 IO
- 定时任务使用后台线程
- 响应压缩（gzip）

### 8.2 前端优化
- 图片懒加载（react-lazy-load-image-component）
- 虚拟滚动（课程表数据量大时）
- 路由懒加载（React.lazy + Suspense）
- 静态资源 CDN

### 8.3 资源占用控制
- 壁纸下载限制并发数（最多 3 个）
- 图片缓存策略（本地缓存 + 定期清理）
- 数据库查询优化（索引 + 分页）
- 内存泄漏检测（定期 GC）

## 九、安全考虑

### 9.1 API 安全
- CORS 配置（限制来源）
- 请求频率限制（防止滥用）
- 输入验证（Pydantic 校验）
- SQL 注入防护（ORM 参数化）

### 9.2 文件安全
- 下载路径白名单校验
- 文件类型校验（仅允许图片）
- 文件大小限制（最大 10MB）
- 权限控制（仅当前用户可访问）

### 9.3 系统安全
- 开机自启需要管理员权限
- 敏感配置加密存储
- 日志脱敏（不记录密码等）

## 十、扩展性设计

### 10.1 插件化架构
```python
# 预留插件接口
class WallpaperProvider(ABC):
    @abstractmethod
    def get_image_url(self) -> str:
        pass
    
    @abstractmethod
    def get_image_info(self) -> dict:
        pass

# 可实现多个 Provider
class BingProvider(WallpaperProvider):
    pass

class UnsplashProvider(WallpaperProvider):
    pass
```

### 10.2 数据库扩展
```python
# 预留 PostgreSQL 支持
# DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///data/app.db")
# 未来可切换到 PostgreSQL
```

### 10.3 前端微服务化
```tsx
// 预留微前端架构
// 未来可接入多个子应用
const MicroApp = lazy(() => import('@micro-app/course'));
```

## 十一、部署方案

### 11.1 开发环境
```bash
# 后端
cd backend
python -m venv venv
.\venv\Scripts\Activate
pip install -r requirements.txt
python app/main.py

# 前端
cd frontend
npm install
npm run dev
```

### 11.2 生产环境
```bash
# 使用 PyInstaller 打包后端
pyinstaller --onefile --name=bing-wallpaper app/main.py

# 前端构建
npm run build

# 运行安装脚本
.\scripts\install.ps1
```

### 11.3 开机自启配置
```powershell
# 使用任务计划程序
.\scripts\setup-autostart.ps1
```

## 十二、测试策略

### 12.1 后端测试
```python
# pytest + pytest-asyncio
def test_download_wallpaper():
    response = client.post("/api/wallpapers/download")
    assert response.status_code == 200
    assert "file_path" in response.json()
```

### 12.2 前端测试
```tsx
// Vitest + React Testing Library
test('renders course table', () => {
  render(<CourseTable />);
  expect(screen.getByText('课程表')).toBeInTheDocument();
});
```

### 12.3 E2E 测试
```typescript
// Playwright
test('can set wallpaper', async ({ page }) => {
  await page.goto('/wallpapers');
  await page.click('[data-testid="wallpaper-1"]');
  await page.click('[data-testid="set-as-wallpaper"]');
  await expect(page.getByText('设置成功')).toBeVisible();
});
```

---

**文档版本**: v1.0  
**创建日期**: 2026-04-21  
**最后更新**: 2026-04-21  
**负责人**: P8 Agent
