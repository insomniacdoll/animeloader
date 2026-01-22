"""
RSS源服务模块
提供RSS源相关的业务逻辑
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from server.models.rss_source import RSSSource


class RSSService:
    """RSS源服务类"""
    
    def __init__(self, db: Session, scheduler_service=None):
        self.db = db
        self.scheduler_service = scheduler_service
    
    def get_rss_source_by_url_and_anime(self, anime_id: int, url: str) -> Optional[RSSSource]:
        """根据动画ID和URL获取RSS源，用于检测重复"""
        return self.db.query(RSSSource).filter(
            RSSSource.anime_id == anime_id,
            RSSSource.url == url
        ).first()
    
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
        # 检查是否已存在相同URL的RSS源
        existing_rss = self.get_rss_source_by_url_and_anime(anime_id, url)
        if existing_rss:
            return existing_rss  # 返回已存在的RSS源
        
        rss_source = RSSSource(
            anime_id=anime_id,
            name=name,
            url=url,
            quality=quality,
            is_active=is_active,
            auto_download=auto_download
        )
        try:
            self.db.add(rss_source)
            self.db.commit()
            self.db.refresh(rss_source)
            
            # 如果启用了自动下载，创建调度任务
            if auto_download and self.scheduler_service:
                from server.utils.config import config
                check_interval = config.get('rss.check_interval', 3600)  # 从配置获取检查间隔，默认1小时
                self.scheduler_service.add_check_job(
                    rss_source_id=rss_source.id,
                    interval=check_interval,
                    auto_download=True
                )
            
            return rss_source
        except IntegrityError:
            # 如果数据库约束冲突，回滚并返回已存在的记录
            self.db.rollback()
            # 重新检查是否存在（以防在事务间被其他请求添加）
            existing_rss = self.get_rss_source_by_url_and_anime(anime_id, url)
            if existing_rss:
                return existing_rss
            else:
                # 如果仍然不存在，可能是其他类型的约束冲突，重新抛出异常
                raise
    
    def get_rss_source(self, rss_source_id: int) -> Optional[RSSSource]:
        """获取单个RSS源"""
        return self.db.query(RSSSource).filter(RSSSource.id == rss_source_id).first()
    
    def get_rss_sources(self, anime_id: int) -> List[RSSSource]:
        """获取动画的所有RSS源"""
        return self.db.query(RSSSource).filter(RSSSource.anime_id == anime_id).all()
    
    def get_all_rss_sources(self) -> List[RSSSource]:
        """获取所有RSS源"""
        return self.db.query(RSSSource).all()
    
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
        
        # 保存原始的auto_download状态，用于后续判断是否需要管理调度任务
        original_auto_download = rss_source.auto_download
        
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
        
        # 如果auto_download状态发生变化，管理调度任务
        if auto_download is not None and auto_download != original_auto_download and self.scheduler_service:
            job_id = f"rss_check_{rss_source_id}"
            if auto_download:
                # 启用自动下载，创建调度任务
                from server.utils.config import config
                check_interval = config.get('rss.check_interval', 3600)  # 从配置获取检查间隔，默认1小时
                self.scheduler_service.add_check_job(
                    rss_source_id=rss_source_id,
                    interval=check_interval,
                    auto_download=True
                )
            else:
                # 禁用自动下载，移除调度任务
                self.scheduler_service.remove_check_job(job_id)
        
        return rss_source
    
    def delete_rss_source(self, rss_source_id: int) -> bool:
        """删除RSS源"""
        rss_source = self.get_rss_source(rss_source_id)
        if not rss_source:
            return False
        
        self.db.delete(rss_source)
        self.db.commit()
        return True