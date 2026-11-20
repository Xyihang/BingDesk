"""
数据模型 - 配置
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from datetime import datetime
from app.database import Base


class Setting(Base):
    """应用配置模型"""
    
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(50), unique=True, nullable=False, comment="配置键")
    value = Column(Text, nullable=False, comment="配置值")
    description = Column(String(200), nullable=True, comment="配置描述")
    updated_at = Column(
        DateTime, 
        default=datetime.now, 
        onupdate=datetime.now, 
        comment="更新时间"
    )
    
    def __repr__(self):
        return f"<Setting(key='{self.key}', value='{self.value}')>"
