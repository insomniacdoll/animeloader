"""
链接服务模块
提供链接相关的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from server.models.link import Link


class LinkService:
    """链接服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def add_link(
        self,
        rss_source_id: int,
        episode_number: Optional[int] = None,
        episode_title: Optional[str] = None,
        link_type: str = "magnet",
        url: str = "",
        file_size: Optional[int] = None,
        publish_date: Optional = None,
        meta_data: Optional[str] = None
    ) -> Link:
        """添加链接"""
        link = Link(
            rss_source_id=rss_source_id,
            episode_number=episode_number,
            episode_title=episode_title,
            link_type=link_type,
            url=url,
            file_size=file_size,
            publish_date=publish_date,
            is_downloaded=False,
            is_available=True,
            meta_data=meta_data
        )
        self.db.add(link)
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def get_link(self, link_id: int) -> Optional[Link]:
        """获取单个链接"""
        return self.db.query(Link).filter(Link.id == link_id).first()
    
    def get_links(
        self,
        rss_source_id: int,
        is_downloaded: Optional[bool] = None,
        link_type: Optional[str] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Link]:
        """获取RSS源的所有链接，支持过滤"""
        query = self.db.query(Link).filter(Link.rss_source_id == rss_source_id)
        
        # 下载状态过滤
        if is_downloaded is not None:
            query = query.filter(Link.is_downloaded == is_downloaded)
        
        # 链接类型过滤
        if link_type is not None:
            query = query.filter(Link.link_type == link_type)
        
        # 排序：按集数降序
        query = query.order_by(Link.episode_number.desc())
        
        # 分页
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    def count_links(
        self,
        rss_source_id: Optional[int] = None,
        is_downloaded: Optional[bool] = None,
        link_type: Optional[str] = None
    ) -> int:
        """统计链接数量"""
        query = self.db.query(Link)
        
        if rss_source_id is not None:
            query = query.filter(Link.rss_source_id == rss_source_id)
        
        if is_downloaded is not None:
            query = query.filter(Link.is_downloaded == is_downloaded)
        
        if link_type is not None:
            query = query.filter(Link.link_type == link_type)
        
        return query.count()
    
    def mark_as_downloaded(self, link_id: int) -> Optional[Link]:
        """标记链接为已下载"""
        link = self.get_link(link_id)
        if not link:
            return None
        
        link.is_downloaded = True
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def update_link_status(
        self,
        link_id: int,
        is_available: Optional[bool] = None,
        is_downloaded: Optional[bool] = None
    ) -> Optional[Link]:
        """更新链接状态"""
        link = self.get_link(link_id)
        if not link:
            return None
        
        if is_available is not None:
            link.is_available = is_available
        if is_downloaded is not None:
            link.is_downloaded = is_downloaded
        
        self.db.commit()
        self.db.refresh(link)
        return link
    
    def get_available_links(self, rss_source_id: int) -> List[Link]:
        """获取可用的下载链接"""
        return self.db.query(Link).filter(
            and_(
                Link.rss_source_id == rss_source_id,
                Link.is_available == True,
                Link.is_downloaded == False
            )
        ).order_by(Link.episode_number.desc()).all()
    
    def filter_links_by_type(
        self,
        rss_source_id: int,
        link_type: str,
        skip: int = 0,
        limit: int = 100
    ) -> List[Link]:
        """按链接类型过滤"""
        return self.db.query(Link).filter(
            and_(
                Link.rss_source_id == rss_source_id,
                Link.link_type == link_type
            )
        ).order_by(Link.episode_number.desc()).offset(skip).limit(limit).all()
    
    def delete_link(self, link_id: int) -> bool:
        """删除链接"""
        link = self.get_link(link_id)
        if not link:
            return False
        
        self.db.delete(link)
        self.db.commit()
        return True
    
    def get_all_links(
        self,
        skip: int = 0,
        limit: int = 100,
        link_type: Optional[str] = None,
        is_downloaded: Optional[bool] = None
    ) -> List[Link]:
        """获取所有链接（支持全局过滤）"""
        query = self.db.query(Link)
        
        if link_type is not None:
            query = query.filter(Link.link_type == link_type)
        
        if is_downloaded is not None:
            query = query.filter(Link.is_downloaded == is_downloaded)
        
        query = query.order_by(Link.publish_date.desc()).offset(skip).limit(limit)
        
        return query.all()