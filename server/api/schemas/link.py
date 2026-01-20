"""
链接相关模型
"""
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class LinkBase(BaseModel):
    """链接基础模型"""
    episode_number: int | None = Field(None, description="集数")
    episode_title: str | None = Field(None, description="集标题", max_length=255)
    link_type: str = Field(default="magnet", description="链接类型 (magnet, ed2k, http, etc.)")
    url: str = Field(..., description="链接地址", min_length=1)
    file_size: int | None = Field(None, description="文件大小 (bytes)")


class LinkCreate(LinkBase):
    """创建链接请求模型"""
    rss_source_id: int = Field(..., description="RSS源ID")


class LinkUpdate(BaseModel):
    """更新链接请求模型"""
    is_available: bool | None = Field(None, description="链接是否可用")
    is_downloaded: bool | None = Field(None, description="是否已下载")


class LinkResponse(LinkBase):
    """链接响应模型"""
    model_config = ConfigDict(from_attributes=True)
    
    id: int
    rss_source_id: int
    publish_date: datetime | None = None
    is_downloaded: bool
    is_available: bool
    meta_data: str | None = None
    created_at: datetime
    updated_at: datetime


class LinkListResponse(BaseModel):
    """链接列表响应模型"""
    total: int
    items: List[LinkResponse]
    skip: int
    limit: int