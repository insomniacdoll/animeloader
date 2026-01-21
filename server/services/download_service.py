"""
下载服务模块
提供下载任务管理相关的业务逻辑
"""
from typing import List, Optional, Dict
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_, or_

from server.models.download import DownloadTask
from server.models.link import Link
from server.models.downloader import Downloader


class DownloadService:
    """下载服务类"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def create_download_task(
        self,
        link_id: int,
        rss_source_id: int,
        downloader_id: Optional[int] = None,
        file_path: Optional[str] = None
    ) -> Optional[DownloadTask]:
        """创建下载任务"""
        # 获取链接信息
        link = self.db.query(Link).filter(Link.id == link_id).first()
        if not link:
            return None
        
        # 如果没有指定下载器，使用默认下载器
        if downloader_id is None:
            downloader = self.db.query(Downloader).filter(
                Downloader.is_default == True
            ).first()
            if not downloader:
                # 如果没有默认下载器，使用第一个可用的下载器
                downloader = self.db.query(Downloader).filter(
                    Downloader.is_active == True
                ).first()
            if not downloader:
                return None
            downloader_id = downloader.id
            downloader_type = downloader.downloader_type
        else:
            downloader = self.db.query(Downloader).filter(
                Downloader.id == downloader_id
            ).first()
            if not downloader:
                return None
            downloader_type = downloader.downloader_type
        
        # 创建下载任务
        task = DownloadTask(
            link_id=link_id,
            rss_source_id=rss_source_id,
            downloader_id=downloader_id,
            downloader_type=downloader_type,
            file_path=file_path,
            status="pending",
            progress=0.0,
            file_size=link.file_size,
            downloaded_size=0,
            download_speed=0.0,
            upload_speed=0.0,
            retry_count=0
        )
        
        self.db.add(task)
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_download_task(self, task_id: int) -> Optional[DownloadTask]:
        """获取单个下载任务"""
        return self.db.query(DownloadTask).filter(DownloadTask.id == task_id).first()
    
    def get_download_tasks(
        self,
        rss_source_id: Optional[int] = None,
        status: Optional[str] = None,
        page: int = 1,
        size: int = 20
    ) -> List[DownloadTask]:
        """获取下载任务列表，支持过滤"""
        query = self.db.query(DownloadTask)
        
        if rss_source_id is not None:
            query = query.filter(DownloadTask.rss_source_id == rss_source_id)
        
        if status is not None:
            query = query.filter(DownloadTask.status == status)
        
        query = query.order_by(DownloadTask.created_at.desc())
        
        # 分页：page从1开始，计算offset
        offset = (page - 1) * size
        return query.offset(offset).limit(size).all()
    
    def get_download_tasks_by_link(self, link_id: int) -> List[DownloadTask]:
        """获取链接的所有下载任务"""
        return self.db.query(DownloadTask).filter(
            DownloadTask.link_id == link_id
        ).order_by(DownloadTask.created_at.desc()).all()
    
    def get_active_downloads(self) -> List[DownloadTask]:
        """获取所有活跃的下载任务"""
        return self.db.query(DownloadTask).filter(
            DownloadTask.status.in_(["pending", "downloading"])
        ).all()
    
    def start_download(self, task_id: int) -> Optional[DownloadTask]:
        """开始下载（Mock实现）"""
        task = self.get_download_task(task_id)
        if not task:
            return None
        
        # Mock 实现：直接标记为下载中
        task.status = "downloading"
        task.started_at = datetime.utcnow()
        task.progress = 0.0
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def pause_download(self, task_id: int) -> Optional[DownloadTask]:
        """暂停下载（Mock实现）"""
        task = self.get_download_task(task_id)
        if not task:
            return None
        
        # Mock 实现：标记为暂停
        task.status = "paused"
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def resume_download(self, task_id: int) -> Optional[DownloadTask]:
        """恢复下载（Mock实现）"""
        task = self.get_download_task(task_id)
        if not task:
            return None
        
        # Mock 实现：标记为下载中
        task.status = "downloading"
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def cancel_download(self, task_id: int) -> Optional[DownloadTask]:
        """取消下载（Mock实现）"""
        task = self.get_download_task(task_id)
        if not task:
            return None
        
        # Mock 实现：标记为已取消
        task.status = "cancelled"
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def get_download_status(self, task_id: int) -> Optional[Dict]:
        """获取下载状态"""
        task = self.get_download_task(task_id)
        if not task:
            return None
        
        # Mock 实现：返回模拟状态
        return {
            "task_id": task.id,
            "status": task.status,
            "progress": task.progress,
            "file_size": task.file_size,
            "downloaded_size": task.downloaded_size,
            "download_speed": task.download_speed,
            "upload_speed": task.upload_speed,
            "error_message": task.error_message,
            "retry_count": task.retry_count,
            "created_at": task.created_at.isoformat() if task.created_at else None,
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None
        }
    
    def sync_download_status(self, task_id: int) -> Optional[DownloadTask]:
        """同步下载器状态到本地（Mock实现）"""
        task = self.get_download_task(task_id)
        if not task:
            return None
        
        # Mock 实现：如果是下载中，模拟进度增长
        if task.status == "downloading":
            task.progress = min(100.0, task.progress + 10.0)
            if task.progress >= 100.0:
                task.status = "completed"
                task.completed_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(task)
        return task
    
    def delete_download_task(self, task_id: int) -> bool:
        """删除下载任务"""
        task = self.get_download_task(task_id)
        if not task:
            return False
        
        self.db.delete(task)
        self.db.commit()
        return True
    
    def count_download_tasks(
        self,
        rss_source_id: Optional[int] = None,
        status: Optional[str] = None
    ) -> int:
        """统计下载任务数量"""
        query = self.db.query(DownloadTask)
        
        if rss_source_id is not None:
            query = query.filter(DownloadTask.rss_source_id == rss_source_id)
        
        if status is not None:
            query = query.filter(DownloadTask.status == status)
        
        return query.count()