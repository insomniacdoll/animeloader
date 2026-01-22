"""
调度服务模块
提供定时任务调度功能
"""
from typing import Optional, Dict, Any, List
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from sqlalchemy.orm import Session
import logging

from server.services.rss_service import RSSService
from server.services.link_service import LinkService
from server.services.download_service import DownloadService
from server.services.downloader_service import DownloaderService
from server.site_parsers.base_rss_parser import BaseRSSParser
from server.site_parsers.mikan_rss_parser import MikanRSSParser


class SchedulerService:
    """调度服务类"""
    
    def __init__(self, db_factory, config=None):
        """
        初始化调度服务

        Args:
            db_factory: 数据库会话工厂函数
            config: 配置对象，可选
        """
        self.db_factory = db_factory
        self.config = config
        self.scheduler = BackgroundScheduler()
        self.is_running = False
        self.jobs = {}  # 存储任务信息 {job_id: job_info}

        # 初始化日志记录器
        self.logger = logging.getLogger(__name__)
        
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
            self.logger.info("调度器启动: 调度器已在运行中")
            return True
        
        try:
            self.scheduler.start()
            self.is_running = True
            self.logger.info("调度器启动: 调度器已成功启动")
            
            # 启动后检查数据库中所有auto_download为True的RSS源并创建调度任务
            self._setup_existing_auto_download_rss_sources()
            self.logger.info("调度器启动: 已完成现有auto_download RSS源的调度任务设置")
            
            return True
        except Exception as e:
            self.logger.error(f"调度器启动: 启动调度器失败: {e}")
            return False
    
    def _setup_existing_auto_download_rss_sources(self):
        """为已存在的auto_download为True的RSS源创建调度任务"""
        try:
            # 创建新的数据库会话来查询RSS源
            db = next(self.db_factory())
            from server.services.rss_service import RSSService
            rss_service = RSSService(db)
            
            # 获取所有auto_download为True的RSS源
            all_rss_sources = rss_service.get_all_rss_sources()
            self.logger.info(f"调度服务启动: 发现 {len(all_rss_sources)} 个RSS源，正在筛选auto_download为True的RSS源")
            auto_download_rss_sources = [rss for rss in all_rss_sources if rss.auto_download and rss.is_active]
            
            self.logger.info(f"调度服务启动: 找到 {len(auto_download_rss_sources)} 个需要自动检查的RSS源")
            
            for rss_source in auto_download_rss_sources:
                # 检查是否已经存在对应的调度任务
                job_id = f"rss_check_{rss_source.id}"
                if job_id not in self.jobs:
                    # 从配置获取检查间隔，默认120秒
                    check_interval = 120  # 默认值
                    if self.config:
                        check_interval = self.config.get('rss.check_interval', 120)
                    
                    # 创建调度任务
                    self.add_check_job(
                        rss_source_id=rss_source.id,
                        interval=check_interval,
                        auto_download=True
                    )
                    self.logger.info(f"调度服务启动: 为RSS源 {rss_source.id} ({rss_source.name}) 创建了调度任务，检查间隔: {check_interval}秒")
                else:
                    self.logger.info(f"调度服务启动: RSS源 {rss_source.id} ({rss_source.name}) 的调度任务已存在")
            
            db.close()
        except Exception as e:
            self.logger.error(f"调度服务启动: 设置已存在auto_download RSS源时出错: {e}")
    
    def stop_scheduler(self) -> bool:
        """停止调度器"""
        if not self.is_running:
            self.logger.info("调度器停止: 调度器未运行")
            return True
        
        try:
            self.scheduler.shutdown()
            self.is_running = False
            self.jobs.clear()
            self.logger.info("调度器停止: 调度器已成功停止")
            return True
        except Exception as e:
            self.logger.error(f"调度器停止: 停止调度器失败: {e}")
            return False
    
    def add_check_job(
        self,
        rss_source_id: int,
        interval: int = None,
        auto_download: bool = False
    ) -> Optional[str]:
        """
        添加RSS源检查任务
        
        Args:
            rss_source_id: RSS源ID
            interval: 检查间隔（秒），如果为None则使用配置文件中的默认值
            auto_download: 是否自动下载新链接
            
        Returns:
            任务ID，失败返回None
        """
        if not self.is_running:
            self.logger.warning("调度任务添加: 调度器未运行，无法添加任务")
            return None
        
        # 如果interval为None，使用配置文件中的默认值
        if interval is None:
            if self.config:
                interval = self.config.get('rss.check_interval', 3600)  # 从配置获取检查间隔，默认1小时
            else:
                interval = 3600  # 默认1小时
        
        job_id = f"rss_check_{rss_source_id}"
        
        # 如果任务已存在，先移除
        if job_id in self.jobs:
            self.logger.info(f"调度任务添加: 任务 {job_id} 已存在，先移除后重新添加")
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
            
            self.logger.info(f"调度任务添加: 成功为RSS源 {rss_source_id} 创建检查任务，间隔: {interval}秒，自动下载: {auto_download}")
            return job_id
        except Exception as e:
            self.logger.error(f"调度任务添加: 添加检查任务失败: {e}")
            return None
    
    def remove_check_job(self, job_id: str) -> bool:
        """移除检查任务"""
        try:
            self.scheduler.remove_job(job_id)
            if job_id in self.jobs:
                del self.jobs[job_id]
                self.logger.info(f"调度任务移除: 成功移除任务 {job_id}")
            else:
                self.logger.warning(f"调度任务移除: 尝试移除不存在的任务 {job_id}")
            return True
        except Exception as e:
            self.logger.error(f"调度任务移除: 移除检查任务失败: {e}")
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
                self.logger.warning(f"调度扫描: RSS源 {rss_source_id} 不存在")
                return {
                    "success": False,
                    "message": f"RSS源 {rss_source_id} 不存在"
                }

            self.logger.info(f"调度扫描: 开始检查RSS源 {rss_source_id} ({rss_source.name}) - URL: {rss_source.url}")

            # 检查RSS源是否激活
            if not rss_source.is_active:
                self.logger.warning(f"调度扫描: RSS源 {rss_source_id} 未激活，跳过检查")
                return {
                    "success": False,
                    "message": f"RSS源 {rss_source_id} 未激活"
                }

            # 获取已存在的链接URL
            existing_links = link_service.get_links(rss_source_id)
            existing_urls = [link.url for link in existing_links]
            self.logger.debug(f"调度扫描: RSS源 {rss_source_id} 已存在 {len(existing_urls)} 个链接")

            # 根据RSS源URL获取对应的解析器
            rss_parser = self._get_rss_parser(rss_source.url)
            if not rss_parser:
                self.logger.error(f"调度扫描: 不支持的RSS源: {rss_source.url}")
                return {
                    "success": False,
                    "message": f"不支持的RSS源: {rss_source.url}"
                }

            # 解析RSS源
            parse_result = rss_parser.parse_rss(rss_source.url, existing_urls)

            if not parse_result.get('success'):
                self.logger.error(f"调度扫描: RSS源 {rss_source_id} 解析失败: {parse_result.get('error', '未知错误')}")
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
                self.logger.info(f"调度扫描: RSS源 {rss_source_id} 检查完成，未发现新链接")
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
                link_type = link_info.get('link_type', 'magnet')
                link_url = link_info.get('url', '')
                
                # 如果是torrent类型，尝试转换为magnet链接
                if link_type == 'torrent':
                    try:
                        # 导入torrent到magnet转换工具
                        from server.utils.torrent_to_magnet import torrent_url_to_magnet
                        magnet_url = torrent_url_to_magnet(link_url)
                        if magnet_url:
                            # 使用转换后的magnet链接
                            self.logger.info(f"调度扫描: 转换torrent链接为magnet - {link_url} -> {magnet_url}")
                            link_type = 'magnet'
                            link_url = magnet_url
                        else:
                            # 如果转换失败，跳过此链接
                            self.logger.warning(f"调度扫描: 跳过无法转换的torrent链接: {link_url}")
                            continue
                    except ImportError:
                        # 如果没有安装bencodepy，跳过此链接
                        self.logger.warning(f"调度扫描: 跳过torrent链接（缺少转换库）: {link_url}")
                        continue
                    except Exception as e:
                        self.logger.error(f"调度扫描: 转换torrent链接时出错: {e}")
                        continue
                
                # 只处理允许的链接类型 (magnet, ed2k)
                if link_type not in ['magnet', 'ed2k']:
                    self.logger.warning(f"调度扫描: 跳过不支持的链接类型 {link_type}: {link_url}")
                    continue  # 跳过不支持的链接类型
                
                try:
                    link = link_service.add_link(
                        rss_source_id=rss_source_id,
                        episode_number=link_info.get('episode_number'),
                        episode_title=link_info.get('episode_title'),
                        link_type=link_type,
                        url=link_url,  # 使用可能已转换的URL
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

                        self.logger.info(f"调度扫描: 成功添加新链接 - ID: {link.id}, 类型: {link.link_type}, URL: {link.url[:50]}...")

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
                                    self.logger.info(f"调度扫描: 自动下载新链接 - 任务ID: {task.id}, 链接ID: {link.id}")
                except ValueError as e:
                    # 如果链接类型不被支持，记录错误但继续处理其他链接
                    self.logger.warning(f"调度扫描: 跳过不支持的链接类型: {e}")
                    continue

            self.logger.info(f"调度扫描: RSS源 {rss_source_id} 检查完成，新增 {new_links_count} 个链接")
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
            self.logger.error(f"调度扫描: 检查RSS源 {rss_source_id} 时发生错误: {str(e)}")
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