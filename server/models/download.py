from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Index
from sqlalchemy.orm import relationship
from server.models.anime import Base


class DownloadTask(Base):
    __tablename__ = 'download_tasks'

    id = Column(Integer, primary_key=True, autoincrement=True)
    link_id = Column(Integer, ForeignKey('links.id'), nullable=False)
    rss_source_id = Column(Integer, ForeignKey('rss_sources.id'), nullable=False)
    downloader_id = Column(Integer, ForeignKey('downloaders.id'), nullable=False)
    downloader_type = Column(String(50), nullable=False)
    file_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default='pending')
    progress = Column(Float, default=0.0, nullable=False)
    file_size = Column(Integer, nullable=True)
    downloaded_size = Column(Integer, default=0, nullable=False)
    download_speed = Column(Float, default=0.0, nullable=False)
    upload_speed = Column(Float, default=0.0, nullable=False)
    error_message = Column(Text, nullable=True)
    retry_count = Column(Integer, default=0, nullable=False)
    task_id_external = Column(String(255), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)

    link = relationship("Link", back_populates="download_tasks")
    downloader = relationship("Downloader", back_populates="download_tasks")

    __table_args__ = (
        Index('idx_download_rss_source_id', 'rss_source_id'),
        Index('idx_download_link_id', 'link_id'),
        Index('idx_download_downloader_id', 'downloader_id'),
        Index('idx_download_downloader_type', 'downloader_type'),
        Index('idx_download_status', 'status'),
    )

    def __repr__(self):
        return f"<DownloadTask(id={self.id}, status='{self.status}', progress={self.progress}%)>"