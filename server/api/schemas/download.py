"""
下载任务相关模型
"""
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DownloadTaskBase(BaseModel):
    """下载任务基础模型"""
    file_path: str | None = Field(None, description="本地保存路径", max_length=500)


class DownloadTaskCreate(DownloadTaskBase):
    """创建下载任务请求模型"""
    link_id: int = Field(..., description="链接ID")
    downloader_id: int | None = Field(None, description="下载器ID（不指定则使用默认下载器）")


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
    file_size: int | None
    downloaded_size: int
    download_speed: float
    upload_speed: float
    error_message: str | None
    retry_count: int
    task_id_external: str | None
    created_at: datetime
    started_at: datetime | None
    completed_at: datetime | None


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
    file_size: int | None
    downloaded_size: int
    download_speed: float
    upload_speed: float
    error_message: str | None
    retry_count: int
    created_at: str | None
    started_at: str | None
    completed_at: str | None