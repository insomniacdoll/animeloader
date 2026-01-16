from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Index
from sqlalchemy.orm import relationship
from server.models.anime import Base


class RSSSource(Base):
    __tablename__ = 'rss_sources'

    id = Column(Integer, primary_key=True, autoincrement=True)
    anime_id = Column(Integer, ForeignKey('animes.id'), nullable=False)
    name = Column(String(255), nullable=False)
    url = Column(String(500), nullable=False)
    quality = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True, nullable=False)
    auto_download = Column(Boolean, default=False, nullable=False)
    last_checked_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    anime = relationship("Anime", backref="rss_sources")
    links = relationship("Link", back_populates="rss_source", cascade="all, delete-orphan")

    __table_args__ = (
        Index('idx_rss_source_anime_id', 'anime_id'),
        Index('idx_rss_source_is_active', 'is_active'),
    )

    def __repr__(self):
        return f"<RSSSource(id={self.id}, name='{self.name}', url='{self.url}')>"