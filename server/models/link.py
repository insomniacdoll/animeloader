from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text, Index, UniqueConstraint
from sqlalchemy.orm import relationship
from server.models.anime import Base


class Link(Base):
    __tablename__ = 'links'

    id = Column(Integer, primary_key=True, autoincrement=True)
    rss_source_id = Column(Integer, ForeignKey('rss_sources.id'), nullable=False)
    episode_number = Column(Integer, nullable=True)
    episode_title = Column(String(255), nullable=True)
    link_type = Column(String(50), nullable=False)
    url = Column(Text, nullable=False)
    file_size = Column(Integer, nullable=True)
    publish_date = Column(DateTime, nullable=True)
    is_downloaded = Column(Boolean, default=False, nullable=False)
    is_available = Column(Boolean, default=True, nullable=False)
    meta_data = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    rss_source = relationship("RSSSource", back_populates="links")
    download_tasks = relationship("DownloadTask", back_populates="link", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_link_rss_source_id', 'rss_source_id'),
        Index('idx_link_type', 'link_type'),
        Index('idx_link_is_downloaded', 'is_downloaded'),
        Index('idx_link_is_available', 'is_available'),
        Index('idx_link_publish_date', 'publish_date'),
        UniqueConstraint('rss_source_id', 'url', name='uq_link_rss_source_url'),  # 添加唯一性约束
    )

    def __repr__(self):
        return f"<Link(id={self.id}, type='{self.link_type}', episode={self.episode_number})>"