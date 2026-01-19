"""
RSS源服务模块
提供RSS源相关的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session

from server.models.rss_source import RSSSource


class RSSService:
    """RSS源服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_rss_source(
        self,
        anime_id: int,
        name: str,
        url: str,
        quality: Optional[str] = None,
        is_active: bool = True,
        auto_download: bool = False
    ) -> RSSSource:
        """创建RSS源记录"""
        rss_source = RSSSource(
            anime_id=anime_id,
            name=name,
            url=url,
            quality=quality,
            is_active=is_active,
            auto_download=auto_download
        )
        self.db.add(rss_source)
        self.db.commit()
        self.db.refresh(rss_source)
        return rss_source
    
    def get_rss_source(self, rss_source_id: int) -> Optional[RSSSource]:
        """获取单个RSS源"""
        return self.db.query(RSSSource).filter(RSSSource.id == rss_source_id).first()
    
    def get_rss_sources(self, anime_id: int) -> List[RSSSource]:
        """获取动画的所有RSS源"""
        return self.db.query(RSSSource).filter(RSSSource.anime_id == anime_id).all()
    
    def update_rss_source(
        self,
        rss_source_id: int,
        name: Optional[str] = None,
        url: Optional[str] = None,
        quality: Optional[str] = None,
        is_active: Optional[bool] = None,
        auto_download: Optional[bool] = None
    ) -> Optional[RSSSource]:
        """更新RSS源信息"""
        rss_source = self.get_rss_source(rss_source_id)
        if not rss_source:
            return None
        
        update_data = {}
        if name is not None:
            update_data['name'] = name
        if url is not None:
            update_data['url'] = url
        if quality is not None:
            update_data['quality'] = quality
        if is_active is not None:
            update_data['is_active'] = is_active
        if auto_download is not None:
            update_data['auto_download'] = auto_download
        
        for key, value in update_data.items():
            setattr(rss_source, key, value)
        
        self.db.commit()
        self.db.refresh(rss_source)
        return rss_source
    
    def delete_rss_source(self, rss_source_id: int) -> bool:
        """删除RSS源"""
        rss_source = self.get_rss_source(rss_source_id)
        if not rss_source:
            return False
        
        self.db.delete(rss_source)
        self.db.commit()
        return True