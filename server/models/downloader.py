from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, Index
from sqlalchemy.orm import relationship
from server.models.anime import Base


class Downloader(Base):
    __tablename__ = 'downloaders'

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    downloader_type = Column(String(50), nullable=False)
    config = Column(Text, nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    max_concurrent_tasks = Column(Integer, default=3, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    download_tasks = relationship("DownloadTask", back_populates="downloader", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_downloader_type', 'downloader_type'),
        Index('idx_downloader_is_active', 'is_active'),
        Index('idx_downloader_is_default', 'is_default'),
    )

    def __repr__(self):
        return f"<Downloader(id={self.id}, name='{self.name}', type='{self.downloader_type}')>"