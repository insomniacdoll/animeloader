from datetime import datetime
from sqlalchemy import Column, Integer, String, Text, DateTime, Index
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Anime(Base):
    __tablename__ = 'animes'

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(255), nullable=False)
    title_en = Column(String(255), nullable=True)
    description = Column(Text, nullable=True)
    cover_url = Column(String(500), nullable=True)
    source_url = Column(String(500), nullable=True)  # 添加来源URL字段，用于去重
    status = Column(String(50), nullable=False, default='ongoing')
    total_episodes = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    __table_args__ = (
        Index('idx_anime_source_url', 'source_url'),  # 为source_url创建索引
    )

    def __repr__(self):
        return f"<Anime(id={self.id}, title='{self.title}')>"