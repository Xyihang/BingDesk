"""
数据库连接管理
"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import select
from app.config import settings

# 创建异步引擎
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,  # 开发环境打印 SQL
    future=True,
)

# 创建会话工厂
async_session_maker = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# 用于非依赖注入的会话
AsyncSessionLocal = async_session_maker

# 基类
Base = declarative_base()


async def get_db() -> AsyncSession:
    """获取数据库会话依赖"""
    async with async_session_maker() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_default_settings(db: AsyncSession):
    """初始化默认配置（如果不存在）"""
    # 延迟导入避免循环依赖
    from app.models.settings import Setting
    
    import hashlib
    
    default_settings = [
        ("auto_change_enabled", "false", "是否自动切换壁纸"),
        ("change_interval", "60", "切换间隔（分钟）"),
        ("download_quality", "uhd", "下载质量"),
        ("auto_start", "false", "开机自启"),
        ("server_port", "8000", "服务端口"),
        ("app_password", hashlib.sha256("wobuzhidao".encode()).hexdigest(), "操作密码"),
        ("grid_password", hashlib.sha256("xiyihang360".encode()).hexdigest(), "网格密码"),
    ]
    
    for key, value, description in default_settings:
        result = await db.execute(select(Setting).where(Setting.key == key))
        existing = result.scalar_one_or_none()
        
        if not existing:
            setting = Setting(key=key, value=value, description=description)
            db.add(setting)
    
    await db.commit()


async def init_db():
    """初始化数据库（创建表并初始化默认数据）"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    
    # 初始化默认设置
    async with async_session_maker() as db:
        await init_default_settings(db)


async def close_db():
    """关闭数据库连接"""
    await engine.dispose()
