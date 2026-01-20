"""
动画相关模型
"""
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict


class AnimeBase(BaseModel):
    """动画基础模型"""
    title: str = Field(..., description="动画标题", min_length=1, max_length=255)
    title_en: str | None = Field(None, description="英文标题", max_length=255)
    description: str | None = Field(None, description="描述")
    cover_url: str | None = Field(None, description="封面URL", max_length=500)
    status: str = Field(default='ongoing', description="状态 (ongoing, completed, etc.)")
    total_episodes: int | None = Field(None, description="总集数", ge=0)


class AnimeCreate(AnimeBase):
    """创建动画请求模型"""
    pass


class AnimeUpdate(BaseModel):
    """更新动画请求模型"""
    title: str | None = Field(None, description="动画标题", min_length=1, max_length=255)
    title_en: str | None = Field(None, description="英文标题", max_length=255)
    description: str | None = Field(None, description="描述")
    cover_url: str | None = Field(None, description="封面URL", max_length=500)
    status: str | None = Field(None, description="状态 (ongoing, completed, etc.)")
    total_episodes: int | None = Field(None, description="总集数", ge=0)


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