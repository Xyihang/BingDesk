"""
数据模型 - 塔罗牌历史记录
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, func
from app.database import Base


class TarotReading(Base):
    """塔罗牌占卜历史记录"""

    __tablename__ = "tarot_readings"

    id = Column(Integer, primary_key=True, autoincrement=True)
    reading_type = Column(String(20), nullable=False, comment="牌阵类型: monthly/daily/celtic")
    question = Column(String(500), nullable=True, comment="用户提出的问题")
    period_months = Column(Integer, nullable=True, comment="月度运势的月份数")
    cards_json = Column(Text, nullable=False, comment="抽到的牌(JSON)")
    ai_interpretation = Column(Text, nullable=True, comment="AI解读结果")
    overall_fortune = Column(String(10), nullable=True, comment="整体运势: 吉/凶")
    created_at = Column(
        DateTime,
        server_default=func.now(),
        comment="创建时间"
    )

    def __repr__(self):
        return f"<TarotReading(id={self.id}, type='{self.reading_type}', question='{self.question}')>"
