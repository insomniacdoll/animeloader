"""
动画服务模块
提供动画相关的业务逻辑
"""
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_

from server.models.anime import Anime


class AnimeService:
    """动画服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_anime(
        self,
        title: str,
        title_en: Optional[str] = None,
        description: Optional[str] = None,
        cover_url: Optional[str] = None,
        status: str = 'ongoing',
        total_episodes: Optional[int] = None
    ) -> Anime:
        """创建动画记录"""
        anime = Anime(
            title=title,
            title_en=title_en,
            description=description,
            cover_url=cover_url,
            status=status,
            total_episodes=total_episodes
        )
        self.db.add(anime)
        self.db.commit()
        self.db.refresh(anime)
        return anime
    
    def get_anime(self, anime_id: int) -> Optional[Anime]:
        """获取单个动画"""
        return self.db.query(Anime).filter(Anime.id == anime_id).first()
    
    def get_animes(
        self,
        skip: int = 0,
        limit: int = 100,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> List[Anime]:
        """获取动画列表，支持搜索和过滤"""
        query = self.db.query(Anime)
        
        # 搜索功能
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Anime.title.like(search_pattern),
                    Anime.title_en.like(search_pattern),
                    Anime.description.like(search_pattern)
                )
            )
        
        # 状态过滤
        if status:
            query = query.filter(Anime.status == status)
        
        # 分页
        query = query.offset(skip).limit(limit)
        
        return query.all()
    
    def update_anime(
        self,
        anime_id: int,
        title: Optional[str] = None,
        title_en: Optional[str] = None,
        description: Optional[str] = None,
        cover_url: Optional[str] = None,
        status: Optional[str] = None,
        total_episodes: Optional[int] = None
    ) -> Optional[Anime]:
        """更新动画信息"""
        anime = self.get_anime(anime_id)
        if not anime:
            return None
        
        update_data = {}
        if title is not None:
            update_data['title'] = title
        if title_en is not None:
            update_data['title_en'] = title_en
        if description is not None:
            update_data['description'] = description
        if cover_url is not None:
            update_data['cover_url'] = cover_url
        if status is not None:
            update_data['status'] = status
        if total_episodes is not None:
            update_data['total_episodes'] = total_episodes
        
        for key, value in update_data.items():
            setattr(anime, key, value)
        
        self.db.commit()
        self.db.refresh(anime)
        return anime
    
    def delete_anime(self, anime_id: int) -> bool:
        """删除动画"""
        anime = self.get_anime(anime_id)
        if not anime:
            return False
        
        self.db.delete(anime)
        self.db.commit()
        return True
    
    def count_animes(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None
    ) -> int:
        """统计动画数量"""
        query = self.db.query(Anime)
        
        if search:
            search_pattern = f"%{search}%"
            query = query.filter(
                or_(
                    Anime.title.like(search_pattern),
                    Anime.title_en.like(search_pattern),
                    Anime.description.like(search_pattern)
                )
            )
        
        if status:
            query = query.filter(Anime.status == status)
        
        return query.count()