"""
调度服务模块
提供定时任务调度功能
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session

from server.services.rss_service import RSSService
from server.services.link_service import LinkService
from server.services.download_service import DownloadService
from server.services.downloader_service import DownloaderService
from server.site_parsers.base_rss_parser import BaseRSSParser
from server.site_parsers.mikan_rss_parser import MikanRSSParser


class SchedulerService:
    """调度服务类"""
    
    def __init__(self, db_factory):
        """
        初始化调度服务

        Args:
            db_factory: 数据库会话工厂函数
        """
        self.db_factory = db_factory
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.jobs = {}  # 存储任务信息 {job_id: job_info}

        # 初始化RSS解析器列表
        self.rss_parsers: List[BaseRSSParser] = [
            MikanRSSParser(),
        ]

    def _get_rss_parser(self, url: str) -> Optional[BaseRSSParser]:
        """
        根据RSS源URL获取对应的解析器

        Args:
            url: RSS源URL

        Returns:
            对应的解析器，如果没有找到返回None
        """
        for parser in self.rss_parsers:
            if parser.can_parse(url):
                return parser
        return None

    def register_rss_parser(self, parser: BaseRSSParser):
        """
        注册新的RSS解析器

        Args:
            parser: RSS解析器实例
        """
        self.rss_parsers.append(parser)

    def get_supported_rss_sites(self) -> List[str]:
        """
        获取支持的RSS源网站列表

        Returns:
            支持的网站名称列表
        """
        return [parser.get_site_name() for parser in self.rss_parsers]

    def start_scheduler(self) -> bool:
        """启动调度器"""
        if self.is_running:
            return True
        
        try:
            self.scheduler.start()
            self.is_running = True
            return True
        except Exception as e:
            print(f"启动调度器失败: {e}")
            return False
    
    def stop_scheduler(self) -> bool:
        """停止调度器"""
        if not self.is_running:
            return True
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            self.jobs.clear()
            return True
        except Exception as e:
            print(f"停止调度器失败: {e}")
            return False
    
    def add_check_job(
        self,
        rss_source_id: int,
        interval: int = 3600,
        auto_download: bool = False
    ) -> Optional[str]:
        """
        添加RSS源检查任务
        
        Args:
            rss_source_id: RSS源ID
            interval: 检查间隔（秒）
            auto_download: 是否自动下载新链接
            
        Returns:
            任务ID，失败返回None
        """
        if not self.is_running:
            print("调度器未运行，无法添加任务")
            return None
        
        job_id = f"rss_check_{rss_source_id}"
        
        # 如果任务已存在，先移除
        if job_id in self.jobs:
            self.remove_check_job(job_id)
        
        try:
            # 添加定时任务
            self.scheduler.add_job(
                self._check_rss_source,
                trigger=IntervalTrigger(seconds=interval),
                id=job_id,
                args=[rss_source_id, auto_download],
                name=f"检查RSS源 {rss_source_id}",
                replace_existing=True
            )
            
            self.jobs[job_id] = {
                "rss_source_id": rss_source_id,
                "interval": interval,
                "auto_download": auto_download,
                "created_at": datetime.utcnow()
            }
            
            return job_id
        except Exception as e:
            print(f"添加检查任务失败: {e}")
            return None
    
    def remove_check_job(self, job_id: str) -> bool:
        """移除检查任务"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
            return True
        except Exception as e:
            print(f"移除检查任务失败: {e}")
            return False
    
    def check_rss_source(self, rss_source_id: int, auto_download: bool = False) -> Dict[str, Any]:
        """
        检查RSS源的新链接

        Args:
            rss_source_id: RSS源ID
            auto_download: 是否自动下载新链接

        Returns:
            检查结果
        """
        db = next(self.db_factory())
        try:
            rss_service = RSSService(db)
            link_service = LinkService(db)
            download_service = DownloadService(db)
            downloader_service = DownloaderService(db)

            # 获取RSS源
            rss_source = rss_service.get_rss_source(rss_source_id)
            if not rss_source:
                return {
                    "success": False,
                    "message": f"RSS源 {rss_source_id} 不存在"
                }

            # 检查RSS源是否激活
            if not rss_source.is_active:
                return {
                    "success": False,
                    "message": f"RSS源 {rss_source_id} 未激活"
                }

            # 获取已存在的链接URL
            existing_links = link_service.get_links(rss_source_id)
            existing_urls = [link.url for link in existing_links]

            # 根据RSS源URL获取对应的解析器
            rss_parser = self._get_rss_parser(rss_source.url)
            if not rss_parser:
                return {
                    "success": False,
                    "message": f"不支持的RSS源: {rss_source.url}"
                }

            # 解析RSS源
            parse_result = rss_parser.parse_rss(rss_source.url, existing_urls)

            if not parse_result.get('success'):
                return {
                    "success": False,
                    "message": f"RSS解析失败: {parse_result.get('error', '未知错误')}"
                }

            # 更新最后检查时间
            rss_source.last_checked_at = datetime.utcnow()
            db.commit()

            # 获取新链接
            new_links_info = parse_result.get('new_links', [])
            new_links_count = len(new_links_info)

            if new_links_count == 0:
                return {
                    "success": True,
                    "message": "检查完成，未发现新链接",
                    "rss_source_id": rss_source_id,
                    "new_links_count": 0,
                    "new_links": [],
                    "checked_at": datetime.utcnow().isoformat()
                }

            # 添加新链接到数据库
            added_links = []
            for link_info in new_links_info:
                link = link_service.add_link(
                    rss_source_id=rss_source_id,
                    episode_number=link_info.get('episode_number'),
                    episode_title=link_info.get('episode_title'),
                    link_type=link_info.get('link_type', 'magnet'),
                    url=link_info.get('url', ''),
                    file_size=link_info.get('file_size'),
                    publish_date=link_info.get('publish_date'),
                    meta_data=link_info.get('meta_data')
                )

                if link:
                    added_links.append({
                        "id": link.id,
                        "episode_number": link.episode_number,
                        "episode_title": link.episode_title,
                        "link_type": link.link_type,
                        "url": link.url,
                        "file_size": link.file_size
                    })

                    # 如果启用了自动下载
                    if auto_download and rss_source.auto_download:
                        # 获取默认下载器
                        downloader = downloader_service.get_default_downloader()
                        if downloader:
                            # 创建下载任务
                            task = download_service.create_download_task(
                                link_id=link.id,
                                rss_source_id=rss_source_id,
                                downloader_id=downloader.id
                            )
                            if task:
                                # 开始下载
                                download_service.start_download(task.id)

            return {
                "success": True,
                "message": f"检查完成，发现 {new_links_count} 个新链接",
                "rss_source_id": rss_source_id,
                "new_links_count": new_links_count,
                "new_links": added_links,
                "checked_at": datetime.utcnow().isoformat()
            }
        except Exception as e:
            db.rollback()
            return {
                "success": False,
                "message": f"检查RSS源失败: {str(e)}"
            }
        finally:
            db.close()
    
    def _check_rss_source(self, rss_source_id: int, auto_download: bool = False):
        """内部方法：检查RSS源（用于定时任务）"""
        self.check_rss_source(rss_source_id, auto_download)
    
    def get_jobs(self) -> Dict[str, Dict[str, Any]]:
        """获取所有任务信息"""
        return self.jobs.copy()
    
    def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """获取任务状态"""
        if job_id not in self.jobs:
            return None
        
        job = self.scheduler.get_job(job_id)
        if not job:
            return None
        
        return {
            "job_id": job_id,
            "name": job.name,
            "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
            "info": self.jobs[job_id]
        }
    
    def pause_job(self, job_id: str) -> bool:
        """暂停任务"""
        try:
            self.scheduler.pause_job(job_id)
            return True
        except Exception as e:
            print(f"暂停任务失败: {e}")
            return False
    
    def resume_job(self, job_id: str) -> bool:
        """恢复任务"""
        try:
            self.scheduler.resume_job(job_id)
            return True
        except Exception as e:
            print(f"恢复任务失败: {e}")
            return False