"""
下载器相关模型
"""
from typing import List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class DownloaderBase(BaseModel):
    """下载器基础模型"""
    name: str = Field(..., description="下载器名称", min_length=1, max_length=255)
    downloader_type: str = Field(default="mock", description="下载器类型 (mock, aria2, pikpak, etc.)")
    max_concurrent_tasks: int = Field(default=3, description="最大并发任务数", ge=1)


class DownloaderCreate(DownloaderBase):
    """创建下载器请求模型"""
    config: Dict[str, Any] | None = Field(default_factory=dict, description="配置信息")
    is_default: bool = Field(default=False, description="是否为默认下载器")


class DownloaderUpdate(BaseModel):
    """更新下载器请求模型"""
    name: str | None = Field(None, description="下载器名称", min_length=1, max_length=255)
    config: Dict[str, Any] | None = Field(None, description="配置信息")
    is_active: bool | None = Field(None, description="是否激活")
    is_default: bool | None = Field(None, description="是否为默认下载器")
    max_concurrent_tasks: int | None = Field(None, description="最大并发任务数", ge=1)


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
    downloader_type: str | None = None


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