"""
API请求和响应的Pydantic模型
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


# ========== 动画相关模型 ==========

class AnimeBase(BaseModel):
    """动画基础模型"""
    title: str = Field(..., description="动画标题", min_length=1, max_length=255)
    title_en: Optional[str] = Field(None, description="英文标题", max_length=255)
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL", max_length=500)
    status: str = Field(default='ongoing', description="状态 (ongoing, completed, etc.)")
    total_episodes: Optional[int] = Field(None, description="总集数", ge=0)


class AnimeCreate(AnimeBase):
    """创建动画请求模型"""
    pass


class AnimeUpdate(BaseModel):
    """更新动画请求模型"""
    title: Optional[str] = Field(None, description="动画标题", min_length=1, max_length=255)
    title_en: Optional[str] = Field(None, description="英文标题", max_length=255)
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL", max_length=500)
    status: Optional[str] = Field(None, description="状态 (ongoing, completed, etc.)")
    total_episodes: Optional[int] = Field(None, description="总集数", ge=0)


class AnimeResponse(AnimeBase):
    """动画响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    created_at: datetime
    updated_at: datetime


class AnimeListResponse(BaseModel):
    """动画列表响应模型"""
    total: int
    items: List[AnimeResponse]
    skip: int
    limit: int


# ========== 智能解析相关模型 ==========

class SmartParseAnimeRequest(BaseModel):
    """智能解析动画请求模型"""
    url: str = Field(..., description="动画网站链接")


class SmartParseAnimeResult(BaseModel):
    """智能解析动画结果模型"""
    title: str = Field(..., description="动画标题")
    title_en: Optional[str] = Field(None, description="英文标题")
    description: Optional[str] = Field(None, description="描述")
    cover_url: Optional[str] = Field(None, description="封面URL")
    status: str = Field(default='ongoing', description="状态")
    total_episodes: Optional[int] = Field(None, description="总集数")
    rss_sources: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="解析到的RSS源信息（可选）"
    )


class SmartParseAnimeResponse(BaseModel):
    """智能解析动画响应模型"""
    site_name: str = Field(..., description="网站名称")
    results: List[SmartParseAnimeResult] = Field(..., description="解析结果列表")


class SmartAddAnimeRequest(BaseModel):
    """智能添加动画请求模型"""
    url: str = Field(..., description="动画网站链接")
    auto_add_rss: bool = Field(default=True, description="是否自动解析并添加RSS源")
    anime_index: Optional[int] = Field(None, description="选择的动画索引（当有多个结果时）")
    rss_indices: Optional[List[int]] = Field(
        default_factory=list,
        description="选择的RSS源索引列表（用于连锁解析RSS时）"
    )


class SmartAddAnimeResponse(BaseModel):
    """智能添加动画响应模型"""
    anime: AnimeResponse
    rss_sources: Optional[List[Dict[str, Any]]] = Field(
        default_factory=list,
        description="添加的RSS源信息"
    )


# ========== 通用响应模型 ==========

class MessageResponse(BaseModel):
    """通用消息响应模型"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """错误响应模型"""
    error: str
    detail: Optional[str] = None
    success: bool = False


# ========== RSS源相关模型 ==========

class RSSSourceBase(BaseModel):
    """RSS源基础模型"""
    name: str = Field(..., description="RSS源名称", min_length=1, max_length=255)
    url: str = Field(..., description="RSS订阅链接", min_length=1, max_length=500)
    quality: Optional[str] = Field(None, description="画质 (1080p, 720p, etc.)", max_length=50)
    is_active: bool = Field(default=True, description="是否激活")
    auto_download: bool = Field(default=False, description="是否自动下载")


class RSSSourceCreate(RSSSourceBase):
    """创建RSS源请求模型"""
    anime_id: int = Field(..., description="动画ID")


class RSSSourceUpdate(BaseModel):
    """更新RSS源请求模型"""
    name: Optional[str] = Field(None, description="RSS源名称", min_length=1, max_length=255)
    url: Optional[str] = Field(None, description="RSS订阅链接", min_length=1, max_length=500)
    quality: Optional[str] = Field(None, description="画质 (1080p, 720p, etc.)", max_length=50)
    is_active: Optional[bool] = Field(None, description="是否激活")
    auto_download: Optional[bool] = Field(None, description="是否自动下载")


class RSSSourceResponse(RSSSourceBase):
    """RSS源响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    anime_id: int
    last_checked_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime


class RSSSourceListResponse(BaseModel):
    """RSS源列表响应模型"""
    total: int
    items: List[RSSSourceResponse]


# ========== 链接相关模型 ==========

class LinkBase(BaseModel):
    """链接基础模型"""
    episode_number: Optional[int] = Field(None, description="集数")
    episode_title: Optional[str] = Field(None, description="集标题", max_length=255)
    link_type: str = Field(default="magnet", description="链接类型 (magnet, ed2k, http, etc.)")
    url: str = Field(..., description="链接地址", min_length=1)
    file_size: Optional[int] = Field(None, description="文件大小 (bytes)")


class LinkCreate(LinkBase):
    """创建链接请求模型"""
    rss_source_id: int = Field(..., description="RSS源ID")


class LinkUpdate(BaseModel):
    """更新链接请求模型"""
    is_available: Optional[bool] = Field(None, description="链接是否可用")
    is_downloaded: Optional[bool] = Field(None, description="是否已下载")


class LinkResponse(LinkBase):
    """链接响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rss_source_id: int
    publish_date: Optional[datetime] = None
    is_downloaded: bool
    is_available: bool
    meta_data: Optional[str] = None
    created_at: datetime
    updated_at: datetime


class LinkListResponse(BaseModel):
    """链接列表响应模型"""
    total: int
    items: List[LinkResponse]
    skip: int
    limit: int


# ========== 下载器相关模型 ==========

class DownloaderBase(BaseModel):
    """下载器基础模型"""
    name: str = Field(..., description="下载器名称", min_length=1, max_length=255)
    downloader_type: str = Field(default="mock", description="下载器类型 (mock, aria2, pikpak, etc.)")
    max_concurrent_tasks: int = Field(default=3, description="最大并发任务数", ge=1)


class DownloaderCreate(DownloaderBase):
    """创建下载器请求模型"""
    config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="配置信息")
    is_default: bool = Field(default=False, description="是否为默认下载器")


class DownloaderUpdate(BaseModel):
    """更新下载器请求模型"""
    name: Optional[str] = Field(None, description="下载器名称", min_length=1, max_length=255)
    config: Optional[Dict[str, Any]] = Field(None, description="配置信息")
    is_active: Optional[bool] = Field(None, description="是否激活")
    is_default: Optional[bool] = Field(None, description="是否为默认下载器")
    max_concurrent_tasks: Optional[int] = Field(None, description="最大并发任务数", ge=1)


class DownloaderResponse(DownloaderBase):
    """下载器响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    config: str  # JSON字符串
    is_active: bool
    is_default: bool
    created_at: datetime
    updated_at: datetime


class DownloaderListResponse(BaseModel):
    """下载器列表响应模型"""
    total: int
    items: List[DownloaderResponse]


class DownloaderTestResponse(BaseModel):
    """下载器测试响应模型"""
    success: bool
    message: str
    downloader_type: Optional[str] = None


class DownloaderStatusResponse(BaseModel):
    """下载器状态响应模型"""
    success: bool
    downloader_id: int
    name: str
    type: str
    is_active: bool
    max_concurrent_tasks: int
    active_tasks: int
    total_tasks: int


# ========== 下载任务相关模型 ==========

class DownloadTaskBase(BaseModel):
    """下载任务基础模型"""
    file_path: Optional[str] = Field(None, description="本地保存路径", max_length=500)


class DownloadTaskCreate(DownloadTaskBase):
    """创建下载任务请求模型"""
    link_id: int = Field(..., description="链接ID")
    downloader_id: Optional[int] = Field(None, description="下载器ID（不指定则使用默认下载器）")


class DownloadTaskResponse(DownloadTaskBase):
    """下载任务响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    link_id: int
    rss_source_id: int
    downloader_id: int
    downloader_type: str
    status: str
    progress: float
    file_size: Optional[int]
    downloaded_size: int
    download_speed: float
    upload_speed: float
    error_message: Optional[str]
    retry_count: int
    task_id_external: Optional[str]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]


class DownloadTaskListResponse(BaseModel):
    """下载任务列表响应模型"""
    total: int
    items: List[DownloadTaskResponse]
    skip: int
    limit: int


class DownloadStatusResponse(BaseModel):
    """下载状态响应模型"""
    task_id: int
    status: str
    progress: float
    file_size: Optional[int]
    downloaded_size: int
    download_speed: float
    upload_speed: float
    error_message: Optional[str]
    retry_count: int
    created_at: Optional[str]
    started_at: Optional[str]
    completed_at: Optional[str]


# ========== 调度服务相关模型 ==========

class SchedulerJobCreate(BaseModel):
    """创建调度任务请求模型"""
    rss_source_id: int = Field(..., description="RSS源ID")
    interval: int = Field(default=3600, description="检查间隔（秒）", ge=60)
    auto_download: bool = Field(default=False, description="是否自动下载新链接")


class SchedulerJobResponse(BaseModel):
    """调度任务响应模型"""
    job_id: str
    name: str
    next_run_time: Optional[str]
    info: Dict[str, Any]


class SchedulerJobsResponse(BaseModel):
    """调度任务列表响应模型"""
    jobs: Dict[str, Dict[str, Any]]


class RSSCheckResponse(BaseModel):
    """RSS检查响应模型"""
    success: bool
    message: str
    rss_source_id: int
    new_links_count: int
    new_links: List[Dict[str, Any]]
    checked_at: str