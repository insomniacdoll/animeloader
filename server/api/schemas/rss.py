"""
RSS源相关模型
"""
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class RSSSourceBase(BaseModel):
    """RSS源基础模型"""
    name: str = Field(..., description="RSS源名称", min_length=1, max_length=255)
    url: str = Field(..., description="RSS订阅链接", min_length=1, max_length=500)
    quality: str | None = Field(None, description="画质 (1080p, 720p, etc.)", max_length=50)
    is_active: bool = Field(default=True, description="是否激活")
    auto_download: bool = Field(default=False, description="是否自动下载")


class RSSSourceCreate(RSSSourceBase):
    """创建RSS源请求模型"""
    anime_id: int = Field(..., description="动画ID")


class RSSSourceUpdate(BaseModel):
    """更新RSS源请求模型"""
    name: str | None = Field(None, description="RSS源名称", min_length=1, max_length=255)
    url: str | None = Field(None, description="RSS订阅链接", min_length=1, max_length=500)
    quality: str | None = Field(None, description="画质 (1080p, 720p, etc.)", max_length=50)
    is_active: bool | None = Field(None, description="是否激活")
    auto_download: bool | None = Field(None, description="是否自动下载")


class RSSSourceResponse(RSSSourceBase):
    """RSS源响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    anime_id: int
    last_checked_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class RSSSourceListResponse(BaseModel):
    """RSS源列表响应模型"""
    total: int
    items: List[RSSSourceResponse]