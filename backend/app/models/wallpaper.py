"""
数据模型 - 壁纸
"""
from sqlalchemy import Column, Integer, String, Boolean, Date, DateTime, func
from datetime import datetime, date
from app.database import Base


class Wallpaper(Base):
    """壁纸模型"""
    
    __tablename__ = "wallpapers"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    file_path = Column(String(500), nullable=False, comment="文件路径")
    source_url = Column(String(500), nullable=True, comment="来源 URL")
    resolution = Column(String(20), nullable=True, comment="分辨率")
    download_date = Column(Date, nullable=False, default=date.today, comment="下载日期")
    is_current = Column(Boolean, default=False, comment="是否当前壁纸")
    bing_date = Column(Date, nullable=True, comment="Bing 原始日期")
    created_at = Column(DateTime, default=datetime.now, comment="创建时间")
    
    def __repr__(self):
        return f"<Wallpaper(id={self.id}, path='{self.file_path}', current={self.is_current})>"
