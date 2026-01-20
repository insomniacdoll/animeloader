"""
API请求和响应的Pydantic模型
"""
from .common import MessageResponse, ErrorResponse
from .anime import (
    AnimeBase,
    AnimeCreate,
    AnimeUpdate,
    AnimeResponse,
    AnimeListResponse
)
from .rss import (
    RSSSourceBase,
    RSSSourceCreate,
    RSSSourceUpdate,
    RSSSourceResponse,
    RSSSourceListResponse
)
from .link import (
    LinkBase,
    LinkCreate,
    LinkUpdate,
    LinkResponse,
    LinkListResponse
)
from .downloader import (
    DownloaderBase,
    DownloaderCreate,
    DownloaderUpdate,
    DownloaderResponse,
    DownloaderListResponse,
    DownloaderTestResponse,
    DownloaderStatusResponse
)
from .download import (
    DownloadTaskBase,
    DownloadTaskCreate,
    DownloadTaskResponse,
    DownloadTaskListResponse,
    DownloadStatusResponse
)
from .scheduler import (
    SchedulerJobCreate,
    SchedulerJobResponse,
    SchedulerJobsResponse,
    RSSCheckResponse
)
from .smart_parser import (
    SmartParseAnimeRequest,
    SmartParseAnimeResult,
    SmartParseAnimeResponse,
    SmartAddAnimeRequest,
    SmartAddAnimeResponse
)

__all__ = [
    # Common
    "MessageResponse",
    "ErrorResponse",
    # Anime
    "AnimeBase",
    "AnimeCreate",
    "AnimeUpdate",
    "AnimeResponse",
    "AnimeListResponse",
    # RSS
    "RSSSourceBase",
    "RSSSourceCreate",
    "RSSSourceUpdate",
    "RSSSourceResponse",
    "RSSSourceListResponse",
    # Link
    "LinkBase",
    "LinkCreate",
    "LinkUpdate",
    "LinkResponse",
    "LinkListResponse",
    # Downloader
    "DownloaderBase",
    "DownloaderCreate",
    "DownloaderUpdate",
    "DownloaderResponse",
    "DownloaderListResponse",
    "DownloaderTestResponse",
    "DownloaderStatusResponse",
    # Download
    "DownloadTaskBase",
    "DownloadTaskCreate",
    "DownloadTaskResponse",
    "DownloadTaskListResponse",
    "DownloadStatusResponse",
    # Scheduler
    "SchedulerJobCreate",
    "SchedulerJobResponse",
    "SchedulerJobsResponse",
    "RSSCheckResponse",
    # Smart Parser
    "SmartParseAnimeRequest",
    "SmartParseAnimeResult",
    "SmartParseAnimeResponse",
    "SmartAddAnimeRequest",
    "SmartAddAnimeResponse",
]